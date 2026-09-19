import sys
import os

# Add the project directory to Python path
sys.path.insert(0, r'P:\JOB Matching')

try:
    from resume_parser_fallback import FallbackResumeParser
    print("✅ Successfully imported FallbackResumeParser")
    
    from resume_parser import GeminiResumeParser
    print("✅ Successfully imported GeminiResumeParser")
    
    print("\n✅ All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("Test completed successfully!")
