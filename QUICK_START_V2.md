# Quick Start - Resume Matcher v2.0

## 5-Minute Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API key

### Step 1: Install Backend Dependencies
```bash
cd p:\JOB Matching
pip install -r requirements.txt
```

### Step 2: Start Backend Server
```bash
python server.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Start Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```

Expected output:
```
> ready - started server on 0.0.0.0:3000
```

### Step 4: Open Application
Visit: **http://localhost:3000**

---

## First Time Usage

### 1. Create a Job Profile
1. Click **"Create New Job"** on the main screen
2. Fill in job details:
   - **Job Title**: e.g., "Senior Software Engineer"
   - **Required Skills**: Add skills (Python, React, etc.)
   - **Requirements**: Describe the role
   - **Experience Years**: e.g., 5
   - **Education Level**: Select from dropdown
   - **Certifications**: Add any required certs
   - **Languages**: Add required languages
   - **Location**: e.g., "Remote" or "New York"
3. Click **"Continue to Resume Upload"**
4. Job is saved to database ✅

### 2. Upload Resumes
1. **Drag and drop** PDF files into the upload area
   - OR click **"Browse Files"** to select
2. You can add multiple files at once
3. Click **"Upload X Resumes"**
4. Watch progress as each resume is:
   - Extracted via Gemini API
   - Matched against job profile
   - Saved to database
5. Click **"View All Candidates"** when done

### 3. Review Candidates
1. See all candidates sorted by match score
2. **Filter** by classification:
   - 🟢 **High** (≥80%)
   - 🟡 **Medium** (50-80%)
   - 🔴 **Low** (<50%)
3. **Click** on candidate to see detailed scores
4. **Add notes** to any candidate
5. **Delete** candidates as needed

### 4. Reuse Job Profile
1. Click **"Back to Jobs"**
2. Click **"Manage Jobs"** on main screen
3. Select your saved job profile
4. Click **"Upload More Resumes"**
5. Add more candidates anytime

---

## Key Features

### 📊 Job Statistics
View at a glance:
- Total candidates uploaded
- High/Medium/Low match counts
- Average match score
- Highest/Lowest scores

### 📝 Candidate Notes
- Add notes to any candidate
- Track interview feedback
- Record hiring decisions
- Edit anytime

### 🔍 Detailed Scoring
View breakdown of match scores:
- Skills match
- Experience match
- Education level
- Certifications
- Languages
- Location
- Years of experience

### 💾 Persistent Storage
- All jobs saved to database
- All candidates saved with scores
- No data lost on refresh
- Reuse jobs unlimited times

---

## Common Tasks

### Upload More Candidates to Existing Job
1. Main menu → **"Manage Jobs"**
2. Click on job profile
3. Click **"Upload More Resumes"**
4. Add new PDF files
5. Click **"Upload"**

### View All Candidates for a Job
1. Main menu → **"Manage Jobs"**
2. Click on job profile
3. See all candidates with scores
4. Filter by classification if needed

### Delete a Candidate
1. In candidates list
2. Click **trash icon** on candidate row
3. Confirm deletion

### Delete a Job Profile
1. Main menu → **"Manage Jobs"**
2. Click **trash icon** on job card
3. Confirm deletion (removes all candidates too)

### Adjust Weights (Original Feature)
- In v1.0: Available after matching
- In v2.0: Coming soon in candidate view
- Currently uses default weights:
  - Skills: 35%
  - Experience: 25%
  - Years of Experience: 15%
  - Education: 10%
  - Certifications: 10%
  - Languages: 3%
  - Location: 2%

---

## Troubleshooting

### "Cannot connect to API"
- ✅ Backend running? `python server.py`
- ✅ Frontend running? `npm run dev`
- ✅ Check http://localhost:8000/health

### "PDF upload fails"
- ✅ Is it a valid PDF file?
- ✅ File size < 10MB?
- ✅ Check browser console for errors

### "No candidates showing"
- ✅ Did upload complete successfully?
- ✅ Check filter isn't hiding results
- ✅ Refresh page

### "Database error"
- ✅ Delete `resume_matcher.db`
- ✅ Restart backend: `python server.py`
- ✅ Database auto-creates on startup

### "Gemini API error"
- ✅ Valid API key in `.env`?
- ✅ Check API quota/billing
- ✅ See backend logs for details

---

## Database Location
```
p:\JOB Matching\resume_matcher.db
```

This SQLite database contains:
- All job profiles
- All candidate matches
- All scores and notes

**Backup this file regularly!**

---

## API Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "ml_engine": "ready",
  "parser": "ready",
  "database": "ready"
}
```

---

## Next Steps

1. **Create multiple jobs** and build a library
2. **Batch upload** candidates for each role
3. **Track candidates** with notes and ratings
4. **Export results** for your ATS
5. **Customize weights** for different roles

---

## Need Help?

Check these files:
- `UPGRADE_GUIDE_V2.md` - Full API documentation
- `README.md` - Original feature documentation
- Backend logs: `python server.py` output
- Browser console: F12 → Console tab

---

**Enjoy your upgraded Resume Matcher! 🚀**
