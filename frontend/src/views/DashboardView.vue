<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">Dashboard</h2>
    <!-- Summary cards, charts akan ditambahkan di sini -->
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import ReportService from '@/services/report'

const summary = ref(null)

onMounted(async () => {
  summary.value = await ReportService.getHomeSummary()
})
</script>
