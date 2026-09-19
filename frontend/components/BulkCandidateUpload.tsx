'use client'

import { useState } from 'react'
import { Upload, X, CheckCircle, AlertCircle } from 'lucide-react'
import axios from 'axios'

interface UploadResult {
  filename: string
  status: 'pending' | 'uploading' | 'success' | 'error'
  message?: string
  score?: number
}

interface BulkCandidateUploadProps {
  jobId: number
  jobTitle: string
  onUploadComplete: () => void
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function BulkCandidateUpload({
  jobId,
  jobTitle,
  onUploadComplete,
}: BulkCandidateUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [uploading, setUploading] = useState(false)
  const [results, setResults] = useState<UploadResult[]>([])
  const [dragActive, setDragActive] = useState(false)

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFiles = Array.from(e.dataTransfer.files).filter((file) => {
      const name = file.name.toLowerCase()
      return name.endsWith('.pdf') || name.endsWith('.docx')
    })

    if (droppedFiles.length > 0) {
      setFiles((prev) => [...prev, ...droppedFiles])
    }
  }

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      setFiles((prev) => [...prev, ...selectedFiles])
    }
  }

  const removeFile = (index: number) => {
    setFiles(files.filter((_, i) => i !== index))
  }

  const handleUploadAll = async () => {
    if (files.length === 0) return

    setUploading(true)
    const newResults: UploadResult[] = files.map((file) => ({
      filename: file.name,
      status: 'pending',
    }))
    setResults(newResults)

    for (let i = 0; i < files.length; i++) {
      try {
        // Update status to uploading
        setResults((prev) => [
          ...prev.slice(0, i),
          { ...prev[i], status: 'uploading' },
          ...prev.slice(i + 1),
        ])

        // Upload file
        const formData = new FormData()
        formData.append('file', files[i])

        const response = await axios.post(
          `${API_BASE_URL}/jobs/${jobId}/candidates`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          }
        )

        // Update status to success
        setResults((prev) => [
          ...prev.slice(0, i),
          {
            ...prev[i],
            status: 'success',
            score: response.data.final_score,
            message: `${response.data.classification} match`,
          },
          ...prev.slice(i + 1),
        ])
      } catch (error) {
        const message = axios.isAxiosError(error)
          ? error.response?.data?.detail || error.message
          : 'Upload failed'

        // Update status to error
        setResults((prev) => [
          ...prev.slice(0, i),
          {
            ...prev[i],
            status: 'error',
            message,
          },
          ...prev.slice(i + 1),
        ])
      }
    }

    setUploading(false)
  }

  const handleReset = () => {
    setFiles([])
    setResults([])
  }

  const successCount = results.filter((r) => r.status === 'success').length
  const errorCount = results.filter((r) => r.status === 'error').length

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-8 shadow-2xl">
      <div className="flex items-center gap-3 mb-6">
        <Upload className="w-6 h-6 text-green-500" />
        <h2 className="text-2xl font-bold text-white">
          Bulk Upload Resumes for {jobTitle}
        </h2>
      </div>

      {results.length === 0 ? (
        <>
          {/* Drop Zone */}
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors mb-6 ${
              dragActive
                ? 'border-blue-500 bg-blue-900/10'
                : 'border-dark-600 bg-dark-700/50 hover:border-dark-500'
            }`}
          >
            <Upload className="w-12 h-12 text-dark-400 mx-auto mb-4" />
            <p className="text-white font-semibold mb-2">
              Drag and drop resumes here (PDF or Word)
            </p>
            <p className="text-dark-300 text-sm mb-4">or</p>
            <label className="inline-block">
              <input
                type="file"
                multiple
                accept=".pdf,.docx"
                onChange={handleFileInput}
                className="hidden"
              />
              <span className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg cursor-pointer transition-colors inline-block">
                Browse Files
              </span>
            </label>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-white mb-4">
                Selected Files ({files.length})
              </h3>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {files.map((file, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between bg-dark-700 p-3 rounded-lg border border-dark-600"
                  >
                    <div className="flex items-center gap-3 flex-1 min-w-0">
                      <span className="text-dark-400">📄</span>
                      <span className="text-white truncate">{file.name}</span>
                      <span className="text-dark-400 text-sm ml-auto flex-shrink-0">
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                    </div>
                    <button
                      onClick={() => removeFile(idx)}
                      className="ml-2 p-1 text-red-400 hover:bg-red-900/30 rounded transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>

              {/* Upload Button */}
              <div className="flex gap-4 mt-6">
                <button
                  onClick={handleUploadAll}
                  disabled={uploading}
                  className="flex-1 py-3 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700 disabled:opacity-50 text-white font-semibold rounded-lg transition-all"
                >
                  {uploading ? 'Uploading...' : `Upload ${files.length} Resume${files.length !== 1 ? 's' : ''}`}
                </button>
                <button
                  onClick={handleReset}
                  disabled={uploading}
                  className="px-6 py-3 bg-dark-700 hover:bg-dark-600 disabled:opacity-50 text-white rounded-lg transition-colors"
                >
                  Clear
                </button>
              </div>
            </div>
          )}
        </>
      ) : (
        <>
          {/* Results Summary */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-dark-700 rounded-lg p-4 border border-dark-600">
              <p className="text-dark-400 text-sm">Total</p>
              <p className="text-2xl font-bold text-white mt-1">{results.length}</p>
            </div>
            <div className="bg-green-900/20 rounded-lg p-4 border border-green-500">
              <p className="text-green-300 text-sm">Success</p>
              <p className="text-2xl font-bold text-green-400 mt-1">{successCount}</p>
            </div>
            <div className="bg-red-900/20 rounded-lg p-4 border border-red-500">
              <p className="text-red-300 text-sm">Failed</p>
              <p className="text-2xl font-bold text-red-400 mt-1">{errorCount}</p>
            </div>
          </div>

          {/* Results List */}
          <div className="space-y-3 max-h-96 overflow-y-auto mb-6">
            {results.map((result, idx) => (
              <div
                key={idx}
                className={`flex items-center justify-between p-4 rounded-lg border ${
                  result.status === 'success'
                    ? 'bg-green-900/20 border-green-500'
                    : result.status === 'error'
                    ? 'bg-red-900/20 border-red-500'
                    : 'bg-dark-700 border-dark-600'
                }`}
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  {result.status === 'success' && (
                    <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                  )}
                  {result.status === 'error' && (
                    <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  )}
                  {result.status === 'uploading' && (
                    <div className="w-5 h-5 rounded-full border-2 border-blue-500 border-t-transparent animate-spin flex-shrink-0" />
                  )}
                  {result.status === 'pending' && (
                    <div className="w-5 h-5 rounded-full border-2 border-dark-500 flex-shrink-0" />
                  )}
                  <div className="min-w-0 flex-1">
                    <p className="text-white truncate">{result.filename}</p>
                    {result.message && (
                      <p
                        className={`text-sm ${
                          result.status === 'success'
                            ? 'text-green-300'
                            : 'text-red-300'
                        }`}
                      >
                        {result.message}
                      </p>
                    )}
                  </div>
                </div>
                {result.score !== undefined && (
                  <span className="ml-4 text-lg font-bold text-white">
                    {result.score.toFixed(1)}%
                  </span>
                )}
              </div>
            ))}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={() => {
                onUploadComplete()
                handleReset()
              }}
              className="flex-1 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold rounded-lg transition-all"
            >
              View All Candidates
            </button>
            <button
              onClick={handleReset}
              className="px-6 py-3 bg-dark-700 hover:bg-dark-600 text-white rounded-lg transition-colors"
            >
              Upload More
            </button>
          </div>
        </>
      )}
    </div>
  )
}
