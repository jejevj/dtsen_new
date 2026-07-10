<template>
  <div class="otp-page">
    <div class="otp-card">

      <div class="otp-header">
        <svg class="logo" viewBox="0 0 40 40" fill="none">
          <rect width="40" height="40" rx="8" fill="#01696f"/>
          <path d="M10 20 C10 13 15 10 20 10 C25 10 30 13 30 20 C30 27 25 30 20 30 C15 30 10 27 10 20Z"
            stroke="white" stroke-width="2" fill="none"/>
          <path d="M16 20 L20 16 L24 20 L20 24 Z" fill="white"/>
        </svg>
        <h1>Verifikasi OTP</h1>
        <p class="subtitle">
          Kode OTP dikirim ke
          <strong>{{ maskedEmail }}</strong>
        </p>
      </div>

      <!-- Form OTP -->
      <div v-if="!verified" class="otp-form">
        <div class="form-group">
          <label for="otpCode">Kode OTP (6 digit)</label>
          <input
            id="otpCode"
            v-model="code"
            type="text"
            inputmode="numeric"
            maxlength="6"
            placeholder="_ _ _ _ _ _"
            autocomplete="one-time-code"
            :class="{ error: otpError }"
            :disabled="loading"
            @keyup.enter="submitOtp"
            ref="otpInput"
          />
          <p v-if="otpError" class="error-msg">{{ otpError }}</p>
        </div>

        <!-- Countdown -->
        <p class="countdown" :class="{ expired: countdown === 0 }">
          <template v-if="countdown > 0">
            ⏱ Kode berlaku {{ mmss }}
          </template>
          <template v-else>
            ⚠️ Kode sudah kadaluarsa.
          </template>
        </p>

        <button class="btn-primary" :disabled="code.length < 6 || loading || countdown === 0" @click="submitOtp">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Verifikasi</span>
        </button>

        <!-- Resend -->
        <div class="resend-row">
          <span class="resend-label">Tidak menerima kode?</span>
          <button
            class="btn-resend"
            :disabled="resendCooldown > 0 || resending"
            @click="handleResend"
          >
            <span v-if="resending">Mengirim…</span>
            <span v-else-if="resendCooldown > 0">Kirim ulang ({{ resendCooldown }}s)</span>
            <span v-else>Kirim ulang</span>
          </button>
        </div>
      </div>

      <!-- Berhasil -->
      <div v-else class="success-full">
        <div class="checkmark">
          <svg viewBox="0 0 52 52" fill="none">
            <circle cx="26" cy="26" r="24" stroke="#01696f" stroke-width="3"/>
            <path d="M14 26l8 8 16-16" stroke="#01696f" stroke-width="3" stroke-linecap="round"/>
          </svg>
        </div>
        <h2>Verifikasi Berhasil</h2>
        <p>Mengalihkan ke dashboard…</p>
      </div>

      <div class="otp-footer">
        <button class="btn-ghost" @click="handleCancel">Batalkan &amp; Keluar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth   = useAuthStore()
const router = useRouter()

const code      = ref('')
const otpError  = ref('')
const loading   = ref(false)
const verified  = ref(false)
const resending = ref(false)
const otpInput  = ref(null)

// Redirect ke home jika tidak ada pending OTP
onMounted(async () => {
  if (!auth.hasPendingOtp) {
    router.replace({ name: 'home' })
    return
  }
  await nextTick()
  otpInput.value?.focus()
  startCountdown()
  startResendCooldown()
})

// Email hint
const maskedEmail = computed(() => auth.pendingUserHint?.email_masked || 'email terdaftar')

// ── Countdown 10 menit ───────────────────────────────────────────────────────
const OTP_TTL  = 10 * 60   // 10 menit
const countdown     = ref(OTP_TTL)
const resendCooldown = ref(60)
let countdownTimer:  ReturnType<typeof setInterval> | null = null
let resendTimer:     ReturnType<typeof setInterval> | null = null

function startCountdown() {
  countdown.value = OTP_TTL
  countdownTimer  = setInterval(() => {
    if (countdown.value > 0) countdown.value--
    else clearInterval(countdownTimer!)
  }, 1000)
}

function startResendCooldown() {
  resendCooldown.value = 60
  resendTimer = setInterval(() => {
    if (resendCooldown.value > 0) resendCooldown.value--
    else clearInterval(resendTimer!)
  }, 1000)
}

const mmss = computed(() => {
  const m = Math.floor(countdown.value / 60).toString().padStart(2, '0')
  const s = (countdown.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

onUnmounted(() => {
  clearInterval(countdownTimer!)
  clearInterval(resendTimer!)
})
// ─────────────────────────────────────────────────────────────────────────────

async function submitOtp() {
  otpError.value = ''
  loading.value  = true
  try {
    await auth.verifyEmailOtp(code.value)
    verified.value = true
    setTimeout(() => router.push({ name: 'dashboard' }), 1200)
  } catch (e) {
    otpError.value = e.message
    code.value     = ''
    otpInput.value?.focus()
  } finally {
    loading.value = false
  }
}

async function handleResend() {
  resending.value = true
  otpError.value  = ''
  try {
    await auth.resendOtp()
    startCountdown()
    startResendCooldown()
    code.value = ''
  } catch (e) {
    otpError.value = 'Gagal mengirim ulang OTP. Coba lagi.'
  } finally {
    resending.value = false
  }
}

function handleCancel() {
  auth.logout()
  router.push({ name: 'home' })
}
</script>

<style scoped>
.otp-page {
  min-height: 100dvh;
  display: flex; align-items: center; justify-content: center;
  background: #f7f6f2; padding: 1.5rem;
}
.otp-card {
  width: 100%; max-width: 420px;
  background: #fff; border-radius: 1rem;
  padding: 2.5rem 2rem;
  box-shadow: 0 4px 24px oklch(0.2 0.01 80 / 0.10);
}
.otp-header { text-align: center; margin-bottom: 2rem; }
.logo { width: 48px; height: 48px; margin: 0 auto 1rem; }
.otp-header h1 { font-size: 1.25rem; font-weight: 700; color: #28251d; margin: 0 0 0.25rem; }
.subtitle { font-size: 0.875rem; color: #7a7974; margin: 0; }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-size: 0.875rem; font-weight: 500; color: #28251d; margin-bottom: 0.5rem; }
.form-group input {
  width: 100%; padding: 0.875rem 1rem;
  border: 1.5px solid #d4d1ca; border-radius: 0.5rem;
  font-size: 1.5rem; font-weight: 700; letter-spacing: 0.5rem; text-align: center;
  outline: none; background: #f9f8f5; color: #28251d;
  transition: border-color 0.18s; box-sizing: border-box;
}
.form-group input:focus  { border-color: #01696f; background: #fff; }
.form-group input.error  { border-color: #dc2626; }
.form-group input:disabled { opacity: 0.6; }
.error-msg { margin-top: 0.4rem; font-size: 0.8125rem; color: #dc2626; }

.countdown {
  font-size: 0.8125rem; color: #01696f; text-align: center;
  margin: 0.5rem 0 1rem; font-weight: 500;
}
.countdown.expired { color: #dc2626; }

.btn-primary {
  width: 100%; padding: 0.875rem;
  background: #01696f; color: white; border: none;
  border-radius: 0.5rem; font-size: 0.9375rem; font-weight: 600;
  cursor: pointer; transition: background 0.18s;
  display: flex; align-items: center; justify-content: center;
  gap: 0.5rem; min-height: 44px;
}
.btn-primary:hover:not(:disabled) { background: #0c4e54; }
.btn-primary:disabled { opacity: 0.55; cursor: not-allowed; }

.resend-row {
  display: flex; align-items: center; justify-content: center;
  gap: 0.5rem; margin-top: 1rem;
}
.resend-label { font-size: 0.8125rem; color: #7a7974; }
.btn-resend {
  background: none; border: none; font-size: 0.8125rem;
  color: #01696f; font-weight: 600; cursor: pointer;
  padding: 0.25rem 0.5rem; border-radius: 0.25rem;
  transition: background 0.15s;
}
.btn-resend:hover:not(:disabled) { background: #f0fdf4; }
.btn-resend:disabled { color: #9ca3af; cursor: not-allowed; }

.spinner {
  width: 18px; height: 18px;
  border: 2.5px solid rgba(255,255,255,0.4);
  border-top-color: white; border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.success-full { text-align: center; padding: 1.5rem 0; }
.checkmark svg { width: 64px; height: 64px; margin: 0 auto 1rem; display: block; }
.success-full h2 { font-size: 1.25rem; font-weight: 700; color: #28251d; margin: 0 0 0.25rem; }
.success-full p  { color: #7a7974; font-size: 0.875rem; margin: 0; }

.otp-footer { margin-top: 1.5rem; text-align: center; }
.btn-ghost {
  background: none; border: none; font-size: 0.875rem;
  color: #7a7974; cursor: pointer; padding: 0.5rem 1rem;
  border-radius: 0.375rem; transition: color 0.18s;
}
.btn-ghost:hover { color: #28251d; }
</style>
