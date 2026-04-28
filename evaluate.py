import google.generativeai as genai
import pandas as pd
import json
import time  # <--- THIS IS NEW (Line 1)

# --- CONFIGURE YOUR API KEY HERE ---
# Make sure this key is correct
GEMINI_API_KEY = "Type ur gemini api key here" 
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('models/gemini-flash-latest')

def get_generated_code(user_question, columns):
    """
    Takes a user question and column list, and returns the AI-generated code.
    This logic is copied from your app.py to ensure the test is accurate.
    """
    # Convert list of columns to a string for the prompt
    columns_str = ", ".join([f"'{col}'" for col in columns])
    
    code_generation_prompt = f"""
    You are an expert Python Pandas data analyst. Your task is to translate the user's question into a single, executable line of Python code for a pandas DataFrame named 'df'.
    The DataFrame `df` has the following columns: [{columns_str}]
    --- RULES ---
    1. Your output MUST be a single line of Python code.
    2. You MUST use the exact column names provided, including spaces or parentheses.
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
    try:
        response = model.generate_content(code_generation_prompt)
        # Clean the response just like in the app
        generated_code = response.text.strip().replace('`', '').replace('python', '')
        return generated_code
    except Exception as e:
        print(f"API Error: {e}")
        return "ERROR_API"

def run_evaluation():
    """
    Loads the benchmark, runs each question through the AI,
    compares the result, and calculates the accuracy score.
    """
    print("--- Starting Code Generation Accuracy Evaluation ---")
    
    try:
        with open('benchmark.json', 'r') as f:
            benchmark_data = json.load(f)
    except FileNotFoundError:
        print("ERROR: 'benchmark.json' file not found.")
        print("Please create it first.")
        return
        
    # --- THIS IS THE CRITICAL UPDATE ---
    # This list now matches your industry_data.csv file
    test_columns = [
        'Year', 'Month', 'Department', 'Manager', 'Workers', 
        'Average_Salary(Salary_per_worker)', 'Total_Salary', 
        'Monthly_Sales', 'Monthly_Profit'
    ]
    
    correct_predictions = 0
    total_questions = len(benchmark_data)
    
    if total_questions == 0:
        print("No questions found in benchmark.json. Aborting.")
        return

    for i, item in enumerate(benchmark_data):
        question = item['question']
        expected_code = item['expected_code']
        
        # Get the code from our AI model
        generated_code = get_generated_code(question, test_columns)
        
        print(f"\n({i+1}/{total_questions}) Evaluating Question: {question}")
        print(f"  - Expected Code: {expected_code}")
        print(f"  - Generated Code: {generated_code}")
        
        # Compare the generated code with the expected answer
        if generated_code == expected_code:
            correct_predictions += 1
            print("  - Result: ✅ MATCH")
        else:
            print("  - Result: ❌ FAIL")
            
        # --- THIS IS NEW (Line 2) ---
        # Add a 6-second pause to respect the 10-requests-per-minute limit
        print("  - Pausing for 6 seconds to respect API rate limit...")
        time.sleep(6)
            
    # Calculate the final accuracy score
    accuracy = (correct_predictions / total_questions) * 100
    
    print("\n--- Evaluation Complete ---")
    print(f"Total Questions: {total_questions}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Code Generation Accuracy: {accuracy:.2f}%")
    print("---------------------------\n")

    # --- SAVE THE SCORE TO A FILE ---
    try:
        with open('accuracy.txt', 'w') as f:
            f.write(f"{accuracy:.2f}")
        print("Successfully saved accuracy score to 'accuracy.txt'")
    except Exception as e:
        print(f"Error saving accuracy score to file: {e}")

if __name__ == '__main__':
    run_evaluation()