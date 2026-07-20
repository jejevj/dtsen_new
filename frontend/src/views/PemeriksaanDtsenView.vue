<template>
  <AppLayout>
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
            <h2 class="text-base font-semibold text-gray-800">Cari Data Mustahik</h2>
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

            <!-- CAPTCHA ARITMATIKA (sama seperti LoginModal) -->
            <div class="mb-5">
              <label class="block text-sm font-medium text-gray-700 mb-1">Verifikasi Keamanan</label>
              <div class="flex items-center gap-3 mb-2">
                <div class="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 select-none flex-shrink-0">
                  <span class="font-mono font-bold text-primary-700 tracking-wider text-base">{{ captcha.question }}</span>
                  <button
                    type="button"
                    @click="refreshCaptcha"
                    :class="['flex items-center p-0.5 text-gray-400 hover:text-primary-600 transition-colors', captchaRefreshing && 'animate-spin']" 
                    title="Ganti soal"
                    aria-label="Ganti soal captcha"
                  >
                    <i class="pi pi-refresh text-sm"></i>
                  </button>
                </div>
                <InputText
                  v-model="form.captcha"
                  class="flex-1"
                  placeholder="Jawaban"
                  inputmode="numeric"
                  maxlength="4"
                  :class="{ 'p-invalid': errors.captcha }"
                  autocomplete="off"
                />
              </div>
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
                <p class="text-sm font-medium text-gray-700">Jawab Verifikasi Aritmatika</p>
                <p class="text-xs text-gray-500 mt-0.5">Selesaikan soal matematika sederhana yang tampil. Klik ikon refresh jika ingin soal baru.</p>
              </div>
            </li>
            <li class="flex gap-3">
              <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">3</span>
              <div>
                <p class="text-sm font-medium text-gray-700">Klik Periksa Data</p>
                <p class="text-xs text-gray-500 mt-0.5">Sistem akan mencocokkan NIK dengan basis data DTSEN dan menampilkan hasil pemeriksaan.</p>
              </div>
            </li>
            <li class="flex gap-3">
              <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">4</span>
              <div>
                <p class="text-sm font-medium text-gray-700">Baca Hasil Pemeriksaan</p>
                <p class="text-xs text-gray-500 mt-0.5">Hasil menampilkan riwayat penerimaan zakat lengkap dari LAZ yang terdaftar.</p>
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

      <!-- Loading state -->
      <transition name="fade-slide">
        <div v-if="isSearching" class="bg-white rounded-xl shadow-sm border border-gray-100 p-10 flex flex-col items-center gap-3">
          <i class="pi pi-spin pi-spinner text-primary-600" style="font-size: 2rem"></i>
          <p class="text-gray-500 text-sm">Mencari data NIK {{ lastSearchedNik }}...</p>
        </div>
      </transition>

      <!-- Error API -->
      <transition name="fade-slide">
        <div v-if="apiError && !isSearching" class="bg-white rounded-xl shadow-sm border border-red-200 overflow-hidden">
          <div class="bg-red-50 border-b border-red-200 px-6 py-4 flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
              <i class="pi pi-times-circle text-red-600 text-xl"></i>
            </div>
            <div>
              <h3 class="font-semibold text-red-800">{{ apiError }}</h3>
              <p class="text-sm text-red-600">NIK: {{ lastSearchedNik }}</p>
            </div>
          </div>
        </div>
      </transition>

      <!-- Data ditemukan: tampilkan tabel riwayat penerimaan -->
      <transition name="fade-slide">
        <div v-if="mustahikRows.length > 0 && !isSearching" class="space-y-4">

          <!-- Identity header card -->
          <div class="bg-white rounded-xl shadow-sm border border-green-200 overflow-hidden">
            <div class="bg-green-50 border-b border-green-200 px-6 py-4 flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                <i class="pi pi-check-circle text-green-600 text-xl"></i>
              </div>
              <div>
                <h3 class="font-semibold text-green-800">Data Ditemukan</h3>
                <p class="text-sm text-green-600">NIK <strong>{{ lastSearchedNik }}</strong> terdaftar dalam basis data DTSEN.</p>
              </div>
              <span class="ml-auto px-3 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full border border-green-300">
                {{ mustahikRows.length }} Riwayat
              </span>
            </div>

            <!-- Identitas Pribadi -->
            <div class="p-6 pb-4">
              <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Identitas Pribadi</h4>
              <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-8 gap-y-3">
                <div>
                  <p class="text-xs text-gray-400">Nama Lengkap</p>
                  <p class="text-sm font-semibold text-gray-800">{{ identity.nama_lengkap || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">NIK</p>
                  <p class="text-sm font-medium text-gray-800">{{ lastSearchedNik }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">Jenis Kelamin</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.jenis_kelamin || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">Tanggal Lahir</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.lahir_tanggal || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">Agama</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.agama || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">Alamat Domisili</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.alamat_domisili || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">Provinsi Domisili</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.provinsi_nama || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">Kab/Kota Domisili</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.kabkota_nama || '-' }}</p>
                </div>
              </div>
            </div>

            <!-- Alamat KTP -->
            <div class="px-6 pb-6">
              <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Alamat KTP</h4>
              <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-8 gap-y-3">
                <div>
                  <p class="text-xs text-gray-400">Alamat KTP</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.ktp_alamat || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">Provinsi KTP</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.ktp_provinsi_nama || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">Kab/Kota KTP</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.ktp_kabkota_nama || '-' }}</p>
                </div>
                <div>
                  <p class="text-xs text-gray-400">Kecamatan KTP</p>
                  <p class="text-sm font-medium text-gray-800">{{ identity.ktp_kecamatan_nama || '-' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Tabel riwayat penerimaan -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-100">
              <h4 class="text-sm font-semibold text-gray-700">Riwayat Penerimaan Zakat / Bantuan</h4>
            </div>
            <div class="overflow-x-auto">
              <table class="w-full text-sm">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">#</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">LAZ</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Skala</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Program</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Tipe</th>
                    <th class="px-4 py-3 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">Nominal</th>
                    <th class="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">Tanggal Terima</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-50">
                  <tr v-for="(row, i) in mustahikRows" :key="i" class="hover:bg-gray-50 transition-colors">
                    <td class="px-4 py-3 text-gray-400 text-xs">{{ i + 1 }}</td>
                    <td class="px-4 py-3">
                      <p class="font-medium text-gray-800">{{ row.laz_nama || '-' }}</p>
                      <p class="text-xs text-gray-400">{{ row.laz_kode }}</p>
                    </td>
                    <td class="px-4 py-3">
                      <span class="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full font-medium">{{ row.skala || '-' }}</span>
                    </td>
                    <td class="px-4 py-3 text-gray-700">{{ row.program_nama || '-' }}</td>
                    <td class="px-4 py-3">
                      <span :class="[
                        'px-2 py-0.5 text-xs rounded-full font-medium',
                        row.tipe_penerimaan === 'langsung' ? 'bg-green-50 text-green-700' : 'bg-orange-50 text-orange-700'
                      ]">{{ row.tipe_penerimaan || '-' }}</span>
                    </td>
                    <td class="px-4 py-3 text-right font-semibold text-gray-800">{{ formatRupiah(row.rupiah) }}</td>
                    <td class="px-4 py-3 text-gray-600">{{ row.tanggal_terima || '-' }}</td>
                  </tr>
                </tbody>
                <tfoot class="bg-gray-50 border-t border-gray-200">
                  <tr>
                    <td colspan="5" class="px-4 py-3 text-xs font-semibold text-gray-500 text-right">Total Diterima</td>
                    <td class="px-4 py-3 text-right font-bold text-green-700">{{ formatRupiah(totalRupiah) }}</td>
                    <td></td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
      </transition>

      <!-- Data tidak ditemukan -->
      <transition name="fade-slide">
        <div v-if="notFound && !isSearching" class="bg-white rounded-xl shadow-sm border border-red-200 overflow-hidden">
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
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import AppLayout from '@/components/layout/AppLayout.vue'
import MustahikService from '@/services/mustahik'

// ── State ──────────────────────────────────────────
const form            = reactive({ nik: '', captcha: '' })
const errors          = reactive({ nik: '', captcha: '' })
const isSearching     = ref(false)
const mustahikRows    = ref([])
const lastSearchedNik = ref('')
const notFound        = ref(false)
const apiError        = ref('')
const captchaRefreshing = ref(false)

// ── CAPTCHA ARITMATIKA (sama persis dengan LoginModal) ──────────────
function generateCaptcha() {
  const ops = ['+', '-', 'x']
  const op  = ops[Math.floor(Math.random() * ops.length)]
  let a, b, answer
  if (op === '+') {
    a = Math.floor(Math.random() * 20) + 1
    b = Math.floor(Math.random() * 20) + 1
    answer = a + b
  } else if (op === '-') {
    a = Math.floor(Math.random() * 20) + 10
    b = Math.floor(Math.random() * 10) + 1
    answer = a - b
  } else {
    a = Math.floor(Math.random() * 9) + 2
    b = Math.floor(Math.random() * 9) + 2
    answer = a * b
  }
  return { question: `${a} ${op} ${b} = ?`, answer: String(answer) }
}

const captcha = reactive(generateCaptcha())

function refreshCaptcha() {
  captchaRefreshing.value = true
  const next = generateCaptcha()
  captcha.question = next.question
  captcha.answer   = next.answer
  form.captcha     = ''
  errors.captcha   = ''
  setTimeout(() => { captchaRefreshing.value = false }, 400)
}
// ──────────────────────────────────────────────────

// ── Computed ───────────────────────────────────────
const identity = computed(() => {
  // Ambil baris pertama yang punya nama_lengkap (sebelum LAG dedup set null)
  return mustahikRows.value[0] || {}
})

const totalRupiah = computed(() =>
  mustahikRows.value.reduce((sum, r) => sum + (parseFloat(r.rupiah) || 0), 0)
)

// ── Validasi ────────────────────────────────────────
function validate() {
  errors.nik     = ''
  errors.captcha = ''
  let valid = true

  if (!form.nik.trim()) {
    errors.nik = 'NIK wajib diisi.'
    valid = false
  } else if (!/^\d{16}$/.test(form.nik.trim())) {
    errors.nik = 'NIK harus terdiri dari 16 digit angka.'
    valid = false
  }

  if (!form.captcha.trim()) {
    errors.captcha = 'Jawaban verifikasi wajib diisi.'
    valid = false
  } else if (form.captcha.trim() !== captcha.answer) {
    errors.captcha = 'Jawaban salah. Soal telah diperbarui, coba lagi.'
    valid = false
  }

  return valid
}

// ── Pencarian — panggil API real ─────────────────────
async function handleSearch() {
  if (!validate()) {
    if (form.captcha.trim() !== captcha.answer) refreshCaptcha()
    return
  }

  const nik = form.nik.trim()
  isSearching.value     = true
  mustahikRows.value    = []
  notFound.value        = false
  apiError.value        = ''
  lastSearchedNik.value = nik

  try {
    const res = await MustahikService.getDetailByNik(nik)

    if (res?.data && Array.isArray(res.data) && res.data.length > 0) {
      mustahikRows.value = res.data
    } else {
      notFound.value = true
    }
  } catch (e) {
    if (e?.response?.status === 404) {
      notFound.value = true
    } else {
      apiError.value = e?.response?.data?.message || 'Terjadi kesalahan saat menghubungi server. Coba lagi.'
    }
  } finally {
    isSearching.value = false
    refreshCaptcha()
  }
}

// ── Format ───────────────────────────────────────────
function formatRupiah(n) {
  const num = parseFloat(n)
  if (!n || isNaN(num)) return 'Rp 0'
  return 'Rp ' + num.toLocaleString('id-ID')
}
</script>

<style scoped>
.fade-slide-enter-active { transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1); }
.fade-slide-enter-from   { opacity: 0; transform: translateY(12px); }
.fade-slide-leave-active { transition: all 0.2s ease; }
.fade-slide-leave-to     { opacity: 0; transform: translateY(-8px); }

@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 0.4s linear infinite; }
</style>
