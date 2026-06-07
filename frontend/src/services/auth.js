import axios from 'axios'

const API = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1'

export default {
  async login(identifier, password) {
    const { data } = await axios.post(`${API}/auth/login`, { identifier, password })
    return data
  },
  async me(token) {
    const { data } = await axios.get(`${API}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    return data
  }
}
