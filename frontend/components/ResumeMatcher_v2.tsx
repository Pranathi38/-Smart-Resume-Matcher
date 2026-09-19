'use client'

import { useState } from 'react'
import { Zap, ChevronLeft } from 'lucide-react'
import JobForm from './JobForm'
import JobProfileManager from './JobProfileManager'
import BulkCandidateUpload from './BulkCandidateUpload'
import CandidatesList from './CandidatesList'
import axios from 'axios'

interface JobProfile {
  id: number
  title: string
  skills: string[]
  requirements: string
  experience_years: number
  education_level: string
  certifications: string[]
  languages: string[]
  location: string
  created_at: string
  updated_at: string
  is_active: boolean
  candidate_count: number
}

interface JobData {
  title: string
  skills: string[]
  requirements: string
  experience_years: number
  education_level: string
  certifications: string[]
  languages: string[]
  location: string
}

type Step = 'main' | 'create-job' | 'manage-job' | 'upload-candidates' | 'view-candidates'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ResumeMatcher() {
  const [step, setStep] = useState<Step>('main')
  const [selectedJob, setSelectedJob] = useState<JobProfile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleCreateJob = async (jobData: JobData) => {
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_BASE_URL}/jobs`, jobData)
      const newJob = response.data
      setSelectedJob(newJob)
      setStep('upload-candidates')
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : 'Failed to create job'
      setError(message)
      console.error('Error creating job:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectJob = (job: JobProfile) => {
    setSelectedJob(job)
    setStep('upload-candidates')
  }

  const handleBackToMain = () => {
    setStep('main')
    setSelectedJob(null)
    setError(null)
  }

  const handleUploadComplete = () => {
    setStep('view-candidates')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-900 via-dark-800 to-dark-900 p-4 md:p-8">
      {/* Header */}
      <div className="max-w-6xl mx-auto mb-12">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-8 h-8 text-blue-500" />
          <h1 className="text-4xl md:text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            Smart Resume Matcher
          </h1>
        </div>
        <p className="text-dark-300 text-lg">
          Persistent Job Profiles & Bulk Candidate Processing
        </p>
      </div>

      {/* Main content */}
      <div className="max-w-6xl mx-auto">
        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-500 rounded-lg text-red-200 flex items-start gap-3">
            <span className="text-xl">⚠️</span>
            <div>
              <p className="font-semibold">Error</p>
              <p>{error}</p>
            </div>
          </div>
        )}

        {/* Back Button */}
        {step !== 'main' && (
          <button
            onClick={handleBackToMain}
            className="mb-6 flex items-center gap-2 px-4 py-2 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Back to Main
          </button>
        )}

        {/* Main Menu */}
        {step === 'main' && (
          <div className="grid md:grid-cols-2 gap-8">
            {/* Create New Job */}
            <div
              onClick={() => setStep('create-job')}
              className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-500 rounded-xl p-8 cursor-pointer hover:border-blue-400 transition-all transform hover:scale-105"
            >
              <div className="text-4xl mb-4">➕</div>
              <h2 className="text-2xl font-bold text-white mb-2">Create New Job</h2>
              <p className="text-dark-300">
                Define a new job profile with requirements and save it for future use.
              </p>
            </div>

            {/* Manage Existing Jobs */}
            <div
              onClick={() => setStep('manage-job')}
              className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-500 rounded-xl p-8 cursor-pointer hover:border-purple-400 transition-all transform hover:scale-105"
            >
              <div className="text-4xl mb-4">📋</div>
              <h2 className="text-2xl font-bold text-white mb-2">Manage Jobs</h2>
              <p className="text-dark-300">
                View, edit, or upload candidates to existing job profiles.
              </p>
            </div>
          </div>
        )}

        {/* Create Job Form */}
        {step === 'create-job' && (
          <div>
            <JobForm
              onSubmit={handleCreateJob}
            />
            {loading && (
              <div className="mt-4 text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                <p className="text-dark-300 mt-2">Creating job profile...</p>
              </div>
            )}
          </div>
        )}

        {/* Manage Jobs */}
        {step === 'manage-job' && (
          <JobProfileManager
            onSelectJob={handleSelectJob}
            onCreateNew={() => setStep('create-job')}
          />
        )}

        {/* Upload Candidates */}
        {step === 'upload-candidates' && selectedJob && (
          <BulkCandidateUpload
            jobId={selectedJob.id}
            jobTitle={selectedJob.title}
            onUploadComplete={handleUploadComplete}
          />
        )}

        {/* View Candidates */}
        {step === 'view-candidates' && selectedJob && (
          <div className="space-y-8">
            <CandidatesList
              jobId={selectedJob.id}
              jobTitle={selectedJob.title}
            />
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => setStep('upload-candidates')}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                Upload More Resumes
              </button>
              <button
                onClick={() => setStep('manage-job')}
                className="px-6 py-3 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
              >
                Back to Jobs
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
