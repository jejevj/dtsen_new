<template>
  <div
    style="position:relative;width:100%;border-radius:12px;overflow:hidden;background:#f0fdf4;"
    :style="{ height: height }"
  >
    <!-- Loading -->
    <div v-if="loading" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#f8fafc;z-index:10;gap:12px;">
      <div class="map-spinner"></div>
      <span style="font-size:13px;color:#64748b;font-family:Inter,sans-serif;">{{ loadingMsg }}</span>
    </div>

    <!-- Error -->
    <div v-if="error" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#fef2f2;z-index:10;gap:8px;">
      <i class="pi pi-exclamation-triangle" style="font-size:28px;color:#ef4444;"></i>
      <span style="font-size:13px;color:#dc2626;font-family:Inter,sans-serif;">Gagal memuat peta. Coba refresh halaman.</span>
    </div>

    <!-- Breadcrumb -->
    <div
      v-if="!loading && currentLevel > 1"
      style="position:absolute;top:12px;left:12px;z-index:1001;display:flex;align-items:center;gap:6px;flex-wrap:wrap;"
    >
      <button @click="drillUp(1)"
        style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:99px;background:white;border:1px solid #e2e8f0;font-size:12px;font-weight:600;color:#374151;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <i class="pi pi-home" style="font-size:11px;"></i> Provinsi
      </button>
      <span style="background:white;padding:5px 12px;border-radius:99px;font-size:12px;font-weight:700;color:#15803d;border:1px solid #dcfce7;box-shadow:0 2px 8px rgba(0,0,0,0.08);">{{ selectedProvinsiNama }}</span>
      <template v-if="currentLevel === 3">
        <i class="pi pi-chevron-right" style="font-size:10px;color:#94a3b8;"></i>
        <button @click="drillUp(2)"
          style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:99px;background:white;border:1px solid #e2e8f0;font-size:12px;font-weight:600;color:#374151;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
          <i class="pi pi-arrow-left" style="font-size:11px;"></i> Kab/Kota
        </button>
        <span style="background:white;padding:5px 12px;border-radius:99px;font-size:12px;font-weight:700;color:#d97706;border:1px solid #fef3c7;box-shadow:0 2px 8px rgba(0,0,0,0.08);">{{ selectedKabkotaNama }}</span>
      </template>
    </div>

    <div ref="mapRef" style="width:100%;height:100%;"></div>

    <!-- Legend -->
    <div v-if="!loading" style="position:absolute;bottom:16px;right:16px;background:white;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.12);padding:12px 14px;z-index:1000;min-width:140px;">
      <p style="font-size:11px;font-weight:700;color:#374151;margin:0 0 8px;text-transform:uppercase;letter-spacing:0.05em;">
        {{ metric === 'mustahik' ? 'Jml. Mustahik' : 'Pendistribusian' }}
      </p>
      <div v-for="step in currentLegend" :key="step.label" style="display:flex;align-items:center;gap:7px;margin-bottom:5px;">
        <div :style="{ width:'14px', height:'10px', borderRadius:'3px', background:step.color, flexShrink:0 }"></div>
        <span style="font-size:11px;color:#6b7280;">{{ step.label }}</span>
      </div>
      <div style="margin-top:8px;padding-top:8px;border-top:1px solid #f1f5f9;">
        <p style="font-size:10px;color:#94a3b8;margin:0;">
          <template v-if="currentLevel === 1">Klik provinsi &rarr; kab/kota</template>
          <template v-else-if="currentLevel === 2">Klik kab/kota &rarr; kecamatan</template>
          <template v-else>Klik kecamatan untuk detail</template>
        </p>
      </div>
    </div>

    <!-- Tooltip -->
    <transition name="fade">
      <div v-if="hovered"
        style="position:absolute;top:16px;left:50%;transform:translateX(-50%);background:white;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.12);padding:14px;z-index:1000;min-width:200px;pointer-events:none;">
        <p style="font-size:13px;font-weight:700;color:#1e293b;margin:0 0 10px;border-bottom:1px solid #f1f5f9;padding-bottom:8px;">{{ hovered.nama }}</p>
        <div style="display:flex;flex-direction:column;gap:6px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:12px;color:#64748b;"><i class="pi pi-users" style="font-size:10px;color:#3b82f6;"></i> Mustahik</span>
            <span style="font-size:12px;font-weight:600;color:#1e293b;">{{ (hovered.mustahik||0).toLocaleString('id-ID') }}</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:12px;color:#64748b;"><i class="pi pi-wallet" style="font-size:10px;color:#16a34a;"></i> Penyaluran</span>
            <span style="font-size:12px;font-weight:600;color:#15803d;">{{ formatRupiah(hovered.penyaluran||0) }}</span>
          </div>
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span style="font-size:12px;color:#64748b;"><i class="pi pi-building" style="font-size:10px;color:#7c3aed;"></i> LAZ Aktif</span>
            <span style="font-size:12px;font-weight:600;color:#1e293b;">{{ hovered.laz_count||0 }}</span>
          </div>
          <div v-if="currentLevel < 3" style="margin-top:4px;padding-top:6px;border-top:1px solid #f1f5f9;">
            <span style="font-size:11px;color:#16a34a;font-weight:600;">
              <i class="pi pi-hand-pointer" style="font-size:10px;"></i>
              {{ currentLevel === 1 ? 'Klik → lihat kab/kota' : 'Klik → lihat kecamatan' }}
            </span>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { formatRupiah } from '@/utils/formatter'
import ReportService from '@/services/report'

// ─────────────────────────────────────────────────────────────────────────────
//  GeoJSON level 3 diambil dari backend API.
//  Base URL diambil dari VITE_API_BASE_URL (sama dengan api.js),
//  sehingga request selalu ke domain backend (dtsenapi.ourtestcloud.my.id).
//  Endpoint: GET <VITE_API_BASE_URL>/geo/level3?provinsi=<NAME_1>&kabupaten=<NAME_2>
// ─────────────────────────────────────────────────────────────────────────────
const API_BASE = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
const GEO_LEVEL3_API = `${API_BASE}/geo/level3`

const props = defineProps({
  mapData:{ type: Array,  default: () => [] },
  height: { type: String, default: '480px' },
  metric: { type: String, default: 'mustahik' },
  tahun:  { type: [String, Number], default: new Date().getFullYear() },
})

const mapRef               = ref(null)
const loading              = ref(true)
const loadingMsg           = ref('Memuat peta Indonesia...')
const error                = ref(false)
const hovered              = ref(null)
const currentLevel         = ref(1)
const selectedProvinsiKode = ref(null)
const selectedProvinsiNama = ref('')
const selectedKabkotaKode  = ref(null)
const selectedKabkotaNama  = ref('')
const kabkotaData          = ref([])
const kecamatanData        = ref([])

let L               = null
let leafletMap      = null
let geojsonLayer    = null
let provinsiOutline = null
let kabkotaOutline  = null

let _provinsiGeoCache = null
let _kabkotaGeoCache  = null
let _kecGeoCache      = {}

// ── Color scales ─────────────────────────────────────────────────────────
const mustahikScaleProv  = [{min:0,max:30000,color:'#dcfce7'},{min:30000,max:80000,color:'#86efac'},{min:80000,max:150000,color:'#4ade80'},{min:150000,max:300000,color:'#16a34a'},{min:300000,max:Infinity,color:'#14532d'}]
const mustahikScaleKab   = [{min:0,max:5000,color:'#dcfce7'},{min:5000,max:15000,color:'#86efac'},{min:15000,max:30000,color:'#4ade80'},{min:30000,max:60000,color:'#16a34a'},{min:60000,max:Infinity,color:'#14532d'}]
const mustahikScaleKec   = [{min:0,max:1000,color:'#dcfce7'},{min:1000,max:3000,color:'#86efac'},{min:3000,max:6000,color:'#4ade80'},{min:6000,max:10000,color:'#16a34a'},{min:10000,max:Infinity,color:'#14532d'}]
const penyaluranScaleProv= [{min:0,max:100e9,color:'#dbeafe'},{min:100e9,max:300e9,color:'#93c5fd'},{min:300e9,max:600e9,color:'#3b82f6'},{min:600e9,max:1000e9,color:'#1d4ed8'},{min:1000e9,max:Infinity,color:'#1e3a8a'}]
const penyaluranScaleKab = [{min:0,max:30e9,color:'#dbeafe'},{min:30e9,max:80e9,color:'#93c5fd'},{min:80e9,max:150e9,color:'#3b82f6'},{min:150e9,max:250e9,color:'#1d4ed8'},{min:250e9,max:Infinity,color:'#1e3a8a'}]
const penyaluranScaleKec = [{min:0,max:5e9,color:'#dbeafe'},{min:5e9,max:15e9,color:'#93c5fd'},{min:15e9,max:30e9,color:'#3b82f6'},{min:30e9,max:50e9,color:'#1d4ed8'},{min:50e9,max:Infinity,color:'#1e3a8a'}]

const legendsProv = {
  mustahik:   [{color:'#dcfce7',label:'< 30 rb'},{color:'#86efac',label:'30–80 rb'},{color:'#4ade80',label:'80–150 rb'},{color:'#16a34a',label:'150–300 rb'},{color:'#14532d',label:'> 300 rb'}],
  penyaluran: [{color:'#dbeafe',label:'< 100 M'},{color:'#93c5fd',label:'100–300 M'},{color:'#3b82f6',label:'300–600 M'},{color:'#1d4ed8',label:'600 M–1 T'},{color:'#1e3a8a',label:'> 1 T'}],
}
const legendsKab = {
  mustahik:   [{color:'#dcfce7',label:'< 5 rb'},{color:'#86efac',label:'5–15 rb'},{color:'#4ade80',label:'15–30 rb'},{color:'#16a34a',label:'30–60 rb'},{color:'#14532d',label:'> 60 rb'}],
  penyaluran: [{color:'#dbeafe',label:'< 30 M'},{color:'#93c5fd',label:'30–80 M'},{color:'#3b82f6',label:'80–150 M'},{color:'#1d4ed8',label:'150–250 M'},{color:'#1e3a8a',label:'> 250 M'}],
}
const legendsKec = {
  mustahik:   [{color:'#dcfce7',label:'< 1 rb'},{color:'#86efac',label:'1–3 rb'},{color:'#4ade80',label:'3–6 rb'},{color:'#16a34a',label:'6–10 rb'},{color:'#14532d',label:'> 10 rb'}],
  penyaluran: [{color:'#dbeafe',label:'< 5 M'},{color:'#93c5fd',label:'5–15 M'},{color:'#3b82f6',label:'15–30 M'},{color:'#1d4ed8',label:'30–50 M'},{color:'#1e3a8a',label:'> 50 M'}],
}
const currentLegend = ref(legendsProv.mustahik)

function getColor(value, scale) {
  for (const s of scale) if (value >= s.min && value < s.max) return s.color
  return '#f1f5f9'
}
function getScaleByLevel(lv) {
  if (lv === 3) return props.metric === 'mustahik' ? mustahikScaleKec  : penyaluranScaleKec
  if (lv === 2) return props.metric === 'mustahik' ? mustahikScaleKab  : penyaluranScaleKab
  return props.metric === 'mustahik' ? mustahikScaleProv : penyaluranScaleProv
}
function getLegendByLevel(lv) {
  if (lv === 3) return legendsKec[props.metric]
  if (lv === 2) return legendsKab[props.metric]
  return legendsProv[props.metric]
}

// ── Normalisasi ──────────────────────────────────────────────────────────────
function normKab(str = '') {
  return str.toLowerCase()
    .replace(/^(kabupaten|kota|kab\.) /g, '')
    .replace(/daerah istimewa /g, '')
    .replace(/daerah khusus ibukota /g, '')
    .trim()
}
function normProv(str = '') { return str.toLowerCase().trim() }
function normMapData(str = '') {
  return str.toLowerCase()
    .replace(/kabupaten /g, 'kab. ').replace(/kepulauan /g, 'kep. ')
    .trim()
}
function normKec(str = '') { return str.toLowerCase().trim() }
function getProvNama(p) { return p.state || p.name || p.NAME_1 || p.PROVINSI || p.Propinsi || '' }

// ── GeoJSON loaders ──────────────────────────────────────────────────────────
const GEOJSON_PROVINSI = [
  'https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia.geojson',
  'https://raw.githubusercontent.com/benkoshy/indonesia/master/indonesia-provinces-simple.geojson',
]
const GEOJSON_KABKOTA = [
  'https://raw.githubusercontent.com/fahadh4ilyas/indonesia-geojson-archive/master/Indonesia_cities.geojson',
]

const PROV_NAME_TO_KODE = {
  'aceh' : '11',
  'sumatera utara' : '12',
  'sumatera barat' : '13',
  'riau' : '14',
  'jambi' : '15',
  'sumatera selatan' : '16',
  'bengkulu' : '17',
  'lampung' : '18',
  'kepulauan bangka belitung' : '19',
  'bangka-belitung' : '19',
  'kepulauan riau' : '21',
  'jakarta raya' : '31',
  'jawa barat' : '32',
  'jawa tengah' : '33',
  'yogyakarta' : '34',
  'jawa timur' : '35',
  'banten' : '36',
  'bali' : '51',
  'nusa tenggara barat' : '52',
  'nusa tenggara timur' : '53',
  'kalimantan barat' : '61',
  'kalimantan tengah' : '62',
  'kalimantan selatan' : '63',
  'kalimantan timur' : '64',
  'kalimantan utara' : '65',
  'sulawesi utara' : '71',
  'sulawesi tengah' : '72',
  'sulawesi selatan' : '73',
  'sulawesi tenggara' : '74',
  'gorontalo' : '75',
  'sulawesi barat' : '76',
  'maluku' : '81',
  'maluku utara' : '82',
  'papua barat' : '92',
  'papua' : '91',
}

async function fetchGeoJSON(urls) {
  const list = Array.isArray(urls) ? urls : [urls]
  for (const url of list) {
    try {
      const res = await fetch(url)
      if (!res.ok) continue
      const data = await res.json()
      if (data?.features?.length) return data
    } catch { /* skip */ }
  }
  return null
}

async function getProvinsiGeoJSON() {
  if (_provinsiGeoCache) return _provinsiGeoCache
  const geo = await fetchGeoJSON(GEOJSON_PROVINSI)
  if (geo) _provinsiGeoCache = geo
  return geo
}

async function getKabkotaGeoJSON() {
  if (_kabkotaGeoCache) return _kabkotaGeoCache
  loadingMsg.value = 'Memuat batas kabupaten/kota...'
  const geo = await fetchGeoJSON(GEOJSON_KABKOTA)
  if (geo) _kabkotaGeoCache = geo
  return geo
}

/**
 * Fetch GeoJSON kecamatan (level 3) dari backend API.
 * URL: <VITE_API_BASE_URL>/geo/level3?provinsi=...&kabupaten=...
 * Contoh: https://dtsenapi.ourtestcloud.my.id/api/v1/geo/level3?provinsi=Jambi&kabupaten=Bungo
 */
async function getKecamatanGeoJSON(kabkotaNama, provinsiNama) {
  const cacheKey = `${normProv(provinsiNama)}__${normKab(kabkotaNama)}`
  if (_kecGeoCache[cacheKey]) return _kecGeoCache[cacheKey]

  loadingMsg.value = `Memuat data kecamatan ${kabkotaNama}...`

  try {
    const params = new URLSearchParams({
      provinsi:  provinsiNama,
      kabupaten: kabkotaNama,
    })
    const res = await fetch(`${GEO_LEVEL3_API}?${params}`)

    if (!res.ok) {
      const errBody = await res.json().catch(() => ({}))
      //console.error('[Map] Backend geo/level3 error:', res.status, errBody.error || '')
      return null
    }

    const rawGeo = await res.json()

    if (!rawGeo?.features?.length) {
      console.warn('[Map] Tidak ada fitur kecamatan untuk:', provinsiNama, '/', kabkotaNama)
      return null
    }

    // Group per NAME_3 → MultiPolygon agar setiap feature = 1 kecamatan
    const byKec = {}
    for (const f of rawGeo.features) {
      const kec = f.properties.NAME_3 || 'Unknown'
      if (!byKec[kec]) byKec[kec] = []
      byKec[kec].push(f.geometry)
    }

    const features = Object.entries(byKec).map(([kecNama, geoms]) => {
      const polys = []
      for (const g of geoms) {
        if (g.type === 'Polygon')      polys.push(...g.coordinates)
        if (g.type === 'MultiPolygon') g.coordinates.forEach(mp => polys.push(...mp))
      }
      return {
        type: 'Feature',
        properties: { NAME_3: kecNama, NAME_2: kabkotaNama, NAME_1: provinsiNama },
        geometry: { type: 'MultiPolygon', coordinates: polys.map(p => [p]) },
      }
    })

    const result = { type: 'FeatureCollection', features }
    _kecGeoCache[cacheKey] = result
    return result

  } catch (e) {
    //console.error('[Map] Gagal fetch kecamatan GeoJSON dari backend:', e)
    return null
  }
}

// ── Render provinsi (level 1) ─────────────────────────────────────────────
async function renderProvinsiLayer() {
  loadingMsg.value = 'Memuat peta Indonesia...'
  const geojson = await getProvinsiGeoJSON()
  if (!geojson) { error.value = true; loading.value = false; return }
  clearOutlines()
  const lookup = {}
  props.mapData.forEach(d => { if (d.provinsi_nama) lookup[normMapData(d.provinsi_nama)] = d })
  const scale = getScaleByLevel(1)
  currentLegend.value = getLegendByLevel(1)
  if (geojsonLayer) { geojsonLayer.remove(); geojsonLayer = null }
  geojsonLayer = L.geoJSON(geojson, {
    style: feature => {
      const raw = getProvNama(feature.properties)
      const val = (lookup[normMapData(raw)] || {})[props.metric] || 0
      return { fillColor: getColor(val, scale), fillOpacity: val > 0 ? 0.85 : 0.3, color: '#ffffff', weight: 1.2, opacity: 1 }
    },
    onEachFeature: (feature, layer) => {
      const raw  = getProvNama(feature.properties) || 'Unknown'
      const data = props.mapData.find(d => normMapData(d.provinsi_nama) === normMapData(raw)) || {}
      layer.on({
        mouseover(e) { e.target.setStyle({ weight: 2.5, fillOpacity: 1, color: '#15803d' }); hovered.value = { nama: raw, ...data } },
        mouseout(e)  { geojsonLayer.resetStyle(e.target); hovered.value = null },
        click()      { drillDownKabkota(data.provinsi_kode || null, raw, layer) },
      })
    },
  }).addTo(leafletMap)
}

// ── Outline helpers ───────────────────────────────────────────────────────
function clearOutlines() {
  if (provinsiOutline) { provinsiOutline.remove(); provinsiOutline = null }
  if (kabkotaOutline)  { kabkotaOutline.remove();  kabkotaOutline  = null }
}
function renderProvinsiOutline(geojson, activeNama) {
  if (provinsiOutline) { provinsiOutline.remove(); provinsiOutline = null }
  const activeNorm = normProv(activeNama)
  provinsiOutline = L.geoJSON(geojson, {
    style: feature => {
      const isActive = normProv(getProvNama(feature.properties)) === activeNorm
      return isActive
        ? { fillColor: '#fef3c7', fillOpacity: 0.18, color: '#f97316', weight: 3.5, opacity: 1 }
        : { fillColor: '#94a3b8', fillOpacity: 0.08, color: '#64748b', weight: 1.5, opacity: 0.8 }
    },
    interactive: false,
  }).addTo(leafletMap)
  if (geojsonLayer)    geojsonLayer.bringToFront()
  if (provinsiOutline) provinsiOutline.bringToFront()
}
function renderKabkotaOutline(geojson, activeNama, provinsiNama) {
  if (kabkotaOutline) { kabkotaOutline.remove(); kabkotaOutline = null }
  const provNorm   = normProv(provinsiNama)
  const activeNorm = normKab(activeNama)
  kabkotaOutline = L.geoJSON(geojson, {
    style: feature => {
      const n1 = normProv(feature.properties.NAME_1 || '')
      if (n1 !== provNorm) return { stroke: false, fill: false }
      const isActive = normKab(feature.properties.NAME_2 || '') === activeNorm
      return isActive
        ? { fillColor: '#fef3c7', fillOpacity: 0.15, color: '#d97706', weight: 3, opacity: 1 }
        : { fillColor: 'transparent', fillOpacity: 0, color: '#94a3b8', weight: 1, opacity: 0.7 }
    },
    interactive: false,
  }).addTo(leafletMap)
  if (geojsonLayer)   geojsonLayer.bringToFront()
  if (kabkotaOutline) kabkotaOutline.bringToFront()
}

// ── Drill down kabkota (level 2) ────────────────────────────────────────
async function drillDownKabkota(provinsiKode, provinsiNama, clickedLayer) {
  loading.value = true; hovered.value = null
  currentLevel.value = 2
  selectedProvinsiKode.value = provinsiKode
  selectedProvinsiNama.value = provinsiNama
  selectedKabkotaKode.value  = null
  selectedKabkotaNama.value  = ''
  kecamatanData.value        = []
  if (clickedLayer) leafletMap.fitBounds(clickedLayer.getBounds(), { padding: [40, 40] })
  try {
    const data = await ReportService.getMapDataKabkota(props.tahun, provinsiKode)
    kabkotaData.value = Array.isArray(data) ? data : []
  } catch { kabkotaData.value = [] }
  const fullGeo = await getKabkotaGeoJSON()
  if (!fullGeo) { renderFallbackMarkers(kabkotaData.value, 2); loading.value = false; return }
  const targetNorm = normProv(provinsiNama)
  const filtered = {
    type: 'FeatureCollection',
    features: fullGeo.features.filter(f => {
      const n1 = normProv(f.properties.NAME_1 || '')
      return n1 === targetNorm || PROV_NAME_TO_KODE[n1] === provinsiKode
    }),
  }
  if (!filtered.features.length) { renderFallbackMarkers(kabkotaData.value, 2); loading.value = false; return }
  renderKabkotaLayer(filtered)
  const provGeo = await getProvinsiGeoJSON()
  if (provGeo) renderProvinsiOutline(provGeo, provinsiNama)
  loading.value = false
}

function renderKabkotaLayer(geojson) {
  const lookup = {}
  kabkotaData.value.forEach(d => { if (d.kabkota_nama) lookup[normKab(d.kabkota_nama)] = d })
  const scale = getScaleByLevel(2)
  currentLegend.value = getLegendByLevel(2)
  if (geojsonLayer) { geojsonLayer.remove(); geojsonLayer = null }
  geojsonLayer = L.geoJSON(geojson, {
    style: feature => {
      const raw = feature.properties.NAME_2 || feature.properties.KABKOTA || feature.properties.name || ''
      const val = (lookup[normKab(raw)] || {})[props.metric] || 0
      return { fillColor: getColor(val, scale), fillOpacity: val > 0 ? 0.85 : 0.35, color: '#ffffff', weight: 1, opacity: 1 }
    },
    onEachFeature: (feature, layer) => {
      const raw  = feature.properties.NAME_2 || feature.properties.KABKOTA || feature.properties.name || 'Unknown'
      const data = kabkotaData.value.find(d => normKab(d.kabkota_nama) === normKab(raw)) || {}
      layer.on({
        mouseover(e) { e.target.setStyle({ weight: 2, fillOpacity: 1, color: '#15803d' }); hovered.value = { nama: raw, ...data } },
        mouseout(e)  { geojsonLayer.resetStyle(e.target); hovered.value = null },
        // click()      { drillDownKecamatan(data.kabkota_kode || null, raw, layer) },
      })
    },
  }).addTo(leafletMap)
  if (provinsiOutline) provinsiOutline.bringToFront()
}

// ── Drill down kecamatan (level 3) ──────────────────────────────────────
async function drillDownKecamatan(kabkotaKode, kabkotaNama, clickedLayer) {
  loading.value = true; hovered.value = null
  currentLevel.value        = 3
  selectedKabkotaKode.value = kabkotaKode
  selectedKabkotaNama.value = kabkotaNama
  if (clickedLayer) leafletMap.fitBounds(clickedLayer.getBounds(), { padding: [40, 40] })
  try {
    const data = await ReportService.getMapDataKecamatan(props.tahun, kabkotaKode)
    kecamatanData.value = Array.isArray(data) ? data : []
  } catch { kecamatanData.value = [] }

  const kecGeo = await getKecamatanGeoJSON(kabkotaNama, selectedProvinsiNama.value)
  if (!kecGeo || !kecGeo.features.length) {
    renderFallbackMarkers(kecamatanData.value, 3)
    loading.value = false
    return
  }
  renderKecamatanLayer(kecGeo)
  const fullKabGeo = await getKabkotaGeoJSON()
  if (fullKabGeo) renderKabkotaOutline(fullKabGeo, kabkotaNama, selectedProvinsiNama.value)
  loading.value = false
}

function renderKecamatanLayer(geojson) {
  const lookup = {}
  kecamatanData.value.forEach(d => { if (d.kecamatan_nama) lookup[normKec(d.kecamatan_nama)] = d })
  const scale = getScaleByLevel(3)
  currentLegend.value = getLegendByLevel(3)
  if (geojsonLayer) { geojsonLayer.remove(); geojsonLayer = null }
  geojsonLayer = L.geoJSON(geojson, {
    style: feature => {
      const raw = feature.properties.NAME_3 || ''
      const val = (lookup[normKec(raw)] || {})[props.metric] || 0
      return { fillColor: getColor(val, scale), fillOpacity: val > 0 ? 0.85 : 0.35, color: '#ffffff', weight: 0.8, opacity: 1 }
    },
    onEachFeature: (feature, layer) => {
      const raw  = feature.properties.NAME_3 || 'Unknown'
      const data = kecamatanData.value.find(d => normKec(d.kecamatan_nama) === normKec(raw)) || {}
      layer.on({
        mouseover(e) { e.target.setStyle({ weight: 2, fillOpacity: 1, color: '#d97706' }); hovered.value = { nama: raw, ...data } },
        mouseout(e)  { geojsonLayer.resetStyle(e.target); hovered.value = null },
        click()      { leafletMap.fitBounds(layer.getBounds(), { padding: [20, 20] }) },
      })
    },
  }).addTo(leafletMap)
  if (kabkotaOutline)  kabkotaOutline.bringToFront()
  if (provinsiOutline) provinsiOutline.bringToFront()
}

// ── Fallback markers ───────────────────────────────────────────────────────────
function renderFallbackMarkers(dataset, level) {
  if (geojsonLayer) { geojsonLayer.remove(); geojsonLayer = null }
  const scale = getScaleByLevel(level)
  currentLegend.value = getLegendByLevel(level)
  const markers = L.layerGroup()
  const center  = leafletMap.getCenter()
  dataset.forEach((d, i) => {
    const angle  = (i / Math.max(dataset.length, 1)) * 2 * Math.PI
    const circle = L.circleMarker(
      [center.lat + 0.4 * Math.sin(angle), center.lng + 0.8 * Math.cos(angle)],
      { radius: Math.max(8, Math.min(22, (d.mustahik||3000)/2000)), fillColor: getColor(d[props.metric]||0, scale), fillOpacity: 0.85, color: '#ffffff', weight: 1.5 }
    )
    circle.on({ mouseover() { hovered.value = { nama: d.kecamatan_nama||d.kabkota_nama||'', ...d } }, mouseout() { hovered.value = null } })
    markers.addLayer(circle)
  })
  geojsonLayer = markers
  markers.addTo(leafletMap)
}

// ── Drill up ──────────────────────────────────────────────────────────────
async function drillUp(toLevel) {
  loading.value = true; hovered.value = null
  if (toLevel === 1) {
    currentLevel.value = 1
    selectedProvinsiKode.value = null; selectedProvinsiNama.value = ''
    selectedKabkotaKode.value  = null; selectedKabkotaNama.value  = ''
    kabkotaData.value = []; kecamatanData.value = []
    leafletMap.setView([-2.5, 118], 5)
    await renderProvinsiLayer()
  } else if (toLevel === 2) {
    currentLevel.value = 2
    selectedKabkotaKode.value = null; selectedKabkotaNama.value = ''
    kecamatanData.value = []
    if (kabkotaOutline) { kabkotaOutline.remove(); kabkotaOutline = null }
    const fullGeo    = await getKabkotaGeoJSON()
    const targetNorm = normProv(selectedProvinsiNama.value)
    const filtered   = fullGeo ? {
      type: 'FeatureCollection',
      features: fullGeo.features.filter(f => {
        const n1 = normProv(f.properties.NAME_1 || '')
        return n1 === targetNorm || PROV_NAME_TO_KODE[n1] === selectedProvinsiKode.value
      }),
    } : null
    if (filtered?.features.length) {
      renderKabkotaLayer(filtered)
      const provGeo = await getProvinsiGeoJSON()
      if (provGeo) renderProvinsiOutline(provGeo, selectedProvinsiNama.value)
    }
  }
  loading.value = false
}

// ── Init ───────────────────────────────────────────────────────────────────
async function initMap() {
  try {
    L = (await import('leaflet')).default || (await import('leaflet'))
    await import('leaflet/dist/leaflet.css')
    leafletMap = L.map(mapRef.value, {
      center: [-2.5, 118], zoom: 5, zoomControl: false,
      scrollWheelZoom: false, attributionControl: false, dragging: true,
    })
    L.control.zoom({ position: 'topright' }).addTo(leafletMap)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
      maxZoom: 14, subdomains: 'abcd',
    }).addTo(leafletMap)
    await renderProvinsiLayer()
    loading.value = false
  } catch (e) {
    //console.error('[Map] Init error:', e)
    loading.value = false; error.value = true
  }
}

watch(() => [props.metric, props.mapData], () => {
  if (!leafletMap || !L || !geojsonLayer?.eachLayer) return
  const lv = currentLevel.value
  const scale = getScaleByLevel(lv)
  currentLegend.value = getLegendByLevel(lv)
  geojsonLayer.eachLayer(layer => {
    if (!layer.feature) return
    const p = layer.feature.properties
    let raw, dataset, key
    if (lv === 3)      { raw = p.NAME_3 || ''; dataset = kecamatanData.value; key = 'kecamatan_nama' }
    else if (lv === 2) { raw = p.NAME_2 || p.KABKOTA || p.name || ''; dataset = kabkotaData.value; key = 'kabkota_nama' }
    else               { raw = getProvNama(p); dataset = props.mapData; key = 'provinsi_nama' }
    const norm = lv === 3 ? normKec : lv === 2 ? normKab : normMapData
    const data = dataset.find(d => norm(d[key]) === norm(raw)) || {}
    layer.setStyle({ fillColor: getColor(data[props.metric]||0, scale), fillOpacity: data[props.metric] > 0 ? 0.85 : 0.3 })
  })
}, { deep: true })

onMounted(initMap)
onUnmounted(() => { if (leafletMap) { leafletMap.remove(); leafletMap = null } })
</script>

<style scoped>
.map-spinner { width:36px;height:36px;border:3px solid #dcfce7;border-top-color:#16a34a;border-radius:50%;animation:spin 0.8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
