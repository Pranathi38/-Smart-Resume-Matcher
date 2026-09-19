'use client'

import { useState, useRef } from 'react'
import { Upload, FileText } from 'lucide-react'

interface ResumeUploadProps {
  onUpload: (file: File) => void
  loading: boolean
  jobTitle?: string
}

export default function ResumeUpload({
  onUpload,
  loading,
  jobTitle,
}: ResumeUploadProps) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

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

    const files = e.dataTransfer.files
    if (files && files[0]) {
      const file = files[0]
      if (file.type === 'application/pdf') {
        setSelectedFile(file)
      }
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files[0]) {
      setSelectedFile(files[0])
    }
  }

  const handleUpload = () => {
    if (selectedFile) {
      onUpload(selectedFile)
    }
  }

  return (
    <div className="bg-dark-800 border border-dark-700 rounded-xl p-8 shadow-2xl">
      <div className="flex items-center gap-3 mb-6">
        <FileText className="w-6 h-6 text-purple-500" />
        <h2 className="text-2xl font-bold text-white">Upload Resume</h2>
      </div>

      {jobTitle && (
        <p className="text-dark-300 mb-6">
          Matching against: <span className="text-blue-400 font-semibold">{jobTitle}</span>
        </p>
      )}

      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-all cursor-pointer ${
          dragActive
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-dark-600 bg-dark-700/50 hover:border-dark-500'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handleFileSelect}
          className="hidden"
        />

        <Upload className="w-12 h-12 text-dark-400 mx-auto mb-4" />

        <h3 className="text-lg font-semibold text-white mb-2">
          {selectedFile ? selectedFile.name : 'Drop your resume here'}
        </h3>

        <p className="text-dark-400 mb-4">
          {selectedFile
            ? 'Ready to analyze'
            : 'or click to select a PDF file'}
        </p>

        {!selectedFile && (
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Select File
          </button>
        )}
      </div>

      {selectedFile && (
        <div className="mt-6 p-4 bg-dark-700 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="w-5 h-5 text-purple-400" />
              <div>
                <p className="text-white font-medium">{selectedFile.name}</p>
                <p className="text-dark-400 text-sm">
                  {(selectedFile.size / 1024).toFixed(2)} KB
                </p>
              </div>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              className="text-dark-400 hover:text-dark-200 transition-colors"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      <div className="mt-8 flex gap-4">
        <button
          onClick={handleUpload}
          disabled={!selectedFile || loading}
          className="flex-1 py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:from-dark-600 disabled:to-dark-600 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-all transform hover:scale-105 disabled:scale-100"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="animate-spin">⚙️</span>
              Analyzing Resume...
            </span>
          ) : (
            'Analyze Resume'
          )}
        </button>
      </div>
    </div>
  )
}
