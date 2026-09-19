# Resume Matcher Scoring Guide

## Overview
The Smart Resume Matcher uses a balanced scoring algorithm that combines semantic similarity with weighted attribute matching. The system has been tuned to provide accurate classification of candidates into High, Medium, and Low matches.

## Scoring Algorithm

### 1. Base Scoring
- **Skills Matching**: 35% weight - Uses semantic similarity to match candidate skills with job requirements
- **Experience Years**: 25% weight - Strict matching (candidate must meet or exceed requirements)
- **Education**: 10% weight - Semantic similarity between education levels
- **Certifications**: 10% weight - List-based semantic matching
- **Languages**: 3% weight - List-based semantic matching
- **Location**: 2% weight - Semantic similarity of locations

### 2. Attribute-Based Penalties
The system applies penalties based on the weakest attribute and number of weak attributes:

#### Minimum Score Penalties:
- **< 20%**: Cap at 20% (Very poor matches)
- **< 35%**: Cap at 35% (Poor matches)
- **< 50%**: Cap at 55% (Below average)
- **< 65%**: Cap at 75% (Average to good)

#### Weak Attribute Penalties:
- **4+ weak attributes**: Cap at 25% (Very low score)
- **3 weak attributes**: Cap at 40% (Low score)
- **2 weak attributes**: Cap at 60% (Medium-low score)

#### Skill-Specific Penalties:
- **< 30% skills**: Cap at 35% (Very poor skill match)
- **< 50% skills**: Cap at 55% (Poor skill match)
- **< 70% skills**: Cap at 75% (Average skill match)

### 3. Gemini API Integration
- **20% weight** for Gemini's semantic analysis
- **80% weight** for traditional scoring
- Graceful fallback when API quota is exceeded

## Classification Thresholds

### High Match (≥ 80%)
- Strong alignment across all critical attributes
- Skills match ≥ 70%
- Experience meets or exceeds requirements
- Maximum 1 weak attribute

### Medium Match (55% - 79%)
- Good alignment with some gaps
- Skills match 50% - 70%
- Experience close to requirements
- Maximum 2 weak attributes

### Low Match (< 55%)
- Poor alignment with significant gaps
- Skills match < 50%
- Multiple weak attributes (3+)
- Recommended for rejection

## Example Scenarios

### Perfect Match - 95%
- Skills: 95% (Python, ML, SQL, Data Science)
- Experience: 100% (5 years vs 4 required)
- Education: 90% (Master's vs Bachelor's)
- Classification: **High Match**

### Good Match - 78%
- Skills: 80% (Python, SQL, Data Analysis)
- Experience: 100% (4 years meets requirement)
- Education: 85% (Bachelor's in CS)
- Classification: **High Match**

### Medium Match - 62%
- Skills: 60% (Python, Basic SQL)
- Experience: 75% (3 years vs 4 required)
- Education: 70% (Bachelor's in Business)
- Classification: **Medium Match**

### Low Match - 35%
- Skills: 20% (HTML, CSS - wrong skills)
- Experience: 25% (1 year vs 4 required)
- Education: 40% (High School)
- Classification: **Low Match**

## Tuning Parameters

The scoring system can be adjusted by modifying:
1. **Attribute weights** - Change the importance of different attributes
2. **Penalty thresholds** - Adjust when penalties are applied
3. **Classification thresholds** - Modify the score ranges for each category
4. **Gemini integration weight** - Change the influence of AI analysis

## Best Practices

1. **Regular Calibration**: Review scoring results and adjust thresholds based on hiring outcomes
2. **Job-Specific Weights**: Consider adjusting weights for different role types
3. **Feedback Loop**: Track which candidates succeed and use this to refine scoring
4. **Balance**: Ensure the system isn't too strict (missing good candidates) or too lenient (too many matches)

## Technical Implementation

The scoring logic is implemented in `ml_engine.py`:
- `calculate_match_score()` - Main scoring function
- `calculate_cosine_similarity()` - Semantic similarity calculation
- `calculate_list_similarity()` - List-based matching
- `analyze_with_gemini()` - AI-powered semantic analysis

## Monitoring

Monitor these metrics to ensure scoring quality:
- Distribution of scores (should be roughly normal)
- Classification accuracy (feedback from hiring managers)
- Gemini API usage and quota management
- Processing time per match
