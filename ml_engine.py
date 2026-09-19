"""
Neural Resume Matching Engine using Sentence Transformers
Handles semantic similarity calculation and weighted aggregation
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NeuralResumeMatcher:
    """
    Semantic-based resume matching using pre-trained sentence embeddings.
    Uses all-MiniLM-L6-v2 model (384-dimensional vectors).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the matcher with a pre-trained model.
        
        Args:
            model_name: HuggingFace model identifier
        """
        logger.info(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        logger.info("Model loaded successfully")

    def encode_text(self, text: str) -> np.ndarray:
        """
        Convert text to embedding vector.
        
        Args:
            text: Input text
            
        Returns:
            384-dimensional embedding vector
        """
        if not text or not isinstance(text, str):
            return np.zeros(384)
        
        text = text.strip()
        if not text:
            return np.zeros(384)
            
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate cosine similarity between two texts (0-100 scale).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-100)
        """
        vec1 = self.encode_text(text1)
        vec2 = self.encode_text(text2)
        
        # Handle zero vectors
        if np.allclose(vec1, 0) or np.allclose(vec2, 0):
            return 0.0
        
        similarity = cosine_similarity([vec1], [vec2])[0][0]
        # Convert from [-1, 1] to [0, 100]
        score = max(0, (similarity + 1) / 2 * 100)
        return float(score)

    def calculate_list_similarity(self, list1: List[str], list2: List[str], threshold: float = 50.0) -> float:
        """
        Calculate average similarity between two lists of items.
        Only counts matches above the threshold (default 50%).
        This allows semantic matching - e.g., "Python" matches "Python (Pandas)", "FastAPI" matches "Backend".
        
        Args:
            list1: First list of items (candidate's items)
            list2: Second list of items (job's required items)
            threshold: Minimum similarity score to count as a match (0-100)
            
        Returns:
            Average similarity score (0-100)
        """
        if not list1 or not list2:
            return 0.0
        
        similarities = []
        for item1 in list1:
            max_sim = 0
            for item2 in list2:
                sim = self.calculate_cosine_similarity(item1, item2)
                max_sim = max(max_sim, sim)
            # Only count if above threshold (strong match)
            if max_sim >= threshold:
                similarities.append(max_sim)
            else:
                similarities.append(0.0)  # Below threshold = no match
        
        return float(np.mean(similarities)) if similarities else 0.0

    def calculate_match_score(
        self,
        candidate_data: Dict,
        job_data: Dict,
        weights: Dict[str, float]
    ) -> Dict:
        """
        Calculate comprehensive match score using weighted semantic similarity.
        
        Args:
            candidate_data: Extracted candidate information
            job_data: Job requirements
            weights: Attribute weights (must sum to 1.0)
            
        Returns:
            Dictionary with individual scores and final match score
        """
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        scores = {}
        
        # Skills matching
        candidate_skills = candidate_data.get("skills", [])
        job_skills = job_data.get("skills", [])
        
        # Handle string inputs
        if isinstance(candidate_skills, str):
            candidate_skills = [s.strip() for s in candidate_skills.split(",") if s.strip()]
        if isinstance(job_skills, str):
            job_skills = [s.strip() for s in job_skills.split(",") if s.strip()]
        
        # Ensure lists
        if not isinstance(candidate_skills, list):
            candidate_skills = []
        if not isinstance(job_skills, list):
            job_skills = []
        
        # Handle case where skills are stored as list with comma-separated strings
        # e.g., ['Python, SQL, Tableau'] should become ['Python', 'SQL', 'Tableau']
        normalized_candidate_skills = []
        for skill in candidate_skills:
            if isinstance(skill, str) and ',' in skill:
                normalized_candidate_skills.extend([s.strip() for s in skill.split(',') if s.strip()])
            else:
                normalized_candidate_skills.append(skill)
        candidate_skills = normalized_candidate_skills
        
        normalized_job_skills = []
        for skill in job_skills:
            if isinstance(skill, str) and ',' in skill:
                normalized_job_skills.extend([s.strip() for s in skill.split(',') if s.strip()])
            else:
                normalized_job_skills.append(skill)
        job_skills = normalized_job_skills
        
        # Calculate skills match
        if job_skills:
            # Job requires skills - match against candidate skills
            if candidate_skills:
                scores["skills"] = self.calculate_list_similarity(candidate_skills, job_skills)
            else:
                # Job requires skills but candidate has none - strict 0%
                scores["skills"] = 0.0
        else:
            # Job doesn't require specific skills - neutral 100%
            scores["skills"] = 100.0
        
        # Experience years matching (removed redundant "experience" attribute)
        candidate_years = float(candidate_data.get("experience_years", 0))
        required_years = float(job_data.get("experience_years", 0))
        if required_years > 0:
            # Strict matching: candidate must meet or exceed required years
            if candidate_years >= required_years:
                exp_match = 100.0
            else:
                # Penalize for insufficient experience
                exp_match = (candidate_years / required_years) * 100
        else:
            # No experience requirement - any experience is acceptable
            exp_match = 100.0 if candidate_years > 0 else 50.0
        scores["experience_years"] = exp_match
        
        # Education matching
        candidate_education = candidate_data.get("education_level", "")
        job_education = job_data.get("education_level", "")
        scores["education"] = self.calculate_cosine_similarity(candidate_education, job_education)
        
        # Certifications matching
        candidate_certs = candidate_data.get("certifications", [])
        job_certs = job_data.get("certifications", [])
        
        # Handle string inputs
        if isinstance(candidate_certs, str):
            candidate_certs = [c.strip() for c in candidate_certs.split(",") if c.strip()]
        if isinstance(job_certs, str):
            job_certs = [c.strip() for c in job_certs.split(",") if c.strip()]
        
        # Ensure lists
        if not isinstance(candidate_certs, list):
            candidate_certs = []
        if not isinstance(job_certs, list):
            job_certs = []
        
        # Handle case where certs are stored as list with comma-separated strings
        normalized_candidate_certs = []
        for cert in candidate_certs:
            if isinstance(cert, str) and ',' in cert:
                normalized_candidate_certs.extend([c.strip() for c in cert.split(',') if c.strip()])
            else:
                normalized_candidate_certs.append(cert)
        candidate_certs = normalized_candidate_certs
        
        normalized_job_certs = []
        for cert in job_certs:
            if isinstance(cert, str) and ',' in cert:
                normalized_job_certs.extend([c.strip() for c in cert.split(',') if c.strip()])
            else:
                normalized_job_certs.append(cert)
        job_certs = normalized_job_certs
        
        # Calculate certifications match
        if job_certs:
            # Job requires certifications
            if candidate_certs:
                scores["certifications"] = self.calculate_list_similarity(candidate_certs, job_certs)
            else:
                scores["certifications"] = 0.0  # Job requires certs but candidate has none
        else:
            # No certifications required
            scores["certifications"] = 100.0  # Neutral
        
        # Languages matching
        candidate_langs = candidate_data.get("languages", [])
        job_langs = job_data.get("languages", [])
        
        # Handle string inputs
        if isinstance(candidate_langs, str):
            candidate_langs = [l.strip() for l in candidate_langs.split(",") if l.strip()]
        if isinstance(job_langs, str):
            job_langs = [l.strip() for l in job_langs.split(",") if l.strip()]
        
        # Ensure lists
        if not isinstance(candidate_langs, list):
            candidate_langs = []
        if not isinstance(job_langs, list):
            job_langs = []
        
        # Handle case where langs are stored as list with comma-separated strings
        normalized_candidate_langs = []
        for lang in candidate_langs:
            if isinstance(lang, str) and ',' in lang:
                normalized_candidate_langs.extend([l.strip() for l in lang.split(',') if l.strip()])
            else:
                normalized_candidate_langs.append(lang)
        candidate_langs = normalized_candidate_langs
        
        normalized_job_langs = []
        for lang in job_langs:
            if isinstance(lang, str) and ',' in lang:
                normalized_job_langs.extend([l.strip() for l in lang.split(',') if l.strip()])
            else:
                normalized_job_langs.append(lang)
        job_langs = normalized_job_langs
        
        # Calculate languages match
        if job_langs:
            # Job requires languages
            if candidate_langs:
                scores["languages"] = self.calculate_list_similarity(candidate_langs, job_langs)
            else:
                scores["languages"] = 0.0  # Job requires languages but candidate doesn't have
        else:
            # No languages required
            scores["languages"] = 100.0  # Neutral
        
        # Location matching
        candidate_location = candidate_data.get("location", "")
        job_location = job_data.get("location", "")
        scores["location"] = self.calculate_cosine_similarity(candidate_location, job_location)
        
        # Calculate weighted final score
        final_score = 0.0
        for attribute, weight in weights.items():
            if attribute in scores:
                final_score += scores[attribute] * weight
        
        # Apply comprehensive attribute-based scoring - consider ALL attributes
        skills_score = scores.get("skills", 0)
        exp_score = scores.get("experience_years", 0)
        edu_score = scores.get("education", 0)
        cert_score = scores.get("certifications", 0)
        lang_score = scores.get("languages", 0)
        loc_score = scores.get("location", 0)
        
        all_scores = [skills_score, exp_score, edu_score, cert_score, lang_score, loc_score]
        
        # Use MINIMUM score approach - if any critical attribute is weak, penalize heavily
        min_score = min(all_scores) if all_scores else 0
        
        # Count how many attributes are below 50% (weak match)
        weak_attributes = sum(1 for score in all_scores if score < 50)
        
        # If minimum attribute score is low, cap the final score based on it
        if min_score < 75:
            final_score = min(final_score, 75.0)
        
        if min_score < 60:
            final_score = min(final_score, 60.0)
        
        if min_score < 50:
            final_score = min(final_score, 50.0)
        
        if min_score < 40:
            final_score = min(final_score, 40.0)
        
        if min_score < 30:
            final_score = min(final_score, 30.0)
        
        # If 2+ attributes are weak (below 50%), additional penalty
        if weak_attributes >= 2:
            final_score = min(final_score, 65.0)
        
        if weak_attributes >= 3:
            final_score = min(final_score, 55.0)
        
        # Relaxed skill-based penalties - minimal strictness
        # Only cap if skills are very low (below 40%)
        if skills_score < 40:
            final_score = min(final_score, 50.0)
        
        # Classify match - balanced thresholds for 75% accuracy
        if final_score >= 80:
            classification = "High Match"
        elif final_score >= 60:
            classification = "Medium Match"
        else:
            classification = "Low Match"
        
        return {
            "scores": scores,
            "weights": weights,
            "final_score": round(final_score, 2),
            "classification": classification
        }

    def get_model_info(self) -> Dict:
        """Get information about the loaded model."""
        return {
            "model_name": self.model_name,
            "embedding_dimension": 384,
            "status": "ready"
        }
