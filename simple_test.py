import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check API key
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("❌ GOOGLE_API_KEY not found in environment variables")
    print("Please set up your .env file with a valid Google API key")
else:
    print(f"✅ API Key found: {api_key[:10]}...")

# Test import
try:
    from gemini_rate_limiter import GeminiRateLimiter
    limiter = GeminiRateLimiter()
    print("✅ Rate limiter imported successfully")
    
    # Test status
    status = limiter.get_status()
    print(f"📊 Rate Limiter Status:")
    print(f"  - Available: {status['available']}")
    print(f"  - Max Requests/Minute: {status['max_requests_per_minute']}")
    print(f"  - Max Retries: {status['max_retries']}")
    
except Exception as e:
    print(f"❌ Error importing rate limiter: {e}")

print("\n✅ Simple test completed!")
