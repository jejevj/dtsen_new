<template>
  <div class="otp-page">
    <div class="otp-card">
      <!-- Logo / Header -->
      <div class="otp-header">
        <svg class="logo" aria-label="DTSEN" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect width="40" height="40" rx="8" fill="#01696f"/>
          <path d="M10 20 C10 13 15 10 20 10 C25 10 30 13 30 20 C30 27 25 30 20 30 C15 30 10 27 10 20Z" stroke="white" stroke-width="2" fill="none"/>
          <path d="M16 20 L20 16 L24 20 L20 24 Z" fill="white"/>
        </svg>
        <h1>Verifikasi Dua Langkah</h1>
        <p class="subtitle">Masukkan kode OTP untuk melanjutkan ke dashboard</p>
      </div>

      <!-- Step Progress -->
      <div class="steps">
        <div class="step" :class="{ done: auth.emailOtpVerified, active: !auth.emailOtpVerified }">
          <div class="step-dot">
            <svg v-if="auth.emailOtpVerified" viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>
            <span v-else>1</span>
          </div>
          <div class="step-label">
            <span class="step-title">OTP Email</span>
            <span class="step-desc">Kode dikirim ke email terdaftar</span>
          </div>
        </div>
        <div class="step-connector" :class="{ done: auth.emailOtpVerified }"></div>
        <div class="step" :class="{ done: auth.waOtpVerified, active: auth.emailOtpVerified && !auth.waOtpVerified, locked: !auth.emailOtpVerified }">
          <div class="step-dot">
            <svg v-if="auth.waOtpVerified" viewBox="0 0 16 16" fill="none"><path d="M3 8l3.5 3.5L13 4" stroke="white" stroke-width="2" stroke-linecap="round"/></svg>
            <span v-else>2</span>
          </div>
          <div class="step-label">
            <span class="step-title">OTP WhatsApp</span>
            <span class="step-desc">Kode dikirim via WhatsApp</span>
          </div>
        </div>
      </div>

      <!-- Step 1: Email OTP -->
      <transition name="slide">
        <div v-if="!auth.emailOtpVerified" class="otp-form">
          <div class="form-group">
            <label for="emailOtp">Kode OTP Email</label>
            <div class="otp-input-row">
              <input
                id="emailOtp"
                v-model="emailCode"
                type="text"
                inputmode="numeric"
                maxlength="6"
                placeholder="_ _ _ _ _ _"
                autocomplete="one-time-code"
                :class="{ error: emailError }"
                @keyup.enter="submitEmailOtp"
              />
            </div>
            <p v-if="emailError" class="error-msg">{{ emailError }}</p>
          </div>
          <button class="btn-primary" :disabled="emailCode.length < 6 || emailLoading" @click="submitEmailOtp">
            <span v-if="emailLoading" class="spinner"></span>
            <span v-else>Verifikasi OTP Email</span>
          </button>
          <p class="proto-hint">🔧 Prototype: gunakan kode <strong>845988</strong></p>
        </div>
      </transition>

      <!-- Step 2: WA OTP -->
      <transition name="slide">
        <div v-if="auth.emailOtpVerified && !auth.waOtpVerified" class="otp-form">
          <div class="success-banner">
            <svg viewBox="0 0 20 20" fill="none"><path d="M4 10l4 4 8-8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            OTP Email berhasil diverifikasi
          </div>
          <div class="form-group">
            <label for="waOtp">Kode OTP WhatsApp</label>
            <div class="otp-input-row">
              <input
                id="waOtp"
                v-model="waCode"
                type="text"
                inputmode="numeric"
                maxlength="6"
                placeholder="_ _ _ _ _ _"
                autocomplete="one-time-code"
                :class="{ error: waError }"
                @keyup.enter="submitWaOtp"
              />
            </div>
            <p v-if="waError" class="error-msg">{{ waError }}</p>
          </div>
          <button class="btn-primary" :disabled="waCode.length < 6 || waLoading" @click="submitWaOtp">
            <span v-if="waLoading" class="spinner"></span>
            <span v-else>Verifikasi OTP WhatsApp</span>
          </button>
          <p class="proto-hint">🔧 Prototype: gunakan kode <strong>990087</strong></p>
        </div>
      </transition>

      <!-- Both done → redirecting -->
      <transition name="fade">
        <div v-if="auth.isOtpComplete" class="success-full">
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
        <button class="btn-ghost" @click="handleLogout">Keluar</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth   = useAuthStore()
const router = useRouter()

const emailCode    = ref('')
const waCode       = ref('')
const emailError   = ref('')
const waError      = ref('')
const emailLoading = ref(false)
const waLoading    = ref(false)

function submitEmailOtp() {
  emailError.value   = ''
  emailLoading.value = true
  setTimeout(() => {
    try {
      auth.verifyEmailOtp(emailCode.value)
    } catch (e) {
      emailError.value = e.message
    } finally {
      emailLoading.value = false
    }
  }, 600)
}

function submitWaOtp() {
  waError.value   = ''
  waLoading.value = true
  setTimeout(() => {
    try {
      auth.verifyWaOtp(waCode.value)
    } catch (e) {
      waError.value = e.message
    } finally {
      waLoading.value = false
    }
  }, 600)
}

function handleLogout() {
  auth.logout()
  router.push({ name: 'home' })
}

// Auto-redirect when both OTPs done
watch(() => auth.isOtpComplete, (done) => {
  if (done) {
    setTimeout(() => router.push({ name: 'dashboard' }), 1200)
  }
})
</script>

<style scoped>
.otp-page {
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7f6f2;
  padding: 1.5rem;
}

.otp-card {
  width: 100%;
  max-width: 460px;
  background: #fff;
  border-radius: 1rem;
  padding: 2.5rem 2rem;
  box-shadow: 0 4px 24px oklch(0.2 0.01 80 / 0.10);
}

.otp-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem;
}

.otp-header h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #28251d;
  margin-bottom: 0.25rem;
}

.subtitle {
  font-size: 0.875rem;
  color: #7a7974;
  max-width: 32ch;
  margin: 0 auto;
}

.steps {
  display: flex;
  align-items: flex-start;
  gap: 0;
  margin-bottom: 2rem;
}

.step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.step-connector {
  height: 2px;
  width: 2rem;
  background: #dcd9d5;
  margin-top: 1rem;
  flex-shrink: 0;
  transition: background 0.4s;
}

.step-connector.done {
  background: #01696f;
}

.step-dot {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #dcd9d5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: #7a7974;
  flex-shrink: 0;
  transition: all 0.3s;
}

.step.active .step-dot {
  border-color: #01696f;
  color: #01696f;
  background: #cedcd8;
}

.step.done .step-dot {
  border-color: #01696f;
  background: #01696f;
  color: white;
}

.step.done .step-dot svg {
  width: 16px;
  height: 16px;
}

.step.locked .step-dot {
  opacity: 0.4;
}

.step-label {
  display: flex;
  flex-direction: column;
}

.step-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #28251d;
}

.step-desc {
  font-size: 0.75rem;
  color: #7a7974;
}

.step.locked .step-title,
.step.locked .step-desc {
  opacity: 0.5;
}

.otp-form {
  margin-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #28251d;
  margin-bottom: 0.5rem;
}

.otp-input-row input {
  width: 100%;
  padding: 0.875rem 1rem;
  border: 1.5px solid #d4d1ca;
  border-radius: 0.5rem;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.5rem;
  text-align: center;
  outline: none;
  transition: border-color 0.18s;
  color: #28251d;
  background: #f9f8f5;
}

.otp-input-row input:focus {
  border-color: #01696f;
  background: #fff;
}

.otp-input-row input.error {
  border-color: #a12c7b;
}

.error-msg {
  margin-top: 0.4rem;
  font-size: 0.8125rem;
  color: #a12c7b;
}

.success-banner {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #d4dfcc;
  color: #1e3f0a;
  border-radius: 0.5rem;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.success-banner svg {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: #437a22;
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
  gap: 0.5rem;
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
  margin-top: 0.75rem;
  font-size: 0.8125rem;
  color: #7a7974;
  text-align: center;
}

.proto-hint strong {
  color: #01696f;
  font-family: monospace;
  font-size: 1rem;
}

.success-full {
  text-align: center;
  padding: 1.5rem 0;
}

.checkmark svg {
  width: 64px;
  height: 64px;
  margin: 0 auto 1rem;
}

.success-full h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #28251d;
  margin-bottom: 0.25rem;
}

.success-full p {
  color: #7a7974;
  font-size: 0.875rem;
}

.otp-footer {
  margin-top: 1.5rem;
  text-align: center;
}

.btn-ghost {
  background: none;
  border: none;
  font-size: 0.875rem;
  color: #7a7974;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  transition: color 0.18s;
}

.btn-ghost:hover {
  color: #28251d;
}

.slide-enter-active, .slide-leave-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
.slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
