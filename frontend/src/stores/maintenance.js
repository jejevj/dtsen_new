import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchMaintenanceStatus } from '@/services/optionsService'

export const useMaintenanceStore = defineStore('maintenance', () => {
  const isMaintenance = ref(false)
  const message = ref(null)
  const checked = ref(false)

  async function check() {
    try {
      const data = await fetchMaintenanceStatus()
      isMaintenance.value = data.maintenance
      message.value = data.message ?? null
    } catch (err) {
      // Kalau API 503 axios throw error — tangkap dan baca responsenya
      if (err?.response?.status === 503) {
        isMaintenance.value = true
        message.value = err.response.data?.message ?? 'Sistem sedang dalam pemeliharaan.'
      } else {
        // Error lain (network, dll) — jangan blokir akses
        isMaintenance.value = false
      }
    } finally {
      checked.value = true
    }
  }

  return { isMaintenance, message, checked, check }
})
