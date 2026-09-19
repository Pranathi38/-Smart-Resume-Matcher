# Smart Resume Matcher - Setup Guide

Complete step-by-step instructions to set up and run the application.

## Prerequisites

Before starting, ensure you have:

- **Python 3.9 or higher** - [Download](https://www.python.org/downloads/)
- **Node.js 18 or higher** - [Download](https://nodejs.org/)
- **Git** (optional, for cloning)
- **Google Gemini API Key** - [Get API Key](https://ai.google.dev/)
- **Text Editor or IDE** - VS Code, PyCharm, etc.

## Step 1: Get Google Gemini API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Click "Get API Key"
3. Create a new API key
4. Copy the key (you'll need it in Step 3)

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

```bash
# Navigate to project directory
cd p:\JOB\ Matching

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2.2 Install Python Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

Expected packages:
- fastapi
- uvicorn
- torch
- sentence-transformers
- google-generativeai
- scikit-learn
- pandas
- numpy

### 2.3 Configure Environment Variables

```bash
# Create .env file in project root
# On Windows (PowerShell):
New-Item -Path ".env" -ItemType File

# Add your Gemini API key:
# GOOGLE_API_KEY=your_api_key_here
```

Or manually create `.env` file with:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 2.4 Test Backend

```bash
# Start the FastAPI server
python server.py

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

### 2.5 Verify Backend is Running

Open browser and go to:
- `http://localhost:8000/docs` - Interactive API documentation
- `http://localhost:8000/health` - Health check endpoint

You should see:
```json
{
  "status": "healthy",
  "ml_engine": "ready",
  "parser": "ready"
}
```

**Keep the backend running in this terminal!**

## Step 3: Frontend Setup

### 3.1 Open New Terminal

Open a new terminal/command prompt window (keep backend terminal open).

### 3.2 Navigate to Frontend Directory

```bash
cd p:\JOB\ Matching\frontend
```

### 3.3 Install Node Dependencies

```bash
# Install all npm packages
npm install

# This may take 2-5 minutes
# You should see:
# added XXX packages in X.XXs
```

### 3.4 Configure Frontend Environment

The `.env.local` file is already configured with:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

If you're running the backend on a different host/port, update this value.

### 3.5 Start Frontend Development Server

```bash
# Start Next.js development server
npm run dev

# Expected output:
# ▲ Next.js 14.0.0
# - Local:        http://localhost:3000
# - Environments: .env.local
#
# ✓ Ready in 2.5s
```

## Step 4: Access the Application

Open your browser and go to:

```
http://localhost:3000
```

You should see the Smart Resume Matcher interface with:
- Header with title and description
- Progress indicator (1, 2, 3)
- Job Details form

## Step 5: Test the Application

### 5.1 Create a Test Job

1. Fill in the Job Details form:
   - **Job Title**: Senior Software Engineer
   - **Required Skills**: Python, FastAPI, React (add each and press Enter)
   - **Job Requirements**: Looking for experienced developer with 5+ years
   - **Required Experience**: 5 years
   - **Education Level**: Bachelors
   - **Location**: Remote

2. Click "Continue to Resume Upload"

### 5.2 Upload a Test Resume

1. You can create a simple text file and save as PDF, or use an existing resume
2. Drag and drop the PDF or click "Select File"
3. Click "Analyze Resume"

**Note**: First run will download the ML model (~100MB), which may take 1-2 minutes.

### 5.3 View Results

Once processing completes, you'll see:
- Candidate information
- Final match score (0-100)
- Classification (High/Medium/Low Match)
- Radar chart with detailed scores
- Weight sliders to adjust matching criteria

### 5.4 Adjust Weights

1. Use the sliders to adjust attribute weights
2. Watch the match score update in real-time
3. Click "Normalize Weights" to ensure they sum to 1.0
4. Click "Reset to Default" to restore original weights

## Troubleshooting

### Backend Issues

**Error: "GOOGLE_API_KEY not found"**
- Ensure `.env` file exists in project root
- Verify API key is correctly set
- Restart the server

**Error: "ModuleNotFoundError"**
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Port 8000 already in use**
- Find and kill process using port 8000
- Or change port in `server.py` (line: `port=8000`)

**Model download fails**
- Check internet connection
- Ensure sufficient disk space (~100MB)
- Try again - downloads are cached after first run

### Frontend Issues

**Error: "Cannot find module"**
- Run `npm install` again
- Delete `node_modules` and `.next` folders
- Run `npm install` and `npm run dev` again

**Port 3000 already in use**
- Kill process using port 3000
- Or run: `npm run dev -- -p 3001`

**API connection errors**
- Verify backend is running on `http://localhost:8000`
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Check browser console for CORS errors

### PDF Upload Issues

**Error: "Only PDF files are supported"**
- Ensure file has `.pdf` extension
- Try converting file to PDF format

**Error: "Error extracting resume"**
- Verify PDF is readable and not corrupted
- Try a different PDF file
- Check Gemini API quota

## Project Structure

```
p:\JOB Matching\
├── requirements.txt          # Python dependencies
├── ml_engine.py             # ML matching logic
├── resume_parser.py         # Gemini API integration
├── server.py                # FastAPI server
├── .env.example             # Environment template
├── README.md                # Full documentation
├── SETUP_GUIDE.md          # This file
└── frontend/
    ├── package.json         # Node dependencies
    ├── next.config.js       # Next.js config
    ├── tailwind.config.js   # Tailwind CSS config
    ├── .env.local           # Frontend env vars
    ├── app/
    │   ├── layout.tsx       # Root layout
    │   ├── page.tsx         # Home page
    │   └── globals.css      # Global styles
    └── components/
        ├── ResumeMatcher.tsx    # Main component
        ├── JobForm.tsx          # Job input form
        ├── ResumeUpload.tsx     # Resume upload
        ├── MatchResults.tsx     # Results display
        └── WeightSliders.tsx    # Weight controls
```

## Performance Tips

1. **First Run**: Model download takes 1-2 minutes, subsequent runs are instant
2. **Large PDFs**: Extraction may take 30-60 seconds depending on content
3. **Batch Processing**: Use `/batch-match` endpoint for multiple candidates
4. **Caching**: Embeddings are cached in memory for faster re-matching

## Next Steps

1. **Customize Weights**: Adjust default weights in `ml_engine.py` or `ResumeMatcher.tsx`
2. **Add More Attributes**: Extend the matching schema in `ml_engine.py`
3. **Deploy**: See README.md for deployment instructions
4. **Fine-tune Model**: Create `train_model.py` with your own dataset
5. **Batch Processing**: Implement CSV upload for multiple resumes

## Support & Resources

- **API Docs**: http://localhost:8000/docs (when backend is running)
- **Sentence Transformers**: https://www.sbert.net/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Next.js**: https://nextjs.org/docs
- **Google Gemini**: https://ai.google.dev/

## Common Commands

```bash
# Backend
python server.py                    # Start backend
python -m pip install -r requirements.txt  # Install deps

# Frontend
npm run dev                         # Start dev server
npm run build                       # Build for production
npm start                          # Start production server
npm run lint                       # Run linter

# Virtual Environment
venv\Scripts\activate              # Activate (Windows)
source venv/bin/activate           # Activate (macOS/Linux)
deactivate                         # Deactivate
```

---

**You're all set! Happy matching! 🎯**
