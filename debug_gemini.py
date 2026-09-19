#!/usr/bin/env python3
"""
Quick test script to debug Gemini API issues
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()

def test_api_key():
    """Test if the API key is valid and working"""
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        logger.error("❌ No GOOGLE_API_KEY found in environment")
        return False
    
    logger.info(f"✅ API key found: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Test with Gemini 3.0 model
        model = genai.GenerativeModel("gemini-3.0-flash")
        logger.info("✅ Model initialized successfully with gemini-3.0-flash")
        
        # Simple test request
        response = model.generate_content("Say 'Hello' in JSON format")
        logger.info(f"✅ API call successful: {response.text}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ API test failed: {type(e).__name__}: {e}")
        return False

def test_resume_parser():
    """Test the resume parser directly"""
    try:
        from resume_parser import GeminiResumeParser
        
        logger.info("🔧 Testing resume parser...")
        parser = GeminiResumeParser()
        logger.info("✅ Resume parser initialized")
        
        # Test with simple text
        test_text = "John Doe\nSkills: Python, SQL\nExperience: 5 years\nEducation: Bachelors"
        result = parser.extract_from_text(test_text)
        
        logger.info(f"✅ Text extraction result: {result}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Resume parser test failed: {type(e).__name__}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting Gemini API diagnostics...")
    
    # Test 1: Basic API connectivity
    api_ok = test_api_key()
    
    # Test 2: Resume parser
    parser_ok = test_resume_parser()
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("📊 DIAGNOSTIC SUMMARY")
    logger.info("="*50)
    logger.info(f"API Key Test: {'✅ PASS' if api_ok else '❌ FAIL'}")
    logger.info(f"Resume Parser Test: {'✅ PASS' if parser_ok else '❌ FAIL'}")
    
    if api_ok and parser_ok:
        logger.info("🎉 All tests passed! The system should work correctly.")
    else:
        logger.error("🚨 Issues detected. Check the logs above for details.")
