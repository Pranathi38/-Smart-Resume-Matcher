# Smart Resume Matcher - Complete Index

## 📖 Documentation

Start here based on your needs:

### 🚀 Getting Started
- **[SETUP_GUIDE.md](./SETUP_GUIDE.md)** - Step-by-step installation and setup
- **[README.md](./README.md)** - Full feature documentation and API reference
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - Project overview and architecture

### 🎯 Quick Links
- **Backend API Docs**: `http://localhost:8000/docs` (when running)
- **Frontend**: `http://localhost:3000`
- **Health Check**: `http://localhost:8000/health`

## 📁 Backend Files

### Core Application
| File | Purpose |
|------|---------|
| `server.py` | FastAPI application with all endpoints |
| `ml_engine.py` | Semantic matching logic using sentence-transformers |
| `resume_parser.py` | Gemini API integration for resume extraction |

### Configuration & Dependencies
| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `.env.example` | Environment variables template |
| `.env` | Your local environment (create from .env.example) |

### Testing & Utilities
| File | Purpose |
|------|---------|
| `test_api.py` | Comprehensive API testing script |
| `start.bat` | Quick start script for Windows |
| `start.sh` | Quick start script for macOS/Linux |

## 📁 Frontend Files

### Configuration
| File | Purpose |
|------|---------|
| `frontend/package.json` | Node.js dependencies |
| `frontend/next.config.js` | Next.js configuration |
| `frontend/tailwind.config.js` | Tailwind CSS configuration |
| `frontend/tsconfig.json` | TypeScript configuration |
| `frontend/.env.local` | Frontend environment variables |

### Application Code
| File | Purpose |
|------|---------|
| `frontend/app/layout.tsx` | Root layout component |
| `frontend/app/page.tsx` | Home page |
| `frontend/app/globals.css` | Global styles |

### Components
| File | Purpose |
|------|---------|
| `frontend/components/ResumeMatcher.tsx` | Main orchestrator component |
| `frontend/components/JobForm.tsx` | Job requirements input form |
| `frontend/components/ResumeUpload.tsx` | PDF upload with drag-and-drop |
| `frontend/components/MatchResults.tsx` | Results display with radar chart |
| `frontend/components/WeightSliders.tsx` | Interactive weight adjustment |

## 🔧 Setup Instructions

### Quick Start (5 minutes)

#### Windows
```bash
# Run the quick start script
start.bat
```

#### macOS/Linux
```bash
chmod +x start.sh
./start.sh
```

#### Manual Setup
```bash
# 1. Backend
python -m venv venv
venv\Scripts\activate  # or: source venv/bin/activate
pip install -r requirements.txt
python server.py

# 2. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Configuration
1. Copy `.env.example` to `.env`
2. Add your Google Gemini API key: `GOOGLE_API_KEY=your_key_here`
3. Frontend uses `frontend/.env.local` (already configured)

## 🚀 Running the Application

### Start Backend
```bash
python server.py
# Runs on http://localhost:8000
```

### Start Frontend
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### Test API
```bash
python test_api.py
# Runs comprehensive tests
```

## 📊 API Endpoints

### Health & Information
```
GET  /health              - System health check
GET  /model-info          - ML model information
```

### Resume Processing
```
POST /extract-resume      - Extract data from PDF resume
POST /match-resume        - Calculate match score
POST /batch-match         - Match multiple candidates
POST /calculate-similarity - Calculate text similarity
```

## 🎨 User Interface Flow

```
1. Job Details Form
   ↓
2. Resume Upload (PDF)
   ↓
3. Resume Extraction (Gemini API)
   ↓
4. Match Calculation (ML Engine)
   ↓
5. Results Display (Radar Chart)
   ↓
6. Weight Adjustment (Real-time Updates)
```

## 🔑 Key Features

### Backend
- ✅ Semantic resume matching using sentence-transformers
- ✅ Gemini API integration for structured extraction
- ✅ Weighted scoring system
- ✅ Batch processing support
- ✅ Comprehensive error handling
- ✅ CORS enabled for frontend

### Frontend
- ✅ Multi-step form interface
- ✅ Drag-and-drop file upload
- ✅ Interactive weight sliders
- ✅ Radar chart visualization
- ✅ Real-time score updates
- ✅ Dark mode UI
- ✅ Responsive design

## 📈 Matching Algorithm

1. **Text Vectorization**: Convert text to 384-dimensional embeddings
2. **Similarity Calculation**: Compute cosine similarity (0-100)
3. **Weighted Aggregation**: Combine scores using custom weights
4. **Classification**: Categorize as High/Medium/Low match

## 🧪 Testing

### API Tests
```bash
python test_api.py
```

Tests:
- Health check
- Model information
- Similarity calculation
- Single match scoring
- Batch matching

### Manual Testing
1. Create a job with requirements
2. Upload a resume PDF
3. Verify extracted data
4. Check match score
5. Adjust weights and verify updates

## 🔐 Environment Variables

### Backend (.env)
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

### Frontend (frontend/.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📦 Dependencies

### Backend
- FastAPI, Uvicorn
- PyTorch, Sentence-Transformers
- Google Generative AI
- Scikit-learn, Pandas, NumPy
- Pydantic

### Frontend
- Next.js, React
- Tailwind CSS
- Recharts, Lucide Icons
- Axios

## 🐛 Troubleshooting

### Backend Issues
- **Module not found**: Activate venv and run `pip install -r requirements.txt`
- **API key error**: Verify `.env` file has correct `GOOGLE_API_KEY`
- **Port 8000 in use**: Change port in `server.py` or kill process using port

### Frontend Issues
- **Module not found**: Run `npm install` in frontend directory
- **API connection error**: Check backend is running and `.env.local` is correct
- **Port 3000 in use**: Run `npm run dev -- -p 3001`

### Resume Extraction Issues
- **PDF not supported**: Ensure file is valid PDF format
- **Extraction timeout**: Try a different PDF or check API quota
- **Model download fails**: Check internet connection and disk space

## 📚 Additional Resources

- [Sentence Transformers Docs](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Google Gemini API](https://ai.google.dev/)
- [Recharts Documentation](https://recharts.org/)

## 🎯 Default Configuration

### Matching Weights
```
Skills:           35%
Experience:       25%
Years of Exp:     15%
Education:        10%
Certifications:   10%
Languages:        3%
Location:         2%
```

### Classification Thresholds
```
High Match:   ≥ 80%
Medium Match: 50-80%
Low Match:    < 50%
```

## 📝 File Checklist

Backend:
- [ ] `requirements.txt` - Dependencies installed
- [ ] `ml_engine.py` - Semantic matching logic
- [ ] `resume_parser.py` - Gemini integration
- [ ] `server.py` - FastAPI server
- [ ] `.env` - API key configured
- [ ] `test_api.py` - Tests available

Frontend:
- [ ] `frontend/package.json` - Dependencies
- [ ] `frontend/app/layout.tsx` - Root layout
- [ ] `frontend/app/page.tsx` - Home page
- [ ] `frontend/components/` - All components
- [ ] `frontend/.env.local` - API URL configured

Documentation:
- [ ] `README.md` - Full documentation
- [ ] `SETUP_GUIDE.md` - Installation guide
- [ ] `PROJECT_SUMMARY.md` - Architecture overview
- [ ] `INDEX.md` - This file

## 🚀 Next Steps

1. **Install**: Follow SETUP_GUIDE.md
2. **Configure**: Add Google API key to .env
3. **Run**: Start backend and frontend
4. **Test**: Run test_api.py
5. **Use**: Open http://localhost:3000

## 💡 Tips

- First model download takes 1-2 minutes (cached after)
- Resume extraction takes 30-60 seconds (API dependent)
- Adjust weights to prioritize different attributes
- Use batch endpoint for multiple candidates
- Check API docs at `/docs` when backend runs

## 📞 Support

- Check README.md for detailed documentation
- Review SETUP_GUIDE.md for installation help
- Run test_api.py to verify backend
- Check browser console for frontend errors

---

**Ready to get started? Go to [SETUP_GUIDE.md](./SETUP_GUIDE.md)!** 🚀
