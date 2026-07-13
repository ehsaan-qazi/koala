import { useAuth } from '../context/AuthContext'
import { Link } from 'react-router-dom'

export default function DashboardPage() {
  const { user, logout } = useAuth()

  return (
    <div className="page-container">
      <header className="topbar">
        <h1>Dashboard</h1>
        <div className="user-controls">
          <span className={`plan-badge ${user?.plan === 'pro' ? 'pro' : 'free'}`}>
            {user?.plan === 'pro' ? 'Pro Plan' : 'Free Plan'}
          </span>
          <span className="user-name">{user?.full_name || user?.email}</span>
        </div>
      </header>
      
      <main className="content">
        <div className="welcome-section">
          <h2>Welcome to Koala, {user?.full_name || 'Student'}!</h2>
          <p>This is the shell dashboard for Phase 1.</p>
        </div>

        <div className="actions-section">
          <Link to="/settings" className="secondary-btn">Go to Settings</Link>
          <button onClick={logout} className="secondary-btn">Logout</button>
        </div>
      </main>
    </div>
  )
}
