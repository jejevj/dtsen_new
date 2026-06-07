<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="bg-white p-8 rounded-xl shadow-md w-full max-w-md">
      <h1 class="text-2xl font-bold text-primary mb-6">DTSEN — Login</h1>
      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700">Email</label>
          <input v-model="form.email" type="email" class="mt-1 w-full border rounded-lg p-2" required />
        </div>
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700">Password</label>
          <input v-model="form.password" type="password" class="mt-1 w-full border rounded-lg p-2" required />
        </div>
        <button type="submit" class="w-full bg-primary text-white py-2 rounded-lg hover:opacity-90">
          Masuk
        </button>
        <p v-if="error" class="mt-3 text-sm text-red-500">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const form = reactive({ email: '', password: '' })
const error = ref('')
const router = useRouter()
const authStore = useAuthStore()

async function handleLogin() {
  try {
    await authStore.login(form.email, form.password)
    router.push({ name: 'dashboard' })
  } catch (e) {
    error.value = 'Email atau password salah.'
  }
}
</script>
