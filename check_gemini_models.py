"""
Check available Gemini models
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if API key is available
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ GOOGLE_API_KEY not found")
    exit(1)

# Configure Gemini
genai.configure(api_key=api_key)

# List available models
print("Available Gemini models:")
models = genai.list_models()

for model in models:
    print(f"  - {model.name}")
    print(f"    Display name: {model.display_name}")
    print(f"    Description: {model.description}")
    print(f"    Supported methods: {model.supported_generation_methods}")
    print()
