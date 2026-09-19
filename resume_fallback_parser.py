"""
Fallback Resume Parser using keyword-based extraction
Works when Gemini API is not available or quota is exceeded
"""

import re
import logging
from typing import Dict, List, Optional
import pdfplumber
from docx import Document

logger = logging.getLogger(__name__)

class FallbackResumeParser:
    """
    Fallback resume parser using keyword-based extraction.
    Used when Gemini API is not available or quota is exceeded.
    """
    
    def __init__(self):
        """Initialize the fallback parser."""
        logger.info("Fallback resume parser initialized")
    
    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills using keyword patterns."""
        # Common technical skills
        skill_keywords = [
            'python', 'java', 'javascript', 'react', 'nodejs', 'angular', 'vue',
            'sql', 'mysql', 'postgresql', 'mongodb', 'nosql',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'machine learning', 'data science', 'analytics', 'tableau', 'power bi',
            'excel', 'word', 'powerpoint', 'office', 'microsoft office',
            'git', 'github', 'gitlab', 'ci/cd', 'devops',
            'html', 'css', 'typescript', 'node', 'express',
            'django', 'flask', 'fastapi', 'spring', 'laravel',
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas',
            'communication', 'leadership', 'management', 'project management',
            'agile', 'scrum', 'jira', 'confluence', 'slack',
            'c++', 'c#', '.net', 'java', 'scala', 'rust', 'go',
            'linux', 'windows', 'macos', 'ubuntu', 'bash', 'shell',
            'rest api', 'graphql', 'microservices', 'api design',
            'testing', 'unit testing', 'integration testing', 'jest', 'pytest',
            'aws certified', 'azure certified', 'google cloud', 'certification',
            'c++', 'c#', '.net', 'java', 'scala', 'rust', 'go',
            'linux', 'windows', 'macos', 'ubuntu', 'bash', 'shell',
            'rest api', 'graphql', 'microservices', 'api design',
            'testing', 'unit testing', 'integration testing', 'jest', 'pytest',
            'aws certified', 'azure certified', 'google cloud', 'certification'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in text_lower:
                found_skills.append(skill.title())
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(found_skills).keys())
    
    def _extract_experience_years(self, text: str) -> int:
        """Extract years of experience from text."""
        # Look for patterns like "5 years", "5+ years", etc.
        patterns = [
            r'(\d+)\+?\s*years?',
            r'over\s+(\d+)\s*years?',
            r'experience\s*:\s*(\d+)',
            r'(\d{4})\s*-\s*(\d{4})',  # Date range like 2019-2023
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # For date range pattern, calculate difference
                if pattern == r'(\d{4})\s*-\s*(\d{4})' and len(matches) > 0:
                    try:
                        if isinstance(matches[0], tuple) and len(matches[0]) == 2:
                            start_year = int(matches[0][0])
                            end_year = int(matches[0][1])
                            years = end_year - start_year
                            if years > 0 and years < 50:
                                return years
                    except:
                        pass
                else:
                    # For single number patterns
                    try:
                        if isinstance(matches[0], tuple):
                            return int(matches[0][0])
                        else:
                            return int(matches[0])
                    except:
                        pass
        
        return 0
    
    def _extract_education(self, text: str) -> str:
        """Extract education level from text."""
        education_levels = [
            ('phd', 'PhD', 'Doctorate', 'Doctor of Philosophy'),
            ('master', 'Master', 'M.S', 'M.Sc', 'MBA'),
            ('bachelor', 'Bachelor', 'B.S', 'B.Sc', 'B.Tech', 'B.Eng'),
            ('associate', 'Associate', 'A.S', 'A.A'),
            ('diploma', 'Diploma', 'Certificate'),
            ('high school', 'H.S', 'High School')
        ]
        
        text_lower = text.lower()
        
        for level, *keywords in education_levels:
            for keyword in keywords:
                if keyword in text_lower:
                    if level == 'master':
                        return "Master's"
                    elif level == 'bachelor':
                        return "Bachelor's"
                    elif level == 'phd':
                        return "PhD"
                    elif level == 'associate':
                        return "Associate's"
                    elif level == 'diploma':
                        return "Diploma"
                    elif level == 'high school':
                        return "High School"
        
        return "Unknown"
    
    def _extract_name(self, text: str) -> str:
        """Extract candidate name from text with improved logic."""
        if not text:
            return "Unknown"
        
        lines = text.split('\n')[:20]  # Check first 20 lines
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip common header patterns
            if any(skip in line.lower() for skip in ['resume', 'cv', 'curriculum', 'vitae', 'phone', 'email', '@', 'http', 'linkedin']):
                continue
            
            # Look for name pattern: 2-4 words, each starting with capital letter
            words = line.split()
            if 2 <= len(words) <= 4:
                # Check if all words start with capital and are not all caps
                if all(word and word[0].isupper() and not word.isupper() for word in words if word):
                    # Exclude common non-name words
                    exclude_words = ['the', 'and', 'or', 'for', 'with', 'from', 'about', 'objective', 'summary']
                    if not any(word.lower() in exclude_words for word in words):
                        # Additional check: names usually don't contain numbers or special chars
                        if not any(char.isdigit() or char in '()[]{}' for char in line):
                            return line
        
        return "Unknown"
    
    def _extract_location(self, text: str) -> str:
        """Extract location from text."""
        # Look for location patterns
        location_patterns = [
            r'([A-Z][a-z]+\s*,\s*[A-Z]{2,})',  # City, State
            r'([A-Z][a-z]+\s+[A-Z]{2,})',  # City State
            r'remote|work\s+from\s+home',  # Remote work
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        
        return "Unknown"
    
    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from text."""
        cert_patterns = [
            r'([A-Z][a-z]+\s+Certified)',
            r'(AWS\s+Certified)',
            r'(Google\s+Cloud)',
            r'(Microsoft\s+Certified)',
            r'(Oracle\s+Certified)',
            r'(PMP|Project\s+Management\s+Professional)',
            r'(Scrum\s+Master)',
            r'(ITIL)',
        ]
        
        found_certs = []
        for pattern in cert_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_certs.extend(matches)
        
        # Remove duplicates
        return list(dict.fromkeys(found_certs).keys())
    
    def _extract_languages(self, text: str) -> List[str]:
        """Extract languages from text."""
        languages = [
            'english', 'spanish', 'french', 'german', 'chinese', 'mandarin',
            'japanese', 'korean', 'portuguese', 'russian', 'arabic',
            'hindi', 'italian', 'dutch', 'swedish', 'norwegian'
        ]
        
        text_lower = text.lower()
        found_langs = []
        
        for lang in languages:
            if lang in text_lower:
                found_langs.append(lang.title())
        
        return list(dict.fromkeys(found_langs).keys())
    
    def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        try:
            text_content = ""
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"Extracting text from {len(pdf.pages)} pages using fallback parser")
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        text_content += f"\n--- PAGE {page_num} ---\n{page_text}\n"
            
            logger.info(f"Extracted {len(text_content)} characters from PDF")
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return ""
    
    def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from Word document."""
        try:
            doc = Document(file_path)
            text_content = ""
            
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content += para.text + "\n"
            
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text.strip():
                            text_content += cell.text + " | "
                    text_content += "\n"
            
            logger.info(f"Extracted {len(text_content)} characters from Word document")
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text from Word document: {e}")
            return ""
    
    def extract_resume_data(self, file_path: str) -> Dict:
        """
        Extract structured data from a resume (PDF or Word document) using keyword-based fallback parsing.
        
        Args:
            file_path: Path to the resume file (PDF or .docx)
            
        Returns:
            Dictionary with extracted resume data
        """
        try:
            logger.info("Using fallback parser (keyword-based extraction) - Gemini API unavailable")
            
            # Extract text from file
            if file_path.lower().endswith('.docx'):
                resume_text = self._extract_text_from_docx(file_path)
            elif file_path.lower().endswith('.pdf'):
                resume_text = self._extract_text_from_pdf(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path}")
                return self._get_empty_data()
            
            if not resume_text or len(resume_text.strip()) < 50:
                logger.warning(f"Very little text extracted ({len(resume_text) if resume_text else 0} chars)")
                return self._get_empty_data()
            
            # Extract using keyword-based methods
            extracted_data = {
                "candidate_name": self._extract_name(resume_text),
                "skills": self._extract_skills(resume_text),
                "experience_years": self._extract_experience_years(resume_text),
                "education_level": self._extract_education(resume_text),
                "certifications": self._extract_certifications(resume_text),
                "languages": self._extract_languages(resume_text),
                "location": self._extract_location(resume_text),
                "experience_description": "",
                "career_objective": "",
                "email": None,
                "salary_expectation": None
            }
            
            logger.info(f"Fallback extraction completed for: {extracted_data['candidate_name']}")
            logger.info(f"  Skills: {extracted_data['skills']} (count: {len(extracted_data['skills'])})")
            logger.info(f"  Experience: {extracted_data['experience_years']} years")
            logger.info(f"  Education: {extracted_data['education_level']}")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error in fallback extraction: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_empty_data()
    
    def _get_empty_data(self) -> Dict:
        """Return a fallback empty extraction structure."""
        return {
            "candidate_name": "Unknown",
            "skills": [],
            "experience_years": 0,
            "education_level": "Unknown",
            "certifications": [],
            "languages": [],
            "location": "Unknown",
            "experience_description": "",
            "career_objective": "",
            "email": None,
            "salary_expectation": None
        }
