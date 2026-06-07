<template>
  <!-- Backdrop -->
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="visible"
        style="
          position:fixed;inset:0;z-index:9999;
          background:rgba(0,0,0,0.55);backdrop-filter:blur(4px);
          display:flex;align-items:center;justify-content:center;
          padding:16px;
        "
        @click.self="$emit('close')"
      >
        <!-- Modal Card -->
        <div
          style="
            background:white;border-radius:20px;
            width:100%;max-width:420px;
            box-shadow:0 25px 60px rgba(0,0,0,0.25);
            overflow:hidden;
          "
        >
          <!-- Header -->
          <div
            style="
              background:linear-gradient(135deg,#052e16,#166534);
              padding:32px 28px 24px;
              text-align:center;
              position:relative;
            "
          >
            <!-- Close button -->
            <button
              @click="$emit('close')"
              style="
                position:absolute;top:14px;right:14px;
                width:32px;height:32px;border-radius:50%;
                background:rgba(255,255,255,0.15);border:none;
                color:white;cursor:pointer;font-size:14px;
                display:flex;align-items:center;justify-content:center;
                transition:background 0.15s;
              "
              @mouseenter="e=>e.target.style.background='rgba(255,255,255,0.28)'"
              @mouseleave="e=>e.target.style.background='rgba(255,255,255,0.15)'"
            >
              <i class="pi pi-times"></i>
            </button>

            <!-- Logo -->
            <div
              style="
                width:60px;height:60px;border-radius:16px;
                background:rgba(245,158,11,0.2);border:2px solid rgba(245,158,11,0.4);
                display:flex;align-items:center;justify-content:center;
                margin:0 auto 14px;
              "
            >
              <i class="pi pi-chart-bar" style="font-size:24px;color:#fbbf24;"></i>
            </div>
            <h2 style="font-size:1.25rem;font-weight:800;color:white;margin:0 0 4px;">Masuk ke DTSEN</h2>
            <p style="font-size:13px;color:#a7f3d0;margin:0;">Sistem Informasi Zakat dan Wakaf</p>
          </div>

          <!-- Body -->
          <div style="padding:28px;">
            <form @submit.prevent="handleLogin">

              <!-- Identifier -->
              <div style="margin-bottom:16px;">
                <label style="display:block;font-size:13px;font-weight:600;color:#374151;margin-bottom:6px;">
                  <i class="pi pi-user" style="margin-right:4px;color:#6b7280;"></i>
                  Username / NIP / Email
                </label>
                <InputText
                  v-model="form.identifier"
                  placeholder="Masukkan username, NIP, atau email"
                  style="width:100%;"
                  :invalid="!!error"
                  autocomplete="username"
                  required
                />
              </div>

              <!-- Password -->
              <div style="margin-bottom:20px;">
                <label style="display:block;font-size:13px;font-weight:600;color:#374151;margin-bottom:6px;">
                  <i class="pi pi-lock" style="margin-right:4px;color:#6b7280;"></i>
                  Password
                </label>
                <Password
                  v-model="form.password"
                  placeholder="••••••••"
                  :feedback="false"
                  toggle-mask
                  input-class="w-full"
                  style="width:100%;"
                  :invalid="!!error"
                  autocomplete="current-password"
                  required
                />
              </div>

              <!-- Error -->
              <Message
                v-if="error"
                severity="error"
                :closable="false"
                style="margin-bottom:16px;"
              >{{ error }}</Message>

              <!-- Submit -->
              <Button
                type="submit"
                label="Masuk"
                icon="pi pi-sign-in"
                style="width:100%;background:#15803d;border-color:#15803d;font-weight:700;"
                :loading="loading"
              />
            </form>
          </div>

          <!-- Footer note -->
          <div
            style="
              padding:14px 28px 20px;
              text-align:center;
              border-top:1px solid #f1f5f9;
            "
          >
            <p style="font-size:12px;color:#9ca3af;margin:0;">
              <i class="pi pi-shield" style="margin-right:4px;"></i>
              Akses terbatas untuk petugas DTSEN yang berwenang
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Password  from 'primevue/password'
import Button    from 'primevue/button'
import Message   from 'primevue/message'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  visible: { type: Boolean, default: false }
})
const emit = defineEmits(['close'])

const form    = reactive({ identifier: '', password: '' })
const error   = ref('')
const loading = ref(false)
const router  = useRouter()
const authStore = useAuthStore()

// Reset form when modal opens
watch(() => props.visible, (val) => {
  if (val) {
    form.identifier = ''
    form.password   = ''
    error.value     = ''
  }
})

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    // pass identifier as email field — backend menentukan lookup
    await authStore.login(form.identifier, form.password)
    emit('close')
    router.push({ name: 'dashboard' })
  } catch {
    error.value = 'Username/NIP/email atau password salah.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.25s ease;
}
.modal-enter-active .modal-card,
.modal-leave-active .modal-card {
  transition: transform 0.25s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
