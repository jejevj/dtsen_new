<template>
  <div class="p-6">
    <h2 class="text-2xl font-bold mb-4">Data Mustahik</h2>
    <!-- Filter panel + tabel mustahik akan ditambahkan di sini -->
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usePagination } from '@/composables/usePagination'
import { useFilter } from '@/composables/useFilter'
import MustahikService from '@/services/mustahik'

const { filters, getActiveFilters, resetFilters } = useFilter({ nama: null, jenis_kelamin: null })
const { page, total, loading, load } = usePagination(MustahikService.getList)
const data = ref([])

async function fetchData() {
  data.value = await load(getActiveFilters())
}

onMounted(fetchData)
</script>
