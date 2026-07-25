import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Load stored authentication state on startup
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
    setLoading(false)
  }, [])

  const login = async (email, password) => {
    let response
    try {
      response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      })
    } catch (err) {
      throw new Error('Unable to connect to the server. Please ensure the backend is running.')
    }
    
    let data = null
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      try {
        data = await response.json()
      } catch (e) {
        // Ignored, default to null
      }
    }

    if (!response.ok) {
      const errorMsg = (data && data.error && data.error.message) || (data && data.detail) || `Server returned error status ${response.status}. Please check backend logs and database connection.`
      throw new Error(errorMsg)
    }

    if (!data || !data.access_token) {
      throw new Error('Server returned an empty or invalid session response.')
    }

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    setToken(data.access_token)
    setUser(data.user)
    return data.user
  }

  const signup = async (name, email, password) => {
    let response
    try {
      response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password, home_currency: 'INR' }),
      })
    } catch (err) {
      throw new Error('Unable to connect to the server. Please ensure the backend is running.')
    }

    let data = null
    const contentType = response.headers.get('content-type')
    if (contentType && contentType.includes('application/json')) {
      try {
        data = await response.json()
      } catch (e) {
        // Ignored, default to null
      }
    }

    if (!response.ok) {
      const errorMsg = (data && data.error && data.error.message) || (data && data.detail) || `Server returned error status ${response.status}. Please check backend logs and database connection.`
      throw new Error(errorMsg)
    }

    if (!data || !data.access_token) {
      throw new Error('Server returned an empty or invalid session response.')
    }

    localStorage.setItem('token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
    setToken(data.access_token)
    setUser(data.user)
    return data.user
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, loading, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
