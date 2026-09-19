"""
Test script for Gemini API integration in Resume Matcher
"""

import os
import sys
from dotenv import load_dotenv
from ml_engine import NeuralResumeMatcher

# Load environment variables
load_dotenv()

def test_gemini_integration():
    """Test the Gemini API integration with sample data."""
    
    # Check if API key is available
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please set up your .env file with a valid Google API key")
        return False
    
    print("✅ Google API key found")
    
    # Initialize the matcher
    print("\n🚀 Initializing Neural Resume Matcher with Gemini integration...")
    matcher = NeuralResumeMatcher()
    
    # Check model info
    model_info = matcher.get_model_info()
    print(f"\n📊 Model Info:")
    print(f"  - Model: {model_info['model_name']}")
    print(f"  - Embedding Dimension: {model_info['embedding_dimension']}")
    print(f"  - Gemini Available: {'✅' if model_info['gemini_available'] else '❌'}")
    print(f"  - Features: {', '.join(model_info['features'])}")
    
    if not model_info['gemini_available']:
        print("\n❌ Gemini API is not available. Please check your API key.")
        return False
    
    # Sample candidate data
    candidate_data = {
        "skills": ["Python", "Machine Learning", "SQL", "Data Analysis", "TensorFlow"],
        "experience_years": 5,
        "education_level": "Master of Science in Computer Science",
        "certifications": ["AWS Certified Machine Learning", "Google Data Analytics"],
        "languages": ["English", "Spanish"],
        "location": "San Francisco, CA"
    }
    
    # Sample job data
    job_data = {
        "skills": ["Python", "Machine Learning", "Deep Learning", "Data Science"],
        "experience_years": 4,
        "education_level": "Bachelor's in Computer Science or related field",
        "certifications": ["AWS Certified", "TensorFlow Developer"],
        "languages": ["English"],
        "location": "San Francisco, CA"
    }
    
    # Default weights
    weights = {
        "skills": 0.35,
        "experience_years": 0.25,
        "education": 0.10,
        "certifications": 0.10,
        "languages": 0.03,
        "location": 0.02
    }
    
    print("\n🔍 Testing resume matching with Gemini integration...")
    print(f"Candidate Skills: {candidate_data['skills']}")
    print(f"Job Skills: {job_data['skills']}")
    
    # Calculate match score
    result = matcher.calculate_match_score(candidate_data, job_data, weights)
    
    print("\n📈 Match Results:")
    print(f"  - Traditional Score: {result['traditional_score']}")
    print(f"  - Final Score (with Gemini): {result['final_score']}")
    print(f"  - Classification: {result['classification']}")
    
    print("\n🧠 Gemini Analysis:")
    gemini = result['gemini_analysis']
    print(f"  - Semantic Match Score: {gemini.get('semantic_match_score', 'N/A')}")
    print(f"  - Key Skills Match: {gemini.get('key_skills_match', 'N/A')}")
    print(f"  - Experience Relevance: {gemini.get('experience_relevance', 'N/A')}")
    print(f"  - Overall Assessment: {gemini.get('overall_assessment', 'N/A')}")
    print(f"  - Insights: {gemini.get('insights', 'N/A')}")
    
    print("\n✅ Gemini API integration test completed successfully!")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Gemini API Integration Test for Resume Matcher")
    print("=" * 60)
    
    success = test_gemini_integration()
    
    if success:
        print("\n🎉 All tests passed! The system is ready to use.")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")
        sys.exit(1)
