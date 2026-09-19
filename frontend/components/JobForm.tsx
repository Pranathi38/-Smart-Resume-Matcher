'use client'

import { useState } from 'react'
import { Briefcase } from 'lucide-react'

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

interface JobFormProps {
  onSubmit: (data: JobData) => void
}

export default function JobForm({ onSubmit }: JobFormProps) {
  const [formData, setFormData] = useState<JobData>({
    title: '',
    skills: [],
    requirements: '',
    experience_years: 0,
    education_level: 'Bachelors',
    certifications: [],
    languages: [],
    location: 'Remote',
  })

  const [skillInput, setSkillInput] = useState('')
  const [certInput, setCertInput] = useState('')
  const [langInput, setLangInput] = useState('')

  const handleAddSkill = () => {
    if (skillInput.trim()) {
      setFormData({
        ...formData,
        skills: [...formData.skills, skillInput.trim()],
      })
      setSkillInput('')
    }
  }

  const handleRemoveSkill = (index: number) => {
    setFormData({
      ...formData,
      skills: formData.skills.filter((_, i) => i !== index),
    })
  }

  const handleAddCert = () => {
    if (certInput.trim()) {
      setFormData({
        ...formData,
        certifications: [...formData.certifications, certInput.trim()],
      })
      setCertInput('')
    }
  }

  const handleRemoveCert = (index: number) => {
    setFormData({
      ...formData,
      certifications: formData.certifications.filter((_, i) => i !== index),
    })
  }

  const handleAddLang = () => {
    if (langInput.trim()) {
      setFormData({
        ...formData,
        languages: [...formData.languages, langInput.trim()],
      })
      setLangInput('')
    }
  }

  const handleRemoveLang = (index: number) => {
    setFormData({
      ...formData,
      languages: formData.languages.filter((_, i) => i !== index),
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.title && formData.skills.length > 0) {
      onSubmit(formData)
    }
  }

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-8 shadow-2xl">
      <div className="flex items-center gap-3 mb-6">
        <Briefcase className="w-6 h-6 text-blue-500" />
        <h2 className="text-2xl font-bold text-white">Job Details</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Job Title */}
        <div>
          <label className="block text-sm font-medium text-dark-200 mb-2">
            Job Title *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) =>
              setFormData({ ...formData, title: e.target.value })
            }
            placeholder="e.g., Senior Software Engineer"
            className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Skills */}
        <div>
          <label className="block text-sm font-medium text-dark-200 mb-2">
            Required Skills *
          </label>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSkill()}
              placeholder="Add a skill and press Enter"
              className="flex-1 px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              type="button"
              onClick={handleAddSkill}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.skills.map((skill, idx) => (
              <div
                key={idx}
                className="bg-blue-900/30 border border-blue-500 text-blue-200 px-3 py-1 rounded-full text-sm flex items-center gap-2"
              >
                {skill}
                <button
                  type="button"
                  onClick={() => handleRemoveSkill(idx)}
                  className="text-blue-400 hover:text-blue-200"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Requirements */}
        <div>
          <label className="block text-sm font-medium text-dark-200 mb-2">
            Job Requirements
          </label>
          <textarea
            value={formData.requirements}
            onChange={(e) =>
              setFormData({ ...formData, requirements: e.target.value })
            }
            placeholder="Describe the job requirements and responsibilities..."
            rows={4}
            className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:border-blue-500 transition-colors resize-none"
          />
        </div>

        {/* Experience Years */}
        <div>
          <label className="block text-sm font-medium text-dark-200 mb-2">
            Required Experience (Years)
          </label>
          <input
            type="number"
            min="0"
            value={formData.experience_years}
            onChange={(e) =>
              setFormData({
                ...formData,
                experience_years: parseFloat(e.target.value) || 0,
              })
            }
            className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Education Level */}
        <div>
          <label className="block text-sm font-medium text-dark-200 mb-2">
            Education Level
          </label>
          <select
            value={formData.education_level}
            onChange={(e) =>
              setFormData({ ...formData, education_level: e.target.value })
            }
            className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white focus:outline-none focus:border-blue-500 transition-colors"
          >
            <option>High School</option>
            <option>Bachelors</option>
            <option>Masters</option>
            <option>PhD</option>
          </select>
        </div>

        {/* Certifications */}
        <div>
          <label className="block text-sm font-medium text-dark-200 mb-2">
            Certifications
          </label>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={certInput}
              onChange={(e) => setCertInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddCert()}
              placeholder="Add a certification"
              className="flex-1 px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              type="button"
              onClick={handleAddCert}
              className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.certifications.map((cert, idx) => (
              <div
                key={idx}
                className="bg-purple-900/30 border border-purple-500 text-purple-200 px-3 py-1 rounded-full text-sm flex items-center gap-2"
              >
                {cert}
                <button
                  type="button"
                  onClick={() => handleRemoveCert(idx)}
                  className="text-purple-400 hover:text-purple-200"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Languages */}
        <div>
          <label className="block text-sm font-medium text-dark-200 mb-2">
            Languages
          </label>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={langInput}
              onChange={(e) => setLangInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddLang()}
              placeholder="Add a language"
              className="flex-1 px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:border-blue-500 transition-colors"
            />
            <button
              type="button"
              onClick={handleAddLang}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
            >
              Add
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.languages.map((lang, idx) => (
              <div
                key={idx}
                className="bg-green-900/30 border border-green-500 text-green-200 px-3 py-1 rounded-full text-sm flex items-center gap-2"
              >
                {lang}
                <button
                  type="button"
                  onClick={() => handleRemoveLang(idx)}
                  className="text-green-400 hover:text-green-200"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-dark-200 mb-2">
            Location
          </label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) =>
              setFormData({ ...formData, location: e.target.value })
            }
            placeholder="e.g., New York, Remote"
            className="w-full px-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-dark-400 focus:outline-none focus:border-blue-500 transition-colors"
          />
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all transform hover:scale-105"
        >
          Continue to Resume Upload
        </button>
      </form>
    </div>
  )
}
