'use client'

import { useState, useEffect } from 'react'
import { Briefcase, Plus, Trash2, Edit2, CheckCircle } from 'lucide-react'
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

interface JobProfileManagerProps {
  onSelectJob: (job: JobProfile) => void
  onCreateNew: () => void
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function JobProfileManager({
  onSelectJob,
  onCreateNew,
}: JobProfileManagerProps) {
  const [jobs, setJobs] = useState<JobProfile[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null)

  useEffect(() => {
    fetchJobProfiles()
  }, [])

  const fetchJobProfiles = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get(`${API_BASE_URL}/jobs?active_only=true`)
      setJobs(response.data)
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : 'Failed to fetch job profiles'
      setError(message)
      console.error('Error fetching jobs:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteJob = async (jobId: number) => {
    if (!confirm('Are you sure you want to delete this job profile?')) return

    try {
      await axios.delete(`${API_BASE_URL}/jobs/${jobId}`)
      setJobs(jobs.filter((j) => j.id !== jobId))
      if (selectedJobId === jobId) {
        setSelectedJobId(null)
      }
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : 'Failed to delete job'
      setError(message)
      console.error('Error deleting job:', err)
    }
  }

  const handleSelectJob = (job: JobProfile) => {
    setSelectedJobId(job.id)
    onSelectJob(job)
  }

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-8 shadow-2xl">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Briefcase className="w-6 h-6 text-blue-500" />
          <h2 className="text-2xl font-bold text-white">Job Profiles</h2>
        </div>
        <button
          onClick={onCreateNew}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Job
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/30 border border-red-500 rounded-lg text-red-200">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <p className="text-dark-300 mt-2">Loading job profiles...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="text-center py-12">
          <Briefcase className="w-12 h-12 text-dark-600 mx-auto mb-4" />
          <p className="text-dark-300 mb-4">No job profiles yet</p>
          <button
            onClick={onCreateNew}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Create First Job
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {jobs.map((job) => (
            <div
              key={job.id}
              onClick={() => handleSelectJob(job)}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                selectedJobId === job.id
                  ? 'bg-blue-900/30 border-blue-500'
                  : 'bg-dark-700 border-dark-600 hover:border-blue-500'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-white">
                      {job.title}
                    </h3>
                    {selectedJobId === job.id && (
                      <CheckCircle className="w-5 h-5 text-green-500" />
                    )}
                  </div>
                  <p className="text-dark-300 text-sm mb-3">
                    {job.requirements.substring(0, 100)}
                    {job.requirements.length > 100 ? '...' : ''}
                  </p>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {job.skills.slice(0, 3).map((skill, idx) => (
                      <span
                        key={idx}
                        className="text-xs bg-blue-900/30 border border-blue-500 text-blue-200 px-2 py-1 rounded"
                      >
                        {skill}
                      </span>
                    ))}
                    {job.skills.length > 3 && (
                      <span className="text-xs text-dark-400">
                        +{job.skills.length - 3} more
                      </span>
                    )}
                  </div>
                  <div className="flex gap-4 text-sm text-dark-400">
                    <span>📍 {job.location}</span>
                    <span>👥 {job.candidate_count} candidates</span>
                    <span>📅 {new Date(job.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    handleDeleteJob(job.id)
                  }}
                  className="ml-4 p-2 text-red-400 hover:bg-red-900/30 rounded-lg transition-colors"
                  title="Delete job profile"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
