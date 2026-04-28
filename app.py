from flask import Flask, render_template, session, redirect, url_for, request, jsonify
import pandas as pd
import io
import os
import time
import google.generativeai as genai
from gtts import gTTS
# --- New Imports for Database ---
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- Gemini API Configuration ---
GEMINI_API_KEY = "Type ur gemini api key here" # Make sure your key is here
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-flash-latest')

# --- Admin Credentials ---
ADMIN_USER = "admin"
ADMIN_PASS = "password123"

# --- In-memory data store ---
data_frames = {}

# --- Database Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey12345'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
# Set the database file path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# --- Define the Database Table Structure ---
class ConversationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    user_question = db.Column(db.String(500), nullable=False)
    generated_code = db.Column(db.String(500))
    bot_response = db.Column(db.String(1000))
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# --- All your existing Flask routes will go here ---
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
    # ... (Keep this function exactly as it was)
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

# --- This is the function we will update in the next step ---
@app.route('/get_response', methods=['POST'])
def get_response():
    user_question = request.json.get('message')
    user_id = session.get('user_id')
    username = session.get('username')

    if not user_id or user_id not in data_frames:
        return jsonify({'bot_text': 'Error: No data file found. Please upload a file first.'})

    df = data_frames[user_id]['df']
    columns = data_frames[user_id]['columns']

    code_generation_prompt = f"""
    You are an expert Python Pandas data analyst. Your task is to translate the user's question into a single, executable line of Python code for a pandas DataFrame named 'df'.
    The DataFrame `df` has the following columns: {columns}
    --- RULES ---
    1. Your output MUST be a single line of Python code.
    2. You MUST use the exact column names provided.
    3. The code must produce a final result.
    4. Do NOT add any explanation, comments, or the word "python".
    5. If the question cannot be answered, return the word "Error: Unanswerable".
    --- EXAMPLE ---
    User Question: "How many people are in the Engineering department?"
    Code: df[df['Department'] == 'Engineering'].shape[0]
    ---
    User Question: "{user_question}"
    Code:
    """

    bot_text = "I encountered an error. Please try rephrasing."
    generated_code = "N/A" # Default value
    try:
        response = model.generate_content(code_generation_prompt)
        generated_code = response.text.strip().replace('`', '').replace('python', '')

        if "Error:" in generated_code:
            bot_text = "I'm sorry, I can't answer that question with the available data."
        else:
            result = eval(generated_code, {"df": df, "pd": pd})
            answer_formatting_prompt = f"""
            You are a helpful data assistant. Your task is to present a calculated result to a user in a friendly, complete sentence.
            User's original question: "{user_question}"
            The calculated answer is: {result}
            RULES:
            1. Be concise and natural.
            2. Do not mention that a calculation was performed.
            3. If the result is a table or a long list, summarize it briefly.
            Answer:
            """
            final_response = model.generate_content(answer_formatting_prompt)
            bot_text = final_response.text.strip()

    except Exception as e:
        print(f"--- EXECUTION OR API ERROR --- \n{e}\n--------------------------")
        bot_text = "I encountered an error trying to answer that. Please try rephrasing your question."
        generated_code = f"ERROR: {e}" # Log the error

    log_entry = ConversationLog(
        username=username,
        user_question=user_question,
        generated_code=generated_code,
        bot_response=bot_text
    )
    db.session.add(log_entry)
    db.session.commit()

    try:
        tts = gTTS(text=bot_text, lang='en', slow=False)
        audio_file_path = os.path.join('static', 'response.mp3')
        tts.save(audio_file_path)

        # --- THIS IS THE MODIFIED LINE ---
        # We add a unique timestamp to the URL to prevent caching
        timestamp = int(time.time())
        audio_url = url_for('static', filename='response.mp3', t=timestamp)

    except Exception as e:
        print(f"gTTS Error: {e}")
        audio_url = None

    return jsonify({'bot_text': bot_text, 'audio_url': audio_url})

@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('chat'))
    if 'username' not in session:
        return redirect(url_for('index'))
        
    # --- NEW: Code to read the accuracy score ---
    accuracy_score = "N/A" # Default value if file doesn't exist
    try:
        with open('accuracy.txt', 'r') as f:
            accuracy_score = f.read().strip()
    except FileNotFoundError:
        print("Accuracy file not found. Run 'python evaluate.py' first.")
    except Exception as e:
        print(f"Error reading accuracy file: {e}")
            
    # --- NEW: Query the database for all conversation logs ---
    try:
        # Fetch all logs from the database, ordering by the most recent first
        all_logs = ConversationLog.query.order_by(ConversationLog.timestamp.desc()).all()
        
        # --- NEW: Perform simple analysis ---
        total_interactions = len(all_logs)
        # Convert to DataFrame for easier analysis with Pandas
        df_logs = pd.DataFrame([(log.username, log.user_question) for log in all_logs], columns=['username', 'question'])
        
        most_active_user = "N/A"
        if not df_logs.empty:
            most_active_user = df_logs['username'].mode()[0]

    except Exception as e:
        print(f"Dashboard Error: {e}")
        all_logs = []
        total_interactions = 0
        most_active_user = "Error"
        
    # Pass the logs and analytics to the template
    return render_template('dashboard.html', 
                           logs=all_logs, 
                           total_interactions=total_interactions,
                           most_active_user=most_active_user,
                           accuracy_score=accuracy_score) # <-- ADDED THIS

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    if user_id and user_id in data_frames:
        del data_frames[user_id]
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # --- Create the database file if it doesn't exist ---
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)