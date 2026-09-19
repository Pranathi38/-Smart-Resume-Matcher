"""
Test Gemini API Rate Limiting and Exponential Backoff
"""

import os
import sys
from dotenv import load_dotenv
from resume_parser import GeminiResumeParser

# Load environment variables
load_dotenv()

def test_rate_limiting():
    """Test the rate limiting functionality."""
    
    print("=" * 60)
    print("Testing Gemini API Rate Limiting")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please set up your .env file with a valid Google API key")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Initialize parser with rate limiting
    try:
        parser = GeminiResumeParser()
        print("✅ Gemini Parser initialized with rate limiting")
        
        # Test rate limiter status
        status = parser.rate_limiter.get_status()
        print(f"📊 Rate Limiter Status:")
        print(f"  - Available: {status['available']}")
        print(f"  - Max Requests/Minute: {status['max_requests_per_minute']}")
        print(f"  - Max Retries: {status['max_retries']}")
        print(f"  - Base Delay: {status['base_delay']}s")
        print(f"  - Max Delay: {status['max_delay']}s")
        print(f"  - Jitter: {status['jitter']}")
        
        # Test extraction with sample text
        sample_resume_text = """
        JOHN DOE
        Email: john.doe@email.com
        Phone: (555) 123-4567
        
        SUMMARY
        Experienced Software Engineer with 5 years of experience in full-stack development.
        Proficient in Python, JavaScript, React, Node.js, and cloud technologies.
        
        EXPERIENCE
        Senior Software Engineer | Tech Corp | 2019 - Present
        - Led development of microservices architecture
        - Implemented RESTful APIs using Node.js and Express
        - Managed team of 5 developers
        - Reduced API response time by 40%
        
        Software Engineer | Startup Inc | 2017 - 2019
        - Developed scalable web applications using React and Redux
        - Integrated PostgreSQL and MongoDB databases
        - Participated in Agile development methodology
        
        EDUCATION
        Bachelor of Science in Computer Science | State University | 2013 - 2017
        GPA: 3.8/4.0
        
        SKILLS
        Technical Skills: Python, JavaScript, React, Node.js, Express, MongoDB, PostgreSQL, Docker, AWS, Git
        Soft Skills: Leadership, Communication, Problem Solving, Team Collaboration
        
        CERTIFICATIONS
        - AWS Certified Solutions Architect (2020)
        - Google Cloud Professional Developer (2021)
        
        LANGUAGES
        - English (Native)
        - Spanish (Fluent)
        """
        
        print("\n🧪 Testing Resume Extraction...")
        
        # Test multiple rapid extractions to trigger rate limiting
        for i in range(3):
            print(f"\n--- Test {i + 1} ---")
            result = parser.extract_from_text(sample_resume_text)
            
            if result:
                print(f"✅ Extraction {i + 1} successful:")
                print(f"  Name: {result.get('candidate_name', 'Unknown')}")
                print(f"  Skills: {result.get('skills', [])}")
                print(f"  Experience: {result.get('experience_years', 0)} years")
                print(f"  Education: {result.get('education_level', 'Unknown')}")
            else:
                print(f"❌ Extraction {i + 1} failed")
        
        # Add delay between tests
        if i < 2:
            print("⏳ Waiting 2 seconds between tests...")
            import time
            time.sleep(2)
    
    except Exception as e:
        print(f"❌ Error testing rate limiting: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Rate limiting test completed!")
    print("\n📝 Recommendations:")
    print("1. Monitor your API usage in Google AI Studio")
    print("2. If you hit rate limits frequently:")
    print("   - Enable Pay-as-you-go billing for higher quotas")
    print("   - Implement request queuing for batch processing")
    print("   - Use longer delays between requests")
    print("3. Rate Limiting in your Code")
    print("   - The system will automatically:")
    print("   - Wait for quota reset when limits are hit")
    print("   - Use exponential backoff with jitter")
    print("   - Fall back to keyword parsing if API fails")
    
    return True

if __name__ == "__main__":
    success = test_rate_limiting()
    sys.exit(0 if success else 1)
