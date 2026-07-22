<template>
  <AppLayout>
    <div style="display:flex;flex-direction:column;gap:20px;">

      <!-- Back -->
      <button @click="$router.back()" style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border:1px solid #e2e8f0;border-radius:8px;background:white;font-size:13px;font-weight:600;cursor:pointer;color:#374151;width:fit-content;">
        <i class="pi pi-arrow-left" style="font-size:11px;"></i> Kembali
      </button>

      <!-- Loading -->
      <div v-if="loading" style="text-align:center;padding:60px;">
        <i class="pi pi-spin pi-spinner" style="font-size:32px;color:#cbd5e1;"></i>
        <p style="color:#94a3b8;margin-top:12px;font-size:13px;">Memuat data keluarga…</p>
      </div>

      <!-- Not found -->
      <div v-else-if="!kkDetail" style="text-align:center;padding:60px 20px;background:white;border-radius:14px;border:1px solid #f1f5f9;">
        <i class="pi pi-home" style="font-size:40px;color:#cbd5e1;"></i>
        <p style="color:#64748b;margin:12px 0 0;">Data keluarga tidak ditemukan</p>
        <p style="color:#94a3b8;font-size:12px;margin-top:4px;">No. KK: {{ maskNik(route.params.nkk) }}</p>
      </div>

      <template v-else>

        <!-- ===== HEADER IDENTITY KK ===== -->
        <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
          <div style="display:flex;align-items:flex-start;gap:20px;flex-wrap:wrap;">
            <div style="width:80px;height:80px;border-radius:16px;background:#f0fdf4;display:flex;align-items:center;justify-content:center;flex-shrink:0;border:2px solid #bbf7d0;">
              <i class="pi pi-home" style="font-size:32px;color:#15803d;"></i>
            </div>
            <div style="flex:1;min-width:0;">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px;">
                <h2 style="font-size:1.25rem;font-weight:800;color:#1e293b;margin:0;">{{ kkDetail.nama_kepala_keluarga ?? kkDetail.nama ?? 'Data Keluarga' }}</h2>
              </div>
              <p style="font-size:13px;color:#64748b;margin:0 0 4px;">No. KK: <strong style="color:#374151;font-family:monospace;">{{ maskNik(kkDetail.nomor_kartu_keluarga) }}</strong></p>
              <p v-if="kkDetail.alamat || kkDetail.nama_desa_kelurahan" style="font-size:12px;color:#94a3b8;margin:0;">
                <i class="pi pi-map-marker" style="font-size:10px;"></i>
                {{ [kkDetail.nama_desa_kelurahan, kkDetail.nama_kecamatan, kkDetail.nama_kabupaten_kota, kkDetail.nama_provinsi].filter(Boolean).join(', ') || kkDetail.alamat || '-' }}
              </p>
            </div>
          </div>
        </div>

        <!-- ===== BANNER DESIL ===== -->
        <div class="desil-banner" :style="desilBannerStyle(kkDetail.desil_nasional)">
          <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
            <div :style="desilIconStyle(kkDetail.desil_nasional)">
              <i class="pi pi-chart-bar" style="font-size:18px;"></i>
            </div>
            <div>
              <p style="font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;margin:0 0 2px;opacity:.75;">Desil Kesejahteraan Nasional</p>
              <p style="font-size:1.35rem;font-weight:900;margin:0;">
                Desil {{ kkDetail.desil_nasional ?? '-' }}
                <span style="font-size:13px;font-weight:500;margin-left:6px;opacity:.7;">{{ desilLabel(kkDetail.desil_nasional) }}</span>
              </p>
            </div>
            <div style="margin-left:auto;text-align:right;">
              <p style="font-size:11px;margin:0;opacity:.65;">Jumlah Anggota</p>
              <p style="font-size:1.1rem;font-family:monospace;font-weight:700;margin:0;">{{ kkMembers.length }} orang</p>
            </div>
          </div>
        </div>

        <!-- ===== DETAIL GROUPS KELUARGA ===== -->
        <template v-if="orderedKeluargaGroups.length">
          <template v-for="(rowPair, ri) in pairedKeluargaGroups" :key="'kk-'+ri">
            <div :class="rowPair.length === 2 ? 'grid-2' : ''">
              <div v-for="group in rowPair" :key="group.group" class="detail-card wm-card">
                <div class="wm-overlay" aria-hidden="true"><svg class="wm-svg" xmlns="http://www.w3.org/2000/svg"><defs><pattern :id="'wm-kk-'+slugGroup(group.group)" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><text x="10" y="40" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text><text x="10" y="70" font-family="Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text></pattern></defs><rect width="100%" height="100%" :fill="'url(#wm-kk-'+slugGroup(group.group)+')'" /></svg></div>
                <div style="position:relative;z-index:1;">
                  <p class="section-title"><i :class="groupIcon(group.group)"></i> {{ group.group }}</p>
                  <table class="info-table">
                    <tbody>
                      <tr v-for="field in group.fields" :key="field.field_key">
                        <td class="td-label">{{ field.field_label }}</td>
                        <td class="td-value">
                          <template v-if="isNikField(field.field_key)">
                            <span style="font-family:monospace;">{{ maskNik(kkDetail[field.field_key]) }}</span>
                          </template>
                          <template v-else-if="field.field_key === 'desil_nasional'">
                            <span :style="desilBadgeStyle(kkDetail.desil_nasional)">
                              Desil {{ kkDetail.desil_nasional ?? '-' }} — {{ desilLabel(kkDetail.desil_nasional) }}
                            </span>
                          </template>
                          <template v-else>{{ resolveValue(field.field_key, kkDetail[field.field_key]) }}</template>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </template>
        </template>

        <!-- ===== TABEL ANGGOTA KK ===== -->
        <div class="detail-card" style="display:flex;flex-direction:column;">
          <p class="section-title">
            <i class="pi pi-users"></i> Anggota dalam KK
            <span style="margin-left:auto;font-size:11px;font-weight:500;color:#94a3b8;font-family:monospace;">{{ maskNik(kkDetail.nomor_kartu_keluarga) }}</span>
          </p>
          <div v-if="loadingMembers" style="text-align:center;padding:30px;color:#94a3b8;font-size:12px;">
            <i class="pi pi-spin pi-spinner" style="font-size:20px;display:block;margin-bottom:8px;"></i>
            Memuat anggota KK…
          </div>
          <template v-else-if="kkMembers.length">
            <div style="overflow-x:auto;">
              <table class="kk-table">
                <thead><tr><th>Nama</th><th>NIK</th><th>Hub. Keluarga</th><th>L/P</th></tr></thead>
                <tbody>
                  <tr
                    v-for="m in kkMembers" :key="m.nomor_induk_kependudukan"
                    style="cursor:pointer;"
                    @click="goToAnggota(m.nomor_induk_kependudukan)"
                  >
                    <td>{{ m.nama ?? '-' }}</td>
                    <td style="font-family:monospace;font-size:11px;">
                      <span class="nik-link">{{ maskNik(m.nomor_induk_kependudukan) }}</span>
                    </td>
                    <td>{{ resolveValue('status_hubungan_keluarga', m.status_hubungan_keluarga) }}</td>
                    <td>
                      <span :style="{ padding:'2px 7px', borderRadius:'99px', fontSize:'10px', fontWeight:'700', background:isLakiVal(m.jenis_kelamin)?'#eff6ff':'#fdf2f8', color:isLakiVal(m.jenis_kelamin)?'#2563eb':'#db2777' }">
                        {{ isLakiVal(m.jenis_kelamin) ? 'L' : 'P' }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
          <div v-else style="text-align:center;padding:30px;color:#94a3b8;font-size:12px;">
            <i class="pi pi-users" style="font-size:24px;display:block;margin-bottom:8px;"></i>
            Data anggota KK tidak ditemukan
          </div>
        </div>

      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import api from '@/services/api'
import { useBaselineRefs } from '@/composables/useBaselineRefs'
import { useWatermark } from '@/composables/useWatermark'
import { maskNik } from '@/utils/formatter'

const route     = useRoute()
const router    = useRouter()

const loading        = ref(true)
const loadingMembers = ref(false)
const kkDetail       = ref(null)
const kkMembers      = ref([])
const keluargaGroups = ref([])

const { resolveValue, getDetailFields } = useBaselineRefs()
const { userIdentifier } = useWatermark()

const NIK_FIELDS = new Set([
  'nomor_induk_kependudukan', 'nik',
  'nomor_kartu_keluarga', 'nkk',
])
function isNikField(key) { return NIK_FIELDS.has(key) }

function isLakiVal(v) {
  const s = (v ?? '').toString()
  return s === '1' || s.toLowerCase() === 'l' || s.toLowerCase() === 'laki-laki'
}

function slugGroup(g) {
  return String(g).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

const PINNED_AFTER_KONDISI_RUMAH = ['Aset Bergerak', 'Aset Tidak Bergerak', 'Fasilitas Rumah']
function reorderKeluargaGroups(groups) {
  const pinnedNames = new Set(PINNED_AFTER_KONDISI_RUMAH)
  const rest   = groups.filter(g => !pinnedNames.has(g.group))
  const pinned = PINNED_AFTER_KONDISI_RUMAH.map(name => groups.find(g => g.group === name)).filter(Boolean)
  const anchorIdx = rest.findIndex(g => g.group === 'Kondisi Rumah')
  const insertAt  = anchorIdx >= 0 ? anchorIdx + 1 : rest.length
  return [...rest.slice(0, insertAt), ...pinned, ...rest.slice(insertAt)]
}

const orderedKeluargaGroups = computed(() => reorderKeluargaGroups(keluargaGroups.value))

const pairedKeluargaGroups = computed(() => {
  const r = []
  for (let i = 0; i < orderedKeluargaGroups.value.length; i += 2)
    r.push(orderedKeluargaGroups.value.slice(i, i + 2))
  return r
})

const GROUP_ICONS = {
  'Data Pribadi': 'pi pi-id-card',
  'Alamat KTP': 'pi pi-map-marker',
  'Alamat Domisili': 'pi pi-map',
  'Alamat': 'pi pi-map-marker',
  'Kondisi Rumah': 'pi pi-home',
  'Fasilitas Rumah': 'pi pi-home',
  'Aset Bergerak': 'pi pi-car',
  'Aset Tidak Bergerak': 'pi pi-building',
  'Ternak': 'pi pi-star',
  'Info Keluarga': 'pi pi-users',
  'Sosial Ekonomi': 'pi pi-wallet',
  'Bansos': 'pi pi-wallet',
  'Lainnya': 'pi pi-list',
}
function groupIcon(g) { return GROUP_ICONS[g] ?? 'pi pi-list' }

const DESIL_COLORS = [
  null,
  { bg:'#fef2f2', border:'#fecaca', text:'#991b1b', icon:'#fca5a5', label:'Desil 1' },
  { bg:'#fff7ed', border:'#fed7aa', text:'#9a3412', icon:'#fb923c', label:'Desil 2' },
  { bg:'#fefce8', border:'#fde68a', text:'#92400e', icon:'#fbbf24', label:'Desil 3' },
  { bg:'#fefce8', border:'#fde68a', text:'#a16207', icon:'#fbbf24', label:'Desil 4' },
  { bg:'#f0fdf4', border:'#bbf7d0', text:'#166534', icon:'#4ade80', label:'Desil 5' },
  { bg:'#f0fdf4', border:'#bbf7d0', text:'#15803d', icon:'#22c55e', label:'Desil 6' },
  { bg:'#ecfdf5', border:'#a7f3d0', text:'#065f46', icon:'#10b981', label:'Desil 7' },
  { bg:'#eff6ff', border:'#bfdbfe', text:'#1e40af', icon:'#60a5fa', label:'Desil 8' },
  { bg:'#eff6ff', border:'#bfdbfe', text:'#1d4ed8', icon:'#3b82f6', label:'Desil 9' },
  { bg:'#f5f3ff', border:'#ddd6fe', text:'#4c1d95', icon:'#a78bfa', label:'Desil 10' },
]
function _desilIdx(v) {
  const n = parseInt(String(v ?? '').trim())
  return (Number.isInteger(n) && n >= 1 && n <= 10) ? n : 0
}
function desilLabel(v) { return DESIL_COLORS[_desilIdx(v)]?.label ?? '' }
function desilBannerStyle(v) {
  const c = DESIL_COLORS[_desilIdx(v)]
  if (!c) return { background:'#f8fafc', border:'1px solid #e2e8f0', borderRadius:'14px', padding:'18px 22px', color:'#64748b' }
  return { background:c.bg, border:`1px solid ${c.border}`, borderRadius:'14px', padding:'18px 22px', color:c.text }
}
function desilIconStyle(v) {
  const c = DESIL_COLORS[_desilIdx(v)]
  if (!c) return { width:'44px', height:'44px', borderRadius:'12px', background:'#e2e8f0', display:'flex', alignItems:'center', justifyContent:'center', color:'#94a3b8', flexShrink:0 }
  return { width:'44px', height:'44px', borderRadius:'12px', background:c.icon+'33', display:'flex', alignItems:'center', justifyContent:'center', color:c.icon, flexShrink:0 }
}
function desilBadgeStyle(v) {
  const c = DESIL_COLORS[_desilIdx(v)]
  if (!c) return { padding:'2px 10px', borderRadius:'99px', fontSize:'11px', fontWeight:'600', background:'#f1f5f9', color:'#64748b', display:'inline-block' }
  return { padding:'2px 10px', borderRadius:'99px', fontSize:'11px', fontWeight:'700', background:c.bg, color:c.text, border:`1px solid ${c.border}`, display:'inline-block' }
}

function goToAnggota(nik) {
  if (!nik) return
  window.scrollTo({ top: 0, behavior: 'smooth' })
  router.push({ name: 'baseline-anggota-detail', params: { nik } })
}

async function loadKKDetail(nkk) {
  try {
    const res = await api.get('/baseline/keluarga', { params: { search: nkk } })
    const rows = res.data?.data ?? []
    kkDetail.value = rows.find(r => String(r.nomor_kartu_keluarga ?? '').trim() === nkk) ?? rows[0] ?? null
  } catch (e) {
    console.error('[KeluargaDetail] gagal load KK:', e)
  }
}

async function loadKKMembers(nkk) {
  loadingMembers.value = true
  try {
    const res = await api.get('/baseline/anggota/by-nkk', { params: { nkk } })
    kkMembers.value = res.data?.data ?? []
  } catch (e) {
    console.error('[KeluargaDetail] gagal load anggota:', e)
  } finally {
    loadingMembers.value = false
  }
}

async function init(nkk) {
  loading.value  = true
  kkDetail.value = null
  kkMembers.value = []
  const [kkGroups] = await Promise.all([
    getDetailFields('keluarga'),
    loadKKDetail(nkk),
  ])
  keluargaGroups.value = kkGroups
  loading.value = false
  loadKKMembers(nkk)
}

onMounted(() => init(String(route.params.nkk)))
</script>

<style scoped>
.grid-2     { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
@media(max-width:768px) { .grid-2 { grid-template-columns:1fr; } }
.detail-card  { background:white; border-radius:14px; border:1px solid #f1f5f9; padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.wm-card      { position:relative; overflow:hidden; }
.wm-overlay   { position:absolute; inset:0; z-index:0; pointer-events:none; user-select:none; }
.wm-svg       { display:block; width:100%; height:100%; }
.section-title { font-size:13px; font-weight:700; color:#374151; margin:0 0 14px; display:flex; align-items:center; gap:6px; }
.info-table   { width:100%; border-collapse:collapse; }
.info-table tr { border-bottom:1px solid #f8fafc; }
.info-table tr:last-child { border-bottom:none; }
.td-label { font-size:12px; color:#94a3b8; font-weight:500; padding:9px 4px; width:45%; vertical-align:top; }
.td-value { font-size:13px; color:#374151; font-weight:600; padding:9px 4px; text-align:right; }
.desil-banner { border-radius:14px; padding:18px 22px; }
.kk-table { width:100%; border-collapse:collapse; font-size:12px; }
.kk-table thead tr { background:#f8fafc; }
.kk-table th { padding:8px 10px; text-align:left; font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.4px; border-bottom:1px solid #f1f5f9; }
.kk-table td { padding:9px 10px; border-bottom:1px solid #f8fafc; color:#374151; font-weight:500; vertical-align:middle; }
.kk-table tr:last-child td { border-bottom:none; }
.kk-table tbody tr:hover td { background:#f8fafc; }
.nik-link { color:#2563eb; text-decoration:underline; cursor:pointer; }
</style>
