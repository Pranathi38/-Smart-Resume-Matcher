'use client'

import { useState } from 'react'
import { Upload, Zap, BarChart3 } from 'lucide-react'
import JobForm from './JobForm'
import ResumeUpload from './ResumeUpload'
import MatchResults from './MatchResults'
import WeightSliders from './WeightSliders'
import axios from 'axios'

interface CandidateData {
  candidate_name: string
  skills: string[]
  experience_years: number
  education_level: string
  certifications: string[]
  languages: string[]
  salary_expectation: number | null
  location: string
  experience_description: string
  career_objective: string
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

interface MatchResult {
  candidate_name: string
  final_score: number
  classification: string
  scores: Record<string, number>
  weights: Record<string, number>
}

interface Weights {
  skills: number
  experience: number
  experience_years: number
  education: number
  certifications: number
  languages: number
  location: number
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function ResumeMatcher() {
  const [step, setStep] = useState<'job' | 'resume' | 'results'>('job')
  const [jobData, setJobData] = useState<JobData | null>(null)
  const [candidateData, setCandidateData] = useState<CandidateData | null>(null)
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null)
  const [weights, setWeights] = useState<Weights>({
    skills: 0.35,
    experience: 0.25,
    experience_years: 0.15,
    education: 0.10,
    certifications: 0.10,
    languages: 0.03,
    location: 0.02,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleJobSubmit = (data: JobData) => {
    setJobData(data)
    setStep('resume')
    setError(null)
  }

  const handleResumeUpload = async (file: File) => {
    setLoading(true)
    setError(null)

    try {
      // Extract resume data
      const formData = new FormData()
      formData.append('file', file)

      const extractResponse = await axios.post(
        `${API_BASE_URL}/extract-resume`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      )

      const extracted = extractResponse.data
      setCandidateData(extracted)

      // Calculate match score
      const matchResponse = await axios.post(
        `${API_BASE_URL}/match-resume`,
        {
          candidate_data: extracted,
          job_data: jobData,
          weights,
        }
      )

      setMatchResult(matchResponse.data)
      setStep('results')
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : 'An error occurred'
      setError(`Error: ${message}`)
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleWeightsChange = async (newWeights: Weights) => {
    setWeights(newWeights)

    if (candidateData && jobData) {
      setLoading(true)
      try {
        const response = await axios.post(
          `${API_BASE_URL}/match-resume`,
          {
            candidate_data: candidateData,
            job_data: jobData,
            weights: newWeights,
          }
        )
        setMatchResult(response.data)
      } catch (err) {
        console.error('Error recalculating match:', err)
      } finally {
        setLoading(false)
      }
    }
  }

  const handleReset = () => {
    setStep('job')
    setJobData(null)
    setCandidateData(null)
    setMatchResult(null)
    setError(null)
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
          Neural Resume Matching with Semantic Search
        </p>
      </div>

      {/* Progress indicator */}
      <div className="max-w-6xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          {(['job', 'resume', 'results'] as const).map((s, idx) => (
            <div key={s} className="flex items-center flex-1">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${
                  step === s
                    ? 'bg-blue-500 text-white scale-110'
                    : step > s
                    ? 'bg-green-500 text-white'
                    : 'bg-dark-700 text-dark-400'
                }`}
              >
                {idx + 1}
              </div>
              <div
                className={`flex-1 h-1 mx-2 transition-all ${
                  step > s ? 'bg-green-500' : 'bg-dark-700'
                }`}
              />
            </div>
          ))}
          <div className="w-10 h-10 rounded-full flex items-center justify-center font-bold bg-dark-700 text-dark-400">
            ✓
          </div>
        </div>
        <div className="flex justify-between mt-4 text-sm">
          <span className="text-dark-300">Job Details</span>
          <span className="text-dark-300">Upload Resume</span>
          <span className="text-dark-300">Results</span>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-6xl mx-auto">
        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-500 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {step === 'job' && <JobForm onSubmit={handleJobSubmit} />}

        {step === 'resume' && (
          <ResumeUpload
            onUpload={handleResumeUpload}
            loading={loading}
            jobTitle={jobData?.title}
          />
        )}

        {step === 'results' && matchResult && candidateData && (
          <div className="space-y-8">
            <MatchResults result={matchResult} candidate={candidateData} />
            <WeightSliders
              weights={weights}
              onChange={handleWeightsChange}
              loading={loading}
            />
            <div className="flex gap-4 justify-center">
              <button
                onClick={handleReset}
                className="px-6 py-3 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
              >
                Start Over
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
