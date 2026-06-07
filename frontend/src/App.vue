<template>
  <router-view />
  <LoginModal :visible="loginModal.visible" @close="loginModal.close()" />
</template>

<script setup>
import LoginModal        from '@/components/common/LoginModal.vue'
import { useLoginModalStore } from '@/stores/loginModal'

const loginModal = useLoginModalStore()
</script>

<style>
/* tidak ada global style di sini — semua di assets/main.css */
</style>
