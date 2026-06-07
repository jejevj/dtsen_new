<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">Detail Mustahik</h2>
    <!-- Detail card mustahik akan ditambahkan di sini -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import MustahikService from '@/services/mustahik'

const route = useRoute()
const detail = ref(null)

onMounted(async () => {
  detail.value = await MustahikService.getDetail(route.params.nikHashed)
})
</script>
