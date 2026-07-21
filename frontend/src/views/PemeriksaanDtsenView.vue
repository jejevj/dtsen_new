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
            <h2 class="text-base font-semibold text-gray-800">Cari Data Berdasarkan NIK</h2>
          </div>

          <form @submit.prevent="handleSearch">
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
                <p class="text-xs text-gray-500 mt-0.5">Nomor Induk Kependudukan 16 digit dari KTP.</p>
              </div>
            </li>
            <li class="flex gap-3">
              <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">2</span>
              <div>
                <p class="text-sm font-medium text-gray-700">Jawab Verifikasi Aritmatika</p>
                <p class="text-xs text-gray-500 mt-0.5">Selesaikan soal matematika sederhana. Klik refresh untuk soal baru.</p>
              </div>
            </li>
            <li class="flex gap-3">
              <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">3</span>
              <div>
                <p class="text-sm font-medium text-gray-700">Klik Periksa Data</p>
                <p class="text-xs text-gray-500 mt-0.5">Sistem memeriksa dua sumber: data DTSEN dan data Mustahik (Penerima Manfaat).</p>
              </div>
            </li>
            <li class="flex gap-3">
              <span class="flex-shrink-0 w-6 h-6 rounded-full bg-primary-100 text-primary-700 text-xs font-bold flex items-center justify-center">4</span>
              <div>
                <p class="text-sm font-medium text-gray-700">Baca Hasil Pemeriksaan</p>
                <p class="text-xs text-gray-500 mt-0.5">Dua panel hasil ditampilkan secara terpisah sesuai sumber data.</p>
              </div>
            </li>
          </ol>
          <div class="mt-5 pt-4 border-t border-gray-100 space-y-2">
            <div class="flex items-start gap-2">
              <span class="mt-0.5 w-3 h-3 rounded-full bg-blue-400 flex-shrink-0"></span>
              <p class="text-xs text-gray-500"><strong class="text-gray-700">Terdata di DTSEN</strong> — NIK tercatat dalam basis data sebagai anggota keluarga.</p>
            </div>
            <div class="flex items-start gap-2">
              <span class="mt-0.5 w-3 h-3 rounded-full bg-green-400 flex-shrink-0"></span>
              <p class="text-xs text-gray-500"><strong class="text-gray-700">Penerima Manfaat</strong> — NIK terdaftar sebagai penerima manfaat Lembaga.</p>
            </div>
          </div>
          <div class="mt-3">
            <p class="text-xs text-gray-400">
              <i class="pi pi-lock mr-1"></i>
              Data bersifat rahasia dan hanya untuk keperluan verifikasi internal.
            </p>
          </div>
        </div>
      </div>

      <!-- ============ HASIL PENCARIAN ============ -->

      <!-- Loading -->
      <transition name="fade-slide">
        <div v-if="isSearching" class="bg-white rounded-xl shadow-sm border border-gray-100 p-10 flex flex-col items-center gap-3">
          <i class="pi pi-spin pi-spinner text-primary-600" style="font-size: 2rem"></i>
          <p class="text-gray-500 text-sm">Memeriksa NIK <strong>{{ maskedLastNik }}</strong> di dua sumber data...</p>
        </div>
      </transition>

      <!-- Error API global -->
      <transition name="fade-slide">
        <div v-if="apiError && !isSearching" class="bg-white rounded-xl shadow-sm border border-red-200 overflow-hidden mb-4">
          <div class="bg-red-50 border-b border-red-200 px-6 py-4 flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center">
              <i class="pi pi-times-circle text-red-600 text-xl"></i>
            </div>
            <div>
              <h3 class="font-semibold text-red-800">{{ apiError }}</h3>
              <p class="text-sm text-red-600">NIK: {{ maskedLastNik }}</p>
            </div>
          </div>
        </div>
      </transition>

      <div v-if="searchDone && !isSearching" class="space-y-4">

        <!-- ══════════════════════════════════════════════════════════════ -->
        <!-- PANEL 1: TERDATA DI DTSEN -->
        <!-- ══════════════════════════════════════════════════════════════ -->

        <transition name="fade-slide">
          <div v-if="zawaData" class="pd-card">
            <!-- Watermark -->
            <div v-if="userIdentifier" class="pd-watermark" aria-hidden="true">
              <svg class="pd-watermark-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="pd-wm-dtsen" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                    <text x="10" y="40" font-family="Inter, sans-serif" font-size="14" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.11)">DO NOT COPY</text>
                    <text x="10" y="70" font-family="Inter, sans-serif" font-size="13" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.09)">{{ userIdentifier }}</text>
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#pd-wm-dtsen)" />
              </svg>
            </div>

            <!-- Konten panel DTSEN -->
            <div class="pd-content">
              <!-- Header panel -->
              <div class="bg-blue-50 border-b border-blue-200 px-6 py-4 flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                  <i class="pi pi-database text-blue-600 text-xl"></i>
                </div>
                <div class="flex-1">
                  <div class="flex items-center gap-2 flex-wrap">
                    <h3 class="font-semibold text-blue-800">Terdata di DTSEN</h3>
                    <span v-if="zawaDesil"
                      :style="{ background: DESIL_COLOR[zawaDesil]?.bg, color: DESIL_COLOR[zawaDesil]?.text, border: '1.5px solid ' + DESIL_COLOR[zawaDesil]?.border }"
                      class="px-3 py-0.5 text-xs font-extrabold rounded-full shadow-sm">
                      ★ {{ DESIL_LABEL[zawaDesil] ?? ('Desil ' + zawaDesil) }}
                    </span>
                  </div>
                  <p class="text-sm text-blue-600"><strong>{{ zawaData.nama || maskedLastNik }}</strong> tercatat sebagai anggota keluarga dalam basis data DTSEN.</p>
                </div>
              </div>

              <!-- Data Kependudukan -->
              <div class="p-6">
                <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Data Kependudukan (DTSEN)</h4>
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-8 gap-y-4">
                  <div>
                    <p class="text-xs text-gray-400">Nama</p>
                    <p class="text-sm font-semibold text-gray-800">{{ zawaData.nama || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">NIK</p>
                    <p class="text-sm font-medium text-gray-800 font-mono tracking-wide">{{ maskNik(zawaData.nomor_induk_kependudukan || lastSearchedNik) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">No. KK</p>
                    <p class="text-sm font-medium text-gray-800 font-mono tracking-wide">{{ maskNik(zawaData.nomor_kartu_keluarga) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Jenis Kelamin</p>
                    <p class="text-sm font-medium text-gray-800">{{ resolveRef(JENIS_KELAMIN, zawaData.jenis_kelamin) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Tanggal Lahir</p>
                    <p class="text-sm font-medium text-gray-800">{{ formatTanggal(zawaData.tanggal_lahir) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Status Kawin</p>
                    <p class="text-sm font-medium text-gray-800">{{ resolveRef(STATUS_KAWIN, zawaData.status_kawin) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Hubungan Keluarga</p>
                    <p class="text-sm font-medium text-gray-800">{{ resolveRef(HUBUNGAN_KELUARGA, zawaData.status_hubungan_keluarga) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Pendidikan Tertinggi</p>
                    <p class="text-sm font-medium text-gray-800">{{ resolveRef(PENDIDIKAN, zawaData.ijazah_tertinggi_yang_dimiliki) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Status Bekerja</p>
                    <p class="text-sm font-medium text-gray-800">{{ resolveRef(STATUS_BEKERJA, zawaData.status_bekerja) }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Alamat KTP</p>
                    <p class="text-sm font-medium text-gray-800">{{ zawaData.alamat_ktp || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Kecamatan KTP</p>
                    <p class="text-sm font-medium text-gray-800">{{ zawaData.kecamatan_ktp || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Kab/Kota KTP</p>
                    <p class="text-sm font-medium text-gray-800">{{ zawaData.kabupaten_kota_ktp || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Provinsi KTP</p>
                    <p class="text-sm font-medium text-gray-800">{{ zawaData.provinsi_ktp || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">PBI Nasional</p>
                    <p class="text-sm font-medium text-gray-800">{{ zawaData.pbi_nas != null ? (zawaData.pbi_nas ? 'Ya' : 'Tidak') : '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">PBI Pemda</p>
                    <p class="text-sm font-medium text-gray-800">{{ zawaData.pbi_pemda != null ? (zawaData.pbi_pemda ? 'Ya' : 'Tidak') : '-' }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </transition>

        <!-- Tidak ditemukan di DTSEN -->
        <transition name="fade-slide">
          <div v-if="!zawaData && !zawaLoading" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                <i class="pi pi-minus-circle text-gray-400 text-lg"></i>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <p class="text-sm font-semibold text-gray-600">Tidak Terdata di DTSEN</p>
                  <span class="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs font-medium rounded-full">DTSEN</span>
                </div>
                <p class="text-xs text-gray-400 mt-0.5">NIK <strong>{{ maskedLastNik }}</strong> tidak ditemukan dalam basis data DTSEN.</p>
              </div>
            </div>
          </div>
        </transition>

        <!-- ══════════════════════════════════════════════════════════════ -->
        <!-- PANEL 2: PENERIMA MANFAAT / MUSTAHIK -->
        <!-- ══════════════════════════════════════════════════════════════ -->

        <transition name="fade-slide">
          <div v-if="mustahikRows.length > 0" class="pd-card">
            <!-- Watermark -->
            <div v-if="userIdentifier" class="pd-watermark" aria-hidden="true">
              <svg class="pd-watermark-svg" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <pattern id="pd-wm-mustahik" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">
                    <text x="10" y="40" font-family="Inter, sans-serif" font-size="14" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.11)">DO NOT COPY</text>
                    <text x="10" y="70" font-family="Inter, sans-serif" font-size="13" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.09)">{{ userIdentifier }}</text>
                  </pattern>
                </defs>
                <rect width="100%" height="100%" fill="url(#pd-wm-mustahik)" />
              </svg>
            </div>

            <!-- Konten panel Mustahik -->
            <div class="pd-content">
              <div class="bg-green-50 border-b border-green-200 px-6 py-4 flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                  <i class="pi pi-check-circle text-green-600 text-xl"></i>
                </div>
                <div class="flex-1">
                  <h3 class="font-semibold text-green-800">Penerima Manfaat</h3>
                  <p class="text-sm text-green-600">NIK <strong>{{ maskedLastNik }}</strong> terdaftar sebagai penerima zakat/bantuan.</p>
                </div>
                <span class="px-3 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full border border-green-300 flex-shrink-0">
                  {{ mustahikRows.length }} Riwayat
                </span>
              </div>

              <div class="p-6 pb-4">
                <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Identitas Pribadi</h4>
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-8 gap-y-3">
                  <div>
                    <p class="text-xs text-gray-400">Nama Lengkap</p>
                    <p class="text-sm font-semibold text-gray-800">{{ mustahikIdentity.nama_lengkap || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">NIK</p>
                    <p class="text-sm font-medium text-gray-800 font-mono tracking-wide">{{ maskedLastNik }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Jenis Kelamin</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.jenis_kelamin || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Tanggal Lahir</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.lahir_tanggal || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Agama</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.agama || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Alamat Domisili</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.alamat_domisili || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Provinsi Domisili</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.provinsi_nama || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Kab/Kota Domisili</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.kabkota_nama || '-' }}</p>
                  </div>
                </div>
              </div>

              <div class="px-6 pb-6">
                <h4 class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-4">Alamat KTP</h4>
                <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-x-8 gap-y-3">
                  <div>
                    <p class="text-xs text-gray-400">Alamat KTP</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.ktp_alamat || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Provinsi KTP</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.ktp_provinsi_nama || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Kab/Kota KTP</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.ktp_kabkota_nama || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-400">Kecamatan KTP</p>
                    <p class="text-sm font-medium text-gray-800">{{ mustahikIdentity.ktp_kecamatan_nama || '-' }}</p>
                  </div>
                </div>
              </div>

              <div class="border-t border-gray-100">
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
          </div>
        </transition>

        <!-- Tidak ditemukan sebagai Mustahik -->
        <transition name="fade-slide">
          <div v-if="mustahikRows.length === 0 && !mustahikLoading" class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
            <div class="px-6 py-4 flex items-center gap-3">
              <div class="w-9 h-9 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                <i class="pi pi-minus-circle text-gray-400 text-lg"></i>
              </div>
              <div>
                <div class="flex items-center gap-2">
                  <p class="text-sm font-semibold text-gray-600">Bukan Penerima Manfaat</p>
                  <span class="px-2 py-0.5 bg-gray-100 text-gray-500 text-xs font-medium rounded-full">MUSTAHIK</span>
                </div>
                <p class="text-xs text-gray-400 mt-0.5">NIK <strong>{{ maskedLastNik }}</strong> tidak terdaftar sebagai mustahik penerima zakat/bantuan LAZ.</p>
              </div>
            </div>
          </div>
        </transition>

        <!-- Pesan bila keduanya tidak ditemukan -->
        <transition name="fade-slide">
          <div v-if="mustahikRows.length === 0 && !zawaData && !mustahikLoading && !zawaLoading"
               class="bg-amber-50 border border-amber-200 rounded-xl px-6 py-4">
            <div class="flex items-start gap-3">
              <i class="pi pi-exclamation-triangle text-amber-500 text-lg mt-0.5"></i>
              <div>
                <p class="text-sm font-semibold text-amber-800">NIK Tidak Ditemukan di Kedua Sumber</p>
                <p class="text-xs text-amber-700 mt-1">NIK <strong>{{ maskedLastNik }}</strong> tidak terdaftar sebagai mustahik maupun dalam basis data DTSEN.</p>
                <ul class="mt-2 text-xs text-amber-600 list-disc list-inside space-y-0.5">
                  <li>Periksa kembali NIK pada KTP</li>
                  <li>Terdapat kemungkinan kesalahan pengetikan</li>
                  <li>Data belum diperbarui pada periode ini</li>
                  <li>Hubungi BAZNAS atau petugas kelurahan setempat</li>
                </ul>
              </div>
            </div>
          </div>
        </transition>

      </div>
      <!-- /hasil -->

    </div>
  </AppLayout>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import AppLayout from '@/components/layout/AppLayout.vue'
import MustahikService from '@/services/mustahik'
import {
  JENIS_KELAMIN, STATUS_KAWIN, HUBUNGAN_KELUARGA,
  PENDIDIKAN, STATUS_BEKERJA, DESIL_LABEL, DESIL_COLOR, resolveRef,
} from '@/data/dtsenRef'
import { fetchBaselineKeluargaByNkk } from '@/services/baselineService'
import { maskNik } from '@/utils/formatter'
import { useWatermark } from '@/composables/useWatermark'

// ── Watermark ───────────────────────────────────────
const { userIdentifier } = useWatermark()

// ── State ──────────────────────────────────────────
const form              = reactive({ nik: '', captcha: '' })
const errors            = reactive({ nik: '', captcha: '' })
const isSearching       = ref(false)
const mustahikRows      = ref([])
const mustahikLoading   = ref(false)
const zawaData          = ref(null)
const zawaLoading       = ref(false)
const lastSearchedNik   = ref('')
const apiError          = ref('')
const searchDone        = ref(false)
const captchaRefreshing = ref(false)
const zawaDesil         = ref(null)

const maskedLastNik = computed(() => maskNik(lastSearchedNik.value))

// ── CAPTCHA ARITMATIKA ──────────────────────────────
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

// ── Computed ───────────────────────────────────────
const mustahikIdentity = computed(() => mustahikRows.value[0] || {})
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

// ── Pencarian Dual API ──────────────────────────────
async function handleSearch() {
  if (!validate()) {
    if (form.captcha.trim() !== captcha.answer) refreshCaptcha()
    return
  }

  const nik = form.nik.trim()
  isSearching.value     = true
  mustahikRows.value    = []
  zawaData.value        = null
  zawaDesil.value       = null
  apiError.value        = ''
  searchDone.value      = false
  lastSearchedNik.value = nik
  mustahikLoading.value = true
  zawaLoading.value     = true

  const [mustahikResult, zawaResult] = await Promise.allSettled([
    MustahikService.getDetailByNik(nik),
    MustahikService.getZawaAnggotaByNik(nik),
  ])

  if (mustahikResult.status === 'fulfilled') {
    const res = mustahikResult.value
    if (res?.data && Array.isArray(res.data) && res.data.length > 0) {
      mustahikRows.value = res.data
    }
  } else {
    const e = mustahikResult.reason
    if (e?.response?.status !== 404) {
      apiError.value = e?.response?.data?.message || 'Error saat mengambil data mustahik.'
    }
  }
  mustahikLoading.value = false

  if (zawaResult.status === 'fulfilled') {
    const anggota = zawaResult.value
    if (anggota && typeof anggota === 'object') {
      zawaData.value = anggota
      const nkk = anggota.nomor_kartu_keluarga
      if (nkk) {
        try {
          const keluarga = await fetchBaselineKeluargaByNkk(nkk)
          zawaDesil.value = keluarga?.desil_nasional ?? null
        } catch {
          zawaDesil.value = null
        }
      }
    }
  }
  zawaLoading.value = false

  isSearching.value = false
  searchDone.value  = true
  refreshCaptcha()
}

// ── Format ───────────────────────────────────────────
function formatRupiah(n) {
  const num = parseFloat(n)
  if (!n || isNaN(num)) return 'Rp 0'
  return 'Rp ' + num.toLocaleString('id-ID')
}

function formatTanggal(val) {
  if (!val) return '-'
  try {
    const d = new Date(val)
    return d.toLocaleDateString('id-ID', { day: '2-digit', month: 'long', year: 'numeric' })
  } catch {
    return val
  }
}
</script>

<style scoped>
/* ── Watermark ── */
.pd-card {
  position: relative;
  background: white;
  border-radius: 0.75rem;
  border: 1px solid;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  overflow: hidden;
}
.pd-card.border-blue-200  { border-color: #bfdbfe; }
.pd-card.border-green-200 { border-color: #bbf7d0; }
.pd-watermark {
  position: absolute;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  user-select: none;
}
.pd-watermark-svg {
  display: block;
  width: 100%;
  height: 100%;
}
.pd-content {
  position: relative;
  z-index: 0;
}

/* ── Transitions ── */
.fade-slide-enter-active { transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1); }
.fade-slide-enter-from   { opacity: 0; transform: translateY(12px); }
.fade-slide-leave-active { transition: all 0.2s ease; }
.fade-slide-leave-to     { opacity: 0; transform: translateY(-8px); }

@keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 0.4s linear infinite; }
</style>
