<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="visible" class="lm-overlay" @mousedown.self="handleClose">
        <div class="lm-card" role="dialog" aria-modal="true" aria-labelledby="lm-title">

          <!-- Header -->
          <div class="lm-header">
            <svg class="lm-logo" aria-label="DTSEN" viewBox="0 0 40 40" fill="none">
              <rect width="40" height="40" rx="8" fill="#01696f"/>
              <path d="M10 20 C10 13 15 10 20 10 C25 10 30 13 30 20 C30 27 25 30 20 30 C15 30 10 27 10 20Z"
                stroke="white" stroke-width="2" fill="none"/>
              <path d="M16 20 L20 16 L24 20 L20 24 Z" fill="white"/>
            </svg>
            <h2 id="lm-title">Masuk ke Satu Data ZIS DSKL</h2>
            <p class="lm-subtitle">Halaman pemantauan pendistribusian dan pendayagunaan ZIS DSKL yang terukur dan tepat sasaran.</p>
            <button class="lm-close" @click="handleClose" aria-label="Tutup">
              <svg viewBox="0 0 20 20" fill="none">
                <path d="M5 5l10 10M15 5L5 15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <!-- Alert Error Banner -->
          <Transition name="alert">
            <div v-if="alertMessage" class="lm-alert" role="alert" aria-live="assertive">
              <svg class="lm-alert-icon" viewBox="0 0 20 20" fill="none" aria-hidden="true">
                <circle cx="10" cy="10" r="9" stroke="currentColor" stroke-width="1.5"/>
                <path d="M10 6v4.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                <circle cx="10" cy="13.5" r="0.9" fill="currentColor"/>
              </svg>
              <div class="lm-alert-body">
                <p class="lm-alert-title">{{ alertMessage.title }}</p>
                <ul v-if="alertMessage.details.length" class="lm-alert-list">
                  <li v-for="d in alertMessage.details" :key="d">{{ d }}</li>
                </ul>
              </div>
              <button class="lm-alert-close" @click="alertMessage = null" aria-label="Tutup notifikasi">
                <svg viewBox="0 0 16 16" fill="none">
                  <path d="M4 4l8 8M12 4L4 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </Transition>

          <!-- Form -->
          <form @submit.prevent="handleLogin" novalidate>
            <div class="lm-group">
              <label for="lm-identifier">Email / No. HP</label>
              <input
                id="lm-identifier"
                v-model="form.identifier"
                type="text"
                placeholder="email@instansi.go.id atau 08xx"
                :class="{ error: errors.identifier }"
                autocomplete="username"
                ref="firstInput"
              />
              <p v-if="errors.identifier" class="lm-err">{{ errors.identifier }}</p>
            </div>

            <div class="lm-group">
              <label for="lm-password">Password</label>
              <div class="lm-input-wrap">
                <input
                  id="lm-password"
                  v-model="form.password"
                  :type="showPw ? 'text' : 'password'"
                  placeholder="Masukkan password"
                  :class="{ error: errors.password }"
                  autocomplete="current-password"
                />
                <button type="button" class="lm-toggle-pw"
                  @click="showPw = !showPw"
                  :aria-label="showPw ? 'Sembunyikan' : 'Tampilkan'">
                  <svg v-if="!showPw" viewBox="0 0 20 20" fill="none">
                    <path d="M1 10s3-7 9-7 9 7 9 7-3 7-9 7-9-7-9-7z" stroke="currentColor" stroke-width="1.5"/>
                    <circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5"/>
                  </svg>
                  <svg v-else viewBox="0 0 20 20" fill="none">
                    <path d="M2 2l16 16M7.5 7.6A3 3 0 0013 13M5 5.2C2.9 6.8 1 10 1 10s3 7 9 7a9 9 0 004.8-1.4"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                    <path d="M11.5 4.2A9 9 0 0119 10s-.8 2-2.4 3.8"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  </svg>
                </button>
              </div>
              <p v-if="errors.password" class="lm-err">{{ errors.password }}</p>
            </div>

            <!-- CAPTCHA -->
            <div class="lm-group">
              <label for="lm-captcha">Verifikasi Keamanan</label>
              <div class="lm-captcha-box">
                <div class="lm-captcha-q">
                  <span class="lm-captcha-text">{{ captcha.question }}</span>
                  <button type="button" class="lm-captcha-refresh" @click="refreshCaptcha"
                    :class="{ spinning: captchaRefreshing }" aria-label="Refresh">
                    <svg viewBox="0 0 20 20" fill="none">
                      <path d="M4 4a7 7 0 1 1 0 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                      <path d="M4 1v4h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
                <input
                  id="lm-captcha"
                  v-model="captchaAnswer"
                  type="text"
                  inputmode="numeric"
                  placeholder="Jawaban"
                  :class="{ error: errors.captcha }"
                  autocomplete="off"
                  maxlength="4"
                />
              </div>
              <p v-if="errors.captcha" class="lm-err">{{ errors.captcha }}</p>
            </div>

            <button type="submit" class="lm-btn" :disabled="auth.loading">
              <span v-if="auth.loading" class="lm-spinner"></span>
              <span v-else>Masuk</span>
            </button>
          </form>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { reactive, ref, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore }       from '@/stores/auth'
import { useLoginModalStore } from '@/stores/loginModal'

const props = defineProps({
  visible: { type: Boolean, default: false }
})
const emit = defineEmits(['close'])

const auth       = useAuthStore()
const loginModal = useLoginModalStore()
const router     = useRouter()
const firstInput = ref(null)

const form   = reactive({ identifier: '', password: '' })
const errors = reactive({ identifier: '', password: '', captcha: '' })
const showPw            = ref(false)
const captchaAnswer     = ref('')
const captchaRefreshing = ref(false)

/** Alert banner: { title: string, details: string[], type: 'error' | 'warning' } */
const alertMessage = ref(null)

// ── CAPTCHA ──────────────────────────────────────────────────────────────────
function generateCaptcha() {
  const ops = ['+', '-', 'x']
  const op  = ops[Math.floor(Math.random() * ops.length)]
  let a, b, answer
  if (op === '+') {
    a = Math.floor(Math.random() * 20) + 1
    b = Math.floor(Math.random() * 20) + 1
    answer = a + b
  } else if (op === '-') {
    a = Math.floor(Math.random() * 20) + 10
    b = Math.floor(Math.random() * 10) + 1
    answer = a - b
  } else {
    a = Math.floor(Math.random() * 9) + 2
    b = Math.floor(Math.random() * 9) + 2
    answer = a * b
  }
  return { question: `${a} ${op} ${b} = ?`, answer: String(answer) }
}
const captcha = reactive(generateCaptcha())

function refreshCaptcha() {
  captchaRefreshing.value = true
  const next = generateCaptcha()
  captcha.question = next.question
  captcha.answer   = next.answer
  captchaAnswer.value = ''
  errors.captcha      = ''
  setTimeout(() => { captchaRefreshing.value = false }, 400)
}
// ─────────────────────────────────────────────────────────────────────────────

// ── Alert helper ───────────────────────────────────────────────────────────────
function showAlert(title, details = []) {
  alertMessage.value = { title, details }
}
function clearAlert() {
  alertMessage.value = null
}
// ─────────────────────────────────────────────────────────────────────────────

watch(() => props.visible, async (val) => {
  if (val) {
    resetForm()
    await nextTick()
    firstInput.value?.focus()
  }
})

function resetForm() {
  form.identifier = ''
  form.password   = ''
  errors.identifier = ''
  errors.password   = ''
  errors.captcha    = ''
  captchaAnswer.value = ''
  clearAlert()
  refreshCaptcha()
}

function handleClose() {
  emit('close')
  if (router.currentRoute.value.name === 'login') router.replace({ name: 'home' })
}

/**
 * Validasi semua field termasuk CAPTCHA.
 * Mengembalikan true hanya jika SEMUA field valid.
 */
function validate() {
  errors.identifier = ''
  errors.password   = ''
  errors.captcha    = ''
  clearAlert()

  const details = []

  if (!form.identifier.trim()) {
    errors.identifier = 'Email atau No. HP wajib diisi.'
    details.push('Email atau No. HP wajib diisi.')
  }

  if (!form.password) {
    errors.password = 'Password wajib diisi.'
    details.push('Password wajib diisi.')
  }

  if (!captchaAnswer.value.trim()) {
    errors.captcha = 'Jawaban verifikasi keamanan wajib diisi.'
    details.push('Jawaban verifikasi keamanan wajib diisi.')
  } else if (captchaAnswer.value.trim() !== captcha.answer) {
    errors.captcha = 'Jawaban verifikasi keamanan salah.'
    details.push('Jawaban verifikasi keamanan salah. Soal telah diperbarui, silakan coba lagi.')
  }

  if (details.length > 0) {
    showAlert('Periksa kembali isian Anda', details)
    return false
  }

  return true
}

async function handleLogin() {
  const isValid = validate()
  if (!isValid) {
    // Jika captcha salah, refresh soal agar tidak bisa brute-force
    if (errors.captcha) refreshCaptcha()
    return
  }

  try {
    await auth.login(form.identifier, form.password)
    // Credentials valid → OTP sudah dikirim ke email → pindah ke halaman verifikasi
    loginModal.close()
    router.push({ name: 'verify-otp' })
  } catch (e) {
    showAlert('Login gagal', [e.message])
    refreshCaptcha()
  }
}

if (typeof window !== 'undefined') {
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && props.visible) handleClose()
  })
}
</script>

<style scoped>
.lm-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0,0,0,0.55);
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
  backdrop-filter: blur(2px);
}

.lm-card {
  position: relative;
  width: 100%; max-width: 420px;
  background: #fff;
  border-radius: 1rem;
  padding: 2.25rem 2rem 2rem;
  box-shadow: 0 8px 40px rgba(0,0,0,0.18);
}

.lm-close {
  position: absolute; top: 1rem; right: 1rem;
  background: none; border: none; cursor: pointer;
  color: #9ca3af; padding: 0.25rem;
  display: flex; align-items: center; justify-content: center;
  border-radius: 0.375rem;
  transition: color 0.15s, background 0.15s;
}
.lm-close:hover { color: #374151; background: #f3f4f6; }
.lm-close svg   { width: 18px; height: 18px; }

.lm-header {
  text-align: center; margin-bottom: 1.75rem;
}
.lm-logo {
  width: 44px; height: 44px; margin: 0 auto 0.875rem;
}
.lm-header h2 {
  font-size: 1.2rem; font-weight: 700; color: #1c1c1c; margin: 0 0 0.25rem;
}
.lm-subtitle {
  font-size: 0.8rem; color: #6b7280; margin: 0;
}

/* ───── Alert Banner ─────────────────────────────────────────────────── */
.lm-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-left: 4px solid #dc2626;
  border-radius: 0.5rem;
  padding: 0.75rem 0.875rem;
  margin-bottom: 1.125rem;
  position: relative;
}
.lm-alert-icon {
  width: 18px; height: 18px;
  color: #dc2626;
  flex-shrink: 0;
  margin-top: 0.1rem;
}
.lm-alert-body { flex: 1; min-width: 0; }
.lm-alert-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #991b1b;
  margin: 0 0 0.25rem;
}
.lm-alert-list {
  margin: 0;
  padding-left: 1rem;
  list-style: disc;
}
.lm-alert-list li {
  font-size: 0.8rem;
  color: #b91c1c;
  line-height: 1.5;
}
.lm-alert-close {
  background: none; border: none; cursor: pointer;
  color: #ef4444; padding: 0.15rem;
  display: flex; flex-shrink: 0;
  border-radius: 0.25rem;
  transition: color 0.15s, background 0.15s;
}
.lm-alert-close:hover { color: #991b1b; background: #fee2e2; }
.lm-alert-close svg { width: 14px; height: 14px; }

/* Alert transition */
.alert-enter-active { transition: all 0.25s ease; }
.alert-leave-active { transition: all 0.2s ease; }
.alert-enter-from   { opacity: 0; transform: translateY(-6px); }
.alert-leave-to     { opacity: 0; transform: translateY(-4px); }
/* ────────────────────────────────────────────────────────────────── */

.lm-group { margin-bottom: 1.125rem; }
.lm-group label {
  display: block; font-size: 0.875rem; font-weight: 500;
  color: #374151; margin-bottom: 0.35rem;
}
.lm-group input {
  width: 100%; padding: 0.7rem 1rem;
  border: 1.5px solid #d1d5db; border-radius: 0.5rem;
  font-size: 0.9375rem; outline: none;
  background: #f9fafb; color: #111827;
  transition: border-color 0.15s;
  box-sizing: border-box;
}
.lm-group input:focus  { border-color: #01696f; background: #fff; }
.lm-group input.error  { border-color: #dc2626; }

.lm-input-wrap { position: relative; }
.lm-input-wrap input { padding-right: 2.8rem; }
.lm-toggle-pw {
  position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer;
  color: #9ca3af; padding: 0.2rem; display: flex;
}
.lm-toggle-pw svg   { width: 17px; height: 17px; }
.lm-toggle-pw:hover { color: #374151; }

.lm-captcha-box { display: flex; gap: 0.625rem; align-items: stretch; }
.lm-captcha-q {
  display: flex; align-items: center; gap: 0.4rem;
  background: #f3f4f6; border: 1.5px solid #d1d5db;
  border-radius: 0.5rem; padding: 0.55rem 0.75rem;
  flex-shrink: 0; user-select: none;
}
.lm-captcha-text {
  font-family: 'Courier New', monospace; font-size: 0.9375rem;
  font-weight: 700; color: #01696f; white-space: nowrap; letter-spacing: 0.06em;
}
.lm-captcha-refresh {
  background: none; border: none; cursor: pointer;
  color: #6b7280; display: flex; padding: 0.15rem;
}
.lm-captcha-refresh:hover { color: #01696f; }
.lm-captcha-refresh svg   { width: 15px; height: 15px; transition: transform 0.4s; }
.lm-captcha-refresh.spinning svg { animation: spin 0.4s ease; }
.lm-captcha-box input { flex: 1; min-width: 0; text-align: center; font-weight: 600; letter-spacing: 0.1em; }

.lm-err { margin-top: 0.3rem; font-size: 0.8rem; color: #dc2626; }

.lm-btn {
  width: 100%; padding: 0.825rem;
  background: #01696f; color: white; border: none;
  border-radius: 0.5rem; font-size: 0.9375rem; font-weight: 600;
  cursor: pointer; transition: background 0.15s;
  display: flex; align-items: center; justify-content: center; min-height: 44px;
  margin-top: 0.5rem;
}
.lm-btn:hover:not(:disabled) { background: #0c4e54; }
.lm-btn:disabled { opacity: 0.55; cursor: not-allowed; }

.lm-spinner {
  width: 17px; height: 17px;
  border: 2.5px solid rgba(255,255,255,0.35);
  border-top-color: white; border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.modal-enter-active, .modal-leave-active { transition: opacity 0.2s ease; }
.modal-enter-active .lm-card, .modal-leave-active .lm-card { transition: transform 0.2s ease, opacity 0.2s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .lm-card, .modal-leave-to .lm-card { transform: scale(0.95) translateY(-10px); opacity: 0; }
</style>
