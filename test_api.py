"""
API Testing Script for Smart Resume Matcher
Tests all backend endpoints without requiring the frontend
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_response(response: requests.Response):
    """Print formatted response"""
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_health():
    """Test health check endpoint"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_model_info():
    """Test model info endpoint"""
    print_section("TEST 2: Model Information")
    
    try:
        response = requests.get(f"{BASE_URL}/model-info")
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_similarity():
    """Test similarity calculation"""
    print_section("TEST 3: Calculate Similarity")
    
    try:
        params = {
            "text1": "Python developer with machine learning experience",
            "text2": "Senior Python engineer specializing in AI and ML"
        }
        response = requests.post(
            f"{BASE_URL}/calculate-similarity",
            params=params
        )
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_match_score():
    """Test match score calculation"""
    print_section("TEST 4: Calculate Match Score")
    
    try:
        candidate_data = {
            "candidate_name": "John Doe",
            "skills": ["Python", "FastAPI", "React", "Machine Learning"],
            "experience_years": 5,
            "education_level": "Masters",
            "certifications": ["AWS Certified Solutions Architect"],
            "languages": ["English", "Spanish"],
            "salary_expectation": 150000,
            "location": "San Francisco",
            "experience_description": "5 years of experience in full-stack development and machine learning",
            "career_objective": "Senior Software Engineer"
        }
        
        job_data = {
            "title": "Senior Software Engineer",
            "skills": ["Python", "FastAPI", "React"],
            "requirements": "Looking for experienced full-stack developer with ML background",
            "experience_years": 5,
            "education_level": "Bachelors",
            "certifications": [],
            "languages": ["English"],
            "location": "Remote"
        }
        
        weights = {
            "skills": 0.35,
            "experience": 0.25,
            "experience_years": 0.15,
            "education": 0.10,
            "certifications": 0.10,
            "languages": 0.03,
            "location": 0.02
        }
        
        payload = {
            "candidate_data": candidate_data,
            "job_data": job_data,
            "weights": weights
        }
        
        response = requests.post(
            f"{BASE_URL}/match-resume",
            json=payload
        )
        print_response(response)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Final Score: {result['final_score']}/100")
            print(f"✓ Classification: {result['classification']}")
            return True
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_batch_match():
    """Test batch matching"""
    print_section("TEST 5: Batch Match Multiple Candidates")
    
    try:
        candidates = [
            {
                "candidate_name": "Alice Smith",
                "skills": ["Python", "FastAPI", "React"],
                "experience_years": 6,
                "education_level": "Masters",
                "certifications": ["AWS Certified"],
                "languages": ["English"],
                "salary_expectation": 160000,
                "location": "San Francisco",
                "experience_description": "6 years in full-stack development",
                "career_objective": "Senior Engineer"
            },
            {
                "candidate_name": "Bob Johnson",
                "skills": ["JavaScript", "Node.js"],
                "experience_years": 2,
                "education_level": "Bachelors",
                "certifications": [],
                "languages": ["English"],
                "salary_expectation": 80000,
                "location": "New York",
                "experience_description": "2 years as junior developer",
                "career_objective": "Mid-level Developer"
            }
        ]
        
        job_data = {
            "title": "Senior Software Engineer",
            "skills": ["Python", "FastAPI", "React"],
            "requirements": "5+ years experience required",
            "experience_years": 5,
            "education_level": "Bachelors",
            "certifications": [],
            "languages": ["English"],
            "location": "Remote"
        }
        
        weights = {
            "skills": 0.35,
            "experience": 0.25,
            "experience_years": 0.15,
            "education": 0.10,
            "certifications": 0.10,
            "languages": 0.03,
            "location": 0.02
        }
        
        payload = {
            "candidates": candidates,
            "job_data": job_data,
            "weights": weights
        }
        
        response = requests.post(
            f"{BASE_URL}/batch-match",
            json=payload
        )
        print_response(response)
        
        if response.status_code == 200:
            results = response.json()
            print(f"\n✓ Matched {len(results)} candidates")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['candidate_name']}: {result['final_score']}/100 ({result['classification']})")
            return True
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Smart Resume Matcher - API Test Suite".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    print(f"\nConnecting to: {BASE_URL}")
    print("Make sure the backend server is running!")
    
    results = {
        "Health Check": test_health(),
        "Model Info": test_model_info(),
        "Similarity": test_similarity(),
        "Match Score": test_match_score(),
        "Batch Match": test_batch_match(),
    }
    
    print_section("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        exit(1)
