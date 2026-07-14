import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useLoginModalStore = defineStore('loginModal', () => {
  const visible = ref(false)

  function open()  { visible.value = true  }
  function close() { visible.value = false }

  return { visible, open, close }
})
