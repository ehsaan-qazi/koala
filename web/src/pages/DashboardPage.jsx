import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { apiFetch } from '../api/client';

// ─── Helpers ────────────────────────────────────────────────────────────────

function getCurrentSemester() {
  const month = new Date().getMonth() + 1;
  if (month >= 1 && month <= 5) return 'Spring';
  if (month >= 6 && month <= 7) return 'Summer';
  return 'Fall';
}

function getCurrentYear() {
  return String(new Date().getFullYear());
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

// ─── New Course Modal ────────────────────────────────────────────────────────

function NewCourseModal({ onClose, onCreated }) {
  const [form, setForm] = useState({
    name: '',
    code: '',
    semester: getCurrentSemester(),
    academic_year: getCurrentYear(),
    credit_hours: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name.trim()) { setError('Course name is required'); return; }
    setLoading(true);
    setError('');
    try {
      const payload = {
        name: form.name.trim(),
        code: form.code.trim() || null,
        semester: form.semester,
        academic_year: form.academic_year,
        credit_hours: form.credit_hours ? parseFloat(form.credit_hours) : null,
      };
      const created = await apiFetch('/courses', {
        method: 'POST',
        body: JSON.stringify(payload),
      });
      onCreated(created);
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to create course');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay open" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">📖 New Course</h2>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Course Name *</label>
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              placeholder="e.g. Software Engineering"
              autoFocus
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label>Course Code</label>
              <input
                name="code"
                value={form.code}
                onChange={handleChange}
                placeholder="e.g. SE301"
              />
            </div>
            <div className="form-group">
              <label>Credit Hours</label>
              <input
                name="credit_hours"
                type="number"
                step="0.5"
                min="0"
                max="10"
                value={form.credit_hours}
                onChange={handleChange}
                placeholder="e.g. 3"
              />
            </div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label>Semester</label>
              <select name="semester" value={form.semester} onChange={handleChange}>
                <option value="Spring">Spring</option>
                <option value="Summer">Summer</option>
                <option value="Fall">Fall</option>
              </select>
            </div>
            <div className="form-group">
              <label>Academic Year</label>
              <input
                name="academic_year"
                value={form.academic_year}
                onChange={handleChange}
                placeholder="e.g. 2026"
              />
            </div>
          </div>
          {error && <div className="error-message">{error}</div>}
          <div className="modal-actions">
            <button type="button" className="secondary-btn" onClick={onClose}>Cancel</button>
            <button type="submit" className="primary-btn" disabled={loading}>
              {loading ? 'Creating...' : 'Create Course'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ─── Course Card ─────────────────────────────────────────────────────────────

function CourseCard({ course, onClick }) {
  const colors = ['#7c6af7', '#34d399', '#60a5fa', '#fbbf24', '#f472b6', '#fb923c'];
  const colorIndex = course.id % colors.length;
  const accent = colors[colorIndex];

  return (
    <div
      className="course-card"
      onClick={onClick}
      style={{ '--course-accent': accent, cursor: 'pointer' }}
    >
      <div className="course-card-top">
        <div className="course-card-icon" style={{ background: `${accent}22`, color: accent }}>
          📖
        </div>
        <div className="course-card-badge">{course.code || '—'}</div>
      </div>
      <div className="course-card-name">{course.name}</div>
      <div className="course-card-meta">
        <span>{course.semester} {course.academic_year}</span>
        {course.credit_hours && <span>· {course.credit_hours} cr</span>}
      </div>
      <div className="course-card-progress">
        <div className="progress-bar" style={{ marginTop: '0.75rem' }}>
          <div
            className="progress-fill"
            style={{ width: '0%', background: accent }}
          />
        </div>
        <div className="course-card-docs">
          📄 {course.doc_upload_count || 0} doc{course.doc_upload_count !== 1 ? 's' : ''}
        </div>
      </div>
    </div>
  );
}

// ─── Dashboard Page ──────────────────────────────────────────────────────────

export default function DashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [courses, setCourses] = useState([]);
  const [loadingCourses, setLoadingCourses] = useState(true);
  const [showAll, setShowAll] = useState(false);
  const [showModal, setShowModal] = useState(false);

  const currentSemester = getCurrentSemester();
  const currentYear = getCurrentYear();

  useEffect(() => {
    apiFetch('/courses')
      .then((data) => setCourses(data))
      .catch(console.error)
      .finally(() => setLoadingCourses(false));
  }, []);

  // Filter to current semester, or show all
  const semesterCourses = courses.filter(
    (c) => c.semester === currentSemester && String(c.academic_year) === currentYear
  );
  const displayedCourses = showAll ? courses : semesterCourses;
  const hasOtherCourses = courses.length > semesterCourses.length;

  const handleCourseCreated = (newCourse) => {
    setCourses((prev) => [newCourse, ...prev]);
  };

  const firstName = user?.full_name?.split(' ')[0] || user?.email?.split('@')[0] || 'there';

  return (
    <div className="page active" id="page-dashboard">
      {/* Page Header */}
      <div className="page-header">
        <div>
          <div className="page-title">{getGreeting()}, {firstName} 👋</div>
          <div className="page-subtitle">
            {currentSemester} {currentYear}
            {semesterCourses.length > 0
              ? ` · ${semesterCourses.length} active course${semesterCourses.length !== 1 ? 's' : ''}`
              : ' · No courses yet — add one!'}
          </div>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          + New Course
        </button>
      </div>

      {/* Stats Row */}
      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-card-top">
            <div className="stat-card-label">Active Courses</div>
            <div className="stat-card-icon">📖</div>
          </div>
          <div className="stat-card-value">{semesterCourses.length}</div>
          <div className="stat-card-sub">{currentSemester} {currentYear}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-top">
            <div className="stat-card-label">Documents Uploaded</div>
            <div className="stat-card-icon">📄</div>
          </div>
          <div className="stat-card-value">
            {semesterCourses.reduce((sum, c) => sum + (c.doc_upload_count || 0), 0)}
          </div>
          <div className="stat-card-sub">Across all courses</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-top">
            <div className="stat-card-label">Topics Completed</div>
            <div className="stat-card-icon">✅</div>
          </div>
          <div className="stat-card-value">—</div>
          <div className="stat-card-sub">Upload syllabus to track</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-top">
            <div className="stat-card-label">Your Plan</div>
            <div className="stat-card-icon">⭐</div>
          </div>
          <div className="stat-card-value" style={{ fontSize: '1.2rem' }}>
            {user?.plan === 'pro' ? 'Pro' : 'Free'}
          </div>
          <div className="stat-card-sub">
            {user?.plan === 'pro' ? 'All features unlocked' : 'Upgrade for AI extraction'}
          </div>
        </div>
      </div>

      {/* Courses Section */}
      <div className="section-header" style={{ marginTop: '1.5rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span className="card-title">
            {showAll ? '📚 All Courses' : `📚 ${currentSemester} ${currentYear} Courses`}
          </span>
          {hasOtherCourses && (
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => setShowAll((v) => !v)}
            >
              {showAll ? `Show ${currentSemester} only` : `Show all (${courses.length})`}
            </button>
          )}
        </div>
        {displayedCourses.length > 0 && (
          <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
            {displayedCourses.length} course{displayedCourses.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {loadingCourses ? (
        <div className="courses-grid">
          {[1, 2, 3].map((i) => (
            <div key={i} className="course-card skeleton-card" style={{ height: '140px' }} />
          ))}
        </div>
      ) : displayedCourses.length === 0 ? (
        <div className="empty-state">
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📖</div>
          <p>
            {showAll
              ? 'No courses yet. Create your first course to get started!'
              : `No courses for ${currentSemester} ${currentYear}. Add one or switch to show all.`}
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button className="primary-btn" style={{ width: 'auto' }} onClick={() => setShowModal(true)}>
              + Add Course
            </button>
            {!showAll && hasOtherCourses && (
              <button className="secondary-btn" onClick={() => setShowAll(true)}>
                Show all semesters
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="courses-grid">
          {displayedCourses.map((course) => (
            <CourseCard
              key={course.id}
              course={course}
              onClick={() => navigate(`/courses/${course.id}`)}
            />
          ))}
          {/* Add course tile */}
          <div
            className="course-card course-card-add"
            onClick={() => setShowModal(true)}
            style={{ cursor: 'pointer' }}
          >
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>+</div>
              <div style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>New Course</div>
            </div>
          </div>
        </div>
      )}

      {/* Quick Tip */}
      {!loadingCourses && courses.length === 0 && (
        <div className="tip-card" style={{ marginTop: '1.5rem' }}>
          <span>💡</span>
          <span>
            Start by creating a course, then upload your syllabus PDF — Koala will extract
            your roadmap, topics, and deadlines automatically.
          </span>
        </div>
      )}

      {/* New Course Modal */}
      {showModal && (
        <NewCourseModal
          onClose={() => setShowModal(false)}
          onCreated={handleCourseCreated}
        />
      )}
    </div>
  );
}
