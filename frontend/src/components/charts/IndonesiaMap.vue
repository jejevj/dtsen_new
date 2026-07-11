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

    <!-- Breadcrumb drill-down -->
    <div
      v-if="!loading && currentLevel > 1"
      style="position:absolute;top:12px;left:12px;z-index:1001;display:flex;align-items:center;gap:6px;flex-wrap:wrap;"
    >
      <!-- Tombol kembali ke provinsi (dari level 2 atau 3) -->
      <button
        @click="drillUp(1)"
        style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:99px;background:white;border:1px solid #e2e8f0;font-size:12px;font-weight:600;color:#374151;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.1);"
      >
        <i class="pi pi-home" style="font-size:11px;"></i>
        Provinsi
      </button>

      <!-- Label provinsi aktif (level 2 & 3) -->
      <span style="background:white;padding:5px 12px;border-radius:99px;font-size:12px;font-weight:700;color:#15803d;border:1px solid #dcfce7;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        {{ selectedProvinsiNama }}
      </span>

      <!-- Pemisah + tombol kembali ke kabkota (hanya level 3) -->
      <template v-if="currentLevel === 3">
        <i class="pi pi-chevron-right" style="font-size:10px;color:#94a3b8;"></i>
        <button
          @click="drillUp(2)"
          style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:99px;background:white;border:1px solid #e2e8f0;font-size:12px;font-weight:600;color:#374151;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.1);"
        >
          <i class="pi pi-arrow-left" style="font-size:11px;"></i>
          Kab/Kota
        </button>
        <span style="background:white;padding:5px 12px;border-radius:99px;font-size:12px;font-weight:700;color:#d97706;border:1px solid #fef3c7;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
          {{ selectedKabkotaNama }}
        </span>
      </template>
    </div>

    <!-- Map container -->
    <div ref="mapRef" style="width:100%;height:100%;"></div>

    <!-- Legend -->
    <div v-if="!loading" style="position:absolute;bottom:16px;right:16px;background:white;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.12);padding:12px 14px;z-index:1000;min-width:140px;">
      <p style="font-size:11px;font-weight:700;color:#374151;margin:0 0 8px;text-transform:uppercase;letter-spacing:0.05em;">
        {{ metric === 'mustahik' ? 'Jml. Mustahik' : 'Penyaluran' }}
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

    <!-- Tooltip hover -->
    <transition name="fade">
      <div
        v-if="hovered"
        style="position:absolute;top:16px;left:50%;transform:translateX(-50%);background:white;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.12);padding:14px;z-index:1000;min-width:200px;pointer-events:none;"
      >
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
import ReportService   from '@/services/report'

const props = defineProps({
  mapData: { type: Array,  default: () => [] },
  height:  { type: String, default: '480px' },
  metric:  { type: String, default: 'mustahik' },
})

const mapRef               = ref(null)
const loading              = ref(true)
const loadingMsg           = ref('Memuat peta Indonesia...')
const error                = ref(false)
const hovered              = ref(null)
const currentLevel         = ref(1)          // 1=provinsi, 2=kabkota, 3=kecamatan
const selectedProvinsiKode = ref(null)
const selectedProvinsiNama = ref('')
const selectedKabkotaKode  = ref(null)
const selectedKabkotaNama  = ref('')
const kabkotaData          = ref([])
const kecamatanData        = ref([])

let L                 = null
let leafletMap        = null
let geojsonLayer      = null     // layer aktif (provinsi / kabkota / kecamatan)
let provinsiOutline   = null     // outline batas provinsi (level 2 & 3)
let kabkotaOutline    = null     // outline batas kabkota (level 3)
let _provinsiGeoCache = null
let _kabkotaGeoCache  = null
let _kecGeoCache      = {}       // key: kabkota_kode → FeatureCollection

// ── Color scales ─────────────────────────────────────────────────────────
const mustahikScaleProv = [{min:0,max:30000,color:'#dcfce7'},{min:30000,max:80000,color:'#86efac'},{min:80000,max:150000,color:'#4ade80'},{min:150000,max:300000,color:'#16a34a'},{min:300000,max:Infinity,color:'#14532d'}]
const mustahikScaleKab  = [{min:0,max:5000,color:'#dcfce7'},{min:5000,max:15000,color:'#86efac'},{min:15000,max:30000,color:'#4ade80'},{min:30000,max:60000,color:'#16a34a'},{min:60000,max:Infinity,color:'#14532d'}]
const mustahikScaleKec  = [{min:0,max:1000,color:'#dcfce7'},{min:1000,max:3000,color:'#86efac'},{min:3000,max:6000,color:'#4ade80'},{min:6000,max:10000,color:'#16a34a'},{min:10000,max:Infinity,color:'#14532d'}]
const penyaluranScaleProv = [{min:0,max:100e9,color:'#dbeafe'},{min:100e9,max:300e9,color:'#93c5fd'},{min:300e9,max:600e9,color:'#3b82f6'},{min:600e9,max:1000e9,color:'#1d4ed8'},{min:1000e9,max:Infinity,color:'#1e3a8a'}]
const penyaluranScaleKab  = [{min:0,max:30e9,color:'#dbeafe'},{min:30e9,max:80e9,color:'#93c5fd'},{min:80e9,max:150e9,color:'#3b82f6'},{min:150e9,max:250e9,color:'#1d4ed8'},{min:250e9,max:Infinity,color:'#1e3a8a'}]
const penyaluranScaleKec  = [{min:0,max:5e9,color:'#dbeafe'},{min:5e9,max:15e9,color:'#93c5fd'},{min:15e9,max:30e9,color:'#3b82f6'},{min:30e9,max:50e9,color:'#1d4ed8'},{min:50e9,max:Infinity,color:'#1e3a8a'}]

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
  for (const s of scale) { if (value >= s.min && value < s.max) return s.color }
  return '#f1f5f9'
}
function getScaleByLevel(level) {
  if (level === 3) return props.metric === 'mustahik' ? mustahikScaleKec : penyaluranScaleKec
  if (level === 2) return props.metric === 'mustahik' ? mustahikScaleKab  : penyaluranScaleKab
  return props.metric === 'mustahik' ? mustahikScaleProv : penyaluranScaleProv
}
function getLegendByLevel(level) {
  if (level === 3) return legendsKec[props.metric]
  if (level === 2) return legendsKab[props.metric]
  return legendsProv[props.metric]
}

// ── GeoJSON sources ───────────────────────────────────────────────────────
const GEOJSON_PROVINSI = [
  'https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia.geojson',
  'https://raw.githubusercontent.com/benkoshy/indonesia/master/indonesia-provinces-simple.geojson',
  'https://raw.githubusercontent.com/rizafahmi/geojson-indonesia/master/prov.json',
]
const GEOJSON_KABKOTA_ALL = [
  'https://raw.githubusercontent.com/fahadh4ilyas/indonesia-geojson-archive/master/Indonesia_cities.geojson',
]
// Level-3: subdistrict GeoJSON (GADM level-3, field NAME_2=kabkota, NAME_3=kecamatan)
// File besar (~60MB), di-fetch sekali lalu di-cache + filter per kabkota
const GEOJSON_KECAMATAN_ALL = [
  'https://raw.githubusercontent.com/fahadh4ilyas/indonesia-geojson-archive/master/Indonesia_subdistrict.geojson',
]

const PROV_NAME_TO_KODE = {
  'aceh':'11','sumatera utara':'12','sumatera barat':'13','riau':'14','jambi':'15',
  'sumatera selatan':'16','bengkulu':'17','lampung':'18',
  'kepulauan bangka belitung':'19','bangka belitung':'19','kepulauan riau':'21',
  'dki jakarta':'31','jawa barat':'32','jawa tengah':'33','di yogyakarta':'34',
  'jawa timur':'35','banten':'36','bali':'51',
  'nusa tenggara barat':'52','nusa tenggara timur':'53',
  'kalimantan barat':'61','kalimantan tengah':'62','kalimantan selatan':'63',
  'kalimantan timur':'64','kalimantan utara':'65',
  'sulawesi utara':'71','sulawesi tengah':'72','sulawesi selatan':'73',
  'sulawesi tenggara':'74','gorontalo':'75','sulawesi barat':'76',
  'maluku':'81','maluku utara':'82','papua barat':'91','papua':'94',
}

async function fetchGeoJSON(urls) {
  const list = Array.isArray(urls) ? urls : [urls]
  for (const url of list) {
    try {
      const res = await fetch(url)
      if (!res.ok) { console.warn('[Map] 404:', url); continue }
      const data = await res.json()
      if (data?.features?.length) return data
    } catch (e) { console.warn('[Map] fetch error:', url, e) }
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
  const geo = await fetchGeoJSON(GEOJSON_KABKOTA_ALL)
  if (geo) _kabkotaGeoCache = geo
  return geo
}
// Kecamatan GeoJSON — filter per kabkota, cache per kabkota_kode
async function getKecamatanGeoJSON(kabkotaNama) {
  const key = kabkotaNama.toLowerCase()
  if (_kecGeoCache[key]) return _kecGeoCache[key]
  loadingMsg.value = 'Memuat batas kecamatan (pertama kali, mohon tunggu...)'
  // Ambil kabkota geo yang sudah ada (sudah difilter provinsi), gunakan NAME_2 sebagai kunci
  const fullGeo = await fetchGeoJSON(GEOJSON_KECAMATAN_ALL)
  if (!fullGeo) return null
  const normTarget = normKab(kabkotaNama)
  const filtered = {
    type: 'FeatureCollection',
    features: fullGeo.features.filter(f => {
      const n2 = normKab(f.properties.NAME_2 || '')
      return n2 === normTarget
    }),
  }
  if (filtered.features.length) _kecGeoCache[key] = filtered
  return filtered.features.length ? filtered : null
}

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
    .replace(/kabupaten /g, 'kab. ').replace(/daerah istimewa /g, 'di ')
    .replace(/daerah khusus ibukota /g, 'dki ').replace(/kepulauan /g, 'kep. ')
    .trim()
}
function normKec(str = '') { return str.toLowerCase().trim() }
function getProvNama(p) { return p.state || p.name || p.NAME_1 || p.PROVINSI || p.Propinsi || '' }

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
    style: (feature) => {
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
    style: (feature) => {
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
  // Tampilkan outline semua kabkota dalam provinsi aktif
  // Kabkota aktif: stroke oranye tua tebal, kabkota lain: stroke abu tipis
  if (kabkotaOutline) { kabkotaOutline.remove(); kabkotaOutline = null }
  const provNorm    = normProv(provinsiNama)
  const activeNorm  = normKab(activeNama)
  kabkotaOutline = L.geoJSON(geojson, {
    style: (feature) => {
      const n1 = normProv(feature.properties.NAME_1 || '')
      if (n1 !== provNorm) return { stroke: false, fill: false }   // luar provinsi: tidak tampil
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

// ── Drill down ke kabkota (level 2) ──────────────────────────────────────
async function drillDownKabkota(provinsiKode, provinsiNama, clickedLayer) {
  loading.value = true; hovered.value = null
  currentLevel.value         = 2
  selectedProvinsiKode.value = provinsiKode
  selectedProvinsiNama.value = provinsiNama
  selectedKabkotaKode.value  = null
  selectedKabkotaNama.value  = ''
  kecamatanData.value        = []

  if (clickedLayer) leafletMap.fitBounds(clickedLayer.getBounds(), { padding: [40, 40] })

  try {
    const data = await ReportService.getMapDataKabkota(provinsiKode)
    kabkotaData.value = Array.isArray(data) ? data : []
  } catch { kabkotaData.value = [] }

  const fullGeo = await getKabkotaGeoJSON()
  if (!fullGeo) { renderFallbackMarkers(kabkotaData.value, 2); loading.value = false; return }

  const targetNorm = normProv(provinsiNama)
  const filtered = {
    type: 'FeatureCollection',
    features: fullGeo.features.filter(f => {
      const n1 = normProv(f.properties.NAME_1 || '')
      if (n1 === targetNorm) return true
      return PROV_NAME_TO_KODE[n1] === provinsiKode
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
    style: (feature) => {
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
        click()      { drillDownKecamatan(data.kabkota_kode || null, raw, layer) },
      })
    },
  }).addTo(leafletMap)
  if (provinsiOutline) provinsiOutline.bringToFront()
}

// ── Drill down ke kecamatan (level 3) ─────────────────────────────────────
async function drillDownKecamatan(kabkotaKode, kabkotaNama, clickedLayer) {
  loading.value = true; hovered.value = null
  currentLevel.value        = 3
  selectedKabkotaKode.value = kabkotaKode
  selectedKabkotaNama.value = kabkotaNama

  if (clickedLayer) leafletMap.fitBounds(clickedLayer.getBounds(), { padding: [40, 40] })

  try {
    const data = await ReportService.getMapDataKecamatan(kabkotaKode)
    kecamatanData.value = Array.isArray(data) ? data : []
  } catch { kecamatanData.value = [] }

  const kecGeo = await getKecamatanGeoJSON(kabkotaNama)
  if (!kecGeo) { renderFallbackMarkers(kecamatanData.value, 3); loading.value = false; return }

  renderKecamatanLayer(kecGeo)

  // Overlay outline kabkota di dalam provinsi aktif
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
    style: (feature) => {
      const raw = feature.properties.NAME_3 || feature.properties.KECAMATAN || feature.properties.name || ''
      const val = (lookup[normKec(raw)] || {})[props.metric] || 0
      return { fillColor: getColor(val, scale), fillOpacity: val > 0 ? 0.85 : 0.35, color: '#ffffff', weight: 0.8, opacity: 1 }
    },
    onEachFeature: (feature, layer) => {
      const raw  = feature.properties.NAME_3 || feature.properties.KECAMATAN || feature.properties.name || 'Unknown'
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

// ── Fallback circle markers (jika GeoJSON tidak tersedia) ──────────────────
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
    const nama = d.kecamatan_nama || d.kabkota_nama || ''
    circle.on({ mouseover() { hovered.value = { nama, ...d } }, mouseout() { hovered.value = null } })
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
    leafletMap.setView([-2.5, 118], 4)
    await renderProvinsiLayer()
  } else if (toLevel === 2) {
    // Kembali ke level kabkota tanpa re-fetch GeoJSON
    currentLevel.value = 2
    selectedKabkotaKode.value = null; selectedKabkotaNama.value = ''
    kecamatanData.value = []
    if (kabkotaOutline) { kabkotaOutline.remove(); kabkotaOutline = null }
    // Re-render kabkota layer dari cache
    const fullGeo = await getKabkotaGeoJSON()
    const targetNorm = normProv(selectedProvinsiNama.value)
    const filtered = fullGeo ? {
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

// ── Init map ──────────────────────────────────────────────────────────────
async function initMap() {
  try {
    L = (await import('leaflet')).default || (await import('leaflet'))
    await import('leaflet/dist/leaflet.css')
    leafletMap = L.map(mapRef.value, {
      center: [-2.5, 118], zoom: 4, zoomControl: false,
      scrollWheelZoom: false, attributionControl: false, dragging: true,
    })
    L.control.zoom({ position: 'topright' }).addTo(leafletMap)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
      maxZoom: 14, subdomains: 'abcd',
    }).addTo(leafletMap)
    await renderProvinsiLayer()
    loading.value = false
  } catch (e) {
    console.error('Map init error', e)
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
    if (lv === 3)      { raw = p.NAME_3 || p.KECAMATAN || p.name || ''; dataset = kecamatanData.value; key = 'kecamatan_nama' }
    else if (lv === 2) { raw = p.NAME_2 || p.KABKOTA   || p.name || ''; dataset = kabkotaData.value;   key = 'kabkota_nama' }
    else               { raw = getProvNama(p);                           dataset = props.mapData;        key = 'provinsi_nama' }
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
