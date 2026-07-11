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
      v-if="!loading && currentLevel === 2"
      style="position:absolute;top:12px;left:12px;z-index:1001;display:flex;align-items:center;gap:6px;flex-wrap:wrap;"
    >
      <button
        @click="drillUp"
        style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:99px;background:white;border:1px solid #e2e8f0;font-size:12px;font-weight:600;color:#374151;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.1);"
      >
        <i class="pi pi-arrow-left" style="font-size:11px;"></i>
        Kembali ke Provinsi
      </button>
      <span style="background:white;padding:5px 12px;border-radius:99px;font-size:12px;font-weight:700;color:#15803d;border:1px solid #dcfce7;box-shadow:0 2px 8px rgba(0,0,0,0.08);">
        {{ selectedProvinsiNama }}
      </span>
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
          {{ currentLevel === 2 ? 'Klik wilayah untuk detail' : 'Klik provinsi → lihat kab/kota' }}
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
          <div v-if="currentLevel === 1" style="margin-top:4px;padding-top:6px;border-top:1px solid #f1f5f9;">
            <span style="font-size:11px;color:#16a34a;font-weight:600;">
              <i class="pi pi-hand-pointer" style="font-size:10px;"></i> Klik untuk lihat kab/kota
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
import ReportService    from '@/services/report'

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
const currentLevel         = ref(1)
const selectedProvinsiKode = ref(null)
const selectedProvinsiNama = ref('')
const kabkotaData          = ref([])

let L            = null
let leafletMap   = null
let geojsonLayer = null

// Cache GeoJSON kabkota (1 file all-Indonesia, lazy load sekali)
let _kabkotaGeoCache = null

// ── Color scales ───────────────────────────────────────────────────────────
const mustahikScaleProv    = [{min:0,max:30000,color:'#dcfce7'},{min:30000,max:80000,color:'#86efac'},{min:80000,max:150000,color:'#4ade80'},{min:150000,max:300000,color:'#16a34a'},{min:300000,max:Infinity,color:'#14532d'}]
const mustahikScaleKab     = [{min:0,max:5000,color:'#dcfce7'},{min:5000,max:15000,color:'#86efac'},{min:15000,max:30000,color:'#4ade80'},{min:30000,max:60000,color:'#16a34a'},{min:60000,max:Infinity,color:'#14532d'}]
const penyaluranScaleProv  = [{min:0,max:100e9,color:'#dbeafe'},{min:100e9,max:300e9,color:'#93c5fd'},{min:300e9,max:600e9,color:'#3b82f6'},{min:600e9,max:1000e9,color:'#1d4ed8'},{min:1000e9,max:Infinity,color:'#1e3a8a'}]
const penyaluranScaleKab   = [{min:0,max:30e9,color:'#dbeafe'},{min:30e9,max:80e9,color:'#93c5fd'},{min:80e9,max:150e9,color:'#3b82f6'},{min:150e9,max:250e9,color:'#1d4ed8'},{min:250e9,max:Infinity,color:'#1e3a8a'}]

const legendsProv = {
  mustahik:   [{color:'#dcfce7',label:'< 30 rb'},{color:'#86efac',label:'30–80 rb'},{color:'#4ade80',label:'80–150 rb'},{color:'#16a34a',label:'150–300 rb'},{color:'#14532d',label:'> 300 rb'}],
  penyaluran: [{color:'#dbeafe',label:'< 100 M'},{color:'#93c5fd',label:'100–300 M'},{color:'#3b82f6',label:'300–600 M'},{color:'#1d4ed8',label:'600 M–1 T'},{color:'#1e3a8a',label:'> 1 T'}],
}
const legendsKab = {
  mustahik:   [{color:'#dcfce7',label:'< 5 rb'},{color:'#86efac',label:'5–15 rb'},{color:'#4ade80',label:'15–30 rb'},{color:'#16a34a',label:'30–60 rb'},{color:'#14532d',label:'> 60 rb'}],
  penyaluran: [{color:'#dbeafe',label:'< 30 M'},{color:'#93c5fd',label:'30–80 M'},{color:'#3b82f6',label:'80–150 M'},{color:'#1d4ed8',label:'150–250 M'},{color:'#1e3a8a',label:'> 250 M'}],
}

const currentLegend = ref(legendsProv.mustahik)

function getColor(value, scale) {
  for (const s of scale) { if (value >= s.min && value < s.max) return s.color }
  return '#f1f5f9'
}

// ── GeoJSON sources ────────────────────────────────────────────────────────
// Level-1 Provinsi — beberapa fallback
const GEOJSON_PROVINSI = [
  'https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia.geojson',
  'https://raw.githubusercontent.com/benkoshy/indonesia/master/indonesia-provinces-simple.geojson',
  'https://raw.githubusercontent.com/rizafahmi/geojson-indonesia/master/prov.json',
]

// Level-2 Kabkota — 1 file all-Indonesia (GADM level-2) dengan fallback
// Semua kabkota seluruh Indonesia dalam satu file, di-filter saat drill-down
// File ini berisi field NAME_1 (provinsi) dan NAME_2 (kabkota)
const GEOJSON_KABKOTA_ALL = [
  'https://raw.githubusercontent.com/fahadh4ilyas/indonesia-geojson-archive/master/indonesia-cities.geojson',
  'https://raw.githubusercontent.com/TheMaggieSimpson/IndonesiaGeoJSON/master/kota-kabupaten.json',
  'https://raw.githubusercontent.com/thetrisatria/geojson-indonesia/master/kota_kabupaten.geojson',
]

// Map: NAME_1 dalam GeoJSON → provinsi_kode BPS
// Digunakan untuk filter fitur kabkota milik provinsi yang diklik
const PROV_NAME_TO_KODE = {
  'aceh': '11', 'sumatera utara': '12', 'sumatera barat': '13',
  'riau': '14', 'jambi': '15', 'sumatera selatan': '16',
  'bengkulu': '17', 'lampung': '18', 'kepulauan bangka belitung': '19',
  'bangka belitung': '19', 'kepulauan riau': '21', 'kep. riau': '21',
  'dki jakarta': '31', 'jakarta raya': '31', 'jakarta': '31',
  'jawa barat': '32', 'jawa tengah': '33', 'di yogyakarta': '34',
  'yogyakarta': '34', 'jawa timur': '35', 'banten': '36',
  'bali': '51', 'nusa tenggara barat': '52', 'nusa tenggara timur': '53',
  'kalimantan barat': '61', 'kalimantan tengah': '62', 'kalimantan selatan': '63',
  'kalimantan timur': '64', 'kalimantan utara': '65',
  'sulawesi utara': '71', 'sulawesi tengah': '72', 'sulawesi selatan': '73',
  'sulawesi tenggara': '74', 'gorontalo': '75', 'sulawesi barat': '76',
  'maluku': '81', 'maluku utara': '82',
  'papua barat': '91', 'papua': '94',
}

async function fetchGeoJSON(urls) {
  const list = Array.isArray(urls) ? urls : [urls]
  for (const url of list) {
    try {
      const res = await fetch(url)
      if (!res.ok) continue
      const data = await res.json()
      if (data?.features?.length) return data
    } catch (_) { /* try next */ }
  }
  return null
}

// Lazy load + cache GeoJSON semua kabkota
async function getKabkotaGeoJSON() {
  if (_kabkotaGeoCache) return _kabkotaGeoCache
  loadingMsg.value = 'Memuat data wilayah kabupaten/kota...'
  const geo = await fetchGeoJSON(GEOJSON_KABKOTA_ALL)
  if (geo) _kabkotaGeoCache = geo
  return geo
}

function normalize(str = '') {
  return str.toLowerCase()
    .replace(/^(kabupaten|kota|kab\.) /g, '')
    .replace(/daerah istimewa /g, '')
    .replace(/daerah khusus ibukota /g, '')
    .replace(/kepulauan /g, 'kep. ')
    .trim()
}

function normalizeProvName(str = '') {
  return str.toLowerCase().trim()
}

// ── Render provinsi ────────────────────────────────────────────────────────
async function renderProvinsiLayer() {
  loadingMsg.value = 'Memuat peta Indonesia...'
  const geojson = await fetchGeoJSON(GEOJSON_PROVINSI)
  if (!geojson) { error.value = true; loading.value = false; return }

  const lookup = {}
  props.mapData.forEach(d => { if (d.provinsi_nama) lookup[normalize(d.provinsi_nama)] = d })

  const scale = props.metric === 'mustahik' ? mustahikScaleProv : penyaluranScaleProv
  currentLegend.value = legendsProv[props.metric]

  if (geojsonLayer) { geojsonLayer.remove(); geojsonLayer = null }

  geojsonLayer = L.geoJSON(geojson, {
    style: (feature) => {
      const raw  = feature.properties.state || feature.properties.name ||
                   feature.properties.NAME_1 || feature.properties.PROVINSI ||
                   feature.properties.Propinsi || ''
      const data = lookup[normalize(raw)] || {}
      const val  = data[props.metric] || 0
      return { fillColor: getColor(val, scale), fillOpacity: val > 0 ? 0.85 : 0.3, color: '#ffffff', weight: 1.2, opacity: 1 }
    },
    onEachFeature: (feature, layer) => {
      const raw  = feature.properties.state || feature.properties.name ||
                   feature.properties.NAME_1 || feature.properties.PROVINSI ||
                   feature.properties.Propinsi || 'Unknown'
      const data = props.mapData.find(d => normalize(d.provinsi_nama) === normalize(raw)) || {}
      layer.on({
        mouseover(e) { e.target.setStyle({ weight: 2.5, fillOpacity: 1, color: '#15803d' }); hovered.value = { nama: raw, ...data } },
        mouseout(e)  { geojsonLayer.resetStyle(e.target); hovered.value = null },
        click()      { drillDown(data.provinsi_kode || null, raw, layer) },
      })
    },
  }).addTo(leafletMap)
}

// ── Drill down ─────────────────────────────────────────────────────────────
async function drillDown(provinsiKode, provinsiNama, clickedLayer) {
  loading.value = true
  hovered.value = null
  currentLevel.value = 2
  selectedProvinsiKode.value = provinsiKode
  selectedProvinsiNama.value = provinsiNama

  // Zoom ke batas provinsi yang diklik
  if (clickedLayer) leafletMap.fitBounds(clickedLayer.getBounds(), { padding: [30, 30] })

  // Fetch data kabkota dari API backend (placeholder / real nanti)
  try {
    const data = await ReportService.getMapDataKabkota(provinsiKode)
    kabkotaData.value = Array.isArray(data) ? data : []
  } catch (_) { kabkotaData.value = [] }

  // Load GeoJSON kabkota (1 file all-Indonesia, filter per provinsi)
  const fullGeo = await getKabkotaGeoJSON()

  if (!fullGeo) {
    // Benar-benar tidak ada GeoJSON — tampilkan pesan bukan error fatal
    renderKabkotaNoGeo()
    loading.value = false
    return
  }

  // Filter hanya fitur milik provinsi ini
  // Pakai NAME_1 yang ada di GeoJSON vs nama provinsi yang diklik
  const targetNama = normalizeProvName(provinsiNama)
  const filtered = {
    type: 'FeatureCollection',
    features: fullGeo.features.filter(f => {
      const n1 = normalizeProvName(
        f.properties.NAME_1 || f.properties.PROVINSI ||
        f.properties.provinsi || f.properties.province || ''
      )
      // Cocokkan langsung atau via kode
      if (n1 === targetNama) return true
      // Fallback via kode BPS
      const kode = PROV_NAME_TO_KODE[n1]
      return kode && kode === provinsiKode
    }),
  }

  if (filtered.features.length === 0) {
    // GeoJSON ada tapi tidak ada fitur yang cocok untuk provinsi ini
    renderKabkotaNoGeo()
    loading.value = false
    return
  }

  renderKabkotaLayer(filtered)
  loading.value = false
}

function renderKabkotaLayer(geojson) {
  const lookup = {}
  kabkotaData.value.forEach(d => { if (d.kabkota_nama) lookup[normalize(d.kabkota_nama)] = d })

  const scale = props.metric === 'mustahik' ? mustahikScaleKab : penyaluranScaleKab
  currentLegend.value = legendsKab[props.metric]

  if (geojsonLayer) { geojsonLayer.remove(); geojsonLayer = null }

  geojsonLayer = L.geoJSON(geojson, {
    style: (feature) => {
      const raw  = feature.properties.NAME_2 || feature.properties.KABKOTA ||
                   feature.properties.kabkota || feature.properties.name || ''
      const data = lookup[normalize(raw)] || {}
      const val  = data[props.metric] || 0
      return { fillColor: getColor(val, scale), fillOpacity: val > 0 ? 0.85 : 0.35, color: '#ffffff', weight: 1, opacity: 1 }
    },
    onEachFeature: (feature, layer) => {
      const raw  = feature.properties.NAME_2 || feature.properties.KABKOTA ||
                   feature.properties.kabkota || feature.properties.name || 'Unknown'
      const data = kabkotaData.value.find(d => normalize(d.kabkota_nama) === normalize(raw)) || {}
      layer.on({
        mouseover(e) { e.target.setStyle({ weight: 2, fillOpacity: 1, color: '#15803d' }); hovered.value = { nama: raw, ...data } },
        mouseout(e)  { geojsonLayer.resetStyle(e.target); hovered.value = null },
        click()      { leafletMap.fitBounds(layer.getBounds(), { padding: [20, 20] }) },
      })
    },
  }).addTo(leafletMap)
}

// Tampilkan info jika GeoJSON kabkota tidak tersedia untuk provinsi ini
function renderKabkotaNoGeo() {
  if (geojsonLayer) { geojsonLayer.remove(); geojsonLayer = null }
  // Render data sebagai circle markers di tengah area provinsi
  const scale   = props.metric === 'mustahik' ? mustahikScaleKab : penyaluranScaleKab
  currentLegend.value = legendsKab[props.metric]
  const markers = L.layerGroup()
  const center  = leafletMap.getCenter()
  kabkotaData.value.forEach((d, i) => {
    const angle = (i / Math.max(kabkotaData.value.length, 1)) * 2 * Math.PI
    const r     = 0.8
    const lat   = center.lat + r * Math.sin(angle) * 0.5
    const lng   = center.lng + r * Math.cos(angle)
    const circle = L.circleMarker([lat, lng], {
      radius:      Math.max(8, Math.min(22, (d.mustahik || 3000) / 2000)),
      fillColor:   getColor(d[props.metric] || 0, scale),
      fillOpacity: 0.85,
      color:       '#ffffff',
      weight:      1.5,
    })
    circle.on({
      mouseover() { hovered.value = { nama: d.kabkota_nama, ...d } },
      mouseout()  { hovered.value = null },
    })
    markers.addLayer(circle)
  })
  geojsonLayer = markers
  markers.addTo(leafletMap)
}

// ── Drill up ───────────────────────────────────────────────────────────────
async function drillUp() {
  loading.value = true
  hovered.value = null
  currentLevel.value = 1
  selectedProvinsiKode.value = null
  selectedProvinsiNama.value = ''
  kabkotaData.value = []
  leafletMap.setView([-2.5, 118], 4)
  await renderProvinsiLayer()
  loading.value = false
}

// ── Init ───────────────────────────────────────────────────────────────────
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
      maxZoom: 12, subdomains: 'abcd',
    }).addTo(leafletMap)
    await renderProvinsiLayer()
    loading.value = false
  } catch (e) {
    console.error('Map init error', e)
    loading.value = false
    error.value   = true
  }
}

watch(() => [props.metric, props.mapData], async () => {
  if (!leafletMap || !L) return
  const isKab   = currentLevel.value === 2
  const scale   = isKab
    ? (props.metric === 'mustahik' ? mustahikScaleKab : penyaluranScaleKab)
    : (props.metric === 'mustahik' ? mustahikScaleProv : penyaluranScaleProv)
  currentLegend.value = isKab ? legendsKab[props.metric] : legendsProv[props.metric]
  if (geojsonLayer?.eachLayer) {
    geojsonLayer.eachLayer(layer => {
      if (!layer.feature) return
      const p    = layer.feature.properties
      const raw  = isKab
        ? (p.NAME_2 || p.KABKOTA || p.kabkota || p.name || '')
        : (p.state  || p.name    || p.NAME_1  || p.PROVINSI || p.Propinsi || '')
      const dataset = isKab ? kabkotaData.value : props.mapData
      const nameKey = isKab ? 'kabkota_nama' : 'provinsi_nama'
      const data  = dataset.find(d => normalize(d[nameKey]) === normalize(raw)) || {}
      layer.setStyle({ fillColor: getColor(data[props.metric]||0, scale), fillOpacity: data[props.metric] > 0 ? 0.85 : 0.3 })
    })
  }
}, { deep: true })

onMounted(initMap)
onUnmounted(() => { if (leafletMap) { leafletMap.remove(); leafletMap = null } })
</script>

<style scoped>
.map-spinner {
  width:36px; height:36px;
  border:3px solid #dcfce7;
  border-top-color:#16a34a;
  border-radius:50%;
  animation:spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
