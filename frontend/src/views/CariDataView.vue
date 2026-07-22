<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:20px;">

      <!-- Header -->
      <div>
        <h2 style="font-size:1.4rem;font-weight:800;color:#1e293b;margin:0 0 4px;">Cari Data</h2>
        <p style="font-size:12px;color:#94a3b8;margin:0;">Pencarian mustahik berdasarkan nama, NIK, kecamatan, atau wilayah</p>
      </div>

      <!-- Search box utama -->
      <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
        <div style="display:flex;gap:10px;">
          <div style="flex:1;position:relative;">
            <i class="pi pi-search" style="position:absolute;left:12px;top:50%;transform:translateY(-50%);color:#94a3b8;font-size:14px;"></i>
            <input
              v-model="searchQuery"
              @keyup.enter="doSearch"
              type="text"
              placeholder="Cari nama, NIK, kecamatan, kab/kota..."
              style="width:100%;padding:10px 12px 10px 36px;border:1.5px solid #e2e8f0;border-radius:10px;font-size:14px;outline:none;"
              @focus="e=>e.target.style.borderColor='#2563eb'"
              @blur="e=>e.target.style.borderColor='#e2e8f0'"
            />
          </div>
          <button @click="doSearch"
            style="padding:10px 24px;background:#2563eb;color:white;border:none;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;white-space:nowrap;transition:background .15s;"
            @mouseenter="e=>e.target.style.background='#1d4ed8'"
            @mouseleave="e=>e.target.style.background='#2563eb'">
            Cari
          </button>
        </div>

        <!-- Advanced filter toggle -->
        <button @click="showAdvanced=!showAdvanced"
          style="margin-top:12px;padding:0;border:none;background:none;font-size:12px;color:#2563eb;cursor:pointer;font-weight:600;display:flex;align-items:center;gap:4px;">
          <i :class="showAdvanced?'pi pi-chevron-up':'pi pi-chevron-down'" style="font-size:10px;"></i>
          {{ showAdvanced ? 'Sembunyikan' : 'Tampilkan' }} Filter Lanjutan
        </button>

        <!-- Advanced filters -->
        <div v-if="showAdvanced" style="margin-top:14px;padding-top:14px;border-top:1px solid #f1f5f9;display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;">
          <div>
            <label style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px;">Desil</label>
            <select v-model="advDesil" style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;outline:none;background:white;">
              <option value="">Semua</option>
              <option value="1">Desil 1 </option>
              <option value="2">Desil 2 </option>
              <option value="3">Desil 3 </option>
              <option value="4">Desil 4 </option>
            </select>
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px;">Jenis Kelamin</label>
            <select v-model="advGender" style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;outline:none;background:white;">
              <option value="">Semua</option>
              <option value="m">Laki-laki</option>
              <option value="f">Perempuan</option>
            </select>
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px;">Provinsi</label>
            <select v-model="advProvinsi" style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;outline:none;background:white;">
              <option value="">Semua</option>
              <option v-for="p in provinsiList" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px;">Status Pernikahan</label>
            <select v-model="advStatus" style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;outline:none;background:white;">
              <option value="">Semua</option>
              <option value="Menikah">Menikah</option>
              <option value="Cerai Mati">Cerai Mati</option>
              <option value="Cerai Hidup">Cerai Hidup</option>
            </select>
          </div>
          <div style="display:flex;align-items:flex-end;">
            <button @click="resetAll" style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;background:#f8fafc;cursor:pointer;color:#64748b;font-weight:600;">Reset Semua</button>
          </div>
        </div>
      </div>

      <!-- Belum search state -->
      <div v-if="!hasSearched" style="text-align:center;padding:60px 20px;background:white;border-radius:14px;border:1px solid #f1f5f9;">
        <i class="pi pi-search" style="font-size:48px;color:#cbd5e1;"></i>
        <p style="font-size:15px;font-weight:600;color:#374151;margin:16px 0 4px;">Mulai Pencarian</p>
        <p style="font-size:13px;color:#94a3b8;margin:0;">Masukkan nama, NIK, atau wilayah lalu tekan tombol Cari</p>
      </div>

      <!-- Hasil kosong -->
      <div v-else-if="results.length===0" style="text-align:center;padding:60px 20px;background:white;border-radius:14px;border:1px solid #f1f5f9;">
        <i class="pi pi-inbox" style="font-size:48px;color:#cbd5e1;"></i>
        <p style="font-size:15px;font-weight:600;color:#374151;margin:16px 0 4px;">Data Tidak Ditemukan</p>
        <p style="font-size:13px;color:#94a3b8;margin:0;">Coba kata kunci lain atau ubah filter</p>
      </div>

      <!-- Hasil pencarian -->
      <div v-else>
        <p style="font-size:12px;color:#64748b;margin:0 0 12px;">Ditemukan <strong>{{ results.length }}</strong> data untuk kata kunci "<em>{{ lastQuery }}</em>"</p>

        <div style="display:flex;flex-direction:column;gap:10px;">
          <div v-for="row in paginatedResults" :key="row.id"
            style="background:white;border-radius:12px;border:1px solid #f1f5f9;padding:16px 20px;box-shadow:0 1px 3px rgba(0,0,0,0.04);display:flex;align-items:center;gap:16px;flex-wrap:wrap;transition:box-shadow .15s;cursor:pointer;"
            @mouseenter="e=>e.currentTarget.style.boxShadow='0 4px 12px rgba(0,0,0,0.08)'"
            @mouseleave="e=>e.currentTarget.style.boxShadow='0 1px 3px rgba(0,0,0,0.04)'"
            @click="$router.push(`/mustahik/${row.nik_hashed}`)">

            <!-- Avatar -->
            <div :style="{ width:'44px', height:'44px', borderRadius:'12px', background:DESIL_COLORS[row.desil].bg, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }">
              <i class="pi pi-user" :style="{ color:DESIL_COLORS[row.desil].text, fontSize:'18px' }"></i>
            </div>

            <!-- Info -->
            <div style="flex:1;min-width:0;">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <p style="font-size:14px;font-weight:700;color:#1e293b;margin:0;">{{ row.nama }}</p>
                <span style="padding:2px 8px;border-radius:99px;font-size:10px;font-weight:700;"
                  :style="{ background:DESIL_COLORS[row.desil].bg, color:DESIL_COLORS[row.desil].text }">Desil {{ row.desil }}</span>
                <span style="font-size:10px;font-weight:600;padding:2px 8px;border-radius:99px;"
                  :style="{ background:row.jenis_kelamin==='m'?'#eff6ff':'#fdf2f8', color:row.jenis_kelamin==='m'?'#2563eb':'#db2777' }">
                  {{ row.jenis_kelamin==='m'?'Laki-laki':'Perempuan' }}
                </span>
              </div>
              <p style="font-size:12px;color:#64748b;margin:3px 0 0;">
                <i class="pi pi-map-marker" style="font-size:10px;margin-right:3px;"></i>
                {{ row.kecamatan }}, {{ row.kab_kota }} · {{ row.provinsi }}
              </p>
              <!-- NIK & No KK masked -->
              <div style="display:flex;gap:16px;margin-top:4px;flex-wrap:wrap;">
                <span v-if="row.nik" style="font-size:11px;color:#94a3b8;display:flex;align-items:center;gap:4px;">
                  <i class="pi pi-id-card" style="font-size:10px;"></i>
                  <span style="font-family:monospace;letter-spacing:.04em;">{{ maskNik(row.nik) }}</span>
                </span>
                <span v-if="row.no_kk || row.kk || row.nomor_kartu_keluarga" style="font-size:11px;color:#94a3b8;display:flex;align-items:center;gap:4px;">
                  <i class="pi pi-home" style="font-size:10px;"></i>
                  <span style="font-family:monospace;letter-spacing:.04em;">{{ maskNik(row.no_kk || row.kk || row.nomor_kartu_keluarga) }}</span>
                </span>
              </div>
            </div>

            <!-- Nominal -->
            <div style="text-align:right;flex-shrink:0;">
              <p style="font-size:13px;font-weight:700;color:#15803d;margin:0;">{{ formatRupiah(row.nominal) }}</p>
              <p style="font-size:11px;color:#94a3b8;margin:2px 0 0;">{{ row.pekerjaan }}</p>
            </div>

            <i class="pi pi-chevron-right" style="color:#cbd5e1;font-size:12px;flex-shrink:0;"></i>
          </div>
        </div>

        <!-- Pagination hasil -->
        <div v-if="totalResPages>1" style="margin-top:14px;display:flex;gap:4px;justify-content:center;">
          <button v-for="p in totalResPages" :key="p" @click="resPage=p"
            style="width:30px;height:30px;border-radius:7px;border:1px solid #e2e8f0;font-size:12px;font-weight:600;cursor:pointer;"
            :style="{ background:p===resPage?'#2563eb':'white', color:p===resPage?'white':'#374151', borderColor:p===resPage?'#2563eb':'#e2e8f0' }">
            {{ p }}
          </button>
        </div>
      </div>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { MOCK_MUSTAHIK, DESIL_COLORS } from '@/data/mockMustahik'
import { formatRupiah, maskNik } from '@/utils/formatter'

const searchQuery  = ref('')
const showAdvanced = ref(false)
const hasSearched  = ref(false)
const lastQuery    = ref('')
const results      = ref([])
const resPage      = ref(1)
const perPage      = 8
const advDesil     = ref('')
const advGender    = ref('')
const advProvinsi  = ref('')
const advStatus    = ref('')

const provinsiList = computed(() => [...new Set(MOCK_MUSTAHIK.map(m=>m.provinsi))].sort())

function doSearch() {
  const q = searchQuery.value.trim().toLowerCase()
  hasSearched.value = true
  lastQuery.value   = searchQuery.value.trim() || '(filter)'
  resPage.value     = 1

  results.value = MOCK_MUSTAHIK.filter(m => {
    const matchQ = !q ||
      m.nama.toLowerCase().includes(q) ||
      m.nik.includes(q) ||
      m.kecamatan.toLowerCase().includes(q) ||
      m.kab_kota.toLowerCase().includes(q) ||
      m.kelurahan.toLowerCase().includes(q) ||
      m.provinsi.toLowerCase().includes(q)
    const matchDesil    = !advDesil.value    || m.desil === Number(advDesil.value)
    const matchGender   = !advGender.value   || m.jenis_kelamin === advGender.value
    const matchProvinsi = !advProvinsi.value || m.provinsi === advProvinsi.value
    const matchStatus   = !advStatus.value   || m.status_pernikahan === advStatus.value
    return matchQ && matchDesil && matchGender && matchProvinsi && matchStatus
  })
}

const totalResPages  = computed(() => Math.max(1, Math.ceil(results.value.length / perPage)))
const paginatedResults = computed(() => {
  const s = (resPage.value-1)*perPage
  return results.value.slice(s, s+perPage)
})

function resetAll() {
  searchQuery.value=''; advDesil.value=''; advGender.value=''; advProvinsi.value=''; advStatus.value=''
  hasSearched.value=false; results.value=[]
}
</script>
