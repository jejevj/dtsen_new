<template>
  <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden bt-card">

    <!-- Watermark overlay -->
    <div
      v-if="userIdentifier"
      class="bt-watermark"
      aria-hidden="true"
    >
      <svg class="bt-watermark-svg" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="bt-watermark-pattern" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
            <text x="10" y="40" font-family="Inter, sans-serif" font-size="14" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.11)">DO NOT COPY</text>
            <text x="10" y="70" font-family="Inter, sans-serif" font-size="13" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.09)">{{ userIdentifier }}</text>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#bt-watermark-pattern)" />
      </svg>
    </div>

    <div class="bt-content">
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
                :title="isNikCol(col) ? String(row[col] ?? '') : displayValue(col, row[col])"
              >
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

                <template v-else-if="isNikCol(col)">
                  <span class="font-mono text-xs tracking-wide">{{ maskNik(row[col]) }}</span>
                </template>

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
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import Button from 'primevue/button'
import { useBaselineRefs } from '@/composables/useBaselineRefs'
import { maskNik } from '@/utils/formatter'
import { useWatermark } from '@/composables/useWatermark'

const props = defineProps({
  loading:      { type: Boolean, default: false },
  error:        { type: String,  default: '' },
  rows:         { type: Array,   default: () => [] },
  columns:      { type: Array,   default: () => [] },
  meta:         { type: Object,  default: () => ({}) },
  historyStack: { type: Array,   default: () => [] },
  emptyHint:    { type: String,  default: 'Tidak ada data.' },
  title:        { type: String,  default: 'Data' },
  type:         { type: String,  default: 'anggota' },
})
defineEmits(['next', 'prev', 'detail'])

const { userIdentifier } = useWatermark()

const NIK_COLS = new Set([
  'nomor_induk_kependudukan', 'nik',
  'nomor_kartu_keluarga', 'nkk',
])
function isNikCol(col) { return NIK_COLS.has(col) }

const { ready, init, resolveValue, hasRefs } = useBaselineRefs()
onMounted(() => init())

function displayValue(col, rawValue) {
  if (!ready.value) {
    if (col === 'jenis_kelamin') {
      const fallback = { '1': 'Laki-laki', '2': 'Perempuan' }
      return fallback[String(rawValue)] ?? (rawValue ?? '-')
    }
    return rawValue ?? '-'
  }
  if (hasRefs(col)) return resolveValue(col, rawValue)
  return rawValue ?? '-'
}

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

<style scoped>
.bt-card { position: relative; }
.bt-watermark {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  user-select: none;
}
.bt-watermark-svg {
  display: block;
  width: 100%;
  height: 100%;
}
.bt-content {
  position: relative;
  z-index: 0;
}
</style>
