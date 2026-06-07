<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:20px;">

      <!-- Back button -->
      <button @click="$router.back()" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border:1px solid #e2e8f0;border-radius:8px;background:white;font-size:13px;font-weight:600;cursor:pointer;color:#374151;width:fit-content;">
        <i class="pi pi-arrow-left" style="font-size:11px;"></i> Kembali
      </button>

      <!-- Not found -->
      <div v-if="!mustahik" style="text-align:center;padding:60px 20px;background:white;border-radius:14px;border:1px solid #f1f5f9;">
        <i class="pi pi-user-minus" style="font-size:40px;color:#cbd5e1;"></i>
        <p style="color:#64748b;margin:12px 0 0;">Data tidak ditemukan</p>
      </div>

      <template v-else>
        <!-- Identity Card -->
        <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
          <div style="display:flex;align-items:flex-start;gap:20px;flex-wrap:wrap;">
            <!-- Avatar -->
            <div :style="{ width:'72px', height:'72px', borderRadius:'16px', background:DESIL_COLORS[mustahik.desil].bg, display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0 }">
              <i :class="mustahik.jenis_kelamin==='m' ? 'pi pi-user' : 'pi pi-user'" :style="{ fontSize:'28px', color:DESIL_COLORS[mustahik.desil].text }"></i>
            </div>
            <div style="flex:1;">
              <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                <h2 style="font-size:1.3rem;font-weight:800;color:#1e293b;margin:0;">{{ mustahik.nama }}</h2>
                <span style="padding:3px 12px;border-radius:99px;font-size:11px;font-weight:700;"
                  :style="{ background:DESIL_COLORS[mustahik.desil].bg, color:DESIL_COLORS[mustahik.desil].text }">
                  Desil {{ mustahik.desil }}
                </span>
                <span style="padding:3px 10px;border-radius:99px;font-size:11px;font-weight:600;"
                  :style="{ background: mustahik.jenis_kelamin==='m'?'#eff6ff':'#fdf2f8', color: mustahik.jenis_kelamin==='m'?'#2563eb':'#db2777' }">
                  {{ mustahik.jenis_kelamin==='m' ? 'Laki-laki' : 'Perempuan' }}
                </span>
              </div>
              <p style="font-size:13px;color:#64748b;margin:6px 0 0;">NIK: {{ maskNIK(mustahik.nik) }}</p>
              <p v-if="mustahik.keterangan&&mustahik.keterangan!=='-'" style="font-size:12px;color:#f59e0b;margin:4px 0 0;font-weight:600;">
                <i class="pi pi-info-circle" style="margin-right:4px;"></i>{{ mustahik.keterangan }}
              </p>
            </div>
            <div style="text-align:right;">
              <p style="font-size:11px;color:#94a3b8;margin:0;">Total Bantuan</p>
              <p style="font-size:1.4rem;font-weight:900;color:#15803d;margin:2px 0 0;">{{ formatRupiah(mustahik.nominal) }}</p>
            </div>
          </div>
        </div>

        <!-- Grid detail -->
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;" class="detail-grid">

          <!-- Data Pribadi -->
          <div class="detail-card">
            <p class="section-title"><i class="pi pi-id-card" style="margin-right:6px;"></i>Data Pribadi</p>
            <div class="field-list">
              <div class="field-row">
                <span class="field-label">Usia</span>
                <span class="field-value">{{ mustahik.usia }} tahun</span>
              </div>
              <div class="field-row">
                <span class="field-label">Agama</span>
                <span class="field-value">{{ mustahik.agama }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">Status Pernikahan</span>
                <span class="field-value">{{ mustahik.status_pernikahan }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">Pekerjaan</span>
                <span class="field-value">{{ mustahik.pekerjaan }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">Penghasilan/Bln</span>
                <span class="field-value" :style="{ color: mustahik.penghasilan===0?'#dc2626':'#374151' }">
                  {{ mustahik.penghasilan===0 ? 'Tidak ada' : formatRupiah(mustahik.penghasilan) }}
                </span>
              </div>
              <div class="field-row">
                <span class="field-label">Jumlah Tanggungan</span>
                <span class="field-value">{{ mustahik.jumlah_tanggungan }} jiwa</span>
              </div>
            </div>
          </div>

          <!-- Domisili -->
          <div class="detail-card">
            <p class="section-title"><i class="pi pi-map-marker" style="margin-right:6px;"></i>Alamat Domisili</p>
            <div class="field-list">
              <div class="field-row">
                <span class="field-label">Kelurahan</span>
                <span class="field-value">{{ mustahik.kelurahan }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">Kecamatan</span>
                <span class="field-value">{{ mustahik.kecamatan }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">Kab/Kota</span>
                <span class="field-value">{{ mustahik.kab_kota }}</span>
              </div>
              <div class="field-row">
                <span class="field-label">Provinsi</span>
                <span class="field-value">{{ mustahik.provinsi }}</span>
              </div>
            </div>
          </div>

        </div>

        <!-- Bantuan info -->
        <div class="detail-card">
          <p class="section-title"><i class="pi pi-wallet" style="margin-right:6px;"></i>Informasi Penyaluran Bantuan</p>
          <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px;" class="bantuan-grid">
            <div style="background:#f0fdf4;border-radius:10px;padding:16px;">
              <p style="font-size:11px;color:#64748b;margin:0 0 4px;font-weight:600;text-transform:uppercase;">Total Bantuan</p>
              <p style="font-size:1.3rem;font-weight:900;color:#15803d;margin:0;">{{ formatRupiah(mustahik.nominal) }}</p>
            </div>
            <div style="background:#eff6ff;border-radius:10px;padding:16px;">
              <p style="font-size:11px;color:#64748b;margin:0 0 4px;font-weight:600;text-transform:uppercase;">Desil Kemiskinan</p>
              <p style="font-size:1.3rem;font-weight:900;margin:0;" :style="{color:DESIL_COLORS[mustahik.desil].text}">Desil {{ mustahik.desil }}</p>
              <p style="font-size:11px;color:#64748b;margin:4px 0 0;">{{ desilDesc(mustahik.desil) }}</p>
            </div>
            <div style="background:#fff7ed;border-radius:10px;padding:16px;">
              <p style="font-size:11px;color:#64748b;margin:0 0 4px;font-weight:600;text-transform:uppercase;">Status</p>
              <p style="font-size:1.1rem;font-weight:700;color:#15803d;margin:0;">Aktif</p>
              <p style="font-size:11px;color:#64748b;margin:4px 0 0;">Tahun 2024</p>
            </div>
          </div>
        </div>

      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { MOCK_MUSTAHIK, DESIL_COLORS } from '@/data/mockMustahik'
import { formatRupiah } from '@/utils/formatter'

const route = useRoute()
const mustahik = computed(() => MOCK_MUSTAHIK.find(m => m.nik_hashed === route.params.nikHashed))

function maskNIK(nik) {
  if (!nik) return '-'
  return nik.slice(0,6) + '****' + nik.slice(-4)
}

function desilDesc(d) {
  const map = { 1:'Sangat Miskin', 2:'Miskin', 3:'Hampir Miskin', 4:'Rentan Miskin' }
  return map[d] || '-'
}
</script>

<style scoped>
.detail-card { background:white; border-radius:14px; border:1px solid #f1f5f9; padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.section-title { font-size:13px; font-weight:700; color:#374151; margin:0 0 14px; display:flex; align-items:center; }
.field-list { display:flex; flex-direction:column; gap:10px; }
.field-row { display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #f8fafc; }
.field-row:last-child { border-bottom:none; }
.field-label { font-size:12px; color:#94a3b8; font-weight:500; }
.field-value { font-size:13px; color:#374151; font-weight:600; text-align:right; max-width:55%; }
.detail-grid { grid-template-columns:1fr 1fr; }
.bantuan-grid { grid-template-columns:repeat(3,1fr); }
@media(max-width:768px) {
  .detail-grid  { grid-template-columns:1fr; }
  .bantuan-grid { grid-template-columns:1fr; }
}
</style>
