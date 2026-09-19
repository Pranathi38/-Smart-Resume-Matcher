# Smart Resume Matcher v2.0 - Upgrade Guide

## Overview
Upgraded from stateless single-match application to **persistent job profile system with bulk candidate processing**.

## What's New

### 🎯 Core Features
1. **Persistent Job Profiles** - Create jobs once, reuse forever
2. **Bulk Candidate Processing** - Upload multiple resumes at once
3. **Candidate History** - All matches stored in SQLite database
4. **Job Statistics** - Track high/medium/low matches per job
5. **Candidate Notes** - Add notes and track candidates
6. **Job Management** - Edit, delete, and organize job profiles

### 📊 Database Architecture
- **SQLite** - Local database (no external server needed)
- **SQLAlchemy ORM** - Type-safe database operations
- **3 Main Tables**:
  - `job_profiles` - Job requirements and metadata
  - `candidate_matches` - Candidate scores and data
  - `weight_presets` - Saved weight configurations

## Installation

### 1. Update Dependencies
```bash
pip install -r requirements.txt
```

New packages added:
- `sqlalchemy>=2.0.0` - ORM and database management
- `alembic>=1.13.0` - Database migrations (optional)

### 2. Backend Setup
The database is automatically initialized on first server start.

```bash
python server.py
```

This creates `resume_matcher.db` in the project root.

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Job Profile Management

#### Create Job Profile
```
POST /jobs
Content-Type: application/json

{
  "title": "Senior Software Engineer",
  "skills": ["Python", "FastAPI", "React"],
  "requirements": "5+ years experience...",
  "experience_years": 5,
  "education_level": "Bachelors",
  "certifications": [],
  "languages": ["English"],
  "location": "Remote"
}

Response: JobProfileResponse (with id)
```

#### List Job Profiles
```
GET /jobs?skip=0&limit=100&active_only=true

Response: List[JobProfileResponse]
```

#### Get Job Profile
```
GET /jobs/{job_id}

Response: JobProfileResponse
```

#### Update Job Profile
```
PUT /jobs/{job_id}
Content-Type: application/json

{...job data...}

Response: JobProfileResponse
```

#### Delete Job Profile (soft delete)
```
DELETE /jobs/{job_id}

Response: {"message": "Job profile deleted successfully"}
```

### Candidate Management

#### Add Candidate to Job
```
POST /jobs/{job_id}/candidates
Content-Type: multipart/form-data

file: <PDF resume>
weights: {optional weight configuration}

Response: CandidateMatchResponse
```

#### List Candidates for Job
```
GET /jobs/{job_id}/candidates?skip=0&limit=100&sort_by=final_score

sort_by options: "final_score", "created_at", "candidate_name"

Response: List[CandidateMatchResponse]
```

#### Get Candidates by Classification
```
GET /jobs/{job_id}/candidates/{classification}

classification: "High" | "Medium" | "Low"

Response: List[CandidateMatchResponse]
```

#### Get Job Statistics
```
GET /jobs/{job_id}/statistics

Response: JobStatistics
{
  "total_candidates": 10,
  "high_match": 3,
  "medium_match": 5,
  "low_match": 2,
  "average_score": 65.5,
  "highest_score": 92.3,
  "lowest_score": 42.1
}
```

#### Update Candidate Notes
```
PUT /candidates/{candidate_id}
Content-Type: application/json

{"notes": "Good technical skills, needs communication training"}

Response: CandidateMatchResponse
```

#### Delete Candidate
```
DELETE /candidates/{candidate_id}

Response: {"message": "Candidate deleted successfully"}
```

## Frontend Components

### New Components

#### JobProfileManager
- Lists all saved job profiles
- Select job to manage
- Delete job profiles
- Shows candidate count per job

#### BulkCandidateUpload
- Drag-and-drop PDF upload
- Multiple file selection
- Real-time upload progress
- Success/error reporting
- Match scores displayed

#### CandidatesList
- View all candidates for a job
- Filter by classification (High/Medium/Low)
- View detailed scores
- Add/edit candidate notes
- Delete candidates
- Job statistics dashboard

#### ResumeMatcher_v2
- Main orchestrator component
- Two-step workflow:
  1. Create new job or manage existing
  2. Upload candidates or view results

## Workflow

### Creating and Using a Job Profile

1. **Create Job Profile**
   - Click "Create New Job"
   - Fill in job details (title, skills, requirements, etc.)
   - Click "Continue to Resume Upload"
   - Job is saved to database with unique ID

2. **Upload Candidates**
   - Drag-and-drop PDF resumes
   - Or click to browse files
   - Click "Upload X Resumes"
   - Each resume is:
     - Extracted via Gemini API
     - Matched against job profile
     - Saved to database with scores

3. **View Results**
   - See all candidates sorted by score
   - Filter by classification
   - View detailed attribute scores
   - Add notes to candidates
   - Delete candidates as needed

4. **Reuse Job Profile**
   - Click "Manage Jobs"
   - Select existing job profile
   - Upload more candidates anytime
   - All candidates tracked together

## Database Schema

### job_profiles Table
```sql
CREATE TABLE job_profiles (
  id INTEGER PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  skills JSON NOT NULL,
  requirements TEXT,
  experience_years FLOAT DEFAULT 0,
  education_level VARCHAR(50) DEFAULT 'Bachelors',
  certifications JSON DEFAULT '[]',
  languages JSON DEFAULT '[]',
  location VARCHAR(255) DEFAULT 'Remote',
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
)
```

### candidate_matches Table
```sql
CREATE TABLE candidate_matches (
  id INTEGER PRIMARY KEY,
  job_profile_id INTEGER NOT NULL FOREIGN KEY,
  candidate_name VARCHAR(255) NOT NULL,
  candidate_data JSON NOT NULL,
  final_score FLOAT NOT NULL,
  classification VARCHAR(50) NOT NULL,
  scores JSON NOT NULL,
  weights JSON NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  resume_filename VARCHAR(255),
  notes TEXT
)
```

### weight_presets Table
```sql
CREATE TABLE weight_presets (
  id INTEGER PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  description TEXT,
  weights JSON NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## Configuration

### Environment Variables
Add to `.env`:
```
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./resume_matcher.db
API_HOST=0.0.0.0
API_PORT=8000
MODEL_NAME=all-MiniLM-L6-v2
```

### Database URL Options
- SQLite (default): `sqlite:///./resume_matcher.db`
- PostgreSQL: `postgresql://user:password@localhost/dbname`
- MySQL: `mysql+pymysql://user:password@localhost/dbname`

## Migration from v1.0

### Data Loss
- Old stateless application had no persistent data
- v2.0 starts fresh with empty database
- No migration needed

### API Compatibility
- Old endpoints still work (backward compatible)
- New endpoints for job/candidate management
- Old single-match flow still available

## Performance Considerations

### Database Optimization
- Indexes on: `job_profiles.id`, `candidate_matches.job_profile_id`, `candidate_matches.final_score`
- Soft deletes (is_active flag) for data retention
- Pagination support (skip/limit)

### Scaling
- SQLite suitable for: <100 jobs, <10k candidates
- For larger scale, switch to PostgreSQL:
  ```
  pip install psycopg2-binary
  # Update DATABASE_URL in .env
  ```

### Caching
- ML model cached after first load (2-3 seconds)
- Resume extraction: 30-60 seconds per candidate
- Match calculation: <100ms per candidate

## Troubleshooting

### Database Issues
```bash
# Reset database (deletes all data)
rm resume_matcher.db

# Restart server to recreate
python server.py
```

### API Connection Issues
- Ensure backend running: `python server.py`
- Check CORS settings in server.py
- Verify API_BASE_URL in frontend .env.local

### Upload Failures
- Ensure PDF files are valid
- Check file size (usually <10MB)
- Verify Gemini API key is valid

## Files Changed/Added

### Backend
- ✅ `database.py` - SQLAlchemy models (NEW)
- ✅ `db_service.py` - Database service layer (NEW)
- ✅ `server.py` - Updated with 15+ new endpoints
- ✅ `requirements.txt` - Added SQLAlchemy, Alembic

### Frontend
- ✅ `components/JobProfileManager.tsx` - Job management (NEW)
- ✅ `components/BulkCandidateUpload.tsx` - Bulk upload (NEW)
- ✅ `components/CandidatesList.tsx` - Candidate management (NEW)
- ✅ `components/ResumeMatcher_v2.tsx` - Main orchestrator (NEW)
- ✅ `app/page.tsx` - Updated to use v2 component

### Backup
- `server_old.py` - Original server.py (backup)

## Next Steps

1. **Test the workflow**
   - Create a job profile
   - Upload sample resumes
   - Verify candidates are saved

2. **Customize weights**
   - Adjust skill/experience weights
   - Create weight presets
   - Save for future use

3. **Scale up**
   - Upload larger batches
   - Monitor database size
   - Consider PostgreSQL for production

4. **Integration**
   - Export candidate data
   - Integrate with ATS
   - Build reporting dashboards

## Support

For issues or questions:
1. Check error messages in browser console
2. Check backend logs: `python server.py`
3. Verify database exists: `ls resume_matcher.db`
4. Check API endpoints: `curl http://localhost:8000/health`

## Version Info
- **Version**: 2.0.0
- **Release Date**: December 2024
- **Database**: SQLite (SQLAlchemy)
- **Breaking Changes**: None (backward compatible)
