<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:20px;">

      <!-- Header -->
      <div>
        <h2 style="font-size:1.4rem;font-weight:800;color:#1e293b;margin:0 0 4px;">Pemeriksaan DTSEN</h2>
        <p style="font-size:12px;color:#94a3b8;margin:0;">Verifikasi kelayakan penerima manfaat berdasarkan NIK</p>
      </div>

      <!-- Dua card berdampingan -->
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start;">

        <!-- Card 1: Form Input -->
        <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
            <div style="width:36px;height:36px;background:#eff6ff;border-radius:10px;display:flex;align-items:center;justify-content:center;">
              <i class="pi pi-id-card" style="color:#2563eb;font-size:16px;"></i>
            </div>
            <div>
              <p style="font-size:14px;font-weight:700;color:#1e293b;margin:0;">Input Data Pencarian</p>
              <p style="font-size:11px;color:#94a3b8;margin:0;">Masukkan NIK dan kode verifikasi</p>
            </div>
          </div>

          <!-- NIK -->
          <div style="margin-bottom:16px;">
            <label style="display:block;font-size:12px;font-weight:600;color:#475569;margin-bottom:6px;text-transform:uppercase;letter-spacing:.04em;">Nomor Induk Kependudukan (NIK)</label>
            <input
              v-model="nik"
              type="text"
              maxlength="16"
              placeholder="Masukkan 16 digit NIK"
              @input="nik = nik.replace(/\D/g,'')"
              style="width:100%;padding:10px 14px;border:1.5px solid #e2e8f0;border-radius:10px;font-size:14px;outline:none;letter-spacing:.08em;font-family:monospace;"
              :style="{ borderColor: nikError ? '#ef4444' : focused==='nik' ? '#2563eb' : '#e2e8f0' }"
              @focus="focused='nik'"
              @blur="focused=''"
            />
            <p v-if="nikError" style="font-size:11px;color:#ef4444;margin:4px 0 0;">{{ nikError }}</p>
            <p v-else style="font-size:11px;color:#94a3b8;margin:4px 0 0;">{{ nik.length }}/16 digit</p>
          </div>

          <!-- Captcha -->
          <div style="margin-bottom:20px;">
            <label style="display:block;font-size:12px;font-weight:600;color:#475569;margin-bottom:6px;text-transform:uppercase;letter-spacing:.04em;">Kode Verifikasi (Captcha)</label>

            <!-- Captcha display box -->
            <div style="display:flex;gap:10px;margin-bottom:8px;align-items:center;">
              <div style="flex:1;background:#f8fafc;border:1px dashed #cbd5e1;border-radius:10px;padding:10px 16px;text-align:center;position:relative;overflow:hidden;">
                <!-- noise lines -->
                <svg style="position:absolute;inset:0;width:100%;height:100%;" aria-hidden="true">
                  <line v-for="l in captchaLines" :key="l.id"
                    :x1="l.x1+'%'" :y1="l.y1+'%'" :x2="l.x2+'%'" :y2="l.y2+'%'"
                    :stroke="l.color" stroke-width="1" opacity="0.4"/>
                </svg>
                <span style="font-size:22px;font-weight:800;letter-spacing:.25em;color:#1e293b;font-family:'Courier New',monospace;position:relative;z-index:1;">{{ captchaCode }}</span>
              </div>
              <button @click="refreshCaptcha" title="Refresh captcha"
                style="width:40px;height:40px;border:1.5px solid #e2e8f0;border-radius:10px;background:white;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;"
                @mouseenter="e=>e.currentTarget.style.borderColor='#2563eb'"
                @mouseleave="e=>e.currentTarget.style.borderColor='#e2e8f0'">
                <i class="pi pi-refresh" style="color:#64748b;font-size:14px;"></i>
              </button>
            </div>

            <input
              v-model="captchaInput"
              type="text"
              maxlength="6"
              placeholder="Masukkan kode di atas"
              style="width:100%;padding:10px 14px;border:1.5px solid #e2e8f0;border-radius:10px;font-size:14px;outline:none;letter-spacing:.12em;text-transform:uppercase;"
              :style="{ borderColor: captchaError ? '#ef4444' : focused==='captcha' ? '#2563eb' : '#e2e8f0' }"
              @focus="focused='captcha'"
              @blur="focused=''"
            />
            <p v-if="captchaError" style="font-size:11px;color:#ef4444;margin:4px 0 0;">{{ captchaError }}</p>
          </div>

          <!-- Submit button -->
          <button @click="doSearch"
            :disabled="isLoading"
            style="width:100%;padding:12px;background:#2563eb;color:white;border:none;border-radius:10px;font-size:14px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;transition:background .15s;"
            :style="{ background: isLoading ? '#93c5fd' : '#2563eb', cursor: isLoading ? 'not-allowed' : 'pointer' }"
            @mouseenter="e=>{ if(!isLoading) e.currentTarget.style.background='#1d4ed8' }"
            @mouseleave="e=>{ if(!isLoading) e.currentTarget.style.background='#2563eb' }">
            <span v-if="isLoading" style="display:inline-block;width:16px;height:16px;border:2px solid rgba(255,255,255,.4);border-top-color:white;border-radius:50%;animation:spin 0.7s linear infinite;"></span>
            <i v-else class="pi pi-search"></i>
            {{ isLoading ? 'Memeriksa...' : 'Periksa Kelayakan' }}
          </button>
        </div>

        <!-- Card 2: Instruksi -->
        <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,0.04);">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;">
            <div style="width:36px;height:36px;background:#f0fdf4;border-radius:10px;display:flex;align-items:center;justify-content:center;">
              <i class="pi pi-info-circle" style="color:#16a34a;font-size:16px;"></i>
            </div>
            <div>
              <p style="font-size:14px;font-weight:700;color:#1e293b;margin:0;">Panduan Penggunaan</p>
              <p style="font-size:11px;color:#94a3b8;margin:0;">Ikuti langkah berikut untuk memeriksa data</p>
            </div>
          </div>

          <ol style="padding:0;margin:0;list-style:none;display:flex;flex-direction:column;gap:14px;">
            <li v-for="(step, idx) in instructions" :key="idx" style="display:flex;gap:12px;align-items:flex-start;">
              <div style="width:24px;height:24px;border-radius:50%;background:#eff6ff;color:#2563eb;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px;">{{ idx+1 }}</div>
              <div>
                <p style="font-size:13px;font-weight:600;color:#1e293b;margin:0 0 2px;">{{ step.title }}</p>
                <p style="font-size:12px;color:#64748b;margin:0;">{{ step.desc }}</p>
              </div>
            </li>
          </ol>

          <div style="margin-top:20px;padding:14px;background:#fef9c3;border-radius:10px;border:1px solid #fde68a;">
            <p style="font-size:12px;color:#854d0e;margin:0;display:flex;gap:6px;align-items:flex-start;">
              <i class="pi pi-exclamation-triangle" style="flex-shrink:0;margin-top:1px;"></i>
              <span>Data yang ditampilkan bersifat <strong>rahasia</strong>. Hanya petugas berwenang yang boleh mengakses dan menggunakan data ini.</span>
            </p>
          </div>

          <!-- Kondisi hasil -->
          <div style="margin-top:18px;">
            <p style="font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin:0 0 10px;">Kemungkinan Hasil</p>
            <div style="display:flex;flex-direction:column;gap:8px;">
              <div style="display:flex;gap:8px;align-items:center;padding:8px 12px;border-radius:8px;background:#f0fdf4;">
                <i class="pi pi-check-circle" style="color:#16a34a;font-size:14px;flex-shrink:0;"></i>
                <span style="font-size:12px;color:#15803d;font-weight:600;">Data ditemukan &amp; layak (Desil 1–4)</span>
              </div>
              <div style="display:flex;gap:8px;align-items:center;padding:8px 12px;border-radius:8px;background:#fff7ed;">
                <i class="pi pi-exclamation-circle" style="color:#ea580c;font-size:14px;flex-shrink:0;"></i>
                <span style="font-size:12px;color:#c2410c;font-weight:600;">Data ditemukan namun tidak memenuhi syarat desil</span>
              </div>
              <div style="display:flex;gap:8px;align-items:center;padding:8px 12px;border-radius:8px;background:#fef2f2;">
                <i class="pi pi-times-circle" style="color:#dc2626;font-size:14px;flex-shrink:0;"></i>
                <span style="font-size:12px;color:#b91c1c;font-weight:600;">NIK tidak terdaftar dalam sistem DTSEN</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== HASIL PENCARIAN ===== -->

      <!-- Kondisi 1: Data ditemukan, desil 1-4 (LAYAK) -->
      <transition name="slide-up">
      <div v-if="result && result.status === 'found'" style="background:white;border-radius:16px;border:1.5px solid #bbf7d0;padding:28px;box-shadow:0 2px 8px rgba(21,128,61,.08);">
        <!-- Banner layak -->
        <div style="display:flex;align-items:center;gap:12px;padding:14px 18px;background:#f0fdf4;border-radius:12px;margin-bottom:22px;border:1px solid #bbf7d0;">
          <i class="pi pi-check-circle" style="color:#16a34a;font-size:24px;flex-shrink:0;"></i>
          <div>
            <p style="font-size:14px;font-weight:800;color:#15803d;margin:0;">Data Ditemukan — Layak Menerima Manfaat</p>
            <p style="font-size:12px;color:#4ade80;margin:0;">NIK terdaftar dalam Data Terpadu Sosial Ekonomi Nasional (DTSEN) pada desil {{ result.data.desil }}</p>
          </div>
          <span style="margin-left:auto;padding:4px 14px;background:#16a34a;color:white;border-radius:99px;font-size:11px;font-weight:700;white-space:nowrap;">Desil {{ result.data.desil }}</span>
        </div>

        <!-- Detail data -->
        <p style="font-size:12px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.05em;margin:0 0 14px;">Detail Penerima</p>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;">
          <div v-for="field in detailFields" :key="field.key" style="">
            <p style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;letter-spacing:.04em;margin:0 0 3px;">{{ field.label }}</p>
            <p style="font-size:13px;font-weight:700;color:#1e293b;margin:0;">{{ getField(result.data, field.key) }}</p>
          </div>
        </div>

        <div style="margin-top:20px;padding-top:20px;border-top:1px solid #f1f5f9;display:flex;gap:10px;flex-wrap:wrap;">
          <router-link :to="`/mustahik/${result.data.nik_hashed}`"
            style="padding:9px 20px;background:#2563eb;color:white;border-radius:10px;font-size:13px;font-weight:700;text-decoration:none;display:flex;align-items:center;gap:6px;">
            <i class="pi pi-external-link"></i> Lihat Detail Lengkap
          </router-link>
          <button @click="resetSearch"
            style="padding:9px 20px;background:white;border:1.5px solid #e2e8f0;border-radius:10px;font-size:13px;font-weight:600;cursor:pointer;color:#64748b;"
            @mouseenter="e=>e.currentTarget.style.borderColor='#94a3b8'"
            @mouseleave="e=>e.currentTarget.style.borderColor='#e2e8f0'">
            <i class="pi pi-refresh" style="margin-right:4px;"></i> Periksa NIK Lain
          </button>
        </div>
      </div>
      </transition>

      <!-- Kondisi 2: Data ditemukan TAPI bukan desil 1-4 (TIDAK LAYAK) -->
      <transition name="slide-up">
      <div v-if="result && result.status === 'not_eligible'" style="background:white;border-radius:16px;border:1.5px solid #fed7aa;padding:28px;box-shadow:0 2px 8px rgba(234,88,12,.08);">
        <div style="display:flex;align-items:center;gap:12px;padding:14px 18px;background:#fff7ed;border-radius:12px;margin-bottom:22px;border:1px solid #fed7aa;">
          <i class="pi pi-exclamation-circle" style="color:#ea580c;font-size:24px;flex-shrink:0;"></i>
          <div>
            <p style="font-size:14px;font-weight:800;color:#c2410c;margin:0;">Data Ditemukan — Tidak Memenuhi Syarat</p>
            <p style="font-size:12px;color:#fb923c;margin:0;">NIK terdaftar namun termasuk {{ result.data.desil_label }} yang tidak masuk kriteria penerima manfaat (desil 1–4)</p>
          </div>
          <span style="margin-left:auto;padding:4px 14px;background:#ea580c;color:white;border-radius:99px;font-size:11px;font-weight:700;white-space:nowrap;">{{ result.data.desil_label }}</span>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:14px;margin-bottom:20px;">
          <div>
            <p style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;margin:0 0 3px;">Nama</p>
            <p style="font-size:13px;font-weight:700;color:#1e293b;margin:0;">{{ result.data.nama }}</p>
          </div>
          <div>
            <p style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;margin:0 0 3px;">Kategori Kesejahteraan</p>
            <p style="font-size:13px;font-weight:700;color:#c2410c;margin:0;">{{ result.data.desil_label }}</p>
          </div>
          <div>
            <p style="font-size:11px;color:#94a3b8;font-weight:600;text-transform:uppercase;margin:0 0 3px;">Wilayah</p>
            <p style="font-size:13px;font-weight:700;color:#1e293b;margin:0;">{{ result.data.kecamatan }}, {{ result.data.kab_kota }}</p>
          </div>
        </div>

        <div style="padding:12px 16px;background:#fef3c7;border-radius:10px;border:1px solid #fde68a;margin-bottom:20px;">
          <p style="font-size:12px;color:#92400e;margin:0;">
            <i class="pi pi-info-circle" style="margin-right:6px;"></i>
            Penduduk ini tidak termasuk dalam kelompok prioritas (desil 1–4). Bantuan sosial ditargetkan untuk kelompok dengan tingkat kesejahteraan yang lebih rendah.
          </p>
        </div>

        <button @click="resetSearch"
          style="padding:9px 20px;background:white;border:1.5px solid #e2e8f0;border-radius:10px;font-size:13px;font-weight:600;cursor:pointer;color:#64748b;"
          @mouseenter="e=>e.currentTarget.style.borderColor='#94a3b8'"
          @mouseleave="e=>e.currentTarget.style.borderColor='#e2e8f0'">
          <i class="pi pi-refresh" style="margin-right:4px;"></i> Periksa NIK Lain
        </button>
      </div>
      </transition>

      <!-- Kondisi 3: Data tidak ditemukan sama sekali -->
      <transition name="slide-up">
      <div v-if="result && result.status === 'not_found'" style="background:white;border-radius:16px;border:1.5px solid #fecaca;padding:28px;box-shadow:0 2px 8px rgba(220,38,38,.06);">
        <div style="display:flex;align-items:center;gap:12px;padding:14px 18px;background:#fef2f2;border-radius:12px;margin-bottom:20px;border:1px solid #fecaca;">
          <i class="pi pi-times-circle" style="color:#dc2626;font-size:24px;flex-shrink:0;"></i>
          <div>
            <p style="font-size:14px;font-weight:800;color:#b91c1c;margin:0;">NIK Tidak Terdaftar</p>
            <p style="font-size:12px;color:#f87171;margin:0;">NIK <strong style="font-family:monospace;letter-spacing:.08em;">{{ lastNik }}</strong> tidak ditemukan dalam basis data DTSEN</p>
          </div>
        </div>

        <ul style="padding:0;margin:0 0 20px;list-style:none;display:flex;flex-direction:column;gap:8px;">
          <li v-for="tip in notFoundTips" :key="tip" style="display:flex;gap:8px;align-items:flex-start;">
            <i class="pi pi-angle-right" style="color:#94a3b8;font-size:12px;margin-top:2px;flex-shrink:0;"></i>
            <span style="font-size:12px;color:#64748b;">{{ tip }}</span>
          </li>
        </ul>

        <button @click="resetSearch"
          style="padding:9px 20px;background:white;border:1.5px solid #e2e8f0;border-radius:10px;font-size:13px;font-weight:600;cursor:pointer;color:#64748b;"
          @mouseenter="e=>e.currentTarget.style.borderColor='#94a3b8'"
          @mouseleave="e=>e.currentTarget.style.borderColor='#e2e8f0'">
          <i class="pi pi-refresh" style="margin-right:4px;"></i> Coba NIK Lain
        </button>
      </div>
      </transition>

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppLayout from '@/components/layout/AppLayout.vue'
import { MOCK_MUSTAHIK } from '@/data/mockMustahik'
import { formatRupiah } from '@/utils/formatter'

// ===== STATE =====
const nik          = ref('')
const captchaInput = ref('')
const captchaCode  = ref('')
const captchaLines = ref([])
const nikError     = ref('')
const captchaError = ref('')
const isLoading    = ref(false)
const result       = ref(null)
const lastNik      = ref('')
const focused      = ref('')

// ===== CAPTCHA =====
const CAPTCHA_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'

function generateCaptcha() {
  let code = ''
  for (let i = 0; i < 6; i++) {
    code += CAPTCHA_CHARS[Math.floor(Math.random() * CAPTCHA_CHARS.length)]
  }
  captchaCode.value = code
  captchaLines.value = Array.from({ length: 5 }, (_, i) => ({
    id: i,
    x1: Math.random() * 100,
    y1: Math.random() * 100,
    x2: Math.random() * 100,
    y2: Math.random() * 100,
    color: `hsl(${Math.random()*360},50%,50%)`
  }))
}

function refreshCaptcha() {
  generateCaptcha()
  captchaInput.value = ''
  captchaError.value = ''
}

onMounted(() => generateCaptcha())

// ===== SEARCH LOGIC =====
const DESIL_LABELS = {
  1: 'Desil 1 — Sangat Miskin',
  2: 'Desil 2 — Miskin',
  3: 'Desil 3 — Hampir Miskin',
  4: 'Desil 4 — Rentan Miskin',
  5: 'Desil 5 — Menuju Sejahtera',
  6: 'Desil 6',
  7: 'Desil 7',
  8: 'Desil 8',
  9: 'Desil 9',
  10: 'Desil 10 — Sejahtera',
}

// Data tambahan: beberapa NIK desil 5-10 untuk simulasi kondisi 2
const MOCK_NON_ELIGIBLE = [
  { id:101, nik_hashed:'hashne01', nama:'Gunawan Harto',    nik:'3201020101800101', desil:5,  kecamatan:'Bogor Tengah',  kab_kota:'Kota Bogor' },
  { id:102, nik_hashed:'hashne02', nama:'Trisna Dewi',      nik:'3275020101850102', desil:7,  kecamatan:'Ciledug',       kab_kota:'Kota Tangerang' },
  { id:103, nik_hashed:'hashne03', nama:'Hendri Kusuma',    nik:'3374020101760103', desil:9,  kecamatan:'Semarang Barat',kab_kota:'Kota Semarang' },
]

function validate() {
  nikError.value = ''
  captchaError.value = ''
  let valid = true
  if (!nik.value || nik.value.length !== 16) {
    nikError.value = 'NIK harus terdiri dari 16 digit angka'
    valid = false
  }
  if (!captchaInput.value) {
    captchaError.value = 'Kode verifikasi tidak boleh kosong'
    valid = false
  } else if (captchaInput.value.toUpperCase() !== captchaCode.value) {
    captchaError.value = 'Kode verifikasi salah, silakan coba lagi'
    refreshCaptcha()
    valid = false
  }
  return valid
}

function doSearch() {
  result.value = null
  if (!validate()) return

  isLoading.value = true
  lastNik.value = nik.value

  // Simulasi delay API
  setTimeout(() => {
    isLoading.value = false

    // Cari di mock desil 1-4
    const found = MOCK_MUSTAHIK.find(m => m.nik === nik.value)
    if (found) {
      result.value = { status: 'found', data: found }
      return
    }

    // Cari di mock non-eligible (desil 5-10)
    const nonEligible = MOCK_NON_ELIGIBLE.find(m => m.nik === nik.value)
    if (nonEligible) {
      result.value = {
        status: 'not_eligible',
        data: { ...nonEligible, desil_label: DESIL_LABELS[nonEligible.desil] }
      }
      return
    }

    // Tidak ditemukan sama sekali
    result.value = { status: 'not_found' }
    refreshCaptcha()
  }, 900)
}

function resetSearch() {
  nik.value = ''
  captchaInput.value = ''
  nikError.value = ''
  captchaError.value = ''
  result.value = null
  lastNik.value = ''
  refreshCaptcha()
}

// ===== HELPERS =====
const detailFields = [
  { key: 'nama',             label: 'Nama Lengkap' },
  { key: 'nik',              label: 'NIK' },
  { key: 'jenis_kelamin',    label: 'Jenis Kelamin' },
  { key: 'usia',             label: 'Usia' },
  { key: 'status_pernikahan',label: 'Status Pernikahan' },
  { key: 'agama',            label: 'Agama' },
  { key: 'kecamatan',        label: 'Kecamatan' },
  { key: 'kelurahan',        label: 'Kelurahan' },
  { key: 'kab_kota',         label: 'Kab/Kota' },
  { key: 'provinsi',         label: 'Provinsi' },
  { key: 'pekerjaan',        label: 'Pekerjaan' },
  { key: 'penghasilan',      label: 'Estimasi Penghasilan' },
  { key: 'jumlah_tanggungan',label: 'Jumlah Tanggungan' },
  { key: 'nominal',          label: 'Nominal Bantuan' },
]

function getField(data, key) {
  if (key === 'jenis_kelamin') return data[key] === 'm' ? 'Laki-laki' : 'Perempuan'
  if (key === 'usia')         return data[key] + ' tahun'
  if (key === 'penghasilan')  return formatRupiah(data[key])
  if (key === 'nominal')      return formatRupiah(data[key])
  if (key === 'jumlah_tanggungan') return data[key] + ' orang'
  return data[key] || '-'
}

const instructions = [
  { title: 'Masukkan NIK', desc: 'Ketikkan 16 digit Nomor Induk Kependudukan yang akan diperiksa.' },
  { title: 'Salin kode verifikasi', desc: 'Ketik ulang kode captcha yang tampil persis seperti yang ditampilkan (case-sensitive).' },
  { title: 'Klik tombol Periksa', desc: 'Sistem akan mencocokkan NIK dengan basis data DTSEN dan menampilkan hasilnya.' },
  { title: 'Baca hasil pemeriksaan', desc: 'Hasil akan menunjukkan apakah penduduk layak, tidak layak, atau tidak terdaftar.' },
]

const notFoundTips = [
  'Pastikan NIK yang dimasukkan benar (16 digit)',
  'Periksa apakah ada salah ketik atau digit yang terbalik',
  'Penduduk mungkin belum terdaftar dalam sistem DTSEN',
  'Hubungi dinas sosial setempat untuk pendaftaran atau pemutakhiran data',
]
</script>

<style scoped>
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
.slide-up-enter-active { animation: slideUp .35s ease; }
.slide-up-leave-active { transition: opacity .2s; }
.slide-up-leave-to    { opacity: 0; }

@media (max-width: 768px) {
  .grid-2col { grid-template-columns: 1fr !important; }
}
</style>
