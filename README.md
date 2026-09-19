# Smart Resume Matcher - Neural Resume Matching Engine

A sophisticated full-stack application that uses semantic search and machine learning to match resumes with job descriptions. The system leverages sentence transformers for deep learning-based similarity calculations and provides an interactive UI for recruiters to adjust matching weights in real-time.

## 🎯 Features

- **Semantic Resume Parsing**: Uses Google Gemini 1.5 Flash API with structured outputs to extract resume data
- **Neural Matching**: Employs sentence-transformers (all-MiniLM-L6-v2) for semantic similarity calculations
- **Weighted Scoring**: Customizable attribute weights (Skills, Experience, Education, Certifications, Languages, Location)
- **Interactive Visualization**: Radar chart showing match analysis across all attributes
- **Real-time Updates**: Adjust weights and see match scores update instantly
- **Dark Mode UI**: Modern, responsive interface built with Next.js, Tailwind CSS, and Lucide icons
- **Batch Processing**: Support for matching multiple candidates against a single job

## 🏗️ Architecture

### Backend (Python + FastAPI)
- **ML Engine** (`ml_engine.py`): Semantic similarity calculations using sentence-transformers
- **Resume Parser** (`resume_parser.py`): Gemini API integration for structured resume extraction
- **API Server** (`server.py`): FastAPI endpoints for resume extraction and matching

### Frontend (Next.js + React)
- **Job Form**: Define job requirements and skills
- **Resume Upload**: PDF upload with drag-and-drop support
- **Match Results**: Detailed scoring with radar chart visualization
- **Weight Sliders**: Interactive controls to adjust matching weights

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- Google Gemini API key (for resume parsing)
- pip and npm

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Navigate to project root
cd p:\JOB\ Matching

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create a .env file with:
# GOOGLE_API_KEY=your_gemini_api_key_here

# Start the FastAPI server
python server.py
```

The backend will run on `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will run on `http://localhost:3000`

## 📖 API Documentation

### Endpoints

#### Health Check
```
GET /health
```
Returns the status of ML engine and parser.

#### Extract Resume
```
POST /extract-resume
Content-Type: multipart/form-data

Body: PDF file
```
Extracts structured data from a resume PDF using Gemini API.

**Response:**
```json
{
  "candidate_name": "John Doe",
  "skills": ["Python", "Machine Learning", "FastAPI"],
  "experience_years": 5,
  "education_level": "Masters",
  "certifications": ["AWS Certified"],
  "languages": ["English", "Spanish"],
  "salary_expectation": 120000,
  "location": "San Francisco",
  "experience_description": "...",
  "career_objective": "..."
}
```

#### Calculate Match Score
```
POST /match-resume
Content-Type: application/json

Body:
{
  "candidate_data": {...},
  "job_data": {
    "title": "Senior ML Engineer",
    "skills": ["Python", "TensorFlow"],
    "requirements": "...",
    "experience_years": 3,
    "education_level": "Bachelors",
    "certifications": [],
    "languages": ["English"],
    "location": "Remote"
  },
  "weights": {
    "skills": 0.35,
    "experience": 0.25,
    "experience_years": 0.15,
    "education": 0.10,
    "certifications": 0.10,
    "languages": 0.03,
    "location": 0.02
  }
}
```

**Response:**
```json
{
  "candidate_name": "John Doe",
  "final_score": 82.5,
  "classification": "High Match",
  "scores": {
    "skills": 85,
    "experience": 78,
    "experience_years": 90,
    "education": 100,
    "certifications": 60,
    "languages": 100,
    "location": 50
  },
  "weights": {...}
}
```

#### Batch Match
```
POST /batch-match
Content-Type: application/json

Body:
{
  "candidates": [{...}, {...}],
  "job_data": {...},
  "weights": {...}
}
```

Returns sorted list of match results (highest score first).

#### Calculate Similarity
```
POST /calculate-similarity
Content-Type: application/json

Body:
{
  "text1": "Python and Machine Learning",
  "text2": "Python developer with ML experience"
}
```

Returns cosine similarity score (0-100).

## 🧠 How Semantic Matching Works

### 1. Text Vectorization
- Uses `all-MiniLM-L6-v2` model from HuggingFace
- Converts text into 384-dimensional embeddings
- Captures semantic meaning, not just keywords

### 2. Similarity Calculation
- **Cosine Similarity**: Measures angle between vectors
- Formula: `S = (V1 · V2) / (||V1|| × ||V2||)`
- Normalized to 0-100 scale

### 3. Weighted Aggregation
```
FinalScore = (S_skills × W_skills) + 
             (S_experience × W_experience) + 
             (S_experience_years × W_experience_years) + 
             (S_education × W_education) + 
             (S_certifications × W_certifications) + 
             (S_languages × W_languages) + 
             (S_location × W_location)
```

### 4. Classification
- **High Match**: Score ≥ 80%
- **Medium Match**: Score 50-80%
- **Low Match**: Score < 50%

## 🎨 UI Components

### JobForm
- Input job title, skills, requirements
- Add certifications, languages, location
- Specify required experience and education level

### ResumeUpload
- Drag-and-drop PDF upload
- File validation and preview
- Loading state during extraction

### MatchResults
- Radar chart visualization of match scores
- Detailed breakdown by attribute
- Candidate information display
- Classification badge

### WeightSliders
- Interactive sliders for each attribute
- Real-time weight adjustment
- Automatic normalization
- Reset to defaults

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```
GOOGLE_API_KEY=your_gemini_api_key
```

**Frontend (.env.local)**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Default Weights
```python
{
    "skills": 0.35,           # 35%
    "experience": 0.25,       # 25%
    "experience_years": 0.15, # 15%
    "education": 0.10,        # 10%
    "certifications": 0.10,   # 10%
    "languages": 0.03,        # 3%
    "location": 0.02          # 2%
}
```

## 📊 Data Flow

```
1. User defines job requirements (JobForm)
   ↓
2. User uploads resume PDF (ResumeUpload)
   ↓
3. Backend extracts resume data via Gemini API (resume_parser.py)
   ↓
4. ML Engine calculates semantic similarities (ml_engine.py)
   ↓
5. Scores are weighted and aggregated (ml_engine.py)
   ↓
6. Results displayed with radar chart (MatchResults)
   ↓
7. User adjusts weights in real-time (WeightSliders)
   ↓
8. Scores recalculated instantly (ResumeMatcher)
```

## 🔐 Security Considerations

- API keys stored in environment variables (never hardcoded)
- CORS enabled for frontend-backend communication
- PDF files processed temporarily and deleted
- No sensitive data stored permanently

## 📦 Dependencies

### Backend
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `sentence-transformers`: Semantic embeddings
- `torch`: Deep learning framework
- `google-generativeai`: Gemini API client
- `scikit-learn`: Machine learning utilities
- `pydantic`: Data validation

### Frontend
- `next`: React framework
- `react`: UI library
- `tailwindcss`: Styling
- `recharts`: Data visualization
- `lucide-react`: Icons
- `axios`: HTTP client

## 🚀 Deployment

### Backend (FastAPI)
```bash
# Using Gunicorn + Uvicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app
```

### Frontend (Next.js)
```bash
npm run build
npm start
```

## 📝 Example Usage

### 1. Create a Job
```
Title: Senior Machine Learning Engineer
Skills: Python, TensorFlow, PyTorch, SQL
Requirements: 5+ years in ML, experience with production systems
Experience: 5 years
Education: Masters
Location: San Francisco
```

### 2. Upload Resume
- Drag and drop a PDF resume
- System extracts: name, skills, experience, education, etc.

### 3. View Results
- See radar chart with match scores
- Adjust weights to prioritize different attributes
- Scores update in real-time

### 4. Export or Compare
- Compare multiple candidates
- Export results for hiring decisions

## 🐛 Troubleshooting

### Gemini API Errors
- Verify `GOOGLE_API_KEY` is set correctly
- Check API quota and rate limits
- Ensure PDF file is valid

### Model Loading Issues
- First run downloads the model (~100MB)
- Requires internet connection
- Check disk space

### CORS Errors
- Ensure backend is running on `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`

## 📚 Additional Resources

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Google Gemini API](https://ai.google.dev/)
- [Recharts Documentation](https://recharts.org/)

## 📄 License

MIT License - Feel free to use this project for personal or commercial purposes.

## 👨‍💻 Author

Built as a comprehensive full-stack AI engineering solution for intelligent resume matching.

---

**Happy Matching! 🎯**
