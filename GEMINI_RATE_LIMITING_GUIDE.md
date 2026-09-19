# Gemini API Rate Limiting and Exponential Backoff Guide

## Problem Identified

You're experiencing **Gemini API quota exceeded** errors when processing multiple resumes. The current system:
- Hits rate limits quickly (15 requests/minute for free tier)
- No retry logic when quota is exceeded
- No exponential backoff to space out requests
- No graceful fallback to keyword parsing when API fails

## Solution Implemented

### 1. **Rate Limiter Class** (`gemini_rate_limiter.py`)
- **Exponential Backoff**: 2s, 4s, 8s, 16s, 32s, 60s max
- **Jitter**: Random 10% variation to avoid thundering herd
- **Quota Reset Detection**: Waits for new hour when limits hit
- **Smart Retry Logic**: Up to 5 retries with different strategies
- **Status Tracking**: Monitors request timing and API availability

### 2. **Enhanced Resume Parser** (`resume_parser.py`)
- **Rate Limited**: Uses `GeminiRateLimiter` for all API calls
- **Graceful Fallback**: Falls back to keyword parsing if API fails
- **Error Handling**: Comprehensive error logging and recovery

### 3. **Configuration Options**
```python
# Free tier settings
limiter = GeminiRateLimiter(
    max_requests_per_minute=15,  # Free tier limit
    max_retries=5,
    base_delay=2.0,  # Start with 2 second delay
    max_delay=60.0,  # Max 1 minute delay
    jitter=True
)
```

## How to Use

### For Free Tier (15 RPM/1M TPM)
1. **Single Resume**: Works fine
2. **Multiple Resumes**: System automatically spaces out requests
3. **Batch Processing**: Add delays between each resume (2-5 seconds)
4. **When Quota Hit**: System waits for reset, then retries with backoff

### Monitoring
```python
# Check rate limiter status
status = parser.rate_limiter.get_status()
print(f"Available: {status['available']}")
print(f"Max RPM: {status['max_requests_per_minute']}")
```

## Benefits

1. **Prevents API Blocking**: Won't get blocked for exceeding limits
2. **Graceful Degradation**: Falls back to keyword parsing when needed
3. **Better User Experience**: No sudden failures, clear error messages
4. **Cost Control**: Avoids unexpected API charges from rapid retries
5. **Reliability**: Automatic recovery from transient errors

## Files Modified

- `gemini_rate_limiter.py` - New rate limiting implementation
- `resume_parser.py` - Enhanced with rate limiting support
- `ml_engine.py` - Gemini analysis integration (when available)
- `server.py` - Uses enhanced parser with fallback support

## Testing

Run `python test_rate_limiting.py` to verify the implementation works correctly.

## Next Steps

1. **Monitor Usage**: Check Google AI Studio for actual usage patterns
2. **Adjust Delays**: Increase base_delay if still hitting limits
3. **Consider Billing**: Upgrade to Pay-as-you-go for higher quotas if needed
4. **Batch Optimization**: Implement request queuing for large volumes
