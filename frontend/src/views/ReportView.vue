<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">Laporan</h2>
    <!-- Filter + charts (gender, bidang, timeseries, desil) akan ditambahkan di sini -->
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ReportService from '@/services/report'

const genderData = ref(null)
const bidangData = ref([])
</script>
