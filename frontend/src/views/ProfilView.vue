<template>
  <AppLayout>
    <div class="p-6 max-w-5xl mx-auto">

      <!-- Page Header -->
      <div class="mb-6">
        <h1 class="text-xl font-bold text-gray-800">Profil Pengguna</h1>
        <p class="text-sm text-gray-500 mt-1">Informasi akun dan pengaturan keamanan.</p>
      </div>

      <!-- Toast notification -->
      <Toast position="top-right" />

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- ==============================
             KOLOM KIRI: Detail Pengguna
        =============================== -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <!-- Card Header -->
          <div class="px-6 py-4 border-b border-gray-100 flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-green-50 flex items-center justify-center">
              <i class="pi pi-user text-green-600" style="font-size:14px;"></i>
            </div>
            <h2 class="text-sm font-semibold text-gray-800">Detail Pengguna</h2>
          </div>

          <!-- Avatar + Nama -->
          <div class="flex flex-col items-center py-6 px-6 border-b border-gray-100 bg-gray-50">
            <div class="w-16 h-16 rounded-full bg-green-600 flex items-center justify-center mb-3">
              <span class="text-white text-xl font-bold">{{ userInitials }}</span>
            </div>
            <p class="text-base font-semibold text-gray-800">{{ auth.userDisplayName }}</p>
            <span
              class="mt-1 inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="auth.isDtsen ? 'bg-blue-50 text-blue-700' : 'bg-green-50 text-green-700'"
            >
              <i class="pi pi-shield" style="font-size:10px;"></i>
              {{ auth.isDtsen ? 'LAZ / DTSEN' : 'Internal' }}
            </span>
          </div>

          <!-- Info Fields -->
          <div class="px-6 py-5 space-y-4">
            <div v-for="field in userFields" :key="field.label" class="flex flex-col gap-1">
              <label class="text-xs font-medium text-gray-400 uppercase tracking-wide">{{ field.label }}</label>
              <p class="text-sm text-gray-800 font-medium">
                <span v-if="field.value && field.value !== '-'">{{ field.value }}</span>
                <span v-else class="text-gray-400 font-normal italic">Tidak tersedia</span>
              </p>
            </div>
          </div>
        </div>

        <!-- ==============================
             KOLOM KANAN: Ubah Password
        =============================== -->
        <div class="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
          <!-- Card Header -->
          <div class="px-6 py-4 border-b border-gray-100 flex items-center gap-3">
            <div class="w-8 h-8 rounded-lg bg-orange-50 flex items-center justify-center">
              <i class="pi pi-lock text-orange-500" style="font-size:14px;"></i>
            </div>
            <h2 class="text-sm font-semibold text-gray-800">Ubah Password</h2>
          </div>

          <!-- Success state setelah password berhasil diubah -->
          <div v-if="changeSuccess" class="px-6 py-8 flex flex-col items-center text-center gap-4">
            <div class="w-16 h-16 rounded-full bg-green-50 flex items-center justify-center">
              <i class="pi pi-check-circle text-green-600" style="font-size:32px;"></i>
            </div>
            <div>
              <p class="text-base font-bold text-gray-800 mb-1">Password Berhasil Diubah!</p>
              <p class="text-sm text-gray-500 leading-relaxed">
                Email notifikasi telah dikirim ke akun Anda.<br>
                Semua sesi login sebelumnya telah dihapus.<br>
                Anda akan diarahkan ke halaman login dalam
                <strong class="text-green-600">{{ countdown }}</strong> detik...
              </p>
            </div>
            <button
              @click="doLogout"
              class="mt-2 flex items-center gap-2 px-6 py-2.5 rounded-lg bg-green-600 hover:bg-green-700 text-white text-sm font-semibold transition cursor-pointer"
            >
              <i class="pi pi-sign-out" style="font-size:13px;"></i>
              Logout Sekarang
            </button>
          </div>

          <!-- Form -->
          <form v-else @submit.prevent="handleChangePassword" class="px-6 py-5 space-y-5">

            <!-- Password Lama -->
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-gray-600">Password Lama <span class="text-red-500">*</span></label>
              <div class="relative">
                <input
                  v-model="form.old_password"
                  :type="showOld ? 'text' : 'password'"
                  placeholder="Masukkan password lama"
                  class="w-full px-3 py-2.5 pr-10 rounded-lg border text-sm transition"
                  :class="errors.old_password ? 'border-red-400 bg-red-50' : 'border-gray-300 bg-white'"
                  style="outline:none;"
                  @focus="e => e.target.style.boxShadow='0 0 0 3px rgba(22,163,74,0.15)'"
                  @blur="e => e.target.style.boxShadow='none'"
                />
                <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" @click="showOld = !showOld">
                  <i :class="showOld ? 'pi pi-eye-slash' : 'pi pi-eye'" style="font-size:14px;"></i>
                </button>
              </div>
              <p v-if="errors.old_password" class="text-xs text-red-500">{{ errors.old_password }}</p>
            </div>

            <!-- Password Baru -->
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-gray-600">Password Baru <span class="text-red-500">*</span></label>
              <div class="relative">
                <input
                  v-model="form.new_password"
                  :type="showNew ? 'text' : 'password'"
                  placeholder="Minimal 8 karakter"
                  class="w-full px-3 py-2.5 pr-10 rounded-lg border text-sm transition"
                  :class="errors.new_password ? 'border-red-400 bg-red-50' : 'border-gray-300 bg-white'"
                  style="outline:none;"
                  @focus="e => e.target.style.boxShadow='0 0 0 3px rgba(22,163,74,0.15)'"
                  @blur="e => e.target.style.boxShadow='none'"
                />
                <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" @click="showNew = !showNew">
                  <i :class="showNew ? 'pi pi-eye-slash' : 'pi pi-eye'" style="font-size:14px;"></i>
                </button>
              </div>
              <!-- Kekuatan password -->
              <div v-if="form.new_password" class="mt-1 space-y-1">
                <div class="flex gap-1">
                  <div v-for="n in 4" :key="n" class="h-1 flex-1 rounded-full transition-all"
                    :class="passwordStrength >= n ? strengthColor : 'bg-gray-200'"
                  />
                </div>
                <p class="text-xs" :class="strengthTextColor">{{ strengthLabel }}</p>
              </div>
              <p v-if="errors.new_password" class="text-xs text-red-500">{{ errors.new_password }}</p>
            </div>

            <!-- Konfirmasi Password -->
            <div class="flex flex-col gap-1.5">
              <label class="text-xs font-semibold text-gray-600">Konfirmasi Password Baru <span class="text-red-500">*</span></label>
              <div class="relative">
                <input
                  v-model="form.confirm_password"
                  :type="showConfirm ? 'text' : 'password'"
                  placeholder="Ulangi password baru"
                  class="w-full px-3 py-2.5 pr-10 rounded-lg border text-sm transition"
                  :class="errors.confirm_password ? 'border-red-400 bg-red-50' : (form.confirm_password && form.confirm_password === form.new_password ? 'border-green-400 bg-green-50' : 'border-gray-300 bg-white')"
                  style="outline:none;"
                  @focus="e => e.target.style.boxShadow='0 0 0 3px rgba(22,163,74,0.15)'"
                  @blur="e => e.target.style.boxShadow='none'"
                />
                <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600" @click="showConfirm = !showConfirm">
                  <i :class="showConfirm ? 'pi pi-eye-slash' : 'pi pi-eye'" style="font-size:14px;"></i>
                </button>
              </div>
              <p v-if="errors.confirm_password" class="text-xs text-red-500">{{ errors.confirm_password }}</p>
              <p v-else-if="form.confirm_password && form.confirm_password === form.new_password" class="text-xs text-green-600 flex items-center gap-1">
                <i class="pi pi-check-circle" style="font-size:11px;"></i> Password cocok
              </p>
            </div>

            <!-- Syarat password -->
            <div class="p-3 rounded-lg bg-gray-50 border border-gray-100">
              <p class="text-xs font-semibold text-gray-500 mb-2">Syarat Password:</p>
              <ul class="space-y-1">
                <li v-for="rule in passwordRules" :key="rule.label" class="flex items-center gap-2 text-xs" :class="rule.met ? 'text-green-600' : 'text-gray-400'">
                  <i :class="rule.met ? 'pi pi-check-circle' : 'pi pi-circle'" style="font-size:11px;"></i>
                  {{ rule.label }}
                </li>
              </ul>
            </div>

            <!-- Error umum dari API -->
            <div v-if="apiError" class="flex items-start gap-2 p-3 rounded-lg bg-red-50 border border-red-200">
              <i class="pi pi-exclamation-triangle text-red-500 mt-0.5" style="font-size:13px;"></i>
              <p class="text-xs text-red-600">{{ apiError }}</p>
            </div>

            <!-- Submit -->
            <button
              type="submit"
              :disabled="submitting"
              class="w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-semibold transition"
              :class="submitting ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700 text-white cursor-pointer'"
            >
              <i v-if="submitting" class="pi pi-spin pi-spinner" style="font-size:13px;"></i>
              <i v-else class="pi pi-lock" style="font-size:13px;"></i>
              {{ submitting ? 'Menyimpan...' : 'Simpan Password Baru' }}
            </button>

          </form>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Toast      from 'primevue/toast'
import AppLayout  from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { authService }  from '@/services/auth'

const auth    = useAuthStore()
const toast   = useToast()
const router  = useRouter()

// ---- User fields ----
const userInitials = computed(() => {
  const name = auth.userDisplayName
  if (!name) return 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
})

const userFields = computed(() => [
  { label: 'Nama Lengkap',   value: auth.user?.nama_lengkap    || auth.user?.user_fullname || '-' },
  { label: 'Username / ID',  value: auth.user?.username        || String(auth.user?.id || '-') },
  { label: 'Email',          value: auth.user?.email           || '-' },
  { label: 'No. Telepon',    value: auth.user?.notelp          || auth.user?.phone || '-' },
  { label: 'Tipe Akun',      value: auth.user?.akun_types === 'laz' ? 'LAZ / DTSEN'
                                   : auth.user?.akun_types === 'baznas' ? 'BAZNAS'
                                   : auth.user?.akun_types === 'internal' ? 'Internal'
                                   : (auth.user?.akun_types || '-') },
  { label: 'LAZ / Instansi', value: auth.user?.laz_nama || auth.user?.instansi || '-' },
])

// ---- Form state ----
const form    = ref({ old_password: '', new_password: '', confirm_password: '' })
const errors  = ref({})
const apiError    = ref('')
const submitting  = ref(false)
const changeSuccess = ref(false)
const countdown   = ref(5)
const showOld     = ref(false)
const showNew     = ref(false)
const showConfirm = ref(false)
let countdownTimer = null

onBeforeUnmount(() => { if (countdownTimer) clearInterval(countdownTimer) })

// ---- Password strength ----
const passwordStrength = computed(() => {
  const p = form.value.new_password
  if (!p) return 0
  let score = 0
  if (p.length >= 8)           score++
  if (/[A-Z]/.test(p))         score++
  if (/[0-9]/.test(p))         score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return score
})

const strengthColor = computed(() => {
  const s = passwordStrength.value
  if (s <= 1) return 'bg-red-400'
  if (s === 2) return 'bg-orange-400'
  if (s === 3) return 'bg-yellow-400'
  return 'bg-green-500'
})

const strengthLabel = computed(() => {
  return ['', 'Sangat Lemah', 'Lemah', 'Cukup', 'Kuat'][passwordStrength.value] || ''
})

const strengthTextColor = computed(() => {
  const s = passwordStrength.value
  if (s <= 1) return 'text-red-500'
  if (s === 2) return 'text-orange-500'
  if (s === 3) return 'text-yellow-600'
  return 'text-green-600'
})

const passwordRules = computed(() => [
  { label: 'Minimal 8 karakter',             met: form.value.new_password.length >= 8 },
  { label: 'Mengandung huruf kapital (A-Z)',  met: /[A-Z]/.test(form.value.new_password) },
  { label: 'Mengandung angka (0-9)',          met: /[0-9]/.test(form.value.new_password) },
  { label: 'Mengandung karakter khusus',      met: /[^A-Za-z0-9]/.test(form.value.new_password) },
])

// ---- Validasi ----
function validate() {
  const e = {}
  if (!form.value.old_password)       e.old_password     = 'Password lama wajib diisi.'
  if (!form.value.new_password)       e.new_password     = 'Password baru wajib diisi.'
  else if (form.value.new_password.length < 8) e.new_password = 'Password minimal 8 karakter.'
  if (!form.value.confirm_password)  e.confirm_password = 'Konfirmasi password wajib diisi.'
  else if (form.value.confirm_password !== form.value.new_password)
    e.confirm_password = 'Konfirmasi password tidak cocok.'
  errors.value = e
  return Object.keys(e).length === 0
}

// ---- Logout helper ----
async function doLogout() {
  if (countdownTimer) clearInterval(countdownTimer)
  await auth.logout()
  router.push('/')
}

// ---- Submit ----
async function handleChangePassword() {
  apiError.value = ''
  if (!validate()) return

  submitting.value = true
  try {
    const res = await authService.changePassword({
      old_password:     form.value.old_password,
      new_password:     form.value.new_password,
      confirm_password: form.value.confirm_password,
    })

    const data = res.data || {}

    changeSuccess.value = true
    form.value = { old_password: '', new_password: '', confirm_password: '' }
    errors.value = {}

    countdown.value = 5
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) doLogout()
    }, 1000)

    if (data.require_relogin) {
      toast.add({
        severity: 'success',
        summary:  'Password Diubah',
        detail:   data.email_sent
          ? 'Email notifikasi telah dikirim. Silakan login kembali.'
          : 'Password berhasil diubah. Silakan login kembali.',
        life: 5000,
      })
    }
  } catch (err) {
    const msg = err.response?.data?.message
              || err.response?.data?.detail
              || 'Gagal mengubah password. Periksa password lama Anda.'
    apiError.value = msg
  } finally {
    submitting.value = false
  }
}
</script>
