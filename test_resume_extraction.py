"""Test resume extraction to debug the issue"""
import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from resume_parser import GeminiResumeParser

# Check API key
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in environment")
    sys.exit(1)
else:
    print(f"API Key found: {api_key[:10]}...{api_key[-4:]}")

# Initialize parser
print("\nInitializing parser...")
try:
    parser = GeminiResumeParser()
    print("Parser initialized successfully")
except Exception as e:
    print(f"ERROR initializing parser: {e}")
    sys.exit(1)

# Test with a sample PDF if available
test_files = list(Path(".").glob("*.pdf")) + list(Path(".").glob("*.docx"))
if not test_files:
    print("\nNo PDF or DOCX files found in current directory for testing")
    print("Please provide a resume file path to test:")
    print("Usage: python test_resume_extraction.py <path_to_resume.pdf>")
    sys.exit(0)

# Use first available file
test_file = test_files[0]
print(f"\nTesting extraction with: {test_file}")

if not test_file.exists():
    print(f"ERROR: File not found: {test_file}")
    sys.exit(1)

print(f"File size: {test_file.stat().st_size} bytes")
print("\n" + "="*60)
print("Starting extraction...")
print("="*60 + "\n")

try:
    result = parser.extract_resume_data(str(test_file))
    
    print("\n" + "="*60)
    print("EXTRACTION RESULT:")
    print("="*60)
    print(f"Candidate Name: {result.get('candidate_name', 'N/A')}")
    print(f"Skills: {result.get('skills', [])} (count: {len(result.get('skills', []))})")
    print(f"Experience Years: {result.get('experience_years', 0)}")
    print(f"Education Level: {result.get('education_level', 'N/A')}")
    print(f"Certifications: {result.get('certifications', [])}")
    print(f"Languages: {result.get('languages', [])}")
    print(f"Location: {result.get('location', 'N/A')}")
    
    # Check if extraction failed
    if result.get('candidate_name') == 'Unknown' and not result.get('skills'):
        print("\n" + "="*60)
        print("WARNING: Extraction appears to have failed!")
        print("All fields are empty/unknown - this indicates a problem.")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("SUCCESS: Extraction completed with data!")
        print("="*60)
        
except Exception as e:
    print(f"\nERROR during extraction: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)








