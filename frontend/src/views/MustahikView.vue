<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:20px;">

      <!-- Header -->
      <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;">
        <div>
          <h2 style="font-size:1.4rem;font-weight:800;color:#1e293b;margin:0 0 2px;">Data Mustahik</h2>
          <p style="font-size:12px;color:#94a3b8;margin:0;">Menampilkan desil 1–4 · {{ filtered.length }} data</p>
        </div>
        <button @click="exportCSV" style="display:flex;align-items:center;gap:6px;padding:8px 16px;border:1px solid #e2e8f0;border-radius:8px;background:white;font-size:13px;font-weight:600;cursor:pointer;color:#374151;">
          <i class="pi pi-download"></i> Export CSV
        </button>
      </div>

      <!-- Filter bar -->
      <div style="background:white;border-radius:14px;border:1px solid #f1f5f9;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;">
          <div>
            <label style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px;">Cari Nama / NIK</label>
            <input v-model="q" type="text" placeholder="Nama atau NIK..." style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;outline:none;"/>
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px;">Desil</label>
            <select v-model="filterDesil" style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;outline:none;background:white;">
              <option value="">Semua Desil</option>
              <option value="1">Desil 1</option>
              <option value="2">Desil 2</option>
              <option value="3">Desil 3</option>
              <option value="4">Desil 4</option>
            </select>
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px;">Jenis Kelamin</label>
            <select v-model="filterGender" style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;outline:none;background:white;">
              <option value="">Semua</option>
              <option value="m">Laki-laki</option>
              <option value="f">Perempuan</option>
            </select>
          </div>
          <div>
            <label style="font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;letter-spacing:.05em;display:block;margin-bottom:4px;">Provinsi</label>
            <select v-model="filterProvinsi" style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;outline:none;background:white;">
              <option value="">Semua</option>
              <option v-for="p in provinsiList" :key="p" :value="p">{{ p }}</option>
            </select>
          </div>
          <div style="display:flex;align-items:flex-end;">
            <button @click="resetFilter" style="width:100%;padding:7px 10px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;background:#f8fafc;cursor:pointer;color:#64748b;font-weight:600;">Reset</button>
          </div>
        </div>
      </div>

      <!-- Table -->
      <div style="background:white;border-radius:14px;border:1px solid #f1f5f9;box-shadow:0 1px 4px rgba(0,0,0,0.04);overflow:hidden;">
        <div style="overflow-x:auto;">
          <table style="width:100%;border-collapse:collapse;font-size:13px;">
            <thead>
              <tr style="background:#f8fafc;border-bottom:1px solid #e2e8f0;">
                <th style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;">#</th>
                <th style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;">Nama</th>
                <th style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;">Desil</th>
                <th style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;">Gender</th>
                <th style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;">Kecamatan</th>
                <th style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;">Provinsi</th>
                <th style="padding:10px 14px;text-align:right;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;">Tanggungan</th>
                <th style="padding:10px 14px;text-align:right;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;white-space:nowrap;">Nominal</th>
                <th style="padding:10px 14px;text-align:center;font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;">Aksi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="paginated.length===0">
                <td colspan="9" style="padding:40px;text-align:center;color:#94a3b8;font-size:13px;">Tidak ada data yang sesuai filter</td>
              </tr>
              <tr
                v-for="(row,i) in paginated" :key="row.id"
                style="border-bottom:1px solid #f1f5f9;transition:background .15s;"
                :style="{ background: hoveredRow===row.id ? '#f8fafc' : 'white' }"
                @mouseenter="hoveredRow=row.id"
                @mouseleave="hoveredRow=null"
              >
                <td style="padding:10px 14px;color:#94a3b8;">{{ (currentPage-1)*perPage+i+1 }}</td>
                <td style="padding:10px 14px;">
                  <router-link :to="`/mustahik/${row.nik_hashed}`" style="color:#2563eb;font-weight:600;text-decoration:none;"
                    @mouseover="e=>e.target.style.textDecoration='underline'"
                    @mouseout="e=>e.target.style.textDecoration='none'">{{ row.nama }}</router-link>
                </td>
                <td style="padding:10px 14px;">
                  <span style="padding:2px 10px;border-radius:99px;font-size:11px;font-weight:700;"
                    :style="{ background:DESIL_COLORS[row.desil].bg, color:DESIL_COLORS[row.desil].text }">
                    Desil {{ row.desil }}
                  </span>
                </td>
                <td style="padding:10px 14px;">
                  <span style="display:inline-flex;align-items:center;gap:4px;font-size:12px;font-weight:600;"
                    :style="{ color: row.jenis_kelamin==='m' ? '#2563eb' : '#db2777' }">
                    <i :class="row.jenis_kelamin==='m' ? 'pi pi-mars' : 'pi pi-venus'" style="font-size:11px;"></i>
                    {{ row.jenis_kelamin==='m' ? 'L' : 'P' }}
                  </span>
                </td>
                <td style="padding:10px 14px;color:#374151;">{{ row.kecamatan }}</td>
                <td style="padding:10px 14px;color:#374151;">{{ row.provinsi }}</td>
                <td style="padding:10px 14px;text-align:right;color:#374151;">{{ row.jumlah_tanggungan }} jiwa</td>
                <td style="padding:10px 14px;text-align:right;font-weight:700;color:#15803d;">{{ formatRupiah(row.nominal) }}</td>
                <td style="padding:10px 14px;text-align:center;">
                  <button @click="$router.push(`/mustahik/${row.nik_hashed}`)"
                    style="padding:5px 12px;border:1px solid #e2e8f0;border-radius:7px;background:white;font-size:12px;cursor:pointer;color:#374151;font-weight:600;display:inline-flex;align-items:center;gap:5px;">
                    <i class="pi pi-eye" style="font-size:11px;"></i> Detail
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div style="padding:12px 16px;border-top:1px solid #f1f5f9;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
          <p style="font-size:12px;color:#64748b;margin:0;">Menampilkan {{ (currentPage-1)*perPage+1 }}–{{ Math.min(currentPage*perPage,filtered.length) }} dari {{ filtered.length }} data</p>
          <div style="display:flex;gap:4px;">
            <button v-for="p in totalPages" :key="p" @click="currentPage=p"
              style="width:30px;height:30px;border-radius:7px;border:1px solid #e2e8f0;font-size:12px;font-weight:600;cursor:pointer;"
              :style="{ background: p===currentPage ? '#2563eb' : 'white', color: p===currentPage ? 'white' : '#374151', borderColor: p===currentPage ? '#2563eb' : '#e2e8f0' }">
              {{ p }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { MOCK_MUSTAHIK, DESIL_COLORS } from '@/data/mockMustahik'
import { formatRupiah } from '@/utils/formatter'

const q              = ref('')
const filterDesil    = ref('')
const filterGender   = ref('')
const filterProvinsi = ref('')
const hoveredRow     = ref(null)
const currentPage    = ref(1)
const perPage        = 10

const provinsiList = computed(() => [...new Set(MOCK_MUSTAHIK.map(m=>m.provinsi))].sort())

const filtered = computed(() => {
  let data = MOCK_MUSTAHIK
  if (q.value) {
    const s = q.value.toLowerCase()
    data = data.filter(m => m.nama.toLowerCase().includes(s) || m.nik.includes(s))
  }
  if (filterDesil.value)    data = data.filter(m => m.desil === Number(filterDesil.value))
  if (filterGender.value)   data = data.filter(m => m.jenis_kelamin === filterGender.value)
  if (filterProvinsi.value) data = data.filter(m => m.provinsi === filterProvinsi.value)
  return data
})

const totalPages = computed(() => Math.max(1, Math.ceil(filtered.value.length / perPage)))
const paginated  = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filtered.value.slice(start, start + perPage)
})

function resetFilter() {
  q.value = ''; filterDesil.value = ''; filterGender.value = ''; filterProvinsi.value = ''
  currentPage.value = 1
}

function exportCSV() {
  const headers = ['Nama','NIK','Desil','Gender','Kecamatan','Kelurahan','Kab/Kota','Provinsi','Tanggungan','Nominal','Pekerjaan','Status Nikah']
  const rows = filtered.value.map(m => [
    m.nama, m.nik, m.desil,
    m.jenis_kelamin==='m'?'Laki-laki':'Perempuan',
    m.kecamatan, m.kelurahan, m.kab_kota, m.provinsi,
    m.jumlah_tanggungan, m.nominal, m.pekerjaan, m.status_pernikahan
  ])
  const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
  const blob = new Blob([csv], { type:'text/csv;charset=utf-8;' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a'); a.href=url; a.download='mustahik_desil1-4.csv'; a.click()
  URL.revokeObjectURL(url)
}
</script>
