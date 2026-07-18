import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import SettingsPage from './pages/SettingsPage'
import CoursePage from './pages/CoursePage'
import Layout from './components/Layout'
import './styles/index.css'

// Protected Route Wrapper
function ProtectedRoute({ children }) {
  const { session, loading } = useAuth()
  
  if (loading) {
    return <div className="loading-screen">Loading...</div>
  }
  
  if (!session) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

function AppRoutes() {
  const { session, loading } = useAuth()

  if (loading) {
    return <div className="loading-screen">Loading...</div>
  }

  return (
    <Routes>
      <Route 
        path="/login" 
        element={session ? <Navigate to="/" replace /> : <LoginPage />} 
      />
      
      <Route element={<ProtectedRoute><Layout /></ProtectedRoute>}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/courses/:id" element={<CoursePage />} />
        <Route path="/settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  )
}
