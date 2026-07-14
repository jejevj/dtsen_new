<template>
  <div class="otp-page">
    <div class="otp-card">

      <!-- Header -->
      <div class="otp-header">
        <svg class="logo" viewBox="0 0 40 40" fill="none">
          <rect width="40" height="40" rx="8" fill="#01696f"/>
          <path d="M10 20 C10 13 15 10 20 10 C25 10 30 13 30 20 C30 27 25 30 20 30 C15 30 10 27 10 20Z"
            stroke="white" stroke-width="2" fill="none"/>
          <path d="M16 20 L20 16 L24 20 L20 24 Z" fill="white"/>
        </svg>
        <h1>Verifikasi Dua Langkah</h1>
      </div>

      <!-- Step indicator -->
      <div class="steps">
        <div class="step" :class="stepClass(1)">
          <div class="step-dot">
            <svg v-if="step > 1" viewBox="0 0 16 16" fill="none">
              <path d="M3 8l3.5 3.5L13 4" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span v-else>1</span>
          </div>
          <div class="step-label">
            <span class="step-title">OTP Email</span>
            <span class="step-desc">{{ auth.pendingUserHint?.email_masked || (step > 1 ? '✓ Terverifikasi' : 'email terdaftar') }}</span>
          </div>
        </div>
        <div class="step-connector" :class="{ done: step > 1 }"></div>
        <div class="step" :class="stepClass(2)">
          <div class="step-dot">
            <svg v-if="step > 2" viewBox="0 0 16 16" fill="none">
              <path d="M3 8l3.5 3.5L13 4" stroke="white" stroke-width="2" stroke-linecap="round"/>
            </svg>
            <span v-else>2</span>
          </div>
          <div class="step-label">
            <span class="step-title">OTP WhatsApp</span>
            <span class="step-desc">{{ step >= 2 ? (auth.pendingWaHint?.phone_masked || 'nomor WA terdaftar') : 'Menunggu step 1' }}</span>
          </div>
        </div>
      </div>

      <!-- Step 1: Email OTP -->
      <transition name="slide">
        <div v-if="step === 1" class="otp-form">
          <p class="step-info">Masukkan kode OTP yang dikirim ke <strong>{{ auth.pendingUserHint?.email_masked || 'email Anda' }}</strong></p>
          <div class="form-group">
            <input
              v-model="code"
              type="text" inputmode="numeric" maxlength="6"
              placeholder="_ _ _ _ _ _"
              autocomplete="one-time-code"
              :class="{ error: otpError }"
              :disabled="loading"
              @keyup.enter="submitEmail"
              ref="otpInput"
            />
            <p v-if="otpError" class="error-msg">{{ otpError }}</p>
          </div>
          <p class="countdown" :class="{ expired: countdown === 0 }">
            <template v-if="countdown > 0">⏱ Berlaku {{ mmss }}</template>
            <template v-else>⚠️ Kode kadaluarsa</template>
          </p>
          <button class="btn-primary" :disabled="code.length < 6 || loading || countdown === 0" @click="submitEmail">
            <span v-if="loading" class="spinner"></span>
            <span v-else>Verifikasi OTP Email</span>
          </button>
          <div class="resend-row">
            <span>Tidak terima kode?</span>
            <button class="btn-resend" :disabled="resendCooldown > 0 || resending" @click="handleResendEmail">
              <span v-if="resending">Mengirim…</span>
              <span v-else-if="resendCooldown > 0">Kirim ulang ({{ resendCooldown }}s)</span>
              <span v-else>Kirim ulang</span>
            </button>
          </div>
        </div>
      </transition>

      <!-- Step 2: WA OTP -->
      <transition name="slide">
        <div v-if="step === 2" class="otp-form">
          <div class="success-banner">
            <svg viewBox="0 0 20 20" fill="none"><path d="M4 10l4 4 8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            OTP Email berhasil diverifikasi
          </div>
          <p class="step-info">Masukkan kode OTP yang dikirim ke WhatsApp <strong>{{ auth.pendingWaHint?.phone_masked || 'nomor Anda' }}</strong></p>
          <div class="form-group">
            <input
              v-model="waCode"
              type="text" inputmode="numeric" maxlength="6"
              placeholder="_ _ _ _ _ _"
              autocomplete="one-time-code"
              :class="{ error: waError }"
              :disabled="loading"
              @keyup.enter="submitWa"
              ref="waInput"
            />
            <p v-if="waError" class="error-msg">{{ waError }}</p>
          </div>
          <p class="countdown" :class="{ expired: waCountdown === 0 }">
            <template v-if="waCountdown > 0">⏱ Berlaku {{ waMmss }}</template>
            <template v-else>⚠️ Kode kadaluarsa</template>
          </p>
          <button class="btn-primary" :disabled="waCode.length < 6 || loading || waCountdown === 0" @click="submitWa">
            <span v-if="loading" class="spinner"></span>
            <span v-else>Verifikasi OTP WhatsApp</span>
          </button>
          <div class="resend-row">
            <span>Tidak terima kode?</span>
            <button class="btn-resend" :disabled="waResendCooldown > 0 || resending" @click="handleResendWa">
              <span v-if="resending">Mengirim…</span>
              <span v-else-if="waResendCooldown > 0">Kirim ulang ({{ waResendCooldown }}s)</span>
              <span v-else>Kirim ulang</span>
            </button>
          </div>
        </div>
      </transition>

      <!-- Selesai -->
      <transition name="fade">
        <div v-if="step === 3" class="success-full">
          <div class="checkmark">
            <svg viewBox="0 0 52 52" fill="none">
              <circle cx="26" cy="26" r="24" stroke="#01696f" stroke-width="3"/>
              <path d="M14 26l8 8 16-16" stroke="#01696f" stroke-width="3" stroke-linecap="round"/>
            </svg>
          </div>
          <h2>Verifikasi Selesai</h2>
          <p>Mengalihkan ke dashboard…</p>
        </div>
      </transition>

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

const step     = ref(1)
const code     = ref('')
const waCode   = ref('')
const otpError = ref('')
const waError  = ref('')
const loading  = ref(false)
const resending = ref(false)
const otpInput = ref(null)
const waInput  = ref(null)

onMounted(async () => {
  if (!auth.hasPendingOtp && !auth.hasPendingWaOtp) {
    router.replace({ name: 'home' })
    return
  }
  // Jika reload saat step 2
  if (!auth.hasPendingOtp && auth.hasPendingWaOtp) {
    step.value = 2
    await nextTick(); waInput.value?.focus()
    startWaCountdown(); startWaResendCooldown()
  } else {
    await nextTick(); otpInput.value?.focus()
    startCountdown(); startResendCooldown()
  }
})

function stepClass(n) {
  if (step.value > n)  return 'done'
  if (step.value === n) return 'active'
  return 'locked'
}

// ── Email countdown ────────────────────────────────────────────────────────
const OTP_TTL       = 10 * 60
const countdown      = ref(OTP_TTL)
const resendCooldown = ref(60)
let countdownTimer  = null
let resendTimer     = null

function startCountdown() {
  if (countdownTimer) clearInterval(countdownTimer)
  countdown.value = OTP_TTL
  countdownTimer  = setInterval(() => {
    if (countdown.value > 0) countdown.value--
    else clearInterval(countdownTimer)
  }, 1000)
}
function startResendCooldown() {
  if (resendTimer) clearInterval(resendTimer)
  resendCooldown.value = 60
  resendTimer = setInterval(() => {
    if (resendCooldown.value > 0) resendCooldown.value--
    else clearInterval(resendTimer)
  }, 1000)
}
const mmss = computed(() => {
  const m = Math.floor(countdown.value / 60).toString().padStart(2, '0')
  const s = (countdown.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

// ── WA countdown ──────────────────────────────────────────────────────────
const waCountdown      = ref(OTP_TTL)
const waResendCooldown = ref(60)
let waCountdownTimer   = null
let waResendTimer      = null

function startWaCountdown() {
  if (waCountdownTimer) clearInterval(waCountdownTimer)
  waCountdown.value = OTP_TTL
  waCountdownTimer  = setInterval(() => {
    if (waCountdown.value > 0) waCountdown.value--
    else clearInterval(waCountdownTimer)
  }, 1000)
}
function startWaResendCooldown() {
  if (waResendTimer) clearInterval(waResendTimer)
  waResendCooldown.value = 60
  waResendTimer = setInterval(() => {
    if (waResendCooldown.value > 0) waResendCooldown.value--
    else clearInterval(waResendTimer)
  }, 1000)
}
const waMmss = computed(() => {
  const m = Math.floor(waCountdown.value / 60).toString().padStart(2, '0')
  const s = (waCountdown.value % 60).toString().padStart(2, '0')
  return `${m}:${s}`
})

onUnmounted(() => {
  clearInterval(countdownTimer); clearInterval(resendTimer)
  clearInterval(waCountdownTimer); clearInterval(waResendTimer)
})

// ── Actions ─────────────────────────────────────────────────────────────────
async function submitEmail() {
  otpError.value = ''; loading.value = true
  try {
    await auth.verifyEmailOtp(code.value)
    step.value = 2
    code.value = ''
    await nextTick()
    waInput.value?.focus()
    startWaCountdown()
    startWaResendCooldown()
  } catch (e) {
    otpError.value = e.message
    code.value = ''; otpInput.value?.focus()
  } finally { loading.value = false }
}

async function submitWa() {
  waError.value = ''; loading.value = true
  try {
    await auth.verifyWaOtp(waCode.value)
    step.value = 3
    setTimeout(() => router.push({ name: 'dashboard' }), 1200)
  } catch (e) {
    waError.value = e.message
    waCode.value = ''; waInput.value?.focus()
  } finally { loading.value = false }
}

async function handleResendEmail() {
  resending.value = true; otpError.value = ''
  try {
    await auth.resendEmailOtp()
    startCountdown(); startResendCooldown()
    code.value = ''
  } catch { otpError.value = 'Gagal mengirim ulang. Coba lagi.' }
  finally { resending.value = false }
}

async function handleResendWa() {
  resending.value = true; waError.value = ''
  try {
    await auth.resendWaOtp()
    startWaCountdown(); startWaResendCooldown()
    waCode.value = ''
  } catch { waError.value = 'Gagal mengirim ulang. Coba lagi.' }
  finally { resending.value = false }
}

function handleCancel() {
  auth.logout()
  router.push({ name: 'home' })
}
</script>

<style scoped>
.otp-page {
  min-height: 100dvh; display: flex; align-items: center; justify-content: center;
  background: #f7f6f2; padding: 1.5rem;
}
.otp-card {
  width: 100%; max-width: 460px; background: #fff;
  border-radius: 1rem; padding: 2.5rem 2rem;
  box-shadow: 0 4px 24px oklch(0.2 0.01 80 / 0.10);
}
.otp-header { text-align: center; margin-bottom: 1.75rem; }
.logo { width: 48px; height: 48px; margin: 0 auto 0.875rem; }
.otp-header h1 { font-size: 1.2rem; font-weight: 700; color: #28251d; margin: 0; }

/* Steps */
.steps { display: flex; align-items: flex-start; margin-bottom: 2rem; }
.step  { display: flex; align-items: center; gap: 0.75rem; flex: 1; }
.step-connector { height: 2px; width: 2rem; background: #dcd9d5; margin-top: 1.1rem; flex-shrink: 0; transition: background .4s; }
.step-connector.done { background: #01696f; }
.step-dot {
  width: 36px; height: 36px; border-radius: 50%; border: 2px solid #dcd9d5;
  display: flex; align-items: center; justify-content: center;
  font-size: .875rem; font-weight: 600; color: #7a7974; flex-shrink: 0; transition: all .3s;
}
.step.active .step-dot { border-color: #01696f; color: #01696f; background: #cedcd8; }
.step.done   .step-dot { border-color: #01696f; background: #01696f; color: white; }
.step.done   .step-dot svg { width: 16px; height: 16px; }
.step.locked .step-dot { opacity: .4; }
.step-label { display: flex; flex-direction: column; }
.step-title { font-size: .875rem; font-weight: 600; color: #28251d; }
.step-desc  { font-size: .75rem; color: #7a7974; }
.step.locked .step-title, .step.locked .step-desc { opacity: .5; }

.step-info { font-size: .875rem; color: #374151; margin: 0 0 1rem; }

.form-group { margin-bottom: .75rem; }
.form-group input {
  width: 100%; padding: .875rem 1rem; border: 1.5px solid #d4d1ca;
  border-radius: .5rem; font-size: 1.5rem; font-weight: 700; letter-spacing: .5rem;
  text-align: center; outline: none; background: #f9f8f5; color: #28251d;
  transition: border-color .18s; box-sizing: border-box;
}
.form-group input:focus   { border-color: #01696f; background: #fff; }
.form-group input.error   { border-color: #dc2626; }
.form-group input:disabled { opacity: .6; }
.error-msg { margin-top: .35rem; font-size: .8125rem; color: #dc2626; }

.countdown { font-size: .8125rem; color: #01696f; text-align: center; margin: 0 0 1rem; font-weight: 500; }
.countdown.expired { color: #dc2626; }

.success-banner {
  display: flex; align-items: center; gap: .5rem;
  background: #d4dfcc; color: #1e3f0a; border-radius: .5rem;
  padding: .625rem 1rem; font-size: .875rem; font-weight: 500; margin-bottom: 1rem;
}
.success-banner svg { width: 18px; height: 18px; flex-shrink: 0; color: #437a22; }

.btn-primary {
  width: 100%; padding: .875rem; background: #01696f; color: white;
  border: none; border-radius: .5rem; font-size: .9375rem; font-weight: 600;
  cursor: pointer; transition: background .18s;
  display: flex; align-items: center; justify-content: center;
  gap: .5rem; min-height: 44px;
}
.btn-primary:hover:not(:disabled) { background: #0c4e54; }
.btn-primary:disabled { opacity: .55; cursor: not-allowed; }

.resend-row { display: flex; align-items: center; justify-content: center; gap: .5rem; margin-top: .875rem; font-size: .8125rem; color: #7a7974; }
.btn-resend { background: none; border: none; font-size: .8125rem; color: #01696f; font-weight: 600; cursor: pointer; padding: .25rem .5rem; border-radius: .25rem; transition: background .15s; }
.btn-resend:hover:not(:disabled) { background: #f0fdf4; }
.btn-resend:disabled { color: #9ca3af; cursor: not-allowed; }

.spinner { width: 18px; height: 18px; border: 2.5px solid rgba(255,255,255,.4); border-top-color: white; border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.success-full { text-align: center; padding: 1.5rem 0; }
.checkmark svg { width: 64px; height: 64px; margin: 0 auto 1rem; display: block; }
.success-full h2 { font-size: 1.25rem; font-weight: 700; color: #28251d; margin: 0 0 .25rem; }
.success-full p  { color: #7a7974; font-size: .875rem; margin: 0; }

.otp-footer { margin-top: 1.5rem; text-align: center; }
.btn-ghost { background: none; border: none; font-size: .875rem; color: #7a7974; cursor: pointer; padding: .5rem 1rem; border-radius: .375rem; transition: color .18s; }
.btn-ghost:hover { color: #28251d; }

.slide-enter-active, .slide-leave-active { transition: all .35s cubic-bezier(.16,1,.3,1); }
.slide-enter-from { opacity: 0; transform: translateY(12px); }
.slide-leave-to   { opacity: 0; transform: translateY(-8px); }
.fade-enter-active, .fade-leave-active { transition: opacity .4s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
