"""
Gemini API Rate Limiter with Exponential Backoff
Handles API quota gracefully by implementing smart retry logic
"""

import time
import random
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

class GeminiRateLimiter:
    """
    Rate limiter for Gemini API with exponential backoff
    """
    
    def __init__(
        self,
        max_requests_per_minute: int = 15,  # Free tier limit
        max_retries: int = 5,
        base_delay: float = 1.0,  # Base delay in seconds
        max_delay: float = 60.0,  # Maximum delay
        jitter: bool = True  # Add random jitter to avoid thundering herd
    ):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests_per_minute: Maximum requests per minute
            max_retries: Maximum retry attempts
            base_delay: Base delay between retries
            max_delay: Maximum delay
            jitter: Add random jitter to avoid synchronized retries
        """
        self.max_requests_per_minute = max_requests_per_minute
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        
        # Track request timing
        self.request_times = []
        self.last_request_time = 0
        
        # Initialize Gemini API only when needed
        self.model = None
        self.available = False
        
        # Initialize Gemini API
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-3.0-flash')
                self.available = True
                logger.info("Gemini API initialized with rate limiting")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini API: {e}")
                self.available = False
        else:
            logger.warning("GOOGLE_API_KEY not found")
            self.available = False
    
    def _wait_for_quota_reset(self) -> bool:
        """
        Wait for quota to reset (typically at the top of the hour)
        """
        current_time = time.time()
        current_minute = time.localtime(current_time).tm_min
        current_hour = time.localtime(current_time).tm_hour
        
        # If we're in a new hour, quota might be reset
        if current_minute == 0 and current_hour == 0:
            logger.info("New hour detected - quota might be reset")
            return True
        
        # If we've waited long enough, assume quota reset
        time_since_last = current_time - self.last_request_time
        if time_since_last > 3600:  # 1 hour
            logger.info("Hour passed - assuming quota reset")
            return True
        
        return False
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay with jitter.
        
        Args:
            attempt: Current attempt number (0-based)
            
        Returns:
            Delay in seconds before next retry
        """
        # Exponential backoff: delay = base_delay * (2^attempt)
        delay = self.base_delay * (2 ** attempt)
        
        # Cap at maximum delay
        delay = min(delay, self.max_delay)
        
        # Add jitter to avoid thundering herd
        if self.jitter:
            jitter_amount = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_amount, jitter_amount)
        
        logger.info(f"Retry attempt {attempt + 1}/{self.max_retries}, delay: {delay:.2f}s")
        return delay
    
    def generate_content_with_retry(self, prompt: str) -> Optional[str]:
        """
        Generate content with rate limiting and retry logic.
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Generated text or None if all retries exhausted
        """
        if not self.available:
            logger.warning("Gemini API not available")
            return None
        
        for attempt in range(self.max_retries):
            try:
                # Check if we should wait for quota reset
                if attempt > 0 and self._wait_for_quota_reset():
                    logger.info("Waiting for quota to reset...")
                    time.sleep(60)  # Wait a full minute
                    continue
                
                logger.info(f"Gemini API request attempt {attempt + 1}/{self.max_retries}")
                
                # Import genai only when needed
                try:
                    import google.generativeai as genai
                    response = self.model.generate_content(prompt)
                except:
                    # If model not initialized, initialize it
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-3.0-flash')
                    response = self.model.generate_content(prompt)
                
                # Check if successful
                if response.text:
                    logger.info("Gemini API request successful")
                    self.last_request_time = time.time()
                    return response.text
                else:
                    logger.warning(f"Gemini API returned empty response on attempt {attempt + 1}")
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # Handle different error types
                if "quota" in error_msg or "429" in error_msg:
                    logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
                    
                    if attempt < self.max_retries - 1:
                        # Wait for quota reset or backoff
                        if self._wait_for_quota_reset():
                            time.sleep(60)
                            continue
                        else:
                            delay = self._calculate_backoff_delay(attempt)
                            logger.info(f"Rate limited, waiting {delay:.2f}s before retry")
                            time.sleep(delay)
                            continue
                    else:
                        logger.error(f"Max retries exceeded for Gemini API: {e}")
                        return None
                else:
                    logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    if attempt < self.max_retries - 1:
                        delay = self._calculate_backoff_delay(attempt)
                        logger.info(f"Unexpected error, waiting {delay:.2f}s before retry")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Max retries exceeded: {e}")
                        return None
        
        logger.error("All Gemini API retries exhausted")
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the rate limiter.
        
        Returns:
            Dictionary with status information
        """
        return {
            "available": self.available,
            "max_requests_per_minute": self.max_requests_per_minute,
            "max_retries": self.max_retries,
            "last_request_time": self.last_request_time,
            "request_times": self.request_times
        }
