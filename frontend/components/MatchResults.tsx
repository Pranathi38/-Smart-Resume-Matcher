'use client'

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { CheckCircle, AlertCircle, TrendingUp } from 'lucide-react'

interface MatchResult {
  candidate_name: string
  final_score: number
  classification: string
  scores: Record<string, number>
  weights: Record<string, number>
}

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

interface MatchResultsProps {
  result: MatchResult
  candidate: CandidateData
}

export default function MatchResults({ result, candidate }: MatchResultsProps) {
  // Prepare data for radar chart
  const radarData = Object.entries(result.scores).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' '),
    value: Math.round(value),
    fullMark: 100,
  }))

  const getClassificationColor = (classification: string) => {
    switch (classification) {
      case 'High Match':
        return 'text-green-400'
      case 'Medium Match':
        return 'text-yellow-400'
      case 'Low Match':
        return 'text-red-400'
      default:
        return 'text-dark-300'
    }
  }

  const getClassificationBg = (classification: string) => {
    switch (classification) {
      case 'High Match':
        return 'bg-green-900/30 border-green-500'
      case 'Medium Match':
        return 'bg-yellow-900/30 border-yellow-500'
      case 'Low Match':
        return 'bg-red-900/30 border-red-500'
      default:
        return 'bg-dark-700 border-dark-600'
    }
  }

  const getClassificationIcon = (classification: string) => {
    switch (classification) {
      case 'High Match':
        return <CheckCircle className="w-6 h-6 text-green-400" />
      case 'Medium Match':
        return <AlertCircle className="w-6 h-6 text-yellow-400" />
      case 'Low Match':
        return <AlertCircle className="w-6 h-6 text-red-400" />
      default:
        return <TrendingUp className="w-6 h-6 text-dark-400" />
    }
  }

  return (
    <div className="space-y-8">
      {/* Header with Score */}
      <div className={`border rounded-xl p-8 ${getClassificationBg(result.classification)}`}>
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">
              {candidate.candidate_name}
            </h2>
            <p className="text-dark-300">{candidate.career_objective}</p>
          </div>
          <div className="flex flex-col items-end">
            {getClassificationIcon(result.classification)}
            <p className={`text-2xl font-bold mt-2 ${getClassificationColor(result.classification)}`}>
              {result.classification}
            </p>
          </div>
        </div>

        {/* Score Display */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Final Score */}
          <div className="bg-dark-800/50 rounded-lg p-6 border border-dark-700">
            <p className="text-dark-300 text-sm mb-2">Final Match Score</p>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white">
                {result.final_score}
              </span>
              <span className="text-dark-400">/100</span>
            </div>
            {/* Score bar */}
            <div className="mt-4 w-full bg-dark-700 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full transition-all ${
                  result.final_score >= 80
                    ? 'bg-green-500'
                    : result.final_score >= 50
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${result.final_score}%` }}
              />
            </div>
          </div>

          {/* Experience */}
          <div className="bg-dark-800/50 rounded-lg p-6 border border-dark-700">
            <p className="text-dark-300 text-sm mb-2">Experience</p>
            <p className="text-3xl font-bold text-white mb-1">
              {candidate.experience_years}
            </p>
            <p className="text-dark-400 text-sm">years</p>
          </div>

          {/* Education */}
          <div className="bg-dark-800/50 rounded-lg p-6 border border-dark-700">
            <p className="text-dark-300 text-sm mb-2">Education</p>
            <p className="text-lg font-semibold text-white">
              {candidate.education_level}
            </p>
            <p className="text-dark-400 text-sm mt-2">
              {candidate.location}
            </p>
          </div>
        </div>
      </div>

      {/* Radar Chart */}
      <div className="bg-dark-800 border border-dark-700 rounded-xl p-8">
        <h3 className="text-xl font-bold text-white mb-6">Match Analysis</h3>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid stroke="#374151" />
            <PolarAngleAxis
              dataKey="name"
              tick={{ fill: '#9ca3af', fontSize: 12 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#6b7280', fontSize: 12 }}
            />
            <Radar
              name="Match Score"
              dataKey="value"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.6}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1f2937',
                border: '1px solid #374151',
                borderRadius: '8px',
              }}
              labelStyle={{ color: '#f3f4f6' }}
              formatter={(value: number) => `${value}%`}
            />
            <Legend wrapperStyle={{ color: '#9ca3af' }} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Scores */}
      <div className="bg-dark-800 border border-dark-700 rounded-xl p-8">
        <h3 className="text-xl font-bold text-white mb-6">Detailed Scores</h3>
        <div className="space-y-4">
          {Object.entries(result.scores).map(([key, score]) => {
            const weight = result.weights[key] || 0
            const displayName = key.charAt(0).toUpperCase() + key.slice(1).replace('_', ' ')
            return (
              <div key={key} className="bg-dark-700/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <p className="text-white font-medium">{displayName}</p>
                    <p className="text-dark-400 text-sm">
                      Weight: {(weight * 100).toFixed(0)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-blue-400">
                      {Math.round(score)}
                    </p>
                    <p className="text-dark-400 text-sm">/100</p>
                  </div>
                </div>
                <div className="w-full bg-dark-600 rounded-full h-2 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all"
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Candidate Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Skills */}
        <div className="bg-dark-800 border border-dark-700 rounded-xl p-8">
          <h3 className="text-lg font-bold text-white mb-4">Skills</h3>
          <div className="flex flex-wrap gap-2">
            {candidate.skills.map((skill, idx) => (
              <span
                key={idx}
                className="bg-blue-900/30 border border-blue-500 text-blue-200 px-3 py-1 rounded-full text-sm"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        {/* Certifications */}
        <div className="bg-dark-800 border border-dark-700 rounded-xl p-8">
          <h3 className="text-lg font-bold text-white mb-4">Certifications</h3>
          {candidate.certifications.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {candidate.certifications.map((cert, idx) => (
                <span
                  key={idx}
                  className="bg-purple-900/30 border border-purple-500 text-purple-200 px-3 py-1 rounded-full text-sm"
                >
                  {cert}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-dark-400">No certifications listed</p>
          )}
        </div>

        {/* Languages */}
        <div className="bg-dark-800 border border-dark-700 rounded-xl p-8">
          <h3 className="text-lg font-bold text-white mb-4">Languages</h3>
          {candidate.languages.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {candidate.languages.map((lang, idx) => (
                <span
                  key={idx}
                  className="bg-green-900/30 border border-green-500 text-green-200 px-3 py-1 rounded-full text-sm"
                >
                  {lang}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-dark-400">No languages listed</p>
          )}
        </div>

        {/* Salary & Location */}
        <div className="bg-dark-800 border border-dark-700 rounded-xl p-8">
          <h3 className="text-lg font-bold text-white mb-4">Additional Info</h3>
          <div className="space-y-3">
            <div>
              <p className="text-dark-400 text-sm">Location</p>
              <p className="text-white font-medium">{candidate.location}</p>
            </div>
            {candidate.salary_expectation && (
              <div>
                <p className="text-dark-400 text-sm">Salary Expectation</p>
                <p className="text-white font-medium">
                  ${candidate.salary_expectation.toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
