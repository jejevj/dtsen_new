<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-800 to-primary-600">
    <div class="w-full max-w-md px-4">
      <Card class="shadow-2xl">
        <template #header>
          <div class="flex flex-col items-center pt-8 pb-4">
            <i class="pi pi-chart-bar text-5xl text-primary-500 mb-3"></i>
            <h1 class="text-2xl font-bold text-gray-800">DTSEN</h1>
            <p class="text-sm text-gray-500 mt-1">Sistem Informasi Zakat dan Wakaf</p>
          </div>
        </template>
        <template #content>
          <form @submit.prevent="handleLogin" class="space-y-4">
            <div class="flex flex-col gap-1">
              <label class="text-sm font-medium text-gray-700">Email</label>
              <InputText
                v-model="form.email"
                type="email"
                placeholder="admin@dtsen.go.id"
                class="w-full"
                :invalid="!!error"
                required
              />
            </div>
            <div class="flex flex-col gap-1">
              <label class="text-sm font-medium text-gray-700">Password</label>
              <Password
                v-model="form.password"
                placeholder="••••••••"
                :feedback="false"
                toggle-mask
                input-class="w-full"
                class="w-full"
                :invalid="!!error"
                required
              />
            </div>
            <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>
            <Button
              type="submit"
              label="Masuk"
              icon="pi pi-sign-in"
              class="w-full"
              :loading="loading"
            />
          </form>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import Card     from 'primevue/card'
import InputText from 'primevue/inputtext'
import Password  from 'primevue/password'
import Button    from 'primevue/button'
import Message   from 'primevue/message'
import { useAuthStore } from '@/stores/auth'

const form    = reactive({ email: '', password: '' })
const error   = ref('')
const loading = ref(false)
const router  = useRouter()
const authStore = useAuthStore()

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(form.email, form.password)
    router.push({ name: 'dashboard' })
  } catch {
    error.value = 'Email atau password salah.'
  } finally {
    loading.value = false
  }
}
</script>
