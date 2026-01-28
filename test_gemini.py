import os
import google.generativeai as genai
import json

# Try to load from secrets.toml first
try:
    with open(".streamlit/secrets.toml", "r") as f:
        for line in f:
            if "GEMINI_API_KEY" in line:
                key = line.split("=")[1].strip().strip('"').strip("'")
                os.environ["GEMINI_API_KEY"] = key
                break
except:
    pass

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ Error: GEMINI_API_KEY not found in environment or secrets.toml")
else:
    print(f"✅ API Key found (starts with: {api_key[:8]}...)")
    try:
        genai.configure(api_key=api_key)
        print("Available Models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name}")
        
        model = genai.GenerativeModel('gemini-2.5-flash')  # Updated to use a supported model
        response = model.generate_content("Hello, are you working? Reply with 'Yes, I am working!' if you see this.")
        print(f"🤖 Gemini Response: {response.text.strip()}")
        print("\n✨ SUCCESS: Gemini API is configured and working correctly!")
    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")