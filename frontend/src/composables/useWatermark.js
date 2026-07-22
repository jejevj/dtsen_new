import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

/**
 * Composable untuk menghasilkan string watermark yang konsisten di seluruh aplikasi.
 *
 * Format output:
 *   - User dtsen dengan LAZ  : "Nama Lengkap - Nama LAZ"
 *   - User dtsen tanpa LAZ   : "Nama Lengkap"
 *   - User tuser             : "Nama Lengkap"
 *   - Tidak login            : "CONFIDENTIAL"
 *
 * Field yang dibaca dari store.user:
 *   - nama_lengkap  (tipe dtsen)
 *   - user_fullname (tipe tuser)
 *   - laz_nama      (hasil join t_laz, diisi oleh backend _dtsen_payload)
 */
export function useWatermark() {
  const store = useAuthStore()

  const userIdentifier = computed(() => {
    const u = store.user
    if (!u) return 'CONFIDENTIAL'

    const nama = u.user_fullname || u.nama_lengkap || u.email || 'CONFIDENTIAL'
    const laz  = u.laz_nama || null

    return laz ? `${nama} - ${laz}` : nama
  })

  return { userIdentifier }
}
