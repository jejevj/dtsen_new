import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import AuthService from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const accessToken = ref(localStorage.getItem('access_token') || null)

  const isAuthenticated = computed(() => !!accessToken.value)

  async function login(email, password) {
    const data = await AuthService.login(email, password)
    accessToken.value = data.access_token
    user.value = data.user
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user', JSON.stringify(data.user))
  }

  function logout() {
    accessToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  return { user, accessToken, isAuthenticated, login, logout }
})
