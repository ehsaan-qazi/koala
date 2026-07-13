import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../api/client'
import { Link } from 'react-router-dom'

export default function SettingsPage() {
  const { user, refreshUser } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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

  // Assuming Free gets 3, Pro gets 20 as defined in plan
  const limit = user?.plan === 'pro' ? 20 : 3

  return (
    <div className="page-container">
      <header className="topbar">
        <h1>Settings</h1>
        <Link to="/" className="text-btn">Back to Dashboard</Link>
      </header>

      <main className="content settings-content">
        <section className="settings-card">
          <h3>Subscription Plan</h3>
          <div className="plan-details">
            <div className="plan-info">
              <span className={`plan-badge ${user?.plan === 'pro' ? 'pro' : 'free'}`}>
                {user?.plan === 'pro' ? 'Pro Plan' : 'Free Plan'}
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
                {loading ? 'Processing...' : 'Upgrade to Pro'}
              </button>
            )}
          </div>
          {error && <p className="error-message">{error}</p>}
        </section>

        <section className="settings-card">
          <h3>Quota Overview (Placeholder)</h3>
          <div className="quota-bar-container">
            <div className="quota-header">
              <span>Document Uploads</span>
              <span>0 / {limit} per course</span>
            </div>
            <div className="quota-bar">
              <div className="quota-fill" style={{ width: '0%' }}></div>
            </div>
            <p className="quota-hint">
              {user?.plan === 'pro' 
                ? 'Your pro plan gives you 20 document uploads per course.' 
                : 'Free tier is limited to 3 document uploads per course.'}
            </p>
          </div>
        </section>
      </main>
    </div>
  )
}
