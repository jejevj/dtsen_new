<template>
  <AppLayout>
    <div class="space-y-4">
      <!-- Back button -->
      <Button icon="pi pi-arrow-left" label="Kembali" text @click="$router.back()" />

      <div v-if="loading" class="flex justify-center py-16">
        <ProgressSpinner />
      </div>

      <div v-else-if="detail?.data?.length" class="space-y-4">
        <div v-for="(item, idx) in detail.data" :key="idx">
          <Card class="shadow-sm">
            <template #title>
              <div class="flex items-center gap-3">
                <Avatar :label="item.nama_lengkap?.[0] || '?'" shape="circle" size="large" class="bg-primary-100 text-primary-700" />
                <div>
                  <p class="text-xl font-bold">{{ item.nama_lengkap || '—' }}</p>
                  <p class="text-sm text-gray-500">{{ item.laz_nama }}</p>
                </div>
              </div>
            </template>
            <template #content>
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-4">
                <div v-for="field in fields(item)" :key="field.label" class="flex flex-col gap-0.5">
                  <span class="text-xs text-gray-400 uppercase tracking-wide">{{ field.label }}</span>
                  <span class="text-sm font-medium text-gray-800">{{ field.value || '—' }}</span>
                </div>
              </div>
              <Divider />
              <div class="flex items-center justify-between">
                <span class="text-sm text-gray-500">Total Penyaluran</span>
                <span class="text-2xl font-bold text-green-600">{{ formatRupiah(item.rupiah) }}</span>
              </div>
            </template>
          </Card>
        </div>
      </div>

      <div v-else class="text-center py-16 text-gray-400">
        <i class="pi pi-inbox text-5xl block mb-3"></i>
        <p>Data tidak ditemukan.</p>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import Button        from 'primevue/button'
import Card          from 'primevue/card'
import Avatar        from 'primevue/avatar'
import Divider       from 'primevue/divider'
import ProgressSpinner from 'primevue/progressspinner'
import AppLayout from '@/components/layout/AppLayout.vue'
import MustahikService from '@/services/mustahik'
import { formatRupiah, formatDate, formatGender } from '@/utils/formatter'

const route   = useRoute()
const detail  = ref(null)
const loading = ref(false)

const fields = (item) => [
  { label: 'NIK',             value: item.nik },
  { label: 'Jenis Kelamin',   value: formatGender(item.jenis_kelamin) },
  { label: 'Tanggal Lahir',   value: formatDate(item.lahir_tanggal) },
  { label: 'Agama',           value: item.agama },
  { label: 'No. KK',          value: item.kk },
  { label: 'Program',         value: item.program_nama },
  { label: 'Skala LAZ',       value: item.skala },
  { label: 'Provinsi',        value: item.provinsi_nama },
  { label: 'Kab/Kota',        value: item.kabkota_nama },
  { label: 'Kecamatan',       value: item.kecamatan_nama },
  { label: 'Kelurahan',       value: item.kelurahan_nama },
  { label: 'Alamat Domisili', value: item.alamat_domisili },
  { label: 'Alamat KTP',      value: item.ktp_alamat },
]

onMounted(async () => {
  loading.value = true
  try {
    detail.value = await MustahikService.getDetail(route.params.nikHashed)
  } finally {
    loading.value = false
  }
})
</script>
