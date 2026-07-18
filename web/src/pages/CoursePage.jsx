import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiFetch, supabase } from '../api/client'

function formatBytes(bytes) {
  if (!bytes) return '—'
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export default function CoursePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [course, setCourse] = useState(null)
  const [documents, setDocuments] = useState([])
  const [topics, setTopics] = useState([])
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)

  // Upload state
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef(null)

  // Extraction state
  const [extracting, setExtracting] = useState(null) // document ID being extracted

  const fetchCourse = async () => {
    try {
      const data = await apiFetch(`/courses/${id}`)
      setCourse(data)
    } catch (err) {
      console.error('Failed to fetch course:', err)
      navigate('/')
    }
  }

  const fetchDocuments = async () => {
    try {
      const data = await apiFetch(`/documents/courses/${id}`)
      setDocuments(data)
    } catch (err) {
      console.error('Failed to fetch documents:', err)
    }
  }

  const fetchTopics = async () => {
    try {
      const data = await apiFetch(`/topics/courses/${id}`)
      setTopics(data)
    } catch (err) {
      console.error('Failed to fetch topics:', err)
    }
  }

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true)
      await Promise.all([fetchCourse(), fetchDocuments(), fetchTopics()])
      setLoading(false)
    }
    loadAll()
  }, [id])

  // File upload handler
  const handleFileUpload = async (file) => {
    if (!file) return

    // Basic validation
    if (file.type !== 'application/pdf') {
      setUploadError('Only PDF files are supported')
      return
    }

    setUploading(true)
    setUploadError('')
    setUploadSuccess('')

    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('doc_type', 'syllabus')

      const { data: { session } } = await supabase.auth.getSession()

      const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
      const response = await fetch(`${API_BASE}/documents/courses/${id}/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.access_token}`,
        },
        body: formData,
      })

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || 'Upload failed')
      }

      setUploadSuccess(`"${file.name}" uploaded successfully!`)
      await fetchDocuments()
      await fetchCourse() // refresh doc count
    } catch (err) {
      setUploadError(err.message || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleFileDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const file = e.dataTransfer.files[0]
    handleFileUpload(file)
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    handleFileUpload(file)
  }

  // Extraction handler
  const handleExtract = async (documentId) => {
    setExtracting(documentId)
    try {
      const result = await apiFetch(`/documents/${documentId}/extract`, { method: 'POST' })
      await fetchTopics()
      await fetchDocuments()
      if (result.topics_extracted > 0) {
        setActiveTab('topics')
      }
    } catch (err) {
      setUploadError(err.message || 'Extraction failed')
    } finally {
      setExtracting(null)
    }
  }

  // Topic toggle handler
  const handleToggleTopic = async (topicId, currentCompleted) => {
    try {
      await apiFetch(`/topics/${topicId}/toggle`, {
        method: 'PATCH',
        body: JSON.stringify({ is_completed: !currentCompleted }),
      })
      await fetchTopics()
    } catch (err) {
      console.error('Toggle failed:', err)
    }
  }

  // Delete document
  const handleDeleteDocument = async (docId) => {
    try {
      await apiFetch(`/documents/${docId}`, { method: 'DELETE' })
      await fetchDocuments()
      await fetchCourse()
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  if (loading) {
    return <div className="loading-screen">Loading course...</div>
  }

  if (!course) {
    return <div className="loading-screen">Course not found</div>
  }

  const completedCount = topics.filter(t => t.is_completed).length
  const progressPercent = topics.length > 0 ? Math.round((completedCount / topics.length) * 100) : 0

  return (
    <div className="page-container">
      {/* Course Header */}
      <div className="course-header">
        <div className="course-header-top">
          <button className="back-btn" onClick={() => navigate('/')}>←</button>
          <h1 className="course-title">{course.name}</h1>
        </div>
        <div className="course-subtitle">
          {course.code && <span>{course.code}</span>}
          <span>📅 {course.semester} {course.academic_year}</span>
          {course.credit_hours && <span>🎓 {course.credit_hours} credits</span>}
          <span>📄 {course.doc_upload_count} documents</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          Documents ({documents.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'topics' ? 'active' : ''}`}
          onClick={() => setActiveTab('topics')}
        >
          Topics ({topics.length})
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div>
          {/* Progress Card */}
          <div className="settings-card">
            <h3>Progress</h3>
            <div className="quota-bar-container">
              <div className="quota-header">
                <span>Topic Completion</span>
                <span>{completedCount}/{topics.length} ({progressPercent}%)</span>
              </div>
              <div className="quota-bar">
                <div className="quota-fill" style={{ width: `${progressPercent}%` }} />
              </div>
              {topics.length === 0 && (
                <p className="quota-hint">Upload a syllabus to extract topics and start tracking your progress.</p>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="settings-card">
            <h3>Quick Actions</h3>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button className="primary-btn" style={{ width: 'auto' }} onClick={() => setActiveTab('documents')}>
                📤 Upload Syllabus
              </button>
              {topics.length > 0 && (
                <button className="secondary-btn" onClick={() => setActiveTab('topics')}>
                  ✅ View Topics
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'documents' && (
        <div>
          {/* Upload Zone */}
          <div
            className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf"
              onChange={handleFileSelect}
            />
            {uploading ? (
              <div>
                <div className="spinner" style={{ width: '32px', height: '32px', borderWidth: '3px', marginBottom: '0.75rem' }} />
                <div className="upload-zone-text">Uploading...</div>
              </div>
            ) : (
              <>
                <div className="upload-zone-icon">📁</div>
                <div className="upload-zone-text">
                  Drag & drop your syllabus PDF here, or click to browse
                </div>
                <div className="upload-zone-hint">
                  PDF files only • Max {user?.plan === 'pro' ? '25' : '10'} MB
                </div>
              </>
            )}
          </div>

          {uploadError && <div className="error-message" style={{ marginTop: '1rem' }}>{uploadError}</div>}
          {uploadSuccess && <div className="success-message" style={{ marginTop: '1rem' }}>✅ {uploadSuccess}</div>}

          {/* Document List */}
          {documents.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem', fontSize: '1rem', fontWeight: 600 }}>Uploaded Documents</h3>
              <div className="document-list">
                {documents.map(doc => (
                  <div key={doc.id} className="document-item">
                    <div className="document-info">
                      <span className="document-icon">📄</span>
                      <div className="document-details">
                        <div className="document-name">{doc.original_filename}</div>
                        <div className="document-meta">
                          {formatBytes(doc.size_bytes)} • {doc.doc_type}
                        </div>
                      </div>
                    </div>
                    <div className="document-actions">
                      <span className={`status-badge ${doc.processing_status}`}>
                        {doc.processing_status}
                      </span>
                      {doc.processing_status === 'pending' && (
                        <button
                          className="extract-btn"
                          onClick={() => handleExtract(doc.id)}
                          disabled={extracting === doc.id}
                        >
                          {extracting === doc.id ? (
                            <><span className="spinner" /> Extracting...</>
                          ) : (
                            <>🤖 Extract Topics</>
                          )}
                        </button>
                      )}
                      <button
                        className="icon-btn danger"
                        title="Delete"
                        onClick={() => handleDeleteDocument(doc.id)}
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'topics' && (
        <div>
          {topics.length === 0 ? (
            <div className="empty-state">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
              <p>No topics yet. Upload a syllabus and extract topics to get started!</p>
              <button className="primary-btn" style={{ width: 'auto' }} onClick={() => setActiveTab('documents')}>
                📤 Upload Syllabus
              </button>
            </div>
          ) : (
            <>
              {/* Progress summary */}
              <div style={{ marginBottom: '1.5rem' }}>
                <div className="quota-bar-container">
                  <div className="quota-header">
                    <span>Completion Progress</span>
                    <span>{completedCount}/{topics.length} topics ({progressPercent}%)</span>
                  </div>
                  <div className="quota-bar">
                    <div className="quota-fill" style={{ width: `${progressPercent}%` }} />
                  </div>
                </div>
              </div>

              {/* Topic checklist */}
              <div className="topic-list">
                {topics.map((topic, idx) => (
                  <div
                    key={topic.id}
                    className={`topic-item ${topic.is_completed ? 'completed' : ''}`}
                    onClick={() => handleToggleTopic(topic.id, topic.is_completed)}
                  >
                    <span className="topic-index">{idx + 1}.</span>
                    <div className="topic-checkbox">
                      <span className="topic-checkbox-mark">✓</span>
                    </div>
                    <span className="topic-title">{topic.title}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  )
}
