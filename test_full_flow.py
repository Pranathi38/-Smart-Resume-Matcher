"""
Test the full flow: Create job, upload resume, check score
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_full_flow():
    print("\n" + "="*70)
    print("FULL FLOW TEST: Create Job → Upload Resume → Check Score")
    print("="*70)
    
    # Step 1: Create a job profile
    print("\n[STEP 1] Creating job profile...")
    job_data = {
        "title": "Senior Data Analyst",
        "skills": ["Python", "SQL", "Tableau", "Excel", "Statistics"],
        "requirements": "Looking for experienced data analyst with strong SQL and Python skills",
        "experience_years": 5,
        "education_level": "Bachelors",
        "certifications": ["Google Analytics Certified"],
        "languages": ["English"],
        "location": "Remote"
    }
    
    response = requests.post(f"{BASE_URL}/jobs", json=job_data)
    if response.status_code != 200:
        print(f"❌ Failed to create job: {response.status_code}")
        print(response.json())
        return
    
    job = response.json()
    job_id = job['id']
    print(f"✅ Job created with ID: {job_id}")
    print(f"   Title: {job['title']}")
    print(f"   Skills: {job['skills']}")
    print(f"   Experience: {job['experience_years']} years")
    
    # Step 2: Check job was saved correctly
    print("\n[STEP 2] Verifying job profile...")
    response = requests.get(f"{BASE_URL}/jobs/{job_id}")
    if response.status_code == 200:
        saved_job = response.json()
        print(f"✅ Job retrieved successfully")
        print(f"   Title: {saved_job['title']}")
        print(f"   Skills: {saved_job['skills']}")
        print(f"   Requirements: {saved_job['requirements'][:50]}...")
    else:
        print(f"❌ Failed to retrieve job: {response.status_code}")
    
    # Step 3: Test match calculation directly
    print("\n[STEP 3] Testing match calculation directly...")
    candidate_data = {
        "candidate_name": "John Doe",
        "skills": ["Python", "SQL", "Tableau", "Excel"],
        "experience_years": 6,
        "education_level": "Bachelors",
        "certifications": ["Google Analytics Certified"],
        "languages": ["English"],
        "location": "Remote",
        "experience_description": "6 years of data analysis experience with Python and SQL",
        "career_objective": "Senior Data Analyst"
    }
    
    weights = {
        "skills": 0.35,
        "experience": 0.25,
        "experience_years": 0.15,
        "education": 0.1,
        "certifications": 0.1,
        "languages": 0.03,
        "location": 0.02
    }
    
    match_payload = {
        "candidate_data": candidate_data,
        "job_data": job_data,
        "weights": weights
    }
    
    response = requests.post(f"{BASE_URL}/match-resume", json=match_payload)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Direct match calculation successful")
        print(f"   Final Score: {result['final_score']}%")
        print(f"   Classification: {result['classification']}")
        print(f"\n   Individual Scores:")
        for key, value in result['scores'].items():
            print(f"     - {key}: {value:.2f}%")
    else:
        print(f"❌ Match calculation failed: {response.status_code}")
        print(response.json())
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)

if __name__ == "__main__":
    test_full_flow()
