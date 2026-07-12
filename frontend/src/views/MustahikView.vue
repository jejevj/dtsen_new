<template>
  <AppLayout>
    <div class="space-y-5">

      <!-- Header -->
      <div class="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Data Mustahik</h2>
          <p class="text-sm text-slate-500 mt-0.5">Daftar penerima manfaat zakat · Desil 1–4</p>
        </div>
        <Button
          :icon="showFilter ? 'pi pi-filter-slash' : 'pi pi-filter'"
          :label="showFilter ? 'Sembunyikan Filter' : 'Tampilkan Filter'"
          :severity="showFilter ? 'secondary' : 'primary'"
          outlined
          size="small"
          @click="showFilter = !showFilter"
        />
      </div>

      <!-- ===== PANEL FILTER DINAMIS ===== -->
      <transition name="slide-down">
        <div v-if="showFilter" class="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm">

          <!-- Loading state -->
          <div v-if="filterLoading" class="flex items-center gap-2 text-slate-400 text-sm py-2">
            <i class="pi pi-spin pi-spinner"></i> Memuat konfigurasi filter…
          </div>

          <!-- Error state -->
          <div v-else-if="filterError" class="text-sm text-red-500 py-2">
            <i class="pi pi-exclamation-triangle mr-1"></i> {{ filterError }}
          </div>

          <!-- Filter fields -->
          <div v-else-if="filterFields.length" class="space-y-4">
            <p class="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
              Filter Pencarian
            </p>

            <!-- Kelompokkan per field_group -->
            <div
              v-for="(groupFields, groupName) in groupedFilterFields"
              :key="groupName"
              class="space-y-2"
            >
              <p v-if="groupName" class="text-xs font-medium text-slate-400">{{ groupName }}</p>
              <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                <div v-for="field in groupFields" :key="field.field_key">
                  <label class="block text-xs font-medium text-slate-600 mb-1">{{ field.field_label }}</label>

                  <!-- Dropdown jika ada referensi kode (String kode) -->
                  <Select
                    v-if="field.refs && field.refs.length"
                    v-model="activeFilters[field.field_key]"
                    :options="[{ ref_value: '', ref_label: 'Semua' }, ...field.refs]"
                    option-label="ref_label"
                    option-value="ref_value"
                    :placeholder="'Semua ' + field.field_label"
                    class="w-full text-sm"
                    show-clear
                  />

                  <!-- Input angka -->
                  <InputNumber
                    v-else-if="field.field_type === 'Integer' || field.field_type === 'Float'"
                    v-model="activeFilters[field.field_key]"
                    :placeholder="field.field_label"
                    class="w-full"
                    :min-fraction-digits="field.field_type === 'Float' ? 2 : 0"
                    :max-fraction-digits="field.field_type === 'Float' ? 2 : 0"
                  />

                  <!-- Input tanggal -->
                  <DatePicker
                    v-else-if="field.field_type === 'Date'"
                    v-model="activeFilters[field.field_key]"
                    :placeholder="field.field_label"
                    date-format="dd/mm/yy"
                    class="w-full"
                    show-button-bar
                  />

                  <!-- Input teks default -->
                  <InputText
                    v-else
                    v-model="activeFilters[field.field_key]"
                    :placeholder="'Cari ' + field.field_label"
                    class="w-full text-sm"
                  />
                </div>
              </div>
            </div>

            <!-- Tombol aksi filter -->
            <div class="flex gap-2 pt-2 border-t border-slate-100">
              <Button
                label="Terapkan Filter"
                icon="pi pi-search"
                size="small"
                @click="applyFilter"
              />
              <Button
                label="Reset"
                icon="pi pi-times"
                size="small"
                severity="secondary"
                outlined
                @click="resetFilter"
              />
            </div>
          </div>

          <!-- Kosong: belum ada field filter dikonfigurasi -->
          <div v-else class="text-sm text-slate-400 py-2">
            <i class="pi pi-info-circle mr-1"></i>
            Belum ada field filter yang dikonfigurasi di master tampilan.
          </div>
        </div>
      </transition>

      <!-- ===== TABEL DATA MUSTAHIK ===== -->
      <div class="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">

        <!-- Toolbar tabel: search global + info -->
        <div class="flex items-center justify-between gap-3 px-5 py-3 border-b border-slate-100">
          <div class="flex items-center gap-2">
            <i class="pi pi-users text-slate-400"></i>
            <span class="text-sm font-semibold text-slate-700">Daftar Mustahik</span>
            <span
              v-if="Object.values(activeFilters).some(v => v !== '' && v != null)"
              class="ml-1 px-2 py-0.5 bg-primary-100 text-primary-700 text-xs font-semibold rounded-full"
            >Filter aktif</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-slate-400">Cari:</span>
            <InputText
              v-model="globalSearch"
              placeholder="Nama / NIK"
              class="text-sm"
              style="width:200px"
              @keyup.enter="applyFilter"
            />
          </div>
        </div>

        <!-- Loading tabel -->
        <div v-if="tableLoading" class="flex justify-center items-center py-16 text-slate-400">
          <i class="pi pi-spin pi-spinner mr-2"></i> Memuat data…
        </div>

        <!-- Error tabel -->
        <div v-else-if="tableError" class="py-12 text-center text-red-500 text-sm">
          <i class="pi pi-exclamation-circle text-2xl mb-2 block"></i>
          {{ tableError }}
        </div>

        <!-- Placeholder: data belum dimuat (sebelum filter diterapkan pertama kali) -->
        <div v-else-if="!tableFetched" class="py-16 text-center text-slate-400 text-sm">
          <i class="pi pi-filter text-3xl mb-3 block opacity-30"></i>
          Gunakan filter di atas lalu klik <strong>Terapkan Filter</strong> untuk menampilkan data.
        </div>

        <!-- Kosong -->
        <div v-else-if="rows.length === 0" class="py-16 text-center text-slate-400 text-sm">
          <i class="pi pi-inbox text-3xl mb-3 block opacity-30"></i>
          Tidak ada data mustahik yang sesuai filter.
        </div>

        <!-- Tabel -->
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-slate-50 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <tr>
                <th class="px-5 py-3 text-left">No</th>
                <th class="px-5 py-3 text-left">Nama Lengkap</th>
                <th class="px-5 py-3 text-left">NIK</th>
                <th class="px-5 py-3 text-left">Jenis Kelamin</th>
                <th class="px-5 py-3 text-left">Kab/Kota</th>
                <th class="px-5 py-3 text-left">Desil</th>
                <th class="px-5 py-3 text-left">Aksi</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr
                v-for="(row, i) in rows" :key="row.id ?? i"
                class="hover:bg-slate-50 transition-colors"
              >
                <td class="px-5 py-3 text-slate-400">{{ (pagination.page - 1) * pagination.perPage + i + 1 }}</td>
                <td class="px-5 py-3 font-medium text-slate-800">{{ row.nama_lengkap ?? '-' }}</td>
                <td class="px-5 py-3 text-slate-600 font-mono text-xs">{{ row.nik ?? '-' }}</td>
                <td class="px-5 py-3">
                  <span
                    :class="row.jenis_kelamin === 'm'
                      ? 'bg-blue-50 text-blue-700'
                      : 'bg-pink-50 text-pink-700'"
                    class="px-2 py-0.5 rounded-full text-xs font-semibold"
                  >
                    {{ row.jenis_kelamin === 'm' ? 'Laki-laki' : 'Perempuan' }}
                  </span>
                </td>
                <td class="px-5 py-3 text-slate-600">{{ row.kabkota ?? row.kab_kota ?? '-' }}</td>
                <td class="px-5 py-3">
                  <span class="px-2 py-0.5 rounded-full text-xs font-bold bg-green-50 text-green-700">
                    Desil {{ row.desil ?? '-' }}
                  </span>
                </td>
                <td class="px-5 py-3">
                  <Button
                    icon="pi pi-eye"
                    text
                    rounded
                    size="small"
                    class="text-primary-600"
                    @click="$router.push('/mustahik/' + (row.nik_hashed ?? row.nik))"
                    v-tooltip="'Lihat Detail'"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div
          v-if="tableFetched && rows.length > 0"
          class="flex items-center justify-between px-5 py-3 border-t border-slate-100"
        >
          <span class="text-xs text-slate-400">
            Halaman {{ pagination.page }} dari {{ pagination.totalPages }}
            · Total {{ pagination.total.toLocaleString('id-ID') }} data
          </span>
          <div class="flex gap-1">
            <Button
              icon="pi pi-angle-left"
              text rounded size="small"
              :disabled="pagination.page <= 1"
              @click="changePage(pagination.page - 1)"
            />
            <Button
              icon="pi pi-angle-right"
              text rounded size="small"
              :disabled="pagination.page >= pagination.totalPages"
              @click="changePage(pagination.page + 1)"
            />
          </div>
        </div>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import AppLayout   from '@/components/layout/AppLayout.vue'
import Button      from 'primevue/button'
import InputText   from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select      from 'primevue/select'
import DatePicker  from 'primevue/datepicker'
import { fetchFilterFields } from '@/services/tampilanDtsenService'
import apiClient             from '@/services/apiClient'

// ── Filter panel state ────────────────────────────────────────────────────────
const showFilter   = ref(false)
const filterLoading = ref(false)
const filterError   = ref('')
const filterFields  = ref([])      // field yang is_filter=1 dari backend
const activeFilters = reactive({}) // { field_key: value }
const globalSearch  = ref('')

// Kelompokkan field per field_group untuk tampilan lebih rapi
const groupedFilterFields = computed(() => {
  const groups = {}
  for (const f of filterFields.value) {
    const g = f.field_group || ''
    if (!groups[g]) groups[g] = []
    groups[g].push(f)
  }
  return groups
})

async function loadFilterFields() {
  filterLoading.value = true
  filterError.value   = ''
  try {
    const data = await fetchFilterFields()
    filterFields.value = data
    // Inisialisasi activeFilters dengan value kosong
    for (const f of data) {
      if (!(f.field_key in activeFilters)) {
        activeFilters[f.field_key] = ''
      }
    }
  } catch (e) {
    filterError.value = 'Gagal memuat konfigurasi filter. Pastikan koneksi ke server aktif.'
    console.error('[TampilanDtsen] fetchFilterFields error:', e)
  } finally {
    filterLoading.value = false
  }
}

// ── Tabel state ───────────────────────────────────────────────────────────────
const tableLoading = ref(false)
const tableError   = ref('')
const tableFetched = ref(false)
const rows         = ref([])
const pagination   = reactive({
  page:       1,
  perPage:    20,
  total:      0,
  totalPages: 1,
})

async function fetchMustahik(page = 1) {
  tableLoading.value = true
  tableError.value   = ''
  try {
    // Bangun query params: gabungkan activeFilters + globalSearch + pagination
    const params = { page, per_page: pagination.perPage }
    if (globalSearch.value.trim()) params.search = globalSearch.value.trim()
    for (const [k, v] of Object.entries(activeFilters)) {
      if (v !== '' && v != null) params[k] = v
    }

    const res = await apiClient.get('/api/v1/mustahik', { params })
    const d   = res.data

    rows.value         = d.data   ?? d.items ?? []
    pagination.page       = d.page       ?? page
    pagination.total      = d.total      ?? rows.value.length
    pagination.totalPages = d.total_pages ?? d.pages ?? 1
    tableFetched.value = true
  } catch (e) {
    tableError.value = 'Gagal memuat data mustahik: ' + (e?.response?.data?.message ?? e.message)
    console.error('[Mustahik] fetchMustahik error:', e)
  } finally {
    tableLoading.value = false
  }
}

function applyFilter() {
  pagination.page = 1
  fetchMustahik(1)
}

function resetFilter() {
  for (const k of Object.keys(activeFilters)) {
    activeFilters[k] = ''
  }
  globalSearch.value = ''
  tableFetched.value = false
  rows.value         = []
}

function changePage(p) {
  fetchMustahik(p)
}

// ── Init ──────────────────────────────────────────────────────────────────────
onMounted(() => {
  loadFilterFields()
})
</script>

<style scoped>
.slide-down-enter-active { transition: all 0.25s ease; }
.slide-down-enter-from   { opacity: 0; transform: translateY(-8px); }
.slide-down-leave-active { transition: all 0.2s ease; }
.slide-down-leave-to     { opacity: 0; transform: translateY(-6px); }
</style>
