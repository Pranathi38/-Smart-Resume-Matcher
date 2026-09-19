"""
SQLAlchemy database models and setup for Resume Matcher
Handles persistent storage of job profiles and candidate matches
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Optional
import os

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./resume_matcher.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class JobProfile(Base):
    """Job profile model for persistent storage"""
    __tablename__ = "job_profiles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    skills = Column(JSON, nullable=False)  # List of required skills
    requirements = Column(Text, nullable=True)
    experience_years = Column(Float, default=0)
    education_level = Column(String(50), default="Bachelors")
    certifications = Column(JSON, default=[])  # List of certifications
    languages = Column(JSON, default=[])  # List of languages
    location = Column(String(255), default="Remote")
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    # Relationships
    candidates = relationship("CandidateMatch", back_populates="job_profile", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "skills": self.skills,
            "requirements": self.requirements,
            "experience_years": self.experience_years,
            "education_level": self.education_level,
            "certifications": self.certifications,
            "languages": self.languages,
            "location": self.location,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
            "candidate_count": len(self.candidates)
        }


class CandidateMatch(Base):
    """Candidate match record linked to a job profile"""
    __tablename__ = "candidate_matches"

    id = Column(Integer, primary_key=True, index=True)
    job_profile_id = Column(Integer, ForeignKey("job_profiles.id"), nullable=False, index=True)
    candidate_name = Column(String(255), nullable=False, index=True)
    
    # Extracted candidate data
    candidate_data = Column(JSON, nullable=False)  # Full extracted resume data
    
    # Match scores
    final_score = Column(Float, nullable=False, index=True)
    classification = Column(String(50), nullable=False)  # High, Medium, Low
    scores = Column(JSON, nullable=False)  # Detailed scores per attribute
    weights = Column(JSON, nullable=False)  # Weights used for calculation
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    resume_filename = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    job_profile = relationship("JobProfile", back_populates="candidates")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "job_profile_id": self.job_profile_id,
            "candidate_name": self.candidate_name,
            "final_score": self.final_score,
            "classification": self.classification,
            "scores": self.scores,
            "weights": self.weights,
            "created_at": self.created_at.isoformat(),
            "resume_filename": self.resume_filename,
            "notes": self.notes
        }


class MatchWeightPreset(Base):
    """Saved weight presets for quick reuse"""
    __tablename__ = "weight_presets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    weights = Column(JSON, nullable=False)  # Weight configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "weights": self.weights,
            "created_at": self.created_at.isoformat()
        }


# Create all tables
def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
