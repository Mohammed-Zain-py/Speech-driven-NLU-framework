import google.generativeai as genai

# --- IMPORTANT ---
# PASTE THE SAME API KEY you are using in your app.py file here.
GEMINI_API_KEY = "Type ur gemini api key here"

genai.configure(api_key=GEMINI_API_KEY)

print("--- Finding available models for your API key ---")

# Loop through all the models and print the ones that can be used for our task
for model in genai.list_models():
  # We need a model that supports the 'generateContent' method
  if 'generateContent' in model.supported_generation_methods:
    print(model.name)

print("-------------------------------------------------")