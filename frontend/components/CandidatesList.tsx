'use client'

import { useState, useEffect } from 'react'
import { Users, Trash2, MessageSquare, TrendingUp } from 'lucide-react'
import axios from 'axios'

interface CandidateMatch {
  id: number
  job_profile_id: number
  candidate_name: string
  final_score: number
  classification: string
  scores: Record<string, number>
  weights: Record<string, number>
  created_at: string
  resume_filename: string
  notes: string | null
}

interface JobStatistics {
  total_candidates: number
  high_match: number
  medium_match: number
  low_match: number
  average_score: number
  highest_score: number
  lowest_score: number
}

interface CandidatesListProps {
  jobId: number
  jobTitle: string
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const getClassificationColor = (classification: string) => {
  if (classification.includes('High')) {
    return 'bg-green-900/30 border-green-500 text-green-200'
  }
  if (classification.includes('Medium')) {
    return 'bg-yellow-900/30 border-yellow-500 text-yellow-200'
  }
  if (classification.includes('Low')) {
    return 'bg-red-900/30 border-red-500 text-red-200'
  }
  return 'bg-dark-700 border-dark-600 text-dark-300'
}

const getScoreColor = (score: number) => {
  if (score >= 80) return 'text-green-400'
  if (score >= 50) return 'text-yellow-400'
  return 'text-red-400'
}

export default function CandidatesList({ jobId, jobTitle }: CandidatesListProps) {
  const [candidates, setCandidates] = useState<CandidateMatch[]>([])
  const [statistics, setStatistics] = useState<JobStatistics | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'High Match' | 'Medium Match' | 'Low Match'>('all')
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editingNotes, setEditingNotes] = useState('')

  useEffect(() => {
    fetchCandidates()
    fetchStatistics()
  }, [jobId])

  const fetchCandidates = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get(
        `${API_BASE_URL}/jobs/${jobId}/candidates?sort_by=final_score`
      )
      setCandidates(response.data)
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : 'Failed to fetch candidates'
      setError(message)
      console.error('Error fetching candidates:', err)
    } finally {
      setLoading(false)
    }
  }

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/jobs/${jobId}/statistics`
      )
      setStatistics(response.data)
    } catch (err) {
      console.error('Error fetching statistics:', err)
    }
  }

  const handleDeleteCandidate = async (candidateId: number) => {
    if (!confirm('Remove this candidate?')) return

    try {
      await axios.delete(`${API_BASE_URL}/candidates/${candidateId}`)
      setCandidates(candidates.filter((c) => c.id !== candidateId))
      await fetchStatistics()
    } catch (err) {
      console.error('Error deleting candidate:', err)
    }
  }

  const handleSaveNotes = async (candidateId: number) => {
    try {
      await axios.put(`${API_BASE_URL}/candidates/${candidateId}`, {
        notes: editingNotes,
      })
      setCandidates(
        candidates.map((c) =>
          c.id === candidateId ? { ...c, notes: editingNotes } : c
        )
      )
      setEditingId(null)
    } catch (err) {
      console.error('Error saving notes:', err)
    }
  }

  const filteredCandidates =
    filter === 'all'
      ? candidates
      : candidates.filter((c) => c.classification === filter)

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-8 shadow-2xl">
      <div className="flex items-center gap-3 mb-6">
        <Users className="w-6 h-6 text-purple-500" />
        <h2 className="text-2xl font-bold text-white">Candidates for {jobTitle}</h2>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/30 border border-red-500 rounded-lg text-red-200">
          {error}
        </div>
      )}

      {/* Statistics */}
      {statistics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-dark-700 rounded-lg p-4 border border-dark-600">
            <p className="text-dark-400 text-sm">Total Candidates</p>
            <p className="text-2xl font-bold text-white mt-1">
              {statistics.total_candidates}
            </p>
          </div>
          <div className="bg-green-900/20 rounded-lg p-4 border border-green-500">
            <p className="text-green-300 text-sm">High Match</p>
            <p className="text-2xl font-bold text-green-400 mt-1">
              {statistics.high_match}
            </p>
          </div>
          <div className="bg-yellow-900/20 rounded-lg p-4 border border-yellow-500">
            <p className="text-yellow-300 text-sm">Medium Match</p>
            <p className="text-2xl font-bold text-yellow-400 mt-1">
              {statistics.medium_match}
            </p>
          </div>
          <div className="bg-dark-700 rounded-lg p-4 border border-dark-600">
            <p className="text-dark-400 text-sm">Avg Score</p>
            <p className="text-2xl font-bold text-white mt-1">
              {statistics.average_score.toFixed(1)}%
            </p>
          </div>
        </div>
      )}

      {/* Filter */}
      <div className="flex gap-2 mb-6 flex-wrap">
        {(['all', 'High Match', 'Medium Match', 'Low Match'] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === f
                ? 'bg-blue-600 text-white'
                : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
            }`}
          >
            {f === 'all' ? 'All' : f}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
          <p className="text-dark-300 mt-2">Loading candidates...</p>
        </div>
      ) : filteredCandidates.length === 0 ? (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-dark-600 mx-auto mb-4" />
          <p className="text-dark-300">
            {candidates.length === 0
              ? 'No candidates yet. Upload resumes to get started.'
              : 'No candidates match this filter.'}
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredCandidates.map((candidate) => (
            <div
              key={candidate.id}
              className="bg-dark-700 border border-dark-600 rounded-lg p-4 hover:border-dark-500 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-white">
                      {candidate.candidate_name}
                    </h3>
                    <span
                      className={`px-3 py-1 rounded-full text-sm font-medium border ${getClassificationColor(
                        candidate.classification
                      )}`}
                    >
                      {candidate.classification}
                    </span>
                  </div>
                  <p className="text-dark-400 text-sm mb-3">
                    📄 {candidate.resume_filename}
                  </p>

                  {/* Score Display */}
                  <div className="flex items-center gap-4 mb-3">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-dark-400" />
                      <span className={`text-2xl font-bold ${getScoreColor(candidate.final_score)}`}>
                        {candidate.final_score.toFixed(1)}%
                      </span>
                    </div>
                    <span className="text-dark-400 text-sm">
                      📅 {new Date(candidate.created_at).toLocaleDateString()}
                    </span>
                  </div>

                  {/* Detailed Scores */}
                  {expandedId === candidate.id && (
                    <div className="bg-dark-800 rounded-lg p-4 mb-3 border border-dark-600">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {Object.entries(candidate.scores).map(([key, value]) => (
                          <div key={key}>
                            <p className="text-dark-400 text-xs capitalize">
                              {key.replace('_', ' ')}
                            </p>
                            <p className="text-white font-semibold">
                              {(value as number).toFixed(1)}%
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Notes Section */}
                  {editingId === candidate.id ? (
                    <div className="mb-3">
                      <textarea
                        value={editingNotes}
                        onChange={(e) => setEditingNotes(e.target.value)}
                        placeholder="Add notes about this candidate..."
                        className="w-full px-3 py-2 bg-dark-800 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:border-blue-500 text-sm"
                        rows={2}
                      />
                      <div className="flex gap-2 mt-2">
                        <button
                          onClick={() => handleSaveNotes(candidate.id)}
                          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-lg transition-colors"
                        >
                          Save
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="px-3 py-1 bg-dark-600 hover:bg-dark-500 text-white text-sm rounded-lg transition-colors"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : candidate.notes ? (
                    <div className="mb-3 p-3 bg-dark-800 rounded-lg border border-dark-600">
                      <p className="text-dark-300 text-sm">{candidate.notes}</p>
                    </div>
                  ) : null}
                </div>

                {/* Actions */}
                <div className="flex gap-2 ml-4">
                  <button
                    onClick={() => {
                      setExpandedId(
                        expandedId === candidate.id ? null : candidate.id
                      )
                    }}
                    className="p-2 text-blue-400 hover:bg-blue-900/30 rounded-lg transition-colors"
                    title="View details"
                  >
                    <TrendingUp className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => {
                      setEditingId(candidate.id)
                      setEditingNotes(candidate.notes || '')
                    }}
                    className="p-2 text-purple-400 hover:bg-purple-900/30 rounded-lg transition-colors"
                    title="Edit notes"
                  >
                    <MessageSquare className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => handleDeleteCandidate(candidate.id)}
                    className="p-2 text-red-400 hover:bg-red-900/30 rounded-lg transition-colors"
                    title="Delete candidate"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
