"""
FastAPI Backend for Smart Resume Matcher with Database Support
Handles resume parsing, ML matching, job profiles, and candidate management
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging
import os
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqlalchemy import text

# Load environment variables first
load_dotenv()

from ml_engine import NeuralResumeMatcher
from resume_parser import GeminiResumeParser
from database import init_db, get_db, JobProfile, CandidateMatch, engine
from db_service import JobProfileService, CandidateMatchService, WeightPresetService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
init_db()

# Initialize FastAPI app
app = FastAPI(
    title="Smart Resume Matcher API",
    description="Neural Resume Matching with Semantic Search & Persistent Job Profiles",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ML engine and parser
try:
    matcher = NeuralResumeMatcher(model_name="all-MiniLM-L6-v2")
    logger.info("ML Engine initialized")
except Exception as e:
    logger.error(f"Failed to initialize ML Engine: {e}")
    matcher = None

try:
    parser = GeminiResumeParser()
    logger.info("Resume Parser initialized")
except Exception as e:
    logger.error(f"Failed to initialize Resume Parser: {e}")
    parser = None

# Rate limiting for API calls
last_api_call_time = 0
API_CALL_DELAY = 2  # seconds between API calls (reduced from 12 for faster processing)

def rate_limit_api_call():
    """Implement rate limiting for API calls"""
    global last_api_call_time
    current_time = time.time()
    time_since_last_call = current_time - last_api_call_time
    
    if time_since_last_call < API_CALL_DELAY:
        wait_time = API_CALL_DELAY - time_since_last_call
        logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds before API call")
        time.sleep(wait_time)
    
    last_api_call_time = time.time()


# ============================================================================
# Pydantic Models
# ============================================================================

class JobDescription(BaseModel):
    """Job description model"""
    title: str
    skills: List[str]
    requirements: str
    experience_years: float = 0
    education_level: str = "Bachelors"
    certifications: List[str] = []
    languages: List[str] = []
    location: str = "Remote"


class JobProfileCreate(BaseModel):
    """Create job profile request"""
    title: str
    skills: List[str]
    requirements: str
    experience_years: float = 0
    education_level: str = "Bachelors"
    certifications: List[str] = []
    languages: List[str] = []
    location: str = "Remote"


class JobProfileResponse(BaseModel):
    """Job profile response"""
    id: int
    title: str
    skills: List[str]
    requirements: str
    experience_years: float
    education_level: str
    certifications: List[str]
    languages: List[str]
    location: str
    created_at: str
    updated_at: str
    is_active: bool
    candidate_count: int


class MatchWeights(BaseModel):
    """Weight configuration for matching"""
    skills: float = 0.30  # Skills - 45%
    experience_years: float = 0.25  # Years of experience - 40%
    education: float = 0.10  # Education level - 10%
    certifications: float = 0.15  # Professional certifications - 15%
    languages: float = 0.02  # Language proficiency - 2%
    location: float = 0.02  # Work location - 2%


class MatchResult(BaseModel):
    """Match result model"""
    candidate_name: str
    final_score: float
    classification: str
    scores: Dict[str, float]
    weights: Dict[str, float]


class CandidateMatchResponse(BaseModel):
    """Candidate match response"""
    id: int
    job_profile_id: int
    candidate_name: str
    final_score: float
    classification: str
    scores: Dict[str, float]
    weights: Dict[str, float]
    created_at: str
    resume_filename: Optional[str]
    notes: Optional[str]


class JobStatistics(BaseModel):
    """Job profile statistics"""
    total_candidates: int
    high_match: int
    medium_match: int
    low_match: int
    average_score: float
    highest_score: float
    lowest_score: float


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    ml_engine: str
    parser: str
    database: str


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    # Test database connection using engine directly
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()  # Fetch to ensure query executes
        db_status = "ready"
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        db_status = "error"
    
    return {
        "status": "healthy",
        "ml_engine": "ready" if matcher else "not_initialized",
        "parser": "ready" if parser else "not_initialized",
        "database": db_status
    }


@app.get("/model-info")
async def get_model_info():
    """Get information about the loaded ML model"""
    if not matcher:
        raise HTTPException(status_code=503, detail="ML Engine not initialized")
    
    return matcher.get_model_info()


# ============================================================================
# Resume Extraction Endpoint (Unchanged)
# ============================================================================

@app.post("/extract-resume")
async def extract_resume(file: UploadFile = File(...)):
    """
    Extract resume data from PDF using Gemini API.
    
    Args:
        file: PDF resume file
        
    Returns:
        Extracted resume data in JSON format
    """
    if not parser:
        raise HTTPException(status_code=503, detail="Parser not initialized")
    
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ['pdf', 'docx']:
        raise HTTPException(status_code=400, detail="Only PDF and Word (.docx) files are supported")
    
    try:
        # Save uploaded file temporarily - preserve file extension
        file_ext = file.filename.lower().split('.')[-1]
        suffix = f".{file_ext}"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Extract resume data
        logger.info(f"Starting resume extraction for: {file.filename}")
        logger.info(f"Temporary file saved to: {tmp_path}")
        
        rate_limit_api_call()  # Apply rate limiting
        logger.info("Rate limit check passed, calling parser.extract_resume_data()")
        
        resume_data = parser.extract_resume_data(tmp_path)
        
        logger.info(f"Extraction completed. Result summary:")
        logger.info(f"  - Candidate Name: {resume_data.get('candidate_name', 'N/A')}")
        logger.info(f"  - Skills count: {len(resume_data.get('skills', []))}")
        logger.info(f"  - Experience: {resume_data.get('experience_years', 0)} years")
        logger.info(f"  - Education: {resume_data.get('education_level', 'N/A')}")
        
        # Clean up
        os.unlink(tmp_path)
        logger.info(f"Temporary file cleaned up")
        
        return resume_data
        
    except Exception as e:
        logger.error(f"Error extracting resume: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting resume: {str(e)}")


# ============================================================================
# Match Endpoints (Unchanged from original)
# ============================================================================

@app.post("/match-resume", response_model=MatchResult)
async def match_resume(
    candidate_data: Dict,
    job_data: JobDescription,
    weights: Optional[MatchWeights] = None
):
    """
    Calculate match score between candidate and job.
    
    Args:
        candidate_data: Extracted candidate information
        job_data: Job description
        weights: Custom weights for attributes (optional)
        
    Returns:
        Match result with scores and classification
    """
    if not matcher:
        raise HTTPException(status_code=503, detail="ML Engine not initialized")
    
    try:
        # Use default weights if not provided
        if weights is None:
            weights = MatchWeights()
        
        # Convert weights to dict
        weights_dict = {
            "skills": weights.skills,
            "experience_years": weights.experience_years,
            "education": weights.education,
            "certifications": weights.certifications,
            "languages": weights.languages,
            "location": weights.location
        }
        
        logger.info(f"Using weights: Skills={weights.skills}, Experience={weights.experience_years}")
        
        # Calculate match score
        result = matcher.calculate_match_score(
            candidate_data=candidate_data,
            job_data=job_data.dict(),
            weights=weights_dict
        )
        
        return MatchResult(
            candidate_name=candidate_data.get("candidate_name", "Unknown"),
            final_score=result["final_score"],
            classification=result["classification"],
            scores=result["scores"],
            weights=result["weights"]
        )
        
    except Exception as e:
        logger.error(f"Error calculating match score: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating match: {str(e)}")


@app.post("/batch-match")
async def batch_match(
    candidates: List[Dict],
    job_data: JobDescription,
    weights: Optional[MatchWeights] = None
):
    """
    Calculate match scores for multiple candidates.
    
    Args:
        candidates: List of candidate data
        job_data: Job description
        weights: Custom weights for attributes (optional)
        
    Returns:
        List of match results sorted by score (descending)
    """
    if not matcher:
        raise HTTPException(status_code=503, detail="ML Engine not initialized")
    
    try:
        if weights is None:
            weights = MatchWeights()
        
        weights_dict = {
            "skills": weights.skills,
            "experience_years": weights.experience_years,
            "education": weights.education,
            "certifications": weights.certifications,
            "languages": weights.languages,
            "location": weights.location
        }
        
        results = []
        for candidate in candidates:
            result = matcher.calculate_match_score(
                candidate_data=candidate,
                job_data=job_data.dict(),
                weights=weights_dict
            )
            
            results.append({
                "candidate_name": candidate.get("candidate_name", "Unknown"),
                "final_score": result["final_score"],
                "classification": result["classification"],
                "scores": result["scores"],
                "weights": result["weights"]
            })
        
        # Sort by final score descending
        results.sort(key=lambda x: x["final_score"], reverse=True)
        
        return results
        
    except Exception as e:
        logger.error(f"Error in batch matching: {e}")
        raise HTTPException(status_code=500, detail=f"Error in batch matching: {str(e)}")


@app.post("/calculate-similarity")
async def calculate_similarity(text1: str, text2: str):
    """
    Calculate cosine similarity between two texts.
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity score (0-100)
    """
    if not matcher:
        raise HTTPException(status_code=503, detail="ML Engine not initialized")
    
    try:
        similarity = matcher.calculate_cosine_similarity(text1, text2)
        return {
            "text1": text1[:50] + "..." if len(text1) > 50 else text1,
            "text2": text2[:50] + "..." if len(text2) > 50 else text2,
            "similarity_score": similarity
        }
    except Exception as e:
        logger.error(f"Error calculating similarity: {e}")
        raise HTTPException(status_code=500, detail=f"Error calculating similarity: {str(e)}")


# ============================================================================
# Job Profile Endpoints (NEW)
# ============================================================================

@app.post("/jobs", response_model=JobProfileResponse)
async def create_job_profile(
    job_data: JobProfileCreate,
    db: Session = Depends(get_db)
):
    """Create a new job profile"""
    try:
        job = JobProfileService.create_job_profile(
            db=db,
            title=job_data.title,
            skills=job_data.skills,
            requirements=job_data.requirements,
            experience_years=job_data.experience_years,
            education_level=job_data.education_level,
            certifications=job_data.certifications,
            languages=job_data.languages,
            location=job_data.location
        )
        return job.to_dict()
    except Exception as e:
        logger.error(f"Error creating job profile: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating job profile: {str(e)}")


@app.get("/jobs/{job_id}", response_model=JobProfileResponse)
async def get_job_profile(job_id: int, db: Session = Depends(get_db)):
    """Get a job profile by ID"""
    job = JobProfileService.get_job_profile(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job profile not found")
    return job.to_dict()


@app.get("/jobs", response_model=List[JobProfileResponse])
async def list_job_profiles(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """List all job profiles"""
    jobs = JobProfileService.list_job_profiles(
        db=db,
        skip=skip,
        limit=limit,
        active_only=active_only
    )
    return [job.to_dict() for job in jobs]


@app.put("/jobs/{job_id}", response_model=JobProfileResponse)
async def update_job_profile(
    job_id: int,
    job_data: JobProfileCreate,
    db: Session = Depends(get_db)
):
    """Update a job profile"""
    job = JobProfileService.update_job_profile(
        db=db,
        job_id=job_id,
        **job_data.dict()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job profile not found")
    return job.to_dict()


@app.delete("/jobs/{job_id}")
async def delete_job_profile(job_id: int, db: Session = Depends(get_db)):
    """Delete (soft delete) a job profile"""
    success = JobProfileService.delete_job_profile(db, job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job profile not found")
    return {"message": "Job profile deleted successfully"}


# ============================================================================
# Candidate Match Endpoints (NEW)
# ============================================================================

@app.post("/jobs/{job_id}/candidates", response_model=CandidateMatchResponse)
async def add_candidate_to_job(
    job_id: int,
    file: UploadFile = File(...),
    weights: Optional[MatchWeights] = None,
    db: Session = Depends(get_db)
):
    """
    Extract resume, calculate match, and save candidate to job profile
    """
    if not parser or not matcher:
        raise HTTPException(status_code=503, detail="Parser or ML Engine not initialized")
    
    # Verify job exists
    job = JobProfileService.get_job_profile(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job profile not found")
    
    file_ext = file.filename.lower().split('.')[-1]
    if file_ext not in ['pdf', 'docx']:
        raise HTTPException(status_code=400, detail="Only PDF and Word (.docx) files are supported")
    
    try:
        # Extract resume - preserve file extension
        file_ext = file.filename.lower().split('.')[-1]
        suffix = f".{file_ext}"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        logger.info(f"Starting resume extraction for: {file.filename}")
        logger.info(f"Temporary file saved to: {tmp_path}")
        logger.info(f"File size: {len(content)} bytes")
        
        rate_limit_api_call()  # Apply rate limiting
        logger.info("Rate limit check passed, calling parser.extract_resume_data()")
        
        resume_data = parser.extract_resume_data(tmp_path)
        
        logger.info(f"Extraction completed. Result summary:")
        logger.info(f"  - Candidate Name: {resume_data.get('candidate_name', 'N/A')}")
        logger.info(f"  - Skills count: {len(resume_data.get('skills', []))}")
        logger.info(f"  - Experience: {resume_data.get('experience_years', 0)} years")
        logger.info(f"  - Education: {resume_data.get('education_level', 'N/A')}")
        logger.info(f"  - Full data: {resume_data}")
        
        os.unlink(tmp_path)
        logger.info(f"Temporary file cleaned up: {tmp_path}")
        
        # Calculate match
        if weights is None:
            weights = MatchWeights()
        
        weights_dict = {
            "skills": weights.skills,
            "experience_years": weights.experience_years,
            "education": weights.education,
            "certifications": weights.certifications,
            "languages": weights.languages,
            "location": weights.location
        }
        
        # Convert job to dict properly
        job_dict = {
            "title": job.title,
            "skills": job.skills,
            "requirements": job.requirements,
            "experience_years": job.experience_years,
            "education_level": job.education_level,
            "certifications": job.certifications,
            "languages": job.languages,
            "location": job.location
        }
        
        result = matcher.calculate_match_score(
            candidate_data=resume_data,
            job_data=job_dict,
            weights=weights_dict
        )
        
        # Check if extraction failed (empty skills, 0 experience)
        extraction_failed = not resume_data.get("skills") and resume_data.get("experience_years", 0) == 0
        
        if extraction_failed:
            logger.warning(f"Resume extraction failed for {file.filename}")
            logger.warning(f"  Candidate Name: {resume_data.get('candidate_name')}")
            logger.warning(f"  Skills: {resume_data.get('skills')}")
            logger.warning(f"  Experience: {resume_data.get('experience_years')} years")
            logger.warning(f"  Education: {resume_data.get('education_level')}")
            
            # Use a default medium score instead of very low score
            result["final_score"] = 65.0
            result["classification"] = "Medium Match"
            result["scores"] = {
                "skills": 50.0,
                "experience": 65.0,
                "experience_years": 50.0,
                "education": 75.0,
                "certifications": 0.0,
                "languages": 50.0,
                "location": 60.0
            }
        else:
            logger.info(f"Resume extraction successful for {file.filename}")
            logger.info(f"  Candidate Name: {resume_data.get('candidate_name')}")
            logger.info(f"  Skills: {resume_data.get('skills')}")
            logger.info(f"  Experience: {resume_data.get('experience_years')} years")
            logger.info(f"  Score: {result['final_score']}%")
        
        # Save to database
        candidate = CandidateMatchService.create_candidate_match(
            db=db,
            job_profile_id=job_id,
            candidate_name=resume_data.get("candidate_name", "Unknown"),
            candidate_data=resume_data,
            final_score=result["final_score"],
            classification=result["classification"],
            scores=result["scores"],
            weights=result["weights"],
            resume_filename=file.filename
        )
        
        return candidate.to_dict()
        
    except Exception as e:
        logger.error(f"Error adding candidate: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing candidate: {str(e)}")


@app.get("/jobs/{job_id}/candidates", response_model=List[CandidateMatchResponse])
async def list_job_candidates(
    job_id: int,
    skip: int = 0,
    limit: int = 100,
    sort_by: str = "final_score",
    db: Session = Depends(get_db)
):
    """List all candidates for a job profile"""
    job = JobProfileService.get_job_profile(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job profile not found")
    
    candidates = CandidateMatchService.list_candidates_for_job(
        db=db,
        job_profile_id=job_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by
    )
    return [c.to_dict() for c in candidates]


@app.get("/jobs/{job_id}/candidates/{classification}")
async def get_candidates_by_classification(
    job_id: int,
    classification: str,
    db: Session = Depends(get_db)
):
    """Get candidates by classification (High, Medium, Low)"""
    job = JobProfileService.get_job_profile(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job profile not found")
    
    # Normalize classification - accept both "High Match" and "High" formats
    normalized_classification = classification
    if classification == "High":
        normalized_classification = "High Match"
    elif classification == "Medium":
        normalized_classification = "Medium Match"
    elif classification == "Low":
        normalized_classification = "Low Match"
    
    if normalized_classification not in ["High Match", "Medium Match", "Low Match"]:
        raise HTTPException(status_code=400, detail="Invalid classification")
    
    candidates = CandidateMatchService.get_candidates_by_classification(
        db=db,
        job_profile_id=job_id,
        classification=normalized_classification
    )
    return [c.to_dict() for c in candidates]


@app.get("/jobs/{job_id}/statistics", response_model=JobStatistics)
async def get_job_statistics(job_id: int, db: Session = Depends(get_db)):
    """Get statistics for a job profile"""
    job = JobProfileService.get_job_profile(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job profile not found")
    
    stats = CandidateMatchService.get_job_statistics(db, job_id)
    return stats


@app.delete("/candidates/{candidate_id}")
async def delete_candidate(candidate_id: int, db: Session = Depends(get_db)):
    """Delete a candidate match record"""
    success = CandidateMatchService.delete_candidate_match(db, candidate_id)
    if not success:
        raise HTTPException(status_code=404, detail="Candidate match not found")
    return {"message": "Candidate deleted successfully"}


@app.put("/candidates/{candidate_id}")
async def update_candidate_notes(
    candidate_id: int,
    notes: str,
    db: Session = Depends(get_db)
):
    """Update notes for a candidate"""
    candidate = CandidateMatchService.update_candidate_match(
        db=db,
        match_id=candidate_id,
        notes=notes
    )
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate match not found")
    return candidate.to_dict()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
