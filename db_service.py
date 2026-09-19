"""
Database service layer for job profiles and candidate matches
Handles all CRUD operations
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from database import JobProfile, CandidateMatch, MatchWeightPreset
from typing import List, Dict, Optional
from datetime import datetime


class JobProfileService:
    """Service for managing job profiles"""
    
    @staticmethod
    def create_job_profile(
        db: Session,
        title: str,
        skills: List[str],
        requirements: str,
        experience_years: float,
        education_level: str,
        certifications: List[str],
        languages: List[str],
        location: str
    ) -> JobProfile:
        """Create a new job profile"""
        job = JobProfile(
            title=title,
            skills=skills,
            requirements=requirements,
            experience_years=experience_years,
            education_level=education_level,
            certifications=certifications,
            languages=languages,
            location=location
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def get_job_profile(db: Session, job_id: int) -> Optional[JobProfile]:
        """Get a job profile by ID"""
        return db.query(JobProfile).filter(JobProfile.id == job_id).first()
    
    @staticmethod
    def list_job_profiles(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> List[JobProfile]:
        """List all job profiles"""
        query = db.query(JobProfile)
        if active_only:
            query = query.filter(JobProfile.is_active == True)
        return query.order_by(desc(JobProfile.created_at)).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_job_profile(
        db: Session,
        job_id: int,
        **kwargs
    ) -> Optional[JobProfile]:
        """Update a job profile"""
        job = db.query(JobProfile).filter(JobProfile.id == job_id).first()
        if not job:
            return None
        
        for key, value in kwargs.items():
            if hasattr(job, key) and key not in ['id', 'created_at']:
                setattr(job, key, value)
        
        job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def delete_job_profile(db: Session, job_id: int) -> bool:
        """Soft delete a job profile"""
        job = db.query(JobProfile).filter(JobProfile.id == job_id).first()
        if not job:
            return False
        
        job.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_job_as_dict(db: Session, job_id: int) -> Optional[Dict]:
        """Get job profile as dictionary for API response"""
        job = JobProfileService.get_job_profile(db, job_id)
        return job.to_dict() if job else None


class CandidateMatchService:
    """Service for managing candidate matches"""
    
    @staticmethod
    def create_candidate_match(
        db: Session,
        job_profile_id: int,
        candidate_name: str,
        candidate_data: Dict,
        final_score: float,
        classification: str,
        scores: Dict,
        weights: Dict,
        resume_filename: Optional[str] = None,
        notes: Optional[str] = None
    ) -> CandidateMatch:
        """Create a new candidate match record"""
        match = CandidateMatch(
            job_profile_id=job_profile_id,
            candidate_name=candidate_name,
            candidate_data=candidate_data,
            final_score=final_score,
            classification=classification,
            scores=scores,
            weights=weights,
            resume_filename=resume_filename,
            notes=notes
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        return match
    
    @staticmethod
    def get_candidate_match(db: Session, match_id: int) -> Optional[CandidateMatch]:
        """Get a candidate match by ID"""
        return db.query(CandidateMatch).filter(CandidateMatch.id == match_id).first()
    
    @staticmethod
    def list_candidates_for_job(
        db: Session,
        job_profile_id: int,
        skip: int = 0,
        limit: int = 100,
        sort_by: str = "final_score"
    ) -> List[CandidateMatch]:
        """List all candidates for a specific job profile"""
        query = db.query(CandidateMatch).filter(
            CandidateMatch.job_profile_id == job_profile_id
        )
        
        if sort_by == "final_score":
            query = query.order_by(desc(CandidateMatch.final_score))
        elif sort_by == "created_at":
            query = query.order_by(desc(CandidateMatch.created_at))
        elif sort_by == "candidate_name":
            query = query.order_by(CandidateMatch.candidate_name)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_candidates_by_classification(
        db: Session,
        job_profile_id: int,
        classification: str
    ) -> List[CandidateMatch]:
        """Get candidates by classification (High, Medium, Low)"""
        return db.query(CandidateMatch).filter(
            and_(
                CandidateMatch.job_profile_id == job_profile_id,
                CandidateMatch.classification == classification
            )
        ).order_by(desc(CandidateMatch.final_score)).all()
    
    @staticmethod
    def update_candidate_match(
        db: Session,
        match_id: int,
        **kwargs
    ) -> Optional[CandidateMatch]:
        """Update a candidate match record"""
        match = db.query(CandidateMatch).filter(CandidateMatch.id == match_id).first()
        if not match:
            return None
        
        for key, value in kwargs.items():
            if hasattr(match, key) and key not in ['id', 'created_at', 'job_profile_id']:
                setattr(match, key, value)
        
        db.commit()
        db.refresh(match)
        return match
    
    @staticmethod
    def delete_candidate_match(db: Session, match_id: int) -> bool:
        """Delete a candidate match record"""
        match = db.query(CandidateMatch).filter(CandidateMatch.id == match_id).first()
        if not match:
            return False
        
        db.delete(match)
        db.commit()
        return True
    
    @staticmethod
    def get_job_statistics(db: Session, job_profile_id: int) -> Dict:
        """Get statistics for a job profile"""
        candidates = db.query(CandidateMatch).filter(
            CandidateMatch.job_profile_id == job_profile_id
        ).all()
        
        if not candidates:
            return {
                "total_candidates": 0,
                "high_match": 0,
                "medium_match": 0,
                "low_match": 0,
                "average_score": 0,
                "highest_score": 0,
                "lowest_score": 0
            }
        
        scores = [c.final_score for c in candidates]
        classifications = [c.classification for c in candidates]
        
        # Count matches - handle both "High Match" and "High" formats for compatibility
        high_count = sum(1 for c in classifications if "High" in c or c == "High")
        medium_count = sum(1 for c in classifications if "Medium" in c or c == "Medium")
        low_count = sum(1 for c in classifications if "Low" in c or c == "Low")
        
        return {
            "total_candidates": len(candidates),
            "high_match": high_count,
            "medium_match": medium_count,
            "low_match": low_count,
            "average_score": sum(scores) / len(scores) if scores else 0,
            "highest_score": max(scores) if scores else 0,
            "lowest_score": min(scores) if scores else 0
        }


class WeightPresetService:
    """Service for managing weight presets"""
    
    @staticmethod
    def create_preset(
        db: Session,
        name: str,
        weights: Dict,
        description: Optional[str] = None
    ) -> MatchWeightPreset:
        """Create a new weight preset"""
        preset = MatchWeightPreset(
            name=name,
            weights=weights,
            description=description
        )
        db.add(preset)
        db.commit()
        db.refresh(preset)
        return preset
    
    @staticmethod
    def get_preset(db: Session, preset_id: int) -> Optional[MatchWeightPreset]:
        """Get a preset by ID"""
        return db.query(MatchWeightPreset).filter(MatchWeightPreset.id == preset_id).first()
    
    @staticmethod
    def get_preset_by_name(db: Session, name: str) -> Optional[MatchWeightPreset]:
        """Get a preset by name"""
        return db.query(MatchWeightPreset).filter(MatchWeightPreset.name == name).first()
    
    @staticmethod
    def list_presets(db: Session) -> List[MatchWeightPreset]:
        """List all weight presets"""
        return db.query(MatchWeightPreset).order_by(MatchWeightPreset.created_at).all()
    
    @staticmethod
    def delete_preset(db: Session, preset_id: int) -> bool:
        """Delete a weight preset"""
        preset = db.query(MatchWeightPreset).filter(MatchWeightPreset.id == preset_id).first()
        if not preset:
            return False
        
        db.delete(preset)
        db.commit()
        return True
