import axios from 'axios'

const token = () => {
  // For demo: generate a simple unsigned JWT-like header if needed; backend expects a valid JWT.
  return localStorage.getItem('token') || ''
}

export const api = axios.create({ baseURL: '' })

api.interceptors.request.use((cfg)=>{
  const t = token()
  if (t) cfg.headers['Authorization'] = `Bearer ${t}`
  return cfg
})
