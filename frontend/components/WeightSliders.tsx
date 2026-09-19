'use client'

import { useState, useEffect } from 'react'
import { Sliders } from 'lucide-react'

interface Weights {
  skills: number
  experience: number
  experience_years: number
  education: number
  certifications: number
  languages: number
  location: number
}

interface WeightSlidersProps {
  weights: Weights
  onChange: (weights: Weights) => void
  loading: boolean
}

const WEIGHT_LABELS: Record<keyof Weights, string> = {
  skills: 'Skills Match',
  experience: 'Experience Description',
  experience_years: 'Years of Experience',
  education: 'Education Level',
  certifications: 'Certifications',
  languages: 'Languages',
  location: 'Location',
}

export default function WeightSliders({
  weights,
  onChange,
  loading,
}: WeightSlidersProps) {
  const [localWeights, setLocalWeights] = useState(weights)
  const [totalWeight, setTotalWeight] = useState(1)

  useEffect(() => {
    setLocalWeights(weights)
  }, [weights])

  useEffect(() => {
    const total = Object.values(localWeights).reduce((a, b) => a + b, 0)
    setTotalWeight(total)
  }, [localWeights])

  const handleWeightChange = (key: keyof Weights, value: number) => {
    const newWeights = { ...localWeights, [key]: value }
    setLocalWeights(newWeights)
    onChange(newWeights)
  }

  const resetWeights = () => {
    const defaultWeights: Weights = {
      skills: 0.35,
      experience: 0.25,
      experience_years: 0.15,
      education: 0.10,
      certifications: 0.10,
      languages: 0.03,
      location: 0.02,
    }
    setLocalWeights(defaultWeights)
    onChange(defaultWeights)
  }

  const normalizeWeights = () => {
    const total = Object.values(localWeights).reduce((a, b) => a + b, 0)
    if (total > 0) {
      const normalized = Object.entries(localWeights).reduce(
        (acc, [key, value]) => ({
          ...acc,
          [key]: value / total,
        }),
        {} as Weights
      )
      setLocalWeights(normalized)
      onChange(normalized)
    }
  }

  const isNormalized = Math.abs(totalWeight - 1) < 0.01

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-8">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <Sliders className="w-6 h-6 text-orange-500" />
          <h3 className="text-2xl font-bold text-white">Adjust Weights</h3>
        </div>
        <div className="text-right">
          <p className="text-dark-300 text-sm">Total Weight</p>
          <p
            className={`text-2xl font-bold ${
              isNormalized ? 'text-green-400' : 'text-yellow-400'
            }`}
          >
            {totalWeight.toFixed(2)}
          </p>
        </div>
      </div>

      <p className="text-dark-300 mb-6">
        Adjust the importance of each attribute. The weights will be automatically
        normalized to calculate the final match score.
      </p>

      <div className="space-y-6 mb-8">
        {(Object.entries(localWeights) as Array<[keyof Weights, number]>).map(
          ([key, value]) => (
            <div key={key}>
              <div className="flex items-center justify-between mb-2">
                <label className="text-white font-medium">
                  {WEIGHT_LABELS[key]}
                </label>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.01"
                    value={value.toFixed(2)}
                    onChange={(e) =>
                      handleWeightChange(key, parseFloat(e.target.value) || 0)
                    }
                    disabled={loading}
                    className="w-16 px-2 py-1 bg-dark-700 border border-dark-600 rounded text-white text-sm focus:outline-none focus:border-orange-500 disabled:opacity-50"
                  />
                  <span className="text-dark-400 text-sm w-12 text-right">
                    {(value * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={value}
                onChange={(e) =>
                  handleWeightChange(key, parseFloat(e.target.value))
                }
                disabled={loading}
                className="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer accent-orange-500 disabled:opacity-50"
              />
            </div>
          )
        )}
      </div>

      <div className="flex gap-4">
        <button
          onClick={normalizeWeights}
          disabled={loading || isNormalized}
          className="flex-1 py-2 bg-orange-600 hover:bg-orange-700 disabled:bg-dark-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
        >
          Normalize Weights
        </button>
        <button
          onClick={resetWeights}
          disabled={loading}
          className="flex-1 py-2 bg-dark-700 hover:bg-dark-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors disabled:opacity-50"
        >
          Reset to Default
        </button>
      </div>

      {!isNormalized && (
        <div className="mt-4 p-3 bg-yellow-900/30 border border-yellow-500 rounded-lg">
          <p className="text-yellow-200 text-sm">
            💡 Weights will be automatically normalized when calculating the match
            score.
          </p>
        </div>
      )}
    </div>
  )
}
