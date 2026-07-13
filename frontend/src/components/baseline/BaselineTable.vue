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
            <th v-for="col in displayColumns" :key="col" class="px-4 py-3 text-left whitespace-nowrap">
              {{ formatColLabel(col) }}
            </th>
            <th class="px-4 py-3 text-center whitespace-nowrap">Aksi</th>
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
              v-for="col in displayColumns" :key="col"
              class="px-4 py-2.5 text-slate-700 max-w-[220px] truncate"
              :title="displayValue(col, row[col])"
            >
              <!-- Badge untuk jenis_kelamin -->
              <template v-if="col === 'jenis_kelamin'">
                <span
                  :class="[
                    'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold',
                    genderClass(row[col])
                  ]"
                >
                  <i :class="genderIcon(row[col])"></i>
                  {{ displayValue(col, row[col]) }}
                </span>
              </template>

              <!-- Nilai biasa dengan ref lookup -->
              <template v-else>
                {{ displayValue(col, row[col]) }}
              </template>
            </td>
            <td class="px-4 py-2.5 text-center">
              <Button
                icon="pi pi-eye" size="small" text rounded
                class="text-primary-600 hover:bg-primary-50"
                title="Lihat Detail"
                @click="$emit('detail', row)"
              />
            </td>
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
import { computed, onMounted } from 'vue'
import Button from 'primevue/button'
import { useBaselineRefs } from '@/composables/useBaselineRefs'

const props = defineProps({
  loading:      { type: Boolean, default: false },
  error:        { type: String,  default: '' },
  rows:         { type: Array,   default: () => [] },
  columns:      { type: Array,   default: () => [] },
  meta:         { type: Object,  default: () => ({}) },
  historyStack: { type: Array,   default: () => [] },
  emptyHint:    { type: String,  default: 'Tidak ada data.' },
  title:        { type: String,  default: 'Data' },
  // 'anggota' | 'keluarga'
  type:         { type: String,  default: 'anggota' },
})
defineEmits(['next', 'prev', 'detail'])

// ── Refs resolver
const { ready, init, resolveValue, hasRefs } = useBaselineRefs()
onMounted(() => init())

/**
 * Tampilkan nilai kolom:
 * - Jika ada mapping di tampilan-dtsen → gunakan label
 * - Jika tidak ada → tampilkan raw
 */
function displayValue(col, rawValue) {
  if (!ready.value) {
    // Belum siap: fallback sementara untuk jenis_kelamin
    if (col === 'jenis_kelamin') {
      const fallback = { '1': 'Laki-laki', '2': 'Perempuan' }
      return fallback[String(rawValue)] ?? (rawValue ?? '-')
    }
    return rawValue ?? '-'
  }
  if (hasRefs(col)) {
    return resolveValue(col, rawValue)
  }
  return rawValue ?? '-'
}

// Badge styling jenis_kelamin
function genderClass(val) {
  const v = String(val)
  if (v === '1') return 'bg-blue-50 text-blue-700 border border-blue-200'
  if (v === '2') return 'bg-pink-50 text-pink-700 border border-pink-200'
  return 'bg-slate-100 text-slate-500'
}
function genderIcon(val) {
  const v = String(val)
  if (v === '1') return 'pi pi-mars'
  if (v === '2') return 'pi pi-venus'
  return 'pi pi-question-circle'
}

// Kolom prioritas per tipe tabel
const ANGGOTA_COLS  = ['nama', 'nomor_induk_kependudukan', 'jenis_kelamin', 'kabupaten_kota_ktp', 'provinsi_ktp']
const KELUARGA_COLS = ['nomor_kartu_keluarga', 'nama_anggota_keluarga', 'jumlah_anggota_keluarga', 'kabupaten_kota', 'provinsi']

const displayColumns = computed(() => {
  const preferred = props.type === 'keluarga' ? KELUARGA_COLS : ANGGOTA_COLS
  const available = props.columns
  const picked = preferred.filter(c => available.includes(c))
  if (picked.length < 4) {
    for (const c of available) {
      if (!picked.includes(c)) picked.push(c)
      if (picked.length >= 5) break
    }
  }
  return picked.slice(0, 5)
})

function formatColLabel(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
}
</script>
