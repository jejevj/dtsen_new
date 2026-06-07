<template>
  <div class="p-6">
    <!-- Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Pemeriksaan DTSEN</h1>
      <p class="text-gray-500 mt-1 text-sm">Verifikasi kelayakan penerima manfaat berdasarkan NIK</p>
    </div>

    <!-- Form + Instruksi -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">

      <!-- Card Form Pencarian -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center gap-2 mb-5">
          <i class="pi pi-search text-primary-600 text-lg"></i>
          <h2 class="text-base font-semibold text-gray-800">Cari Data Penduduk</h2>
        </div>

        <form @submit.prevent="handleSearch">
          <!-- NIK -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Nomor Induk Kependudukan (NIK)</label>
            <InputText
              v-model="form.nik"
              class="w-full"
              placeholder="Masukkan 16 digit NIK"
              maxlength="16"
              :class="{ 'p-invalid': errors.nik }"
            />
            <small v-if="errors.nik" class="p-error text-xs">{{ errors.nik }}</small>
          </div>

          <!-- CAPTCHA -->
          <div class="mb-5">
            <label class="block text-sm font-medium text-gray-700 mb-1">Kode Keamanan (CAPTCHA)</label>
            <div class="flex items-center gap-3 mb-2">
              <!-- CAPTCHA Display -->
              <div class="relative select-none">
                <canvas
                  ref="captchaCanvas"
                  width="160"
                  height="52"
                  class="rounded-lg border border-gray-200"
                  style="letter-spacing: 4px;"
                />
              </div>
              <button
                type="button"
                @click="refreshCaptcha"
                class="flex items-center gap-1.5 text-sm text-primary-600 hover:text-primary-800 font-medium transition-colors"
                title="Muat ulang CAPTCHA"
              >
                <i class="pi pi-refresh" :class="{ 'animate-spin': captchaRefreshing }"></i>
                <span>Refresh</span>
              </button>
            </div>
            <InputText
              v-model="form.captcha"
              class="w-full"
              placeholder="Ketik teks di atas"
              :class="{ 'p-invalid': errors.captcha }"
              autocomplete="off"
            />
            <small v-if="errors.captcha" class="p-error text-xs">{{ errors.captcha }}</small>
          </div>

          <!-- Submit -->
          <Button
            type="submit"
            label="Periksa Data"
            icon="pi pi-search"
            class="w-full"
            :loading="isSearching"
          />
        </form>
      </div>

      <!-- Card Instruksi -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex items-center gap-2 mb-5">
          <i class="pi pi-info-circle text-blue-500 text-lg"></i>
          <h2 class="text-base font-semibold text-gray-800">Petunjuk Penggunaan</h2>
        </div>

        <ol class="space-y-4">
          <li class="flex gap-3">
            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">1</span>
            <div>
              <p class="text-sm font-medium text-gray-700">Masukkan NIK</p>
              <p class="text-xs text-gray-500 mt-0.5">Nomor Induk Kependudukan terdiri dari 16 digit angka yang tertera pada KTP.</p>
            </div>
          </li>
          <li class="flex gap-3">
            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">2</span>
            <div>
              <p class="text-sm font-medium text-gray-700">Masukkan Kode CAPTCHA</p>
              <p class="text-xs text-gray-500 mt-0.5">Ketik teks yang tampil pada gambar CAPTCHA. Kode bersifat case-sensitive. Jika sulit dibaca, klik tombol Refresh.</p>
            </div>
          </li>
          <li class="flex gap-3">
            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">3</span>
            <div>
              <p class="text-sm font-medium text-gray-700">Klik Periksa Data</p>
              <p class="text-xs text-gray-500 mt-0.5">Sistem akan mencocokkan NIK dengan basis data DTSEN dan menampilkan status kelayakan.</p>
            </div>
          </li>
          <li class="flex gap-3">
            <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">4</span>
            <div>
              <p class="text-sm font-medium text-gray-700">Baca Hasil Pemeriksaan</p>
              <p class="text-xs text-gray-500 mt-0.5">Hasil akan menampilkan status: <strong>Layak</strong> (Desil 1–4), <strong>Tidak Memenuhi Kriteria</strong> (Desil 5–10), atau <strong>Data Tidak Ditemukan</strong>.</p>
            </div>
          </li>
        </ol>

        <div class="mt-5 pt-4 border-t border-gray-100">
          <p class="text-xs text-gray-400">
            <i class="pi pi-lock mr-1"></i>
            Data bersifat rahasia dan hanya untuk keperluan verifikasi internal.
          </p>
        </div>
      </div>
    </div>

    <!-- ============ HASIL PENCARIAN ============ -->

    <!-- Kondisi 1: Data ditemukan + desil 1-4 (LAYAK) -->
    <transition name="fade-slide">
      <div v-if="result && result.status === 'layak'" class="bg-white rounded-xl shadow-sm border border-green-200 overflow-hidden">
        <!-- Banner -->
        <div class="bg-green-50 border-b border-green-200 px-6 py-4 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
            <i class="pi pi-check-circle text-green-600 text-xl"></i>
          </div>
          <div>
            <h3 class="font-semibold text-green-800">Data Ditemukan — Layak sebagai Penerima Manfaat</h3>
            <p class="text-sm text-green-600">Penduduk ini terdaftar dalam DTSEN pada Desil {{ result.data.desil }} dan memenuhi kriteria penerima zakat.</p>
          </div>
          <span class="ml-auto px-3 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full border border-green-300">DESIL {{ result.data.desil }}</span>
        </div>

        <!-- Detail Data -->
        <div class="p-6">
          <h4 class="text-sm font-semibold text-gray-700 mb-4 uppercase tracking-wide">Informasi Penduduk</h4>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-4">
            <div v-for="field in detailFields" :key="field.key">
              <p class="text-xs text-gray-400 mb-0.5">{{ field.label }}</p>
              <p class="text-sm font-medium text-gray-800">{{ formatField(field.key, result.data) }}</p>
            </div>
          </div>

          <div class="mt-6 pt-5 border-t border-gray-100">
            <h4 class="text-sm font-semibold text-gray-700 mb-3 uppercase tracking-wide">Informasi Bantuan</h4>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div class="bg-green-50 rounded-lg p-4 border border-green-100">
                <p class="text-xs text-gray-500 mb-1">Nominal Bantuan</p>
                <p class="text-lg font-bold text-green-700">{{ formatCurrency(result.data.nominal) }}</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-4 border border-gray-100">
                <p class="text-xs text-gray-500 mb-1">Keterangan</p>
                <p class="text-sm font-medium text-gray-700">{{ result.data.keterangan || '-' }}</p>
              </div>
              <div class="bg-gray-50 rounded-lg p-4 border border-gray-100">
                <p class="text-xs text-gray-500 mb-1">Jumlah Tanggungan</p>
                <p class="text-sm font-medium text-gray-700">{{ result.data.jumlah_tanggungan }} orang</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </transition>

    <!-- Kondisi 2: Data ditemukan tapi desil 5-10 (TIDAK LAYAK) -->
    <transition name="fade-slide">
      <div v-if="result && result.status === 'tidak_layak'" class="bg-white rounded-xl shadow-sm border border-yellow-200 overflow-hidden">
        <div class="bg-yellow-50 border-b border-yellow-200 px-6 py-4 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-yellow-100 flex items-center justify-center">
            <i class="pi pi-exclamation-triangle text-yellow-600 text-xl"></i>
          </div>
          <div>
            <h3 class="font-semibold text-yellow-800">Data Ditemukan — Tidak Memenuhi Kriteria</h3>
            <p class="text-sm text-yellow-700">Penduduk ini terdaftar dalam DTSEN pada Desil {{ result.data.desil }}, namun <strong>tidak termasuk dalam kelompok penerima manfaat</strong> (hanya Desil 1–4).</p>
          </div>
          <span class="ml-auto px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-bold rounded-full border border-yellow-300">DESIL {{ result.data.desil }}</span>
        </div>
        <div class="p-6">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-4">
            <div v-for="field in basicFields" :key="field.key">
              <p class="text-xs text-gray-400 mb-0.5">{{ field.label }}</p>
              <p class="text-sm font-medium text-gray-800">{{ formatField(field.key, result.data) }}</p>
            </div>
          </div>
          <div class="mt-5 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <p class="text-sm text-yellow-800">
              <i class="pi pi-info-circle mr-2"></i>
              Kriteria penerima manfaat DTSEN adalah penduduk yang masuk dalam kelompok <strong>Desil 1 hingga Desil 4</strong>. Penduduk ini berada di Desil {{ result.data.desil }} sehingga tidak berhak menerima bantuan pada periode ini.
            </p>
          </div>
        </div>
      </div>
    </transition>

    <!-- Kondisi 3: Data tidak ditemukan -->
    <transition name="fade-slide">
      <div v-if="result && result.status === 'not_found'" class="bg-white rounded-xl shadow-sm border border-red-200 overflow-hidden">
        <div class="bg-red-50 border-b border-red-200 px-6 py-4 flex items-center gap-3">
          <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
            <i class="pi pi-times-circle text-red-600 text-xl"></i>
          </div>
          <div>
            <h3 class="font-semibold text-red-800">Data Tidak Ditemukan</h3>
            <p class="text-sm text-red-600">NIK <strong>{{ lastSearchedNik }}</strong> tidak terdaftar dalam basis data DTSEN.</p>
          </div>
        </div>
        <div class="p-6">
          <div class="flex flex-col sm:flex-row gap-4">
            <div class="flex-1 p-4 bg-gray-50 rounded-lg border border-gray-100">
              <p class="text-sm font-medium text-gray-700 mb-1">Kemungkinan penyebab:</p>
              <ul class="text-sm text-gray-500 space-y-1 list-disc list-inside">
                <li>NIK yang dimasukkan tidak terdaftar di DTSEN</li>
                <li>Terdapat kesalahan pengetikan pada NIK</li>
                <li>Data belum diperbarui pada periode ini</li>
              </ul>
            </div>
            <div class="flex-1 p-4 bg-blue-50 rounded-lg border border-blue-100">
              <p class="text-sm font-medium text-blue-700 mb-1">Langkah selanjutnya:</p>
              <ul class="text-sm text-blue-600 space-y-1 list-disc list-inside">
                <li>Periksa kembali NIK pada KTP</li>
                <li>Hubungi petugas kelurahan setempat</li>
                <li>Laporkan ke BAZNAS untuk pendataan ulang</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { MOCK_MUSTAHIK } from '@/data/mockMustahik'

// ── State ──────────────────────────────────────────
const form = reactive({ nik: '', captcha: '' })
const errors = reactive({ nik: '', captcha: '' })
const isSearching = ref(false)
const result = ref(null)
const lastSearchedNik = ref('')
const captchaCanvas = ref(null)
const captchaText = ref('')
const captchaRefreshing = ref(false)

// ── CAPTCHA ─────────────────────────────────────────
const CAPTCHA_CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789'

function generateCaptchaText(len = 6) {
  let s = ''
  for (let i = 0; i < len; i++) s += CAPTCHA_CHARS[Math.floor(Math.random() * CAPTCHA_CHARS.length)]
  return s
}

function drawCaptcha(text) {
  const canvas = captchaCanvas.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  const W = canvas.width
  const H = canvas.height

  // Background gradient
  const grad = ctx.createLinearGradient(0, 0, W, H)
  grad.addColorStop(0, '#f0f7ff')
  grad.addColorStop(1, '#e8f4fd')
  ctx.fillStyle = grad
  ctx.fillRect(0, 0, W, H)

  // Noise lines
  for (let i = 0; i < 5; i++) {
    ctx.strokeStyle = `rgba(${Math.random()*80|0},${Math.random()*80|0},${Math.random()*200|0},0.25)`
    ctx.lineWidth = 1
    ctx.beginPath()
    ctx.moveTo(Math.random() * W, Math.random() * H)
    ctx.lineTo(Math.random() * W, Math.random() * H)
    ctx.stroke()
  }

  // Noise dots
  for (let i = 0; i < 40; i++) {
    ctx.fillStyle = `rgba(${Math.random()*100|0},${Math.random()*100|0},${Math.random()*200|0},0.2)`
    ctx.beginPath()
    ctx.arc(Math.random() * W, Math.random() * H, Math.random() * 2 + 0.5, 0, Math.PI * 2)
    ctx.fill()
  }

  // Characters
  const charW = W / (text.length + 1)
  for (let i = 0; i < text.length; i++) {
    ctx.save()
    const x = charW * (i + 0.8) + Math.random() * 4 - 2
    const y = H / 2 + Math.random() * 6 - 3
    ctx.translate(x, y)
    ctx.rotate((Math.random() - 0.5) * 0.4)
    const fontSize = 22 + Math.random() * 6 | 0
    ctx.font = `${Math.random() > 0.5 ? 'bold ' : ''}${fontSize}px "Courier New", monospace`
    const hue = Math.random() * 60 | 0
    ctx.fillStyle = `hsl(${200 + hue}, 70%, 30%)`
    ctx.fillText(text[i], 0, 0)
    ctx.restore()
  }

  // Border
  ctx.strokeStyle = '#cbd5e1'
  ctx.lineWidth = 1
  ctx.strokeRect(0, 0, W, H)
}

async function refreshCaptcha() {
  captchaRefreshing.value = true
  form.captcha = ''
  errors.captcha = ''
  captchaText.value = generateCaptchaText()
  await nextTick()
  drawCaptcha(captchaText.value)
  setTimeout(() => { captchaRefreshing.value = false }, 400)
}

onMounted(async () => {
  await nextTick()
  captchaText.value = generateCaptchaText()
  drawCaptcha(captchaText.value)
})

// ── Validasi ────────────────────────────────────────
function validate() {
  let valid = true
  errors.nik = ''
  errors.captcha = ''

  if (!form.nik.trim()) {
    errors.nik = 'NIK wajib diisi.'
    valid = false
  } else if (!/^\d{16}$/.test(form.nik.trim())) {
    errors.nik = 'NIK harus terdiri dari 16 digit angka.'
    valid = false
  }

  if (!form.captcha.trim()) {
    errors.captcha = 'Kode CAPTCHA wajib diisi.'
    valid = false
  } else if (form.captcha.trim() !== captchaText.value) {
    errors.captcha = 'Kode CAPTCHA tidak sesuai. Silakan coba lagi.'
    valid = false
  }

  return valid
}

// ── Pencarian ────────────────────────────────────────
function handleSearch() {
  if (!validate()) {
    // Selalu refresh CAPTCHA setelah submit (berhasil atau gagal captcha)
    if (form.captcha !== captchaText.value) refreshCaptcha()
    return
  }

  isSearching.value = true
  result.value = null
  lastSearchedNik.value = form.nik.trim()

  // Simulasi delay API
  setTimeout(() => {
    const found = MOCK_MUSTAHIK.find(m => m.nik === form.nik.trim())

    if (!found) {
      result.value = { status: 'not_found' }
    } else if (found.desil >= 1 && found.desil <= 4) {
      result.value = { status: 'layak', data: found }
    } else {
      result.value = { status: 'tidak_layak', data: found }
    }

    isSearching.value = false
    // Refresh CAPTCHA setelah setiap pencarian berhasil
    refreshCaptcha()
  }, 800)
}

// ── Format Helpers ───────────────────────────────────
const detailFields = [
  { key: 'nama',             label: 'Nama Lengkap' },
  { key: 'nik',              label: 'NIK' },
  { key: 'jenis_kelamin',    label: 'Jenis Kelamin' },
  { key: 'usia',             label: 'Usia' },
  { key: 'kab_kota',         label: 'Kabupaten/Kota' },
  { key: 'provinsi',         label: 'Provinsi' },
  { key: 'kecamatan',        label: 'Kecamatan' },
  { key: 'kelurahan',        label: 'Kelurahan' },
  { key: 'pekerjaan',        label: 'Pekerjaan' },
  { key: 'penghasilan',      label: 'Penghasilan/Bulan' },
  { key: 'status_pernikahan',label: 'Status Pernikahan' },
  { key: 'agama',            label: 'Agama' },
]

const basicFields = [
  { key: 'nama',          label: 'Nama Lengkap' },
  { key: 'nik',           label: 'NIK' },
  { key: 'jenis_kelamin', label: 'Jenis Kelamin' },
  { key: 'usia',          label: 'Usia' },
  { key: 'kab_kota',      label: 'Kabupaten/Kota' },
  { key: 'provinsi',      label: 'Provinsi' },
]

function formatField(key, data) {
  const val = data[key]
  if (key === 'jenis_kelamin') return val === 'm' ? 'Laki-laki' : 'Perempuan'
  if (key === 'usia') return val + ' tahun'
  if (key === 'penghasilan') return formatCurrency(val)
  return val || '-'
}

function formatCurrency(n) {
  if (!n) return 'Rp 0'
  return 'Rp ' + n.toLocaleString('id-ID')
}
</script>

<style scoped>
.fade-slide-enter-active { transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1); }
.fade-slide-enter-from   { opacity: 0; transform: translateY(12px); }
.fade-slide-leave-active { transition: all 0.2s ease; }
.fade-slide-leave-to     { opacity: 0; transform: translateY(-8px); }

@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 0.6s linear infinite; }
</style>
