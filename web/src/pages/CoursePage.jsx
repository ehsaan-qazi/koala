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

function toDateInputValue(iso) {
  if (!iso) return ''
  // Expect ISO datetime/date; return YYYY-MM-DD for <input type="date">
  return String(iso).slice(0, 10)
}

const NODE_TYPES = ['Assignment', 'Quiz', 'Exam', 'Project', 'Lab', 'Other']

export default function CoursePage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [course, setCourse] = useState(null)
  const [documents, setDocuments] = useState([])
  const [topics, setTopics] = useState([])
  const [roadmap, setRoadmap] = useState([])
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)

  // Limits state
  const [limits, setLimits] = useState(null)

  // Upload state
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')
  const [uploadSuccess, setUploadSuccess] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef(null)

  // Extraction + roadmap state
  const [extracting, setExtracting] = useState(null) // document ID being extracted
  const [polling, setPolling] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [draft, setDraft] = useState({ title: '', node_type: 'Other', deadline: '', weight_percent: '' })

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

  const fetchRoadmap = async () => {
    try {
      const data = await apiFetch(`/roadmap-nodes/courses/${id}`)
      setRoadmap(data)
    } catch (err) {
      console.error('Failed to fetch roadmap:', err)
    }
  }

  const fetchLimits = async () => {
    try {
      const data = await apiFetch('/billing/limits')
      setLimits(data)
    } catch (err) {
      console.error('Failed to fetch limits:', err)
    }
  }

  useEffect(() => {
    const loadAll = async () => {
      setLoading(true)
      await Promise.all([fetchCourse(), fetchDocuments(), fetchTopics(), fetchRoadmap(), fetchLimits()])
      setLoading(false)
    }
    loadAll()
  }, [id])

  // File upload handler
  const handleFileUpload = async (file) => {
    if (!file) return

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

  // Roadmap extraction (Phase 2 core) — 202 + poll status
  const handleExtractRoadmap = async (documentId) => {
    setExtracting(documentId)
    setUploadError('')
    try {
      await apiFetch(`/documents/${documentId}/extract-roadmap`, { method: 'POST' })
      await pollExtraction(documentId)
      await fetchRoadmap()
      await fetchDocuments()
      setActiveTab('roadmap')
    } catch (err) {
      setUploadError(err.message || 'Roadmap extraction failed')
    } finally {
      setExtracting(null)
    }
  }

  const pollExtraction = async (documentId) => {
    setPolling(true)
    try {
      for (let i = 0; i < 40; i++) {
        const status = await apiFetch(`/documents/${documentId}/extraction-status`)
        if (status.status === 'processed' || status.status === 'failed') {
          if (status.status === 'failed') {
            setUploadError(status.error_message || 'Extraction failed')
          }
          return status
        }
        await new Promise((r) => setTimeout(r, 1500))
      }
    } finally {
      setPolling(false)
    }
  }

  // Topic extraction (Phase 3 — Pro)
  const handleExtractTopics = async (documentId) => {
    setExtracting(documentId)
    try {
      const result = await apiFetch(`/documents/${documentId}/extract`, { method: 'POST' })
      await fetchTopics()
      await fetchDocuments()
      if (result.topics_extracted > 0) setActiveTab('topics')
    } catch (err) {
      setUploadError(err.message || 'Extraction failed')
    } finally {
      setExtracting(null)
    }
  }

  // Roadmap node actions
  const handleConfirmNode = async (nodeId) => {
    try {
      await apiFetch(`/roadmap-nodes/${nodeId}/confirm`, { method: 'POST' })
      await fetchRoadmap()
    } catch (err) {
      console.error('Confirm failed:', err)
    }
  }

  const handleDeleteNode = async (nodeId) => {
    try {
      await apiFetch(`/roadmap-nodes/${nodeId}`, { method: 'DELETE' })
      await fetchRoadmap()
    } catch (err) {
      console.error('Delete failed:', err)
    }
  }

  const startEdit = (node) => {
    setEditingId(node.id)
    setDraft({
      title: node.title,
      node_type: node.node_type,
      deadline: toDateInputValue(node.deadline),
      weight_percent: node.weight_percent ?? '',
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setDraft({ title: '', node_type: 'Other', deadline: '', weight_percent: '' })
  }

  const saveEdit = async (nodeId) => {
    try {
      const patch = {
        title: draft.title.trim(),
        node_type: draft.node_type,
        deadline: draft.deadline || null,
        weight_percent: draft.weight_percent === '' ? null : parseFloat(draft.weight_percent),
      }
      await apiFetch(`/roadmap-nodes/${nodeId}`, {
        method: 'PUT',
        body: JSON.stringify(patch),
      })
      setEditingId(null)
      await fetchRoadmap()
    } catch (err) {
      setUploadError(err.message || 'Failed to save node')
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

  const confirmedCount = roadmap.filter((n) => n.is_confirmed).length
  const roadmapProgress = roadmap.length > 0 ? Math.round((confirmedCount / roadmap.length) * 100) : 0
  const completedTopics = topics.filter((t) => t.is_completed).length
  const topicProgress = topics.length > 0 ? Math.round((completedTopics / topics.length) * 100) : 0

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
          <span>📄 {course.doc_upload_count} / {limits?.upload_limit_per_course || (user?.plan === 'pro' ? 20 : 3)} documents</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
          Overview
        </button>
        <button className={`tab-btn ${activeTab === 'documents' ? 'active' : ''}`} onClick={() => setActiveTab('documents')}>
          Documents ({documents.length})
        </button>
        <button className={`tab-btn ${activeTab === 'roadmap' ? 'active' : ''}`} onClick={() => setActiveTab('roadmap')}>
          Roadmap ({roadmap.length})
        </button>
        <button className={`tab-btn ${activeTab === 'topics' ? 'active' : ''}`} onClick={() => setActiveTab('topics')}>
          Topics ({topics.length})
        </button>
      </div>

      {uploadError && <div className="error-message" style={{ marginTop: '1rem' }}>{uploadError}</div>}
      {uploadSuccess && <div className="success-message" style={{ marginTop: '1rem' }}>✅ {uploadSuccess}</div>}

      {/* ───────── Overview ───────── */}
      {activeTab === 'overview' && (
        <div>
          <div className="settings-card">
            <h3>Progress</h3>
            <div className="quota-bar-container">
              <div className="quota-header">
                <span>Roadmap Confirmation</span>
                <span>{confirmedCount}/{roadmap.length} ({roadmapProgress}%)</span>
              </div>
              <div className="quota-bar">
                <div className="quota-fill" style={{ width: `${roadmapProgress}%` }} />
              </div>
              {roadmap.length === 0 && (
                <p className="quota-hint">Upload a syllabus and extract your roadmap to start tracking assessments.</p>
              )}
            </div>
          </div>

          <div className="settings-card">
            <h3>Quick Actions</h3>
            <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button className="primary-btn" style={{ width: 'auto' }} onClick={() => setActiveTab('documents')}>
                📤 Upload Syllabus
              </button>
              {roadmap.length > 0 && (
                <button className="secondary-btn" onClick={() => setActiveTab('roadmap')}>
                  🗺️ View Roadmap
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ───────── Documents ───────── */}
      {activeTab === 'documents' && (
        <div>
          <div
            className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input ref={fileInputRef} type="file" accept=".pdf" onChange={handleFileSelect} />
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
                  PDF files only • Max {limits?.max_file_size_mb || (user?.plan === 'pro' ? 25 : 10)} MB
                </div>
              </>
            )}
          </div>

          {documents.length > 0 && (
            <div style={{ marginTop: '1.5rem' }}>
              <h3 style={{ marginBottom: '1rem', fontSize: '1rem', fontWeight: 600 }}>Uploaded Documents</h3>
              <div className="document-list">
                {documents.map((doc) => (
                  <div key={doc.id} className="document-item">
                    <div className="document-info">
                      <span className="document-icon">📄</span>
                      <div className="document-details">
                        <div className="document-name">{doc.original_filename}</div>
                        <div className="document-meta">{formatBytes(doc.size_bytes)} • {doc.doc_type}</div>
                      </div>
                    </div>
                    <div className="document-actions">
                      <span className={`status-badge ${doc.processing_status}`}>{doc.processing_status}</span>
                      {doc.processing_status === 'pending' && (
                        <>
                          <button
                            className="extract-btn"
                            onClick={() => handleExtractRoadmap(doc.id)}
                            disabled={extracting === doc.id || polling}
                          >
                            {extracting === doc.id || polling ? <><span className="spinner" /> Extracting…</> : <>🗺️ Extract Roadmap</>}
                          </button>
                          {user?.plan === 'pro' && (
                            <button
                              className="extract-btn secondary"
                              onClick={() => handleExtractTopics(doc.id)}
                              disabled={extracting === doc.id || polling}
                            >
                              📋 Topics
                            </button>
                          )}
                        </>
                      )}
                      <button className="icon-btn danger" title="Delete" onClick={() => handleDeleteDocument(doc.id)}>🗑️</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ───────── Roadmap (Confirm-before-lock) ───────── */}
      {activeTab === 'roadmap' && (
        <div>
          {roadmap.length === 0 ? (
            <div className="empty-state">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🗺️</div>
              <p>No roadmap yet. Upload a syllabus and extract your assessments!</p>
              <button className="primary-btn" style={{ width: 'auto' }} onClick={() => setActiveTab('documents')}>
                📤 Upload Syllabus
              </button>
            </div>
          ) : (
            <>
              <div style={{ marginBottom: '1.5rem' }}>
                <div className="quota-bar-container">
                  <div className="quota-header">
                    <span>Roadmap Confirmation</span>
                    <span>{confirmedCount}/{roadmap.length} confirmed ({roadmapProgress}%)</span>
                  </div>
                  <div className="quota-bar">
                    <div className="quota-fill" style={{ width: `${roadmapProgress}%` }} />
                  </div>
                </div>
                <p className="quota-hint">Review each assessment, fill any missing dates/weights, then confirm to lock it in.</p>
              </div>

              <div className="roadmap-list">
                {roadmap.map((node) => (
                  <div
                    key={node.id}
                    className={`roadmap-item ${node.is_confirmed ? 'confirmed' : ''} ${node.is_placeholder ? 'placeholder' : ''}`}
                  >
                    {editingId === node.id ? (
                      <div className="roadmap-edit">
                        <input
                          className="roadmap-input"
                          value={draft.title}
                          onChange={(e) => setDraft({ ...draft, title: e.target.value })}
                          placeholder="Assessment title"
                        />
                        <div className="roadmap-edit-row">
                          <select value={draft.node_type} onChange={(e) => setDraft({ ...draft, node_type: e.target.value })}>
                            {NODE_TYPES.map((t) => <option key={t} value={t}>{t}</option>)}
                          </select>
                          <input
                            type="date"
                            value={draft.deadline}
                            onChange={(e) => setDraft({ ...draft, deadline: e.target.value })}
                          />
                          <input
                            type="number"
                            step="0.5"
                            min="0"
                            placeholder="Weight %"
                            value={draft.weight_percent}
                            onChange={(e) => setDraft({ ...draft, weight_percent: e.target.value })}
                          />
                        </div>
                        <div className="roadmap-edit-actions">
                          <button className="primary-btn" style={{ width: 'auto' }} onClick={() => saveEdit(node.id)}>Save</button>
                          <button className="secondary-btn" onClick={cancelEdit}>Cancel</button>
                        </div>
                      </div>
                    ) : (
                      <div className="roadmap-view">
                        <div className="roadmap-main">
                          <span className={`status-badge node-type ${node.node_type.toLowerCase()}`}>{node.node_type}</span>
                          <span className="roadmap-title">{node.title}</span>
                          {node.is_placeholder && <span className="badge placeholder-badge">⚠ Needs info</span>}
                          {node.is_confirmed && <span className="badge confirmed-badge">✓ Confirmed</span>}
                        </div>
                        <div className="roadmap-meta">
                          <span>📅 {node.deadline ? toDateInputValue(node.deadline) : '—'}</span>
                          <span>⚖️ {node.weight_percent != null ? `${node.weight_percent}%` : '—'}</span>
                          {node.extraction_confidence != null && (
                            <span title="AI confidence">🤖 {Math.round(node.extraction_confidence * 100)}%</span>
                          )}
                        </div>
                        <div className="roadmap-actions">
                          {!node.is_confirmed && (
                            <button className="primary-btn" style={{ width: 'auto' }} onClick={() => handleConfirmNode(node.id)}>
                              ✓ Confirm
                            </button>
                          )}
                          <button className="secondary-btn" onClick={() => startEdit(node)}>✏️ Edit</button>
                          <button className="icon-btn danger" onClick={() => handleDeleteNode(node.id)}>🗑️</button>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* ───────── Topics ───────── */}
      {activeTab === 'topics' && (
        <div>
          {topics.length === 0 ? (
            <div className="empty-state">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📋</div>
              <p>No topics yet. Upload slides and extract topics to get started! (Pro)</p>
              <button className="primary-btn" style={{ width: 'auto' }} onClick={() => setActiveTab('documents')}>
                📤 Upload Document
              </button>
            </div>
          ) : (
            <>
              <div style={{ marginBottom: '1.5rem' }}>
                <div className="quota-bar-container">
                  <div className="quota-header">
                    <span>Completion Progress</span>
                    <span>{completedTopics}/{topics.length} topics ({topicProgress}%)</span>
                  </div>
                  <div className="quota-bar">
                    <div className="quota-fill" style={{ width: `${topicProgress}%` }} />
                  </div>
                </div>
              </div>

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
