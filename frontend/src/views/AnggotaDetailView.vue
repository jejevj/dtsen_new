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
        <p style="color:#94a3b8;margin-top:12px;font-size:13px;">Memuat data…</p>
      </div>

      <!-- Not found -->
      <div v-else-if="!data" style="text-align:center;padding:60px 20px;background:white;border-radius:14px;border:1px solid #f1f5f9;">
        <i class="pi pi-user-minus" style="font-size:40px;color:#cbd5e1;"></i>
        <p style="color:#64748b;margin:12px 0 0;">Data anggota tidak ditemukan</p>
        <p style="color:#94a3b8;font-size:12px;margin-top:4px;">NIK: {{ route.params.nik }}</p>
      </div>

      <template v-else>

        <!-- ===== HEADER IDENTITY ===== -->
        <div style="background:white;border-radius:16px;border:1px solid #f1f5f9;padding:28px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">
          <div style="display:flex;align-items:flex-start;gap:20px;flex-wrap:wrap;">
            <div :style="{ width:'80px', height:'80px', borderRadius:'16px', background: isLaki?'#eff6ff':'#fdf2f8', display:'flex', alignItems:'center', justifyContent:'center', flexShrink:0, border:'2px solid '+(isLaki?'#bfdbfe':'#fbcfe8') }">
              <i class="pi pi-user" :style="{ fontSize:'32px', color: isLaki?'#2563eb':'#db2777' }"></i>
            </div>
            <div style="flex:1;min-width:0;">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px;">
                <h2 style="font-size:1.25rem;font-weight:800;color:#1e293b;margin:0;">{{ data.nama ?? '-' }}</h2>
                <span v-if="data.jenis_kelamin" :style="{ padding:'3px 10px', borderRadius:'99px', fontSize:'11px', fontWeight:'700', background:isLaki?'#eff6ff':'#fdf2f8', color:isLaki?'#2563eb':'#db2777' }">
                  {{ isLaki ? 'Laki-laki' : 'Perempuan' }}
                </span>
              </div>
              <p style="font-size:13px;color:#64748b;margin:0 0 4px;">NIK: <strong style="color:#374151;font-family:monospace;">{{ data.nomor_induk_kependudukan ?? '-' }}</strong></p>
              <p style="font-size:13px;color:#64748b;margin:0;">No. KK: <strong style="color:#374151;font-family:monospace;">{{ data.nomor_kartu_keluarga ?? '-' }}</strong></p>
            </div>
            <div style="display:flex;flex-direction:column;gap:6px;flex-shrink:0;">
              <span v-if="data.pbi_nas === '1'" style="padding:4px 12px;border-radius:99px;font-size:11px;font-weight:700;background:#fef3c7;color:#b45309;"><i class="pi pi-shield" style="font-size:10px;"></i> PBI Nasional</span>
              <span v-if="data.pbi_pemda === '1'" style="padding:4px 12px;border-radius:99px;font-size:11px;font-weight:700;background:#ede9fe;color:#6d28d9;"><i class="pi pi-shield" style="font-size:10px;"></i> PBI Pemda</span>
              <span v-if="data.pbi_nas !== '1' && data.pbi_pemda !== '1'" style="padding:4px 12px;border-radius:99px;font-size:11px;font-weight:600;background:#f1f5f9;color:#94a3b8;">Non PBI</span>
            </div>
          </div>
        </div>

        <!-- ===== FIELD GROUPS (individu) ===== -->
        <template v-if="detailGroups.length">
          <template v-for="(rowPair, ri) in pairedGroups" :key="ri">

            <!-- Stat-group -->
            <template v-if="rowPair.some(g => isStatGroup(g.group))">
              <div style="display:flex;flex-direction:column;gap:16px;">
                <div v-for="group in rowPair" :key="group.group" class="detail-card wm-card">
                  <div class="wm-overlay" aria-hidden="true"><svg class="wm-svg" xmlns="http://www.w3.org/2000/svg"><defs><pattern :id="'wm-'+slugGroup(group.group)" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><text x="10" y="40" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text><text x="10" y="70" font-family="Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text></pattern></defs><rect width="100%" height="100%" :fill="'url(#wm-'+slugGroup(group.group)+')'" /></svg></div>
                  <div style="position:relative;z-index:1;">
                    <p class="section-title"><i :class="groupIcon(group.group)"></i> {{ group.group }}</p>
                    <div class="grid-stat">
                      <div v-for="field in group.fields" :key="field.field_key" class="stat-box" :style="statBoxBg(field.field_key, data[field.field_key])">
                        <p class="stat-label">{{ field.field_label }}</p>
                        <template v-if="field.field_key === 'id_pelanggan_pln'">
                          <p style="font-size:1rem;font-family:monospace;font-weight:900;margin:0;" :style="{ color: data[field.field_key]?'#15803d':'#94a3b8' }">{{ data[field.field_key] ?? 'Tidak ada' }}</p>
                        </template>
                        <template v-else-if="field.field_key === 'pbi_nas'">
                          <p class="stat-val" :style="{ color: data[field.field_key]==='1'?'#b45309':'#94a3b8' }">{{ data[field.field_key]==='1' ? 'Terdaftar' : 'Tidak' }}</p>
                        </template>
                        <template v-else-if="field.field_key === 'pbi_pemda'">
                          <p class="stat-val" :style="{ color: data[field.field_key]==='1'?'#6d28d9':'#94a3b8' }">{{ data[field.field_key]==='1' ? 'Terdaftar' : 'Tidak' }}</p>
                        </template>
                        <template v-else>
                          <p class="stat-val" style="color:#374151;">{{ resolveValue(field.field_key, data[field.field_key]) }}</p>
                        </template>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </template>

            <!-- Disabilitas group: tabel 2-kolom (deteksi partial case-insensitive) -->
            <template v-else-if="rowPair.some(g => isDisabilitasGroup(g))">
              <div>
                <div v-for="group in rowPair" :key="group.group" class="detail-card wm-card">
                  <div class="wm-overlay" aria-hidden="true"><svg class="wm-svg" xmlns="http://www.w3.org/2000/svg"><defs><pattern :id="'wm-'+slugGroup(group.group)" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><text x="10" y="40" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text><text x="10" y="70" font-family="Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text></pattern></defs><rect width="100%" height="100%" :fill="'url(#wm-'+slugGroup(group.group)+')'" /></svg></div>
                  <div style="position:relative;z-index:1;">
                    <p class="section-title"><i :class="groupIcon(group.group)"></i> {{ group.group }}</p>
                    <table class="disab-table">
                      <thead>
                        <tr>
                          <th class="disab-th">Aspek</th>
                          <th class="disab-th" style="text-align:right;">Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="field in group.fields" :key="field.field_key" class="disab-tr">
                          <td class="disab-td-aspek">{{ stripDisabPrefix(field.field_label) }}</td>
                          <td class="disab-td-status">
                            <span :style="disabBadgeStyle(data[field.field_key])">{{ disabBadgeLabel(data[field.field_key]) }}</span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </template>

            <!-- Normal group -->
            <template v-else>
              <div :class="rowPair.length === 2 ? 'grid-2' : ''">
                <div v-for="group in rowPair" :key="group.group" class="detail-card wm-card">
                  <div class="wm-overlay" aria-hidden="true"><svg class="wm-svg" xmlns="http://www.w3.org/2000/svg"><defs><pattern :id="'wm-'+slugGroup(group.group)" x="0" y="0" width="320" height="120" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)"><text x="10" y="40" font-family="Inter,sans-serif" font-size="11" font-weight="700" letter-spacing="2" fill="rgba(15,23,42,0.09)">DO NOT COPY</text><text x="10" y="70" font-family="Inter,sans-serif" font-size="10" font-weight="600" letter-spacing="1" fill="rgba(15,23,42,0.07)">{{ userIdentifier }}</text></pattern></defs><rect width="100%" height="100%" :fill="'url(#wm-'+slugGroup(group.group)+')'" /></svg></div>
                  <div style="position:relative;z-index:1;">
                    <p class="section-title"><i :class="groupIcon(group.group)"></i> {{ group.group }}</p>
                    <table class="info-table">
                      <tbody>
                        <tr v-for="field in group.fields" :key="field.field_key">
                          <td class="td-label">{{ field.field_label }}</td>
                          <td class="td-value">
                            <template v-if="field.field_key === 'kelas_tertinggi_yang_diduduki'">{{ data[field.field_key] != null ? 'Kelas ' + data[field.field_key] : '-' }}</template>
                            <template v-else-if="field.field_key === 'tanggal_lahir'">{{ formatTanggal(data[field.field_key]) }}</template>
                            <template v-else-if="field.field_key === 'omzet_usaha_utama'">{{ data[field.field_key] ? formatRupiah(data[field.field_key]) : '-' }}</template>
                            <template v-else-if="field.field_key === 'jumlah_usaha'">{{ data[field.field_key] != null ? data[field.field_key] + ' usaha' : '-' }}</template>
                            <template v-else-if="field.field_key === 'jumlah_pekerja_yang_dibayar_dari_usaha_utama'">{{ data[field.field_key] ?? '-' }} orang</template>
                            <template v-else>{{ resolveValue(field.field_key, data[field.field_key]) }}</template>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </template>

          </template>
        </template>

        <div v-else-if="!loading" style="text-align:center;padding:40px;color:#94a3b8;font-size:13px;">
          <i class="pi pi-spin pi-spinner"></i> Memuat konfigurasi tampilan…
        </div>

        <!-- ===== KARTU KELUARGA SECTION ===== -->
        <div v-if="loadingKK" style="text-align:center;padding:20px;color:#94a3b8;font-size:12px;">
          <i class="pi pi-spin pi-spinner"></i> Memuat data keluarga…
        </div>
        <template v-else>

          <!-- Banner desil -->
          <div v-if="kkDetail" class="desil-banner" :style="desilBannerStyle(kkDetail.desil_nasional)">
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
                <p style="font-size:11px;margin:0;opacity:.65;">No. KK</p>
                <p style="font-size:12px;font-family:monospace;font-weight:700;margin:0;">{{ kkDetail.nomor_kartu_keluarga }}</p>
              </div>
            </div>
          </div>

          <!-- Detail Keluarga groups -->
          <template v-if="kkDetail && keluargaGroups.length">
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
                          <td class="td-value">{{ resolveValue(field.field_key, kkDetail[field.field_key]) }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </template>
          </template>

          <!-- Tabel Anggota KK -->
          <div class="detail-card" style="display:flex;flex-direction:column;">
            <p class="section-title">
              <i class="pi pi-users"></i> Anggota dalam KK
              <span style="margin-left:auto;font-size:11px;font-weight:500;color:#94a3b8;font-family:monospace;">{{ data.nomor_kartu_keluarga ?? '-' }}</span>
            </p>
            <template v-if="kkMembers.length">
              <div style="overflow-x:auto;">
                <table class="kk-table">
                  <thead><tr><th>Nama</th><th>NIK</th><th>Hub. Keluarga</th><th>L/P</th></tr></thead>
                  <tbody>
                    <tr
                      v-for="m in kkMembers" :key="m.nomor_induk_kependudukan"
                      :class="{ 'kk-active-row': m.nomor_induk_kependudukan === data.nomor_induk_kependudukan }"
                      style="cursor:pointer;" @click="goToMember(m.nomor_induk_kependudukan)"
                    >
                      <td><span v-if="m.nomor_induk_kependudukan === data.nomor_induk_kependudukan" class="kk-you-badge">Ini</span>{{ m.nama ?? '-' }}</td>
                      <td style="font-family:monospace;font-size:11px;">{{ m.nomor_induk_kependudukan ?? '-' }}</td>
                      <td>{{ resolveValue('status_hubungan_keluarga', m.status_hubungan_keluarga) }}</td>
                      <td><span :style="{ padding:'2px 7px', borderRadius:'99px', fontSize:'10px', fontWeight:'700', background:isLakiVal(m.jenis_kelamin)?'#eff6ff':'#fdf2f8', color:isLakiVal(m.jenis_kelamin)?'#2563eb':'#db2777' }">{{ isLakiVal(m.jenis_kelamin)?'L':'P' }}</span></td>
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

      </template>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AppLayout from '@/components/layout/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import { fetchBaselineProvinsi } from '@/services/baselineService'
import { useBaselineRefs } from '@/composables/useBaselineRefs'

const route     = useRoute()
const router    = useRouter()
const authStore = useAuthStore()

const loading        = ref(true)
const data           = ref(null)
const detailGroups   = ref([])
const keluargaGroups = ref([])
const loadingKK      = ref(false)
const kkMembers      = ref([])
const kkDetail       = ref(null)

const { resolveValue, getDetailFields } = useBaselineRefs()

const userIdentifier = computed(() => {
  const u = authStore.user
  if (!u) return 'CONFIDENTIAL'
  return u.email || u.tuser_email || u.notelp || u.user_id || 'CONFIDENTIAL'
})

// Kunci field disabilitas — dipakai juga untuk deteksi group
const DISAB_KEYS = new Set([
  'penglihatan', 'pendengaran', 'berbicara_komunikasi',
  'berjalan_atau_naik_tangga', 'menggunakan_tangan_jari',
  'mengingat_berkonsentrasi', 'mengurus_diri',
  'belajar_kemampuan_intelektual', 'pengendalian_perilaku', 'kesedihan_depresi',
])

/**
 * Sebuah group dianggap "disabilitas" jika:
 *   (a) nama group mengandung kata "disabilitas" (case-insensitive), ATAU
 *   (b) mayoritas field-nya adalah field disabilitas
 */
function isDisabilitasGroup(group) {
  if (!group) return false
  const nameLower = (group.group ?? '').toLowerCase()
  if (nameLower.includes('disabilitas')) return true
  const fields = group.fields ?? []
  if (!fields.length) return false
  const disabCount = fields.filter(f => DISAB_KEYS.has(f.field_key)).length
  return disabCount / fields.length >= 0.5
}

/** Hapus prefix "Disabilitas: " atau "Disabilitas " dari label */
function stripDisabPrefix(label) {
  return String(label ?? '').replace(/^disabilitas[:\s]+/i, '').trim() || label
}

function slugGroup(g) {
  return String(g).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

const STAT_GROUPS = new Set(['Sosial Ekonomi', 'Lainnya', 'Bansos'])
function isStatGroup(g) { return STAT_GROUPS.has(g) }

function statBoxBg(key, val) {
  if (key === 'pbi_nas')          return { background: val==='1' ? '#fefce8' : '#f8fafc' }
  if (key === 'pbi_pemda')        return { background: val==='1' ? '#ede9fe' : '#f8fafc' }
  if (key === 'id_pelanggan_pln') return { background: val ? '#f0fdf4' : '#f8fafc' }
  return { background: '#f8fafc' }
}

const DISAB_LEVELS = {
  '0': { label: 'Tidak mengalami kesulitan', bg: '#f0fdf4', color: '#15803d' },
  '1': { label: 'Ya, sedikit kesulitan',     bg: '#fefce8', color: '#a16207' },
  '2': { label: 'Ya, banyak kesulitan',      bg: '#fff7ed', color: '#c2410c' },
  '3': { label: 'Tidak bisa sama sekali',    bg: '#fef2f2', color: '#b91c1c' },
}
function disabBadgeLabel(v) {
  const s = String(v ?? '').trim()
  return (DISAB_LEVELS[s] ?? DISAB_LEVELS['0']).label
}
function disabBadgeStyle(v) {
  const s = String(v ?? '').trim()
  const lvl = DISAB_LEVELS[s] ?? DISAB_LEVELS['0']
  return {
    background: lvl.bg, color: lvl.color,
    padding: '2px 10px', borderRadius: '99px',
    fontSize: '11px', fontWeight: '600', whiteSpace: 'nowrap',
    display: 'inline-block',
  }
}

// Desil banner
const DESIL_COLORS = [
  null,
  { bg:'#fef2f2', border:'#fecaca', text:'#991b1b', icon:'#fca5a5', label:'Sangat Miskin' },
  { bg:'#fff7ed', border:'#fed7aa', text:'#9a3412', icon:'#fb923c', label:'Miskin' },
  { bg:'#fefce8', border:'#fde68a', text:'#92400e', icon:'#fbbf24', label:'Hampir Miskin' },
  { bg:'#fefce8', border:'#fde68a', text:'#a16207', icon:'#fbbf24', label:'Rentan Miskin' },
  { bg:'#f0fdf4', border:'#bbf7d0', text:'#166534', icon:'#4ade80', label:'Menengah Bawah' },
  { bg:'#f0fdf4', border:'#bbf7d0', text:'#15803d', icon:'#22c55e', label:'Menengah' },
  { bg:'#ecfdf5', border:'#a7f3d0', text:'#065f46', icon:'#10b981', label:'Menengah Atas' },
  { bg:'#eff6ff', border:'#bfdbfe', text:'#1e40af', icon:'#60a5fa', label:'Sejahtera' },
  { bg:'#eff6ff', border:'#bfdbfe', text:'#1d4ed8', icon:'#3b82f6', label:'Sangat Sejahtera' },
  { bg:'#f5f3ff', border:'#ddd6fe', text:'#4c1d95', icon:'#a78bfa', label:'Paling Sejahtera' },
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

const pairedGroups = computed(() => _pair(detailGroups.value))
const pairedKeluargaGroups = computed(() => _pair(keluargaGroups.value))
function _pair(arr) {
  const r = []
  for (let i = 0; i < arr.length; i += 2) r.push(arr.slice(i, i + 2))
  return r
}

const isLaki = computed(() => isLakiVal(data.value?.jenis_kelamin))
function isLakiVal(v) {
  const s = (v ?? '').toString()
  return s === '1' || s.toLowerCase() === 'l' || s.toLowerCase() === 'laki-laki'
}

const GROUP_ICONS = {
  'Data Pribadi': 'pi pi-id-card', 'Alamat KTP': 'pi pi-map-marker',
  'Alamat Domisili': 'pi pi-map', 'Pendidikan': 'pi pi-book',
  'Pekerjaan': 'pi pi-briefcase', 'Pekerjaan & Usaha': 'pi pi-briefcase',
  'Kesehatan': 'pi pi-heart', 'Disabilitas': 'pi pi-accessibility',
  'Kesehatan & Disabilitas': 'pi pi-heart',
  'Sosial Ekonomi': 'pi pi-wallet', 'Bansos': 'pi pi-wallet', 'Lainnya': 'pi pi-list',
  'Kondisi Rumah': 'pi pi-home', 'Fasilitas Rumah': 'pi pi-home',
  'Aset Bergerak': 'pi pi-car', 'Aset Tidak Bergerak': 'pi pi-building',
  'Ternak': 'pi pi-star', 'Info Keluarga': 'pi pi-users',
  'Alamat': 'pi pi-map-marker',
}
function groupIcon(g) {
  const lower = (g ?? '').toLowerCase()
  if (lower.includes('disabilitas')) return 'pi pi-accessibility'
  return GROUP_ICONS[g] ?? 'pi pi-list'
}

function goToMember(nik) {
  if (!nik || nik === data.value?.nomor_induk_kependudukan) return
  router.push({ name: 'AnggotaDetail', params: { nik } })
}

async function loadData() {
  const nik = route.params.nik
  try {
    const provinsiList = await fetchBaselineProvinsi()
    for (const prov of provinsiList) {
      const res = await api.get('/baseline/anggota', { params: { provinsi: prov.kode, search: nik } })
      const found = (res.data?.data ?? []).find(r => r.nomor_induk_kependudukan === nik || r.nik === nik)
      if (found) { data.value = found; break }
    }
  } catch (e) { console.error('[AnggotaDetail] gagal load:', e) }
}

async function loadKKData(nkk) {
  if (!nkk) return
  loadingKK.value = true
  kkMembers.value = []
  kkDetail.value  = null
  try {
    const [anggotaRes, keluargaRes] = await Promise.all([
      api.get('/baseline/anggota/by-nkk', { params: { nkk } }),
      api.get('/baseline/keluarga', { params: { search: nkk } }),
    ])
    kkMembers.value = anggotaRes.data?.data ?? []
    const kkRows    = keluargaRes.data?.data ?? []
    kkDetail.value  = kkRows.find(r => String(r.nomor_kartu_keluarga ?? '').trim() === nkk) ?? kkRows[0] ?? null
  } catch (e) {
    console.error('[AnggotaDetail] gagal load KK:', e)
  } finally {
    loadingKK.value = false
  }
}

function formatTanggal(v) {
  if (!v) return '-'
  const str = String(v).includes('T') ? v : v + 'T00:00:00'
  const d = new Date(str)
  return isNaN(d.getTime()) ? String(v) : d.toLocaleDateString('id-ID', { day:'2-digit', month:'long', year:'numeric' })
}
function formatRupiah(n) {
  if (!n && n !== 0) return '-'
  return 'Rp ' + Number(n).toLocaleString('id-ID')
}

onMounted(async () => {
  loading.value = true
  const [indGroups, kkGroups] = await Promise.all([
    getDetailFields('individu'),
    getDetailFields('keluarga'),
    loadData(),
  ])
  detailGroups.value   = indGroups
  keluargaGroups.value = kkGroups
  loading.value = false
  if (data.value?.nomor_kartu_keluarga) loadKKData(data.value.nomor_kartu_keluarga)
})
</script>

<style scoped>
.grid-2    { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.grid-stat { display:grid; grid-template-columns:repeat(auto-fill, minmax(140px, 1fr)); gap:12px; }
@media(max-width:768px) { .grid-2 { grid-template-columns:1fr; } .grid-stat { grid-template-columns:1fr 1fr; } }
.detail-card { background:white; border-radius:14px; border:1px solid #f1f5f9; padding:22px; box-shadow:0 1px 4px rgba(0,0,0,0.04); }
.wm-card { position:relative; overflow:hidden; }
.wm-overlay { position:absolute; inset:0; z-index:0; pointer-events:none; user-select:none; }
.wm-svg { display:block; width:100%; height:100%; }
.section-title { font-size:13px; font-weight:700; color:#374151; margin:0 0 14px; display:flex; align-items:center; gap:6px; }
.info-table { width:100%; border-collapse:collapse; }
.info-table tr { border-bottom:1px solid #f8fafc; }
.info-table tr:last-child { border-bottom:none; }
.td-label { font-size:12px; color:#94a3b8; font-weight:500; padding:9px 4px; width:45%; vertical-align:top; }
.td-value  { font-size:13px; color:#374151; font-weight:600; padding:9px 4px; text-align:right; }
.stat-box  { border-radius:10px; padding:16px; }
.stat-label { font-size:11px; color:#64748b; font-weight:600; text-transform:uppercase; letter-spacing:.5px; margin:0 0 4px; }
.stat-val   { font-size:1.25rem; font-weight:900; margin:0; }
/* ---- Disabilitas tabel ---- */
.disab-table { width:100%; border-collapse:collapse; }
.disab-th { font-size:10px; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:.4px; padding:6px 8px 8px; border-bottom:2px solid #f1f5f9; }
.disab-tr { border-bottom:1px solid #f8fafc; transition:background .15s; }
.disab-tr:last-child { border-bottom:none; }
.disab-tr:hover { background:#f8fafc; }
.disab-td-aspek  { font-size:12px; color:#374151; font-weight:500; padding:9px 8px; width:55%; }
.disab-td-status { font-size:12px; padding:9px 8px; text-align:right; }
/* ---- Desil banner ---- */
.desil-banner { border-radius:14px; padding:18px 22px; }
/* ---- KK table ---- */
.kk-table { width:100%; border-collapse:collapse; font-size:12px; }
.kk-table thead tr { background:#f8fafc; }
.kk-table th { padding:8px 10px; text-align:left; font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.4px; border-bottom:1px solid #f1f5f9; }
.kk-table td { padding:9px 10px; border-bottom:1px solid #f8fafc; color:#374151; font-weight:500; vertical-align:middle; }
.kk-table tr:last-child td { border-bottom:none; }
.kk-table tbody tr:hover td { background:#f8fafc; }
.kk-active-row td { background:#eff6ff !important; }
.kk-you-badge { display:inline-block; padding:1px 6px; border-radius:99px; font-size:10px; font-weight:700; background:#2563eb; color:white; margin-right:5px; vertical-align:middle; }
</style>
