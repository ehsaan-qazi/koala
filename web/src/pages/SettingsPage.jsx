import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../api/client'
import { Link } from 'react-router-dom'

export default function SettingsPage() {
  const { user, refreshUser } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [limits, setLimits] = useState(null)

  useEffect(() => {
    const fetchLimits = async () => {
      try {
        const data = await apiFetch('/billing/limits')
        setLimits(data)
      } catch (err) {
        console.error('Failed to fetch limits:', err)
      }
    }
    fetchLimits()
  }, [])

  const handleUpgrade = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await apiFetch('/billing/checkout-url')
      if (response.checkout_url) {
        window.location.href = response.checkout_url
      }
    } catch (err) {
      setError(err.message || 'Failed to get checkout URL')
    } finally {
      setLoading(false)
    }
  }

  const uploadLimit = limits?.upload_limit_per_course || (user?.plan === 'pro' ? 20 : 3)

  return (
    <div className="page active">
      <div className="page-header">
        <div>
          <div className="page-title">⚙️ Settings</div>
          <div className="page-subtitle">Manage your account and subscription</div>
        </div>
        <Link to="/" className="btn btn-ghost btn-sm">← Dashboard</Link>
      </div>

      <section className="settings-card">
        <h3>Account</h3>
        <div style={{ fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
          <div><strong style={{ color: 'var(--text-primary)' }}>Email:</strong> {user?.email || '—'}</div>
          <div><strong style={{ color: 'var(--text-primary)' }}>Name:</strong> {user?.full_name || '—'}</div>
        </div>
      </section>

      <section className="settings-card">
        <h3>Subscription Plan</h3>
        <div className="plan-details">
          <div className="plan-info">
            <span className={`plan-badge ${user?.plan === 'pro' ? 'pro' : 'free'}`}>
              {user?.plan === 'pro' ? '✨ Pro Plan' : 'Free Plan'}
            </span>
            <p className="plan-description">
              {user?.plan === 'pro'
                ? 'You have access to all premium features including AI topic extraction.'
                : 'You are on the free tier. Upgrade to unlock AI topic extraction and higher upload limits.'}
            </p>
          </div>

          {user?.plan !== 'pro' && (
            <button
              className="primary-btn upgrade-btn"
              onClick={handleUpgrade}
              disabled={loading}
            >
              {loading ? 'Processing...' : '⚡ Upgrade to Pro'}
            </button>
          )}
        </div>
        {error && <p className="error-message" style={{ marginTop: '0.75rem' }}>{error}</p>}
      </section>

      <section className="settings-card">
        <h3>Quota Overview</h3>
        <div className="quota-bar-container">
          <div className="quota-header">
            <span>Document Uploads</span>
            <span>0 / {uploadLimit} per course</span>
          </div>
          <div className="quota-bar">
            <div className="quota-fill" style={{ width: '0%' }} />
          </div>
          <p className="quota-hint">
            {user?.plan === 'pro'
              ? `Your Pro plan gives you ${uploadLimit} document uploads per course.`
              : `Free tier is limited to ${uploadLimit} document uploads per course. Upgrade for more.`}
          </p>
        </div>
      </section>
    </div>
  )
}
