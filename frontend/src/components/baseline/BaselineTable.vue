<template>
  <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">

    <!-- Toolbar -->
    <div class="flex items-center justify-between gap-3 px-5 py-3 border-b border-slate-100">
      <div class="flex items-center gap-2">
        <i class="pi pi-database text-slate-400"></i>
        <span class="text-sm font-semibold text-slate-700">
          {{ title }}{{ meta.label && meta.label !== 'Keluarga' ? ' · ' + meta.label : '' }}
        </span>
        <span
          v-if="meta.totalItems > 0"
          class="ml-1 px-2 py-0.5 bg-primary-50 text-primary-700 border border-primary-200 text-xs font-semibold rounded-full"
        >{{ meta.totalItems.toLocaleString('id-ID') }} total</span>
      </div>
    </div>

    <!-- States -->
    <div v-if="loading" class="flex justify-center items-center py-16 text-slate-400">
      <i class="pi pi-spin pi-spinner mr-2"></i> Memuat data…
    </div>
    <div v-else-if="error" class="py-12 text-center text-red-500 text-sm">
      <i class="pi pi-exclamation-circle text-2xl mb-2 block"></i>{{ error }}
    </div>
    <div v-else-if="rows.length === 0" class="py-20 text-center text-slate-400 text-sm">
      <i class="pi pi-inbox text-4xl mb-3 block opacity-30"></i>{{ emptyHint }}
    </div>

    <!-- Tabel -->
    <div v-else class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          <tr>
            <th class="px-4 py-3 text-left whitespace-nowrap">No</th>
            <th v-for="col in columns" :key="col" class="px-4 py-3 text-left whitespace-nowrap">
              {{ formatColLabel(col) }}
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr
            v-for="(row, i) in rows" :key="i"
            class="hover:bg-slate-50 transition-colors"
          >
            <td class="px-4 py-2.5 text-slate-400 text-xs">
              {{ (meta.currentPage - 1) * meta.limit + i + 1 }}
            </td>
            <td
              v-for="col in columns" :key="col"
              class="px-4 py-2.5 text-slate-700 max-w-[220px] truncate"
              :title="String(row[col] ?? '')"
            >{{ row[col] ?? '-' }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="rows.length > 0" class="flex items-center justify-between px-5 py-3 border-t border-slate-100">
      <span class="text-xs text-slate-400">
        Halaman {{ meta.currentPage }} dari {{ meta.totalPages.toLocaleString('id-ID') }}
        &middot; {{ meta.totalItems.toLocaleString('id-ID') }} data
      </span>
      <div class="flex gap-1">
        <Button
          icon="pi pi-angle-left" text rounded size="small"
          :disabled="!meta.hasPreviousPage || historyStack.length === 0"
          @click="$emit('prev')"
        />
        <Button
          icon="pi pi-angle-right" text rounded size="small"
          :disabled="!meta.hasNextPage"
          @click="$emit('next')"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button'

defineProps({
  loading:      { type: Boolean, default: false },
  error:        { type: String,  default: '' },
  rows:         { type: Array,   default: () => [] },
  columns:      { type: Array,   default: () => [] },
  meta:         { type: Object,  default: () => ({}) },
  historyStack: { type: Array,   default: () => [] },
  emptyHint:    { type: String,  default: 'Tidak ada data.' },
  title:        { type: String,  default: 'Data' },
})
defineEmits(['next', 'prev'])

function formatColLabel(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}
</script>
