"""
Test strict scoring logic for Resume Matcher
"""

import os
import sys
from dotenv import load_dotenv
from ml_engine import NeuralResumeMatcher

# Load environment variables
load_dotenv()

def test_strict_scoring():
    """Test the strict scoring logic with various candidate profiles."""
    
    # Initialize the matcher
    matcher = NeuralResumeMatcher()
    
    # Job requirements
    job_data = {
        "skills": ["Python", "Machine Learning", "SQL", "Data Science"],
        "experience_years": 4,
        "education_level": "Bachelor's in Computer Science",
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
    
    print("=" * 60)
    print("Testing Strict Scoring Logic")
    print("=" * 60)
    
    # Test Case 1: Perfect Match
    print("\n1. PERFECT MATCH:")
    perfect_candidate = {
        "skills": ["Python", "Machine Learning", "SQL", "Data Science", "TensorFlow"],
        "experience_years": 5,
        "education_level": "Master of Science in Computer Science",
        "certifications": ["AWS Certified Machine Learning", "TensorFlow Developer"],
        "languages": ["English", "Spanish"],
        "location": "San Francisco, CA"
    }
    
    result = matcher.calculate_match_score(perfect_candidate, job_data, weights)
    print(f"   Score: {result['final_score']}%")
    print(f"   Classification: {result['classification']}")
    
    # Test Case 2: Good Match
    print("\n2. GOOD MATCH:")
    good_candidate = {
        "skills": ["Python", "SQL", "Data Analysis"],
        "experience_years": 4,
        "education_level": "Bachelor's in Computer Science",
        "certifications": ["AWS Certified"],
        "languages": ["English"],
        "location": "San Francisco, CA"
    }
    
    result = matcher.calculate_match_score(good_candidate, job_data, weights)
    print(f"   Score: {result['final_score']}%")
    print(f"   Classification: {result['classification']}")
    
    # Test Case 3: Medium Match (some weak attributes)
    print("\n3. MEDIUM MATCH:")
    medium_candidate = {
        "skills": ["Python", "Basic SQL"],
        "experience_years": 3,
        "education_level": "Bachelor's in Business",
        "certifications": [],
        "languages": ["English"],
        "location": "Los Angeles, CA"
    }
    
    result = matcher.calculate_match_score(medium_candidate, job_data, weights)
    print(f"   Score: {result['final_score']}%")
    print(f"   Classification: {result['classification']}")
    
    # Test Case 4: Low Match (should be rejected)
    print("\n4. LOW MATCH (REJECTED):")
    low_candidate = {
        "skills": ["HTML", "CSS"],  # Wrong skills
        "experience_years": 1,
        "education_level": "High School",
        "certifications": [],
        "languages": ["Spanish"],  # Wrong language
        "location": "New York, NY"  # Wrong location
    }
    
    result = matcher.calculate_match_score(low_candidate, job_data, weights)
    print(f"   Score: {result['final_score']}%")
    print(f"   Classification: {result['classification']}")
    
    # Test Case 5: Very Poor Match (should be strongly rejected)
    print("\n5. VERY POOR MATCH (STRONGLY REJECTED):")
    poor_candidate = {
        "skills": [],  # No skills
        "experience_years": 0,
        "education_level": "",
        "certifications": [],
        "languages": [],
        "location": ""
    }
    
    result = matcher.calculate_match_score(poor_candidate, job_data, weights)
    print(f"   Score: {result['final_score']}%")
    print(f"   Classification: {result['classification']}")
    
    print("\n" + "=" * 60)
    print("✅ Strict scoring test completed!")
    print("   - High Match: 75%+")
    print("   - Medium Match: 50-74%")
    print("   - Low Match: <50% (Rejected)")
    print("=" * 60)

if __name__ == "__main__":
    test_strict_scoring()
