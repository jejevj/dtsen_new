import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * Composable untuk watermark identifier user.
 * Format: "Nama Lengkap - Nama LAZ" atau "Nama Lengkap" jika tidak ada LAZ.
 */
export function useWatermark() {
  const authStore = useAuthStore()

  const userIdentifier = computed(() => {
    const u = authStore.user
    if (!u) return 'CONFIDENTIAL'

    const nama = u.user_fullname || u.nama_lengkap || u.email || u.tuser_email || 'CONFIDENTIAL'
    const laz  = u.laz_nama || u.laz_kode || null

    return laz ? `${nama} - ${laz}` : nama
  })

  return { userIdentifier }
}
