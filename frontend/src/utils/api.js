import axios from 'axios'

// Create a configured axios instance
const api = axios.create({
  baseURL: '', // Vite proxy will map relative /api requests to localhost:8000
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add a request interceptor to attach the JWT token automatically
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Add a response interceptor to extract data or parse standard errors
api.interceptors.response.use(
  (response) => {
    // If the response follows the success shape {"data": ..., "error": null}
    if (response.data && response.data.data !== undefined) {
      return response.data // Return the wrapped envelope (data and error keys)
    }
    return response
  },
  (error) => {
    // If backend returned a structured error response
    if (error.response && error.response.data && error.response.data.error) {
      const apiErr = error.response.data.error
      return Promise.reject(new Error(apiErr.message || 'An API error occurred.'))
    }
    
    // Fallback error messages
    const fallbackMessage = 
      error.response?.data?.detail?.message || 
      error.response?.data?.detail || 
      error.message || 
      'An unexpected network error occurred.'
      
    return Promise.reject(new Error(fallbackMessage))
  }
)

export default api
