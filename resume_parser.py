"""
Resume Parser using Google Gemini API with Text-First Approach
Extracts resume data into a standardized JSON format using pdfplumber for better layout handling
"""

import google.generativeai as genai
import google.api_core.exceptions
import json
import logging
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import pdfplumber
import re
from docx import Document
import time
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_json_response(response_text: str) -> str:
    """
    Removes Markdown formatting (```json ... ```) to prevent JSONDecodeError.
    
    Args:
        response_text: Raw response from Gemini
        
    Returns:
        Cleaned JSON string
    """
    if not response_text:
        return ""
    
    cleaned = re.sub(r"```json\s*", "", response_text, flags=re.IGNORECASE)  # Remove opening ```json
    cleaned = re.sub(r"```\s*$", "", cleaned, flags=re.MULTILINE)           # Remove closing ```
    cleaned = re.sub(r"^```\s*", "", cleaned, flags=re.MULTILINE)           # Remove opening ``` (any language)
    cleaned = cleaned.strip()
    
    # Remove any leading/trailing whitespace and newlines
    cleaned = cleaned.lstrip().rstrip()
    
    return cleaned


class GeminiResumeParser:
    """
    Parse resumes using Google Gemini API with structured output.
    Enforces JSON schema for consistent extraction.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the parser with Gemini API.
        
        Args:
            api_key: Google Gemini API key (uses env var if not provided)
        """
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Use Gemini 3.0 for better performance and accuracy
        # Try gemini-3.0-flash first, fallback to alternatives if not available
        try:
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            logger.info("Gemini API configured successfully with gemini-2.5-flash")
        except Exception as e:
            logger.warning(f"gemini-2.5-flash not available, trying gemini-2.5-flash: {e}")
            try:
                self.model = genai.GenerativeModel("gemini-2.5-flash")
                logger.info("Gemini API configured successfully with gemini-2.5-flash")
            except Exception as e2:
                logger.warning(f"gemini-2.5-flash not available, trying gemini-2.5-pro: {e2}")
                self.model = genai.GenerativeModel("gemini-3-pro")
                logger.info("Gemini API configured successfully with gemini-2.5-pro")

    def _clean_and_trim_text(self, text: str, max_length: int = 3000) -> str:
        """
        Clean and trim text to reduce token usage.
        
        Args:
            text: Raw text to clean
            max_length: Maximum characters to keep
            
        Returns:
            Cleaned and trimmed text
        """
        # Remove extra whitespace and newlines
        cleaned = re.sub(r'\s+', ' ', text)
        cleaned = re.sub(r'[^\x00-\x7F]+', '', cleaned)  # Remove non-ASCII
        cleaned = cleaned.strip()
        
        # Trim to max_length if needed
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length] + "..."
            logger.info(f"Text trimmed from {len(text)} to {max_length} characters")
        
        return cleaned
    
    def _extract_name_from_text(self, text: str) -> str:
        """
        Extract candidate name from resume text as fallback.
        Looks for name patterns in the first few lines.
        """
        if not text:
            return "Unknown"
        
        lines = text.split('\n')[:15]  # Check first 15 lines
        
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
    
    @retry(
        wait=wait_exponential(multiplier=1, min=5, max=30),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type(google.api_core.exceptions.ResourceExhausted)
    )
    def _call_gemini_api(self, prompt: str):
        """
        Call Gemini API with retry logic for rate limiting.
        
        Args:
            prompt: The prompt to send to Gemini
            
        Returns:
            Gemini response
        """
        try:
            logger.info("Making API call to Gemini...")
            # Add timeout to prevent hanging (60 seconds max)
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.1
                ),
                request_options={"timeout": 60}  # 60 second timeout
            )
            logger.info("API call successful")
            
            # Validate response
            if not response:
                logger.error("Gemini API returned None response")
                raise ValueError("Empty response from Gemini API")
            
            if not hasattr(response, 'text'):
                logger.error(f"Response missing 'text' attribute. Response type: {type(response)}")
                logger.error(f"Response attributes: {dir(response)}")
                raise ValueError("Invalid response format from Gemini API")
            
            if not response.text or not response.text.strip():
                logger.error("Gemini API returned empty text")
                raise ValueError("Empty text in Gemini API response")
            
            logger.info(f"Response received: {len(response.text)} characters")
            return response
        except Exception as e:
            logger.error(f"API call failed: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise

    def _extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF preserving layout using pdfplumber.
        
        Args:
            file_path: Path to the resume PDF file
            
        Returns:
            Extracted text with layout preserved
        """
        try:
            text_content = ""
            with pdfplumber.open(file_path) as pdf:
                logger.info(f"Extracting text from {len(pdf.pages)} pages")
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text preserving physical layout (good for columns)
                    page_text = page.extract_text(layout=True)
                    if page_text:
                        text_content += f"\n--- PAGE {page_num} ---\n{page_text}\n"
            
            logger.info(f"Extracted {len(text_content)} characters from PDF")
            if len(text_content.strip()) < 50:
                logger.warning(f"Very little text extracted ({len(text_content)} chars). PDF might be image-based or corrupted.")
            return text_content
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return ""

    def _extract_text_from_docx(self, file_path: str) -> str:
        """
        Extract text from Word document (.docx).
        
        Args:
            file_path: Path to the resume Word document
            
        Returns:
            Extracted text
        """
        try:
            doc = Document(file_path)
            text_content = ""
            
            # Extract text from paragraphs
            for para in doc.paragraphs:
                if para.text.strip():
                    text_content += para.text + "\n"
            
            # Extract text from tables
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
        Extract structured data from a resume (PDF or Word document) using text-first approach.
        
        Args:
            file_path: Path to the resume file (PDF or .docx)
            
        Returns:
            Dictionary with extracted resume data
        """
        try:
            # Step 1: Extract text from file based on format
            logger.info(f"Extracting text from: {file_path}")
            
            if file_path.lower().endswith('.docx'):
                logger.info("Detected Word document format (.docx)")
                resume_text = self._extract_text_from_docx(file_path)
            elif file_path.lower().endswith('.pdf'):
                logger.info("Detected PDF format")
                resume_text = self._extract_text_from_pdf(file_path)
            else:
                logger.error(f"Unsupported file format: {file_path}")
                return self._get_fallback_extraction()
            
            if not resume_text or len(resume_text.strip()) < 50:
                logger.warning(f"No text extracted from PDF (length: {len(resume_text) if resume_text else 0}), using fallback")
                logger.warning("This could indicate:")
                logger.warning("  1. PDF is image-based (scanned) and needs OCR")
                logger.warning("  2. PDF is corrupted or encrypted")
                logger.warning("  3. PDF extraction library issue")
                return self._get_fallback_extraction()
            
            # Clean and trim text to reduce token usage and processing time
            # Increase max_length for better extraction accuracy
            resume_text = self._clean_and_trim_text(resume_text, max_length=5000)
            logger.info(f"Cleaned text length: {len(resume_text)} characters")
            
            # Step 2: Parse text with Gemini using strict JSON output
            logger.info("Parsing extracted text with Gemini API")
            
            prompt = f"""
            You are a strict data extraction engine. Extract the following details from the resume text below.
            
            RULES:
            1. Extract CANDIDATE_NAME - This is CRITICAL. Look for the person's full name at the top of the resume, usually the first line or header. Extract the complete name (e.g., "John Doe", "Jane Smith"). If you cannot find a name, return "Unknown".
            2. Extract SKILLS as a list of strings. Look for technical terms (e.g., Python, SQL, Tableau).
            3. Extract EXPERIENCE_YEARS as a single integer. If strictly unknown, return 0.
            4. Extract EDUCATION_LEVEL (e.g., "Bachelors", "Masters", "PhD", "High School").
            5. Extract LOCATION (City, Country/State) or "Remote".
            6. Do NOT add markdown formatting. Return RAW JSON only.
            7. Do NOT wrap response in ```json blocks.

            RESUME TEXT:
            {resume_text}

            REQUIRED JSON SCHEMA (return ONLY this, no explanation):
            {{
                "candidate_name": "Full Name or Unknown",
                "skills": ["Skill1", "Skill2", "Skill3"],
                "experience_years": 0,
                "education_level": "Bachelors",
                "location": "City, Country",
                "certifications": ["Cert1"],
                "languages": ["English"],
                "experience_description": "Brief summary",
                "career_objective": "Career goals"
            }}
            """
            
            # Generate response with retry logic for rate limiting
            response = self._call_gemini_api(prompt)
            
            # Parse the response with robust cleaning
            if not response:
                logger.error("Gemini API returned None or empty response")
                return self._get_fallback_extraction()
            
            # Check if response has text attribute
            if not hasattr(response, 'text') or not response.text:
                logger.error(f"Gemini API response missing text attribute. Response type: {type(response)}")
                logger.error(f"Response object: {response}")
                return self._get_fallback_extraction()
            
            response_text = response.text.strip()
            logger.info(f"Raw Gemini response (first 200 chars): {response_text[:200]}")
            
            # Clean markdown formatting
            cleaned_json = clean_json_response(response_text)
            logger.info(f"Cleaned JSON (first 200 chars): {cleaned_json[:200]}")
            
            extracted_data = json.loads(cleaned_json)
            
            # Normalize the response to match expected schema
            # Extract name with better handling - try multiple sources
            candidate_name = extracted_data.get("candidate_name", "").strip()
            if not candidate_name or candidate_name.lower() in ["unknown", "n/a", "na", "", "null"]:
                # Try to extract name from resume text directly as fallback
                candidate_name = self._extract_name_from_text(resume_text)
                logger.info(f"Name not found in API response, extracted from text: {candidate_name}")
            
            normalized_data = {
                "candidate_name": candidate_name if candidate_name else "Unknown",
                "skills": extracted_data.get("skills", []),
                "experience_years": float(extracted_data.get("experience_years", 0)) if extracted_data.get("experience_years") else 0,
                "education_level": extracted_data.get("education_level") or "Unknown",
                "certifications": extracted_data.get("certifications", []),
                "languages": extracted_data.get("languages", []),
                "location": extracted_data.get("location") or "Unknown",
                "experience_description": extracted_data.get("experience_description") or "",
                "career_objective": extracted_data.get("career_objective") or "",
                "email": extracted_data.get("email") or None,
                "salary_expectation": extracted_data.get("salary_expectation") or None
            }
            
            logger.info(f"Successfully extracted data for: {normalized_data['candidate_name']}")
            logger.info(f"  Skills: {normalized_data['skills']} (count: {len(normalized_data['skills'])})")
            logger.info(f"  Experience: {normalized_data['experience_years']} years")
            logger.info(f"  Education: {normalized_data['education_level']}")
            logger.info(f"  Certifications: {normalized_data['certifications']}")
            logger.info(f"  Languages: {normalized_data['languages']}")
            
            return normalized_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            if 'response_text' in locals():
                logger.error(f"Response text (first 500 chars): {response_text[:500]}")
                logger.error(f"Response text (full length): {len(response_text)} characters")
            logger.warning("Falling back to keyword-based extraction")
            return self._use_keyword_fallback(file_path)
        except AttributeError as e:
            logger.error(f"Attribute error accessing response: {e}")
            logger.error(f"This usually means the API response format changed")
            import traceback
            logger.error(traceback.format_exc())
            logger.warning("Falling back to keyword-based extraction")
            return self._use_keyword_fallback(file_path)
        except google.api_core.exceptions.ResourceExhausted as e:
            error_str = str(e).lower()
            if "quota" in error_str or "429" in error_str:
                logger.error("="*70)
                logger.error("GEMINI API QUOTA EXCEEDED")
                logger.error("="*70)
                logger.error("The free tier quota has been exhausted.")
                logger.error("Switching to keyword-based fallback extraction.")
                logger.error("Note: Fallback extraction is less accurate but will still extract:")
                logger.error("  - Skills (keyword matching)")
                logger.error("  - Experience years (pattern matching)")
                logger.error("  - Education level (keyword matching)")
                logger.error("  - Certifications, languages, location")
                logger.error("="*70)
                logger.warning("To restore full functionality:")
                logger.warning("  1. Wait for quota to reset (usually daily)")
                logger.warning("  2. Upgrade to a paid plan")
                logger.warning("  3. Check usage at: https://ai.dev/usage?tab=rate-limit")
                logger.error("="*70)
            logger.warning("Falling back to keyword-based extraction")
            return self._use_keyword_fallback(file_path)
        except Exception as e:
            logger.error(f"Error extracting resume data: {type(e).__name__}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            logger.warning("Falling back to keyword-based extraction")
            return self._use_keyword_fallback(file_path)

    def _use_keyword_fallback(self, file_path: str) -> Dict:
        """Use keyword-based fallback parser when Gemini API fails."""
        try:
            from resume_fallback_parser import FallbackResumeParser
            fallback_parser = FallbackResumeParser()
            logger.info("Using keyword-based fallback parser")
            return fallback_parser.extract_resume_data(file_path)
        except Exception as e:
            logger.error(f"Fallback parser also failed: {e}")
            return self._get_fallback_extraction()
    
    def _get_fallback_extraction(self) -> Dict:
        """Return a fallback empty extraction structure."""
        logger.warning("Using empty fallback extraction - all parsing methods failed.")
        return {
            "candidate_name": "Unknown",
            "skills": [],
            "experience_years": 0,
            "education_level": "Unknown",
            "certifications": [],
            "languages": [],
            "salary_expectation": None,
            "location": "Unknown",
            "experience_description": "",
            "career_objective": ""
        }

    def extract_from_text(self, resume_text: str) -> Dict:
        """
        Extract structured data from resume text (without file upload).
        
        Args:
            resume_text: Resume content as text
            
        Returns:
            Dictionary with extracted resume data
        """
        try:
            extraction_schema = {
                "type": "object",
                "properties": {
                    "candidate_name": {"type": "string"},
                    "skills": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "experience_years": {"type": "number"},
                    "education_level": {"type": "string"},
                    "certifications": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "salary_expectation": {"type": ["number", "null"]},
                    "location": {"type": "string"},
                    "experience_description": {"type": "string"},
                    "career_objective": {"type": "string"}
                },
                "required": [
                    "candidate_name",
                    "skills",
                    "experience_years",
                    "education_level"
                ]
            }
            
            prompt = f"""
            Please extract the following information from this resume text and return it as JSON:
            - candidate_name: Full name of the candidate
            - skills: List of technical and professional skills
            - experience_years: Total years of professional experience
            - education_level: Highest education level (e.g., Bachelors, Masters, PhD)
            - certifications: List of professional certifications
            - languages: List of languages the candidate speaks
            - salary_expectation: Expected salary (if mentioned)
            - location: Current location or preferred work location
            - experience_description: Brief summary of work experience
            - career_objective: Career goals or objective statement
            
            Resume Text:
            {resume_text}
            
            Return ONLY valid JSON, no additional text.
            """
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=extraction_schema
                )
            )
            
            extracted_data = json.loads(response.text)
            logger.info(f"Successfully extracted data for: {extracted_data.get('candidate_name', 'Unknown')}")
            
            return extracted_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            return self._get_fallback_extraction()
        except Exception as e:
            logger.error(f"Error extracting resume data: {e}")
            return self._get_fallback_extraction()
