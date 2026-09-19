"""
Test Maria's scoring to ensure she gets High Match
"""

import os
import sys
from dotenv import load_dotenv
from ml_engine import NeuralResumeMatcher

# Load environment variables
load_dotenv()

def test_maria_scoring():
    """Test Maria's profile to ensure she gets High Match."""
    
    # Initialize the matcher
    matcher = NeuralResumeMatcher()
    
    # Job requirements (example for Data Analyst role)
    job_data = {
        "skills": ["Python", "SQL", "Data Analysis", "Machine Learning"],
        "experience_years": 3,
        "education_level": "Bachelor's in Computer Science",
        "certifications": ["AWS Certified", "Google Data Analytics"],
        "languages": ["English"],
        "location": "San Francisco, CA"
    }
    
    # Maria's data (from the image)
    maria_data = {
        "skills": ["Python", "SQL", "Data Analysis", "Machine Learning", "Tableau"],
        "experience_years": 5,
        "education_level": "Master of Science in Data Science",
        "certifications": ["AWS Certified Data Analytics", "Google Cloud Professional"],
        "languages": ["English", "Spanish"],
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
    
    print("=" * 60)
    print("Testing Maria's Scoring")
    print("=" * 60)
    
    # Calculate match score
    result = matcher.calculate_match_score(maria_data, job_data, weights)
    
    print("\n📊 Individual Scores:")
    for attr, score in result['scores'].items():
        print(f"  - {attr.title()}: {score:.1f}%")
    
    print(f"\n📈 Overall Results:")
    print(f"  - Traditional Score: {result['traditional_score']}%")
    print(f"  - Final Score (with Gemini): {result['final_score']}%")
    print(f"  - Classification: {result['classification']}")
    
    print(f"\n🧠 Gemini Analysis:")
    gemini = result['gemini_analysis']
    print(f"  - Overall Assessment: {gemini.get('overall_assessment', 'N/A')}")
    print(f"  - Insights: {gemini.get('insights', 'N/A')}")
    
    # Check if Maria gets High Match
    if result['classification'] == "High Match":
        print("\n✅ SUCCESS: Maria is correctly classified as High Match!")
    else:
        print(f"\n❌ ISSUE: Maria is classified as {result['classification']} instead of High Match")
        print("   Expected: High Match (≥80%)")
        print(f"   Actual: {result['final_score']}%")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_maria_scoring()
