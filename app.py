from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import pandas as pd
import io
import os
import time
import google.generativeai as genai
from gtts import gTTS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

# --- Gemini API Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") # Make sure your key is here
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-3.5-flash')

# --- Admin Credentials ---
ADMIN_USER = os.getenv('ADMIN_USER')
ADMIN_PASS = os.getenv('ADMIN_PASS') # You can also create a .env file and move the API key and this password there 

# --- In-memory data store ---
data_frames = {}

# --- Database Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class ConversationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    user_question = db.Column(db.String(500), nullable=False)
    generated_code = db.Column(db.String(500))
    bot_response = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form.get('password')
    session['username'] = username
    session['user_id'] = os.urandom(24).hex()
    if username == ADMIN_USER and password == ADMIN_PASS:
        session['role'] = 'admin'
    else:
        session['role'] = 'user'
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))
    if 'user_id' not in session:
        session['user_id'] = os.urandom(24).hex()
    user_id = session.get('user_id')
    if user_id in data_frames:
        column_names = data_frames[user_id]['columns']
        return render_template('chat.html', file_uploaded=True, columns=column_names)
    else:
        return render_template('chat.html', file_uploaded=False)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'username' not in session:
        return redirect(url_for('index'))
    file = request.files.get('file')
    if not file or file.filename == '':
        return "No file selected", 400
    if not file.filename.endswith('.csv'):
        return "Invalid file type. Please upload a .csv file.", 400
    try:
        df = pd.read_csv(file.stream)
        df = df.dropna(axis=1, how='all')
        user_id = session['user_id']
        data_frames[user_id] = {'df': df, 'columns': df.columns.tolist(), 'filename': file.filename}
    except Exception as e:
        print(f"------------ ERROR PROCESSING FILE ------------\nError: {e}\n---------------------------------------------")
        return "Error processing file. Check terminal for details.", 500
    return redirect(url_for('chat'))

@app.route('/get_response', methods=['POST'])
def get_response():
    user_question = request.json.get('message')
    user_id = session.get('user_id')
    username = session.get('username')

    if not user_id or user_id not in data_frames:
        return jsonify({'bot_text': 'Error: No data file found. Please upload a file first.'})

    df = data_frames[user_id]['df']
    columns = data_frames[user_id]['columns']

    # --- MEMORY: Fetch the last 3 interactions ---
    past_logs = ConversationLog.query.filter_by(username=username).order_by(ConversationLog.timestamp.desc()).limit(3).all()
    history_text = ""
    if past_logs:
        history_text = "\n--- CONVERSATION HISTORY ---\n"
        for log in reversed(past_logs): 
            history_text += f"User: {log.user_question}\nSystem: {log.bot_response}\n"
        history_text += "----------------------------\n"

    code_generation_prompt = f"""
    You are an expert Python Pandas data analyst. Translate the user's question into a single, executable line of Python code for a pandas DataFrame named 'df'.
    Columns: {columns}
    {history_text}
    --- RULES ---
    1. Your output MUST be a single line of Python code.
    2. Use the exact column names provided.
    3. Do NOT add any explanation, comments, or the word "python".
    4. MULTI-LANGUAGE RULE: If the user asks in Kannada, Hindi, or any mix of languages (e.g. Kanglish), internally translate it to understand the intent, but your final output MUST STILL BE ONLY RAW PYTHON CODE.
    5. DATA VISUALIZATION: If the user asks for a chart, graph, or visual trend, your pandas code MUST return a Python dictionary with this exact structure: 
       {{'labels': list_of_categorical_names_NOT_index_numbers, 'values': list_of_y_values, 'type': 'bar', 'title': 'A short title'}}
       Example: {{'labels': df['Department'].tolist(), 'values': df['Total_Salary'].tolist(), 'type': 'bar', 'title': 'Salary by Dept'}}
    ---
    User Question: "{user_question}"
    Code:
    """

    bot_text = "I encountered an error. Please try rephrasing."
    generated_code = "N/A"
    chart_data = None
    lang_code = 'en' # Safety default

    try:
        response = model.generate_content(code_generation_prompt)
        generated_code = response.text.strip().replace('`', '').replace('python', '')

        if "Error:" in generated_code:
            bot_text = "I'm sorry, I can't answer that question with the available data."
        else:
            result = eval(generated_code, {"df": df, "pd": pd})
            
            if isinstance(result, dict) and 'labels' in result and 'values' in result:
                chart_data = result
                calculated_context = "Chart data generated successfully."
            else:
                calculated_context = str(result)

            answer_formatting_prompt = f"""
            You are a helpful data assistant. 
            User's original question: "{user_question}"
            Calculated result: {calculated_context}
            --- RULES ---
            1. Be concise and natural. Do not mention that a calculation was performed.
            2. If a chart was generated, simply say "Here is the chart you requested."
            3. MULTI-LANGUAGE: You MUST reply in the exact same language/script the user asked the question in.
            4. You MUST append the two-letter language code of your response at the very end, separated by '|||'. (Use 'kn' for Kannada, 'hi' for Hindi, 'en' for English).
            Answer:
            """
            
            final_response = model.generate_content(answer_formatting_prompt).text.strip()
            
            parts = final_response.split('|||')
            bot_text = parts[0].strip()
            lang_code = parts[1].strip().lower() if len(parts) > 1 else 'en'
            
            valid_langs = ['en', 'hi', 'kn', 'es', 'fr', 'de', 'it', 'pt', 'ta', 'te', 'ml']
            if lang_code not in valid_langs:
                lang_code = 'en'

    except Exception as e:
        print(f"--- EXECUTION OR API ERROR --- \n{e}\n--------------------------")
        # Smart fallback: If chart succeeded but text failed, just acknowledge the chart!
        if chart_data:
            bot_text = "Here is the visualization you requested. (Note: Audio response timed out)."
        else:
            bot_text = "I encountered an error trying to answer that. Let me provide the data in English instead."
        
        generated_code = f"ERROR: {e}"
        lang_code = 'en'

    log_entry = ConversationLog(
        username=username,
        user_question=user_question,
        generated_code=generated_code,
        bot_response=bot_text
    )
    db.session.add(log_entry)
    db.session.commit()

    audio_url = None
    try:
        tts = gTTS(text=bot_text, lang=lang_code, slow=False)
        audio_file_path = os.path.join('static', 'response.mp3')
        tts.save(audio_file_path)
        timestamp = int(time.time())
        audio_url = url_for('static', filename='response.mp3', t=timestamp)
    except ValueError:
        try:
            print(f"Language {lang_code} rejected. Falling back to English audio.")
            tts = gTTS(text=bot_text, lang='en', slow=False)
            tts.save(audio_file_path)
            audio_url = url_for('static', filename='response.mp3', t=int(time.time()))
        except Exception as fallback_error:
            print(f"Total audio failure: {fallback_error}")

    return jsonify({'bot_text': bot_text, 'audio_url': audio_url, 'chart_data': chart_data})

@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('chat'))
    if 'username' not in session:
        return redirect(url_for('index'))
        
    accuracy_score = "N/A" 
    try:
        with open('accuracy.txt', 'r') as f:
            accuracy_score = f.read().strip()
    except FileNotFoundError:
        pass
            
    try:
        all_logs = ConversationLog.query.order_by(ConversationLog.timestamp.desc()).all()
        total_interactions = len(all_logs)
        df_logs = pd.DataFrame([(log.username, log.user_question) for log in all_logs], columns=['username', 'question'])
        most_active_user = "N/A"
        if not df_logs.empty:
            most_active_user = df_logs['username'].mode()[0]
    except Exception as e:
        all_logs = []
        total_interactions = 0
        most_active_user = "Error"
        
    return render_template('dashboard.html', 
                           logs=all_logs, 
                           total_interactions=total_interactions,
                           most_active_user=most_active_user,
                           accuracy_score=accuracy_score)

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id and user_id in data_frames:
        del data_frames[user_id]
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)