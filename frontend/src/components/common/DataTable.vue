<template>
  <DataTable
    :value="data"
    :loading="loading"
    lazy
    paginator
    :rows="rows"
    :total-records="total"
    :rows-per-page-options="[10, 20, 50]"
    paginator-template="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
    current-page-report-template="Menampilkan {first} - {last} dari {totalRecords} data"
    striped-rows
    responsive-layout="scroll"
    class="p-datatable-sm"
    @page="$emit('page', $event)"
  >
    <template #empty>
      <div class="text-center py-8 text-gray-400">
        <i class="pi pi-inbox text-4xl block mb-2"></i>
        <span>Tidak ada data ditemukan.</span>
      </div>
    </template>
    <template #loading>
      <div class="text-center py-8 text-gray-400">
        <i class="pi pi-spin pi-spinner text-2xl"></i>
      </div>
    </template>
    <slot />
  </DataTable>
</template>

<script setup>
import DataTable from 'primevue/datatable'

defineProps({
  data:    { type: Array,   default: () => [] },
  loading: { type: Boolean, default: false },
  total:   { type: Number,  default: 0 },
  rows:    { type: Number,  default: 20 }
})
defineEmits(['page'])
</script>
