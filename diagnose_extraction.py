"""
Diagnostic script to test resume extraction and identify issues
Run this to see detailed logs of what happens during extraction
"""
import os
import sys
import logging
from pathlib import Path

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_extraction(file_path: str):
    """Test extraction with detailed logging"""
    from resume_parser import GeminiResumeParser
    
    print("\n" + "="*70)
    print("RESUME EXTRACTION DIAGNOSTIC TEST")
    print("="*70)
    print(f"File: {file_path}")
    print("="*70 + "\n")
    
    # Check file exists
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY not found in environment")
        return False
    else:
        print(f"API Key: {api_key[:10]}...{api_key[-4:]} (valid)")
    
    # Initialize parser
    print("\n[STEP 1] Initializing parser...")
    try:
        parser = GeminiResumeParser()
        print("✓ Parser initialized successfully")
    except Exception as e:
        print(f"✗ ERROR initializing parser: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test PDF text extraction
    print("\n[STEP 2] Testing PDF text extraction...")
    try:
        if file_path.lower().endswith('.pdf'):
            text = parser._extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            text = parser._extract_text_from_docx(file_path)
        else:
            print(f"✗ Unsupported file type: {file_path}")
            return False
        
        text_length = len(text) if text else 0
        print(f"✓ Extracted {text_length:,} characters from file")
        
        if text_length < 50:
            print(f"⚠ WARNING: Very little text extracted ({text_length} chars)")
            print("  This could indicate:")
            print("    - PDF is image-based (scanned) and needs OCR")
            print("    - PDF is corrupted or encrypted")
            print("    - PDF extraction library issue")
            print("\nFirst 200 chars of extracted text:")
            print("-" * 70)
            print(text[:200] if text else "(empty)")
            print("-" * 70)
            return False
        else:
            print(f"✓ Text extraction successful")
            print(f"\nFirst 300 characters of extracted text:")
            print("-" * 70)
            print(text[:300])
            print("-" * 70)
            
    except Exception as e:
        print(f"✗ ERROR extracting text: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test full extraction
    print("\n[STEP 3] Testing full extraction with Gemini API...")
    print("This may take 30-60 seconds...")
    try:
        result = parser.extract_resume_data(file_path)
        
        print("\n" + "="*70)
        print("EXTRACTION RESULT:")
        print("="*70)
        print(f"Candidate Name: {result.get('candidate_name', 'N/A')}")
        print(f"Skills: {result.get('skills', [])}")
        print(f"  - Count: {len(result.get('skills', []))}")
        print(f"Experience Years: {result.get('experience_years', 0)}")
        print(f"Education Level: {result.get('education_level', 'N/A')}")
        print(f"Certifications: {result.get('certifications', [])}")
        print(f"Languages: {result.get('languages', [])}")
        print(f"Location: {result.get('location', 'N/A')}")
        print("="*70)
        
        # Check if extraction failed
        if result.get('candidate_name') == 'Unknown' and not result.get('skills'):
            print("\n" + "="*70)
            print("⚠ EXTRACTION FAILED - All fields are empty/unknown")
            print("="*70)
            print("\nPossible causes:")
            print("  1. Gemini API call failed (check API key, quota, network)")
            print("  2. JSON parsing failed (API returned invalid JSON)")
            print("  3. PDF text extraction failed (image-based PDF)")
            print("  4. API response format changed")
            return False
        else:
            print("\n" + "="*70)
            print("✓ EXTRACTION SUCCESSFUL!")
            print("="*70)
            return True
            
    except Exception as e:
        print(f"\n✗ ERROR during extraction: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Look for test files
    test_files = []
    
    # Check dataset folder
    dataset_dir = Path("dataset")
    if dataset_dir.exists():
        test_files.extend(list(dataset_dir.glob("*.pdf")))
        test_files.extend(list(dataset_dir.glob("*.docx")))
    
    # Check current directory
    test_files.extend(list(Path(".").glob("*.pdf")))
    test_files.extend(list(Path(".").glob("*.docx")))
    
    if len(sys.argv) > 1:
        # Use provided file
        test_file = sys.argv[1]
    elif test_files:
        # Use first found file
        test_file = str(test_files[0])
        print(f"Found test file: {test_file}")
    else:
        print("No test files found!")
        print("\nUsage:")
        print("  python diagnose_extraction.py <path_to_resume.pdf>")
        print("\nOr place a PDF file in the current directory or dataset/ folder")
        sys.exit(1)
    
    success = test_extraction(test_file)
    sys.exit(0 if success else 1)








