<template>
  <!-- Halaman /login tidak dirender — langsung redirect ke home dan buka modal -->
  <div></div>
</template>

<script setup>
import { onMounted }           from 'vue'
import { useRouter }           from 'vue-router'
import { useLoginModalStore }  from '@/stores/loginModal'
import { useAuthStore }        from '@/stores/auth'

const router     = useRouter()
const loginModal = useLoginModalStore()
const auth       = useAuthStore()

onMounted(() => {
  if (auth.isAuthenticated) {
    router.replace({ name: 'dashboard' })
  } else {
    router.replace({ name: 'home' })
    loginModal.open()
  }
})
</script>
