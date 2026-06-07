<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <svg class="logo" aria-label="DTSEN" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="40" height="40" rx="8" fill="#01696f"/>
          <path d="M10 20 C10 13 15 10 20 10 C25 10 30 13 30 20 C30 27 25 30 20 30 C15 30 10 27 10 20Z" stroke="white" stroke-width="2" fill="none"/>
          <path d="M16 20 L20 16 L24 20 L20 24 Z" fill="white"/>
        </svg>
        <h1>Masuk ke DTSEN</h1>
        <p class="subtitle">Sistem Data Terpadu Sosial Ekonomi Nasional</p>
      </div>

      <form @submit.prevent="handleLogin" novalidate>
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            placeholder="nama@instansi.go.id"
            :class="{ error: errors.email }"
            autocomplete="username"
          />
          <p v-if="errors.email" class="error-msg">{{ errors.email }}</p>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <div class="input-with-toggle">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Masukkan password"
              :class="{ error: errors.password }"
              autocomplete="current-password"
            />
            <button type="button" class="toggle-pw" @click="showPassword = !showPassword" :aria-label="showPassword ? 'Sembunyikan password' : 'Tampilkan password'">
              <svg v-if="!showPassword" viewBox="0 0 20 20" fill="none"><path d="M1 10s3-7 9-7 9 7 9 7-3 7-9 7-9-7-9-7z" stroke="currentColor" stroke-width="1.5"/><circle cx="10" cy="10" r="3" stroke="currentColor" stroke-width="1.5"/></svg>
              <svg v-else viewBox="0 0 20 20" fill="none"><path d="M2 2l16 16M7.5 7.6A3 3 0 0013 13M5 5.2C2.9 6.8 1 10 1 10s3 7 9 7a9 9 0 004.8-1.4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M11.5 4.2A9 9 0 0119 10s-.8 2-2.4 3.8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
            </button>
          </div>
          <p v-if="errors.password" class="error-msg">{{ errors.password }}</p>
        </div>

        <!-- CAPTCHA -->
        <div class="form-group">
          <label for="captcha">Verifikasi Keamanan</label>
          <div class="captcha-box">
            <div class="captcha-question">
              <span class="captcha-text">{{ captcha.question }}</span>
              <button type="button" class="captcha-refresh" @click="refreshCaptcha" aria-label="Refresh CAPTCHA">
                <svg viewBox="0 0 20 20" fill="none" :class="{ spinning: captchaRefreshing }">
                  <path d="M4 4a7 7 0 1 1 0 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                  <path d="M4 1v4h4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
            <input
              id="captcha"
              v-model="captchaAnswer"
              type="text"
              inputmode="numeric"
              placeholder="Jawaban"
              :class="{ error: errors.captcha }"
              autocomplete="off"
              maxlength="4"
            />
          </div>
          <p v-if="errors.captcha" class="error-msg">{{ errors.captcha }}</p>
        </div>

        <p v-if="errors.global" class="error-msg global-error">{{ errors.global }}</p>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Masuk</span>
        </button>
      </form>

      <p class="proto-hint">🔧 Prototype: gunakan email &amp; password apapun</p>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth   = useAuthStore()
const router = useRouter()

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '', captcha: '', global: '' })
const loading      = ref(false)
const showPassword = ref(false)
const captchaAnswer    = ref('')
const captchaRefreshing = ref(false)

// ── CAPTCHA helpers ──────────────────────────────────────────────────────────
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
  errors.captcha = ''
  setTimeout(() => { captchaRefreshing.value = false }, 400)
}
// ─────────────────────────────────────────────────────────────────────────────

function validate() {
  errors.email = errors.password = errors.captcha = errors.global = ''
  if (!form.email)    errors.email    = 'Email wajib diisi.'
  if (!form.password) errors.password = 'Password wajib diisi.'
  if (!captchaAnswer.value.trim()) {
    errors.captcha = 'Jawaban CAPTCHA wajib diisi.'
  } else if (captchaAnswer.value.trim() !== captcha.answer) {
    errors.captcha = 'Jawaban CAPTCHA salah. Silakan coba lagi.'
    // auto-refresh captcha on wrong answer
    refreshCaptcha()
  }
  return !errors.email && !errors.password && !errors.captcha
}

async function handleLogin() {
  if (!validate()) return
  loading.value = true
  await new Promise(r => setTimeout(r, 700))
  try {
    auth.login(form.email, form.password)
    // refresh captcha so it cannot be reused
    refreshCaptcha()
    router.push({ name: 'verify-otp' })
  } catch (e) {
    errors.global = e.message
    refreshCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7f6f2;
  padding: 1.5rem;
}

.login-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 1rem;
  padding: 2.5rem 2rem;
  box-shadow: 0 4px 24px oklch(0.2 0.01 80 / 0.10);
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem;
}

.login-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #28251d;
  margin-bottom: 0.25rem;
}

.subtitle {
  font-size: 0.8125rem;
  color: #7a7974;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #28251d;
  margin-bottom: 0.4rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1.5px solid #d4d1ca;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  outline: none;
  background: #f9f8f5;
  color: #28251d;
  transition: border-color 0.18s;
}

.form-group input:focus {
  border-color: #01696f;
  background: #fff;
}

.form-group input.error {
  border-color: #a12c7b;
}

.input-with-toggle {
  position: relative;
}

.input-with-toggle input {
  padding-right: 3rem;
}

.toggle-pw {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #7a7974;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-pw svg {
  width: 18px;
  height: 18px;
}

.toggle-pw:hover { color: #28251d; }

/* CAPTCHA */
.captcha-box {
  display: flex;
  gap: 0.75rem;
  align-items: stretch;
}

.captcha-question {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #f3f0ec;
  border: 1.5px solid #d4d1ca;
  border-radius: 0.5rem;
  padding: 0.6rem 0.875rem;
  flex-shrink: 0;
  user-select: none;
}

.captcha-text {
  font-family: 'Courier New', Courier, monospace;
  font-size: 1rem;
  font-weight: 700;
  color: #01696f;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

.captcha-refresh {
  background: none;
  border: none;
  padding: 0.2rem;
  cursor: pointer;
  color: #7a7974;
  display: flex;
  align-items: center;
}

.captcha-refresh:hover { color: #01696f; }

.captcha-refresh svg {
  width: 16px;
  height: 16px;
  transition: transform 0.4s ease;
}

.captcha-refresh svg.spinning {
  animation: spin 0.4s ease;
}

.captcha-box input {
  flex: 1;
  min-width: 0;
  text-align: center;
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: 0.1em;
}

.error-msg {
  margin-top: 0.375rem;
  font-size: 0.8125rem;
  color: #a12c7b;
}

.global-error {
  text-align: center;
  margin-bottom: 0.75rem;
}

.btn-primary {
  width: 100%;
  padding: 0.875rem;
  background: #01696f;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.18s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
}

.btn-primary:hover:not(:disabled) {
  background: #0c4e54;
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2.5px solid rgba(255,255,255,0.4);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.proto-hint {
  margin-top: 1.25rem;
  font-size: 0.8125rem;
  color: #7a7974;
  text-align: center;
}
</style>
