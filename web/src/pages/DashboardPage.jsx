import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../api/client'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')

  // New course form state
  const [newCourse, setNewCourse] = useState({
    name: '',
    code: '',
    semester: 'Fall',
    academic_year: '2026-2027',
    credit_hours: '',
  })

  const fetchCourses = async () => {
    try {
      const data = await apiFetch('/courses')
      setCourses(data)
    } catch (err) {
      console.error('Failed to fetch courses:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCourses()
  }, [])

  const handleCreateCourse = async (e) => {
    e.preventDefault()
    setCreating(true)
    setError('')

    try {
      const payload = {
        ...newCourse,
        credit_hours: newCourse.credit_hours ? parseFloat(newCourse.credit_hours) : null,
      }
      await apiFetch('/courses', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      setShowModal(false)
      setNewCourse({ name: '', code: '', semester: 'Fall', academic_year: '2026-2027', credit_hours: '' })
      await fetchCourses()
    } catch (err) {
      setError(err.message || 'Failed to create course')
    } finally {
      setCreating(false)
    }
  }

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  return (
    <div className="page-container">
      <header className="topbar">
        <h1>Dashboard</h1>
        <div className="user-controls">
          <span className={`plan-badge ${user?.plan === 'pro' ? 'pro' : 'free'}`}>
            {user?.plan === 'pro' ? 'Pro Plan' : 'Free Plan'}
          </span>
          <span className="user-name">{user?.full_name || user?.email}</span>
          <Link to="/settings" className="icon-btn" title="Settings">⚙️</Link>
          <button onClick={logout} className="icon-btn" title="Logout">🚪</button>
        </div>
      </header>

      <main className="content">
        <div className="welcome-section">
          <h2>Welcome back, {user?.full_name?.split(' ')[0] || 'Student'} 👋</h2>
        </div>

        {/* Course List */}
        <section>
          <div className="courses-header">
            <h3>Your Courses</h3>
            <button className="primary-btn" style={{ width: 'auto' }} onClick={() => setShowModal(true)}>
              + New Course
            </button>
          </div>

          {loading ? (
            <div className="loading-screen" style={{ height: '200px' }}>Loading courses...</div>
          ) : courses.length === 0 ? (
            <div className="empty-state">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📚</div>
              <p>No courses yet. Create your first course to get started!</p>
              <button className="primary-btn" style={{ width: 'auto' }} onClick={() => setShowModal(true)}>
                + Create Course
              </button>
            </div>
          ) : (
            <div className="courses-grid">
              {courses.map(course => (
                <Link to={`/courses/${course.id}`} key={course.id} className="course-card">
                  <div className="course-card-name">{course.name}</div>
                  {course.code && <div className="course-card-code">{course.code}</div>}
                  <div className="course-card-meta">
                    <span>📅 {course.semester} {course.academic_year}</span>
                    <span>📄 {course.doc_upload_count} docs</span>
                    {course.credit_hours && <span>🎓 {course.credit_hours} cr</span>}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>
      </main>

      {/* Create Course Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <h3>Create New Course</h3>
            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleCreateCourse}>
              <div className="form-group">
                <label>Course Name *</label>
                <input
                  type="text"
                  value={newCourse.name}
                  onChange={e => setNewCourse({ ...newCourse, name: e.target.value })}
                  placeholder="e.g. Data Structures & Algorithms"
                  required
                />
              </div>

              <div className="form-group">
                <label>Course Code</label>
                <input
                  type="text"
                  value={newCourse.code}
                  onChange={e => setNewCourse({ ...newCourse, code: e.target.value })}
                  placeholder="e.g. CS201"
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label>Semester *</label>
                  <select
                    value={newCourse.semester}
                    onChange={e => setNewCourse({ ...newCourse, semester: e.target.value })}
                    style={{
                      width: '100%', padding: '0.75rem', background: 'var(--bg-hover)',
                      border: '1px solid var(--border)', borderRadius: 'var(--radius-md)',
                      color: 'var(--text-main)', outline: 'none', fontFamily: 'inherit'
                    }}
                  >
                    <option value="Fall">Fall</option>
                    <option value="Spring">Spring</option>
                    <option value="Summer">Summer</option>
                    <option value="Winter">Winter</option>
                  </select>
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label>Academic Year</label>
                  <input
                    type="text"
                    value={newCourse.academic_year}
                    onChange={e => setNewCourse({ ...newCourse, academic_year: e.target.value })}
                    placeholder="2026-2027"
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Credit Hours</label>
                <input
                  type="number"
                  step="0.5"
                  min="0"
                  max="12"
                  value={newCourse.credit_hours}
                  onChange={e => setNewCourse({ ...newCourse, credit_hours: e.target.value })}
                  placeholder="e.g. 3"
                />
              </div>

              <div className="modal-actions">
                <button type="button" className="secondary-btn" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="primary-btn" style={{ width: 'auto' }} disabled={creating}>
                  {creating ? 'Creating...' : 'Create Course'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
