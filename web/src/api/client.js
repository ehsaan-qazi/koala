import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  console.error("Missing Supabase env variables. Please check your .env file.")
}

export const supabase = createClient(supabaseUrl || '', supabaseAnonKey || '')

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

export async function apiFetch(endpoint, options = {}) {
  // Get current session token
  const { data: { session } } = await supabase.auth.getSession()
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail?.message || errorData.detail || 'API request failed')
  }

  // Handle empty responses (e.g., 204 No Content)
  if (response.status === 204) return null;
  
  return response.json()
}
