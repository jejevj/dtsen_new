<template>
  <div
    style="position:relative;width:100%;border-radius:12px;overflow:hidden;background:#f0fdf4;"
    :style="{ height: height }"
  >
    <!-- Loading -->
    <div v-if="loading" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#f8fafc;z-index:10;gap:12px;">
      <div class="map-spinner"></div>
      <span style="font-size:13px;color:#64748b;font-family:Inter,sans-serif;">Memuat peta...</span>
    </div>

    <!-- Error -->
    <div v-if="error" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#fef2f2;z-index:10;gap:8px;">
      <i class="pi pi-exclamation-triangle" style="font-size:28px;color:#ef4444;"></i>
      <span style="font-size:13px;color:#dc2626;font-family:Inter,sans-serif;">Gagal memuat peta. Coba refresh halaman.</span>
    </div>

    <!-- Breadcrumb drill-down -->
    <div
      v-if="!loading && currentLevel === 2"
      style="position:absolute;top:12px;left:12px;z-index:1001;display:flex;align-items:center;gap:6px;"
    >
      <button
        @click="drillUp"
        style="display:inline-flex;align-items:center;gap:6px;padding:7px 14px;border-radius:99px;background:white;border:1px solid #e2e8f0;font-size:12px;font-weight:600;color:#374151;cursor:pointer;box-shadow:0 2px 8px rgba(0,0,0,0.1);transition:background 0.15s;"
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
      <div v-if="currentLevel === 2" style="margin-top:8px;padding-top:8px;border-top:1px solid #f1f5f9;">
        <p style="font-size:10px;color:#94a3b8;margin:0;">Klik wilayah untuk detail</p>
      </div>
      <div v-else style="margin-top:8px;padding-top:8px;border-top:1px solid #f1f5f9;">
        <p style="font-size:10px;color:#94a3b8;margin:0;">Klik provinsi → lihat kab/kota</p>
      </div>
    </div>

    <!-- Tooltip hover -->
    <div v-if="hovered" style="position:absolute;top:16px;left:50%;transform:translateX(-50%);background:white;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.12);padding:14px;z-index:1000;min-width:200px;pointer-events:none;">
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
          <span style="font-size:11px;color:#16a34a;font-weight:600;"><i class="pi pi-mouse" style="font-size:10px;"></i> Klik untuk lihat kab/kota</span>
        </div>
      </div>
    </div>
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

const mapRef              = ref(null)
const loading             = ref(true)
const error               = ref(false)
const hovered             = ref(null)
const currentLevel        = ref(1)           // 1=provinsi, 2=kabkota
const selectedProvinsiKode = ref(null)
const selectedProvinsiNama = ref('')
const kabkotaData         = ref([])          // cache data kabkota

let L            = null
let leafletMap   = null
let geojsonLayer = null

// ── Color scales ──────────────────────────────────────────────────────────
const mustahikScaleProv = [
  { min: 0,       max: 30000,    color: '#dcfce7' },
  { min: 30000,   max: 80000,    color: '#86efac' },
  { min: 80000,   max: 150000,   color: '#4ade80' },
  { min: 150000,  max: 300000,   color: '#16a34a' },
  { min: 300000,  max: Infinity, color: '#14532d' },
]
const mustahikScaleKab = [
  { min: 0,       max: 5000,     color: '#dcfce7' },
  { min: 5000,    max: 15000,    color: '#86efac' },
  { min: 15000,   max: 30000,    color: '#4ade80' },
  { min: 30000,   max: 60000,    color: '#16a34a' },
  { min: 60000,   max: Infinity, color: '#14532d' },
]
const penyaluranScaleProv = [
  { min: 0,       max: 100e9,    color: '#dbeafe' },
  { min: 100e9,   max: 300e9,    color: '#93c5fd' },
  { min: 300e9,   max: 600e9,    color: '#3b82f6' },
  { min: 600e9,   max: 1000e9,   color: '#1d4ed8' },
  { min: 1000e9,  max: Infinity, color: '#1e3a8a' },
]
const penyaluranScaleKab = [
  { min: 0,       max: 30e9,     color: '#dbeafe' },
  { min: 30e9,    max: 80e9,     color: '#93c5fd' },
  { min: 80e9,    max: 150e9,    color: '#3b82f6' },
  { min: 150e9,   max: 250e9,    color: '#1d4ed8' },
  { min: 250e9,   max: Infinity, color: '#1e3a8a' },
]

const legendsProv = {
  mustahik:    [{color:'#dcfce7',label:'< 30 rb'},{color:'#86efac',label:'30–80 rb'},{color:'#4ade80',label:'80–150 rb'},{color:'#16a34a',label:'150–300 rb'},{color:'#14532d',label:'> 300 rb'}],
  penyaluran:  [{color:'#dbeafe',label:'< 100 M'},{color:'#93c5fd',label:'100–300 M'},{color:'#3b82f6',label:'300–600 M'},{color:'#1d4ed8',label:'600 M–1 T'},{color:'#1e3a8a',label:'> 1 T'}],
}
const legendsKab = {
  mustahik:    [{color:'#dcfce7',label:'< 5 rb'},{color:'#86efac',label:'5–15 rb'},{color:'#4ade80',label:'15–30 rb'},{color:'#16a34a',label:'30–60 rb'},{color:'#14532d',label:'> 60 rb'}],
  penyaluran:  [{color:'#dbeafe',label:'< 30 M'},{color:'#93c5fd',label:'30–80 M'},{color:'#3b82f6',label:'80–150 M'},{color:'#1d4ed8',label:'150–250 M'},{color:'#1e3a8a',label:'> 250 M'}],
}

const currentLegend = ref(legendsProv.mustahik)

function getColor(value, scale) {
  for (const s of scale) { if (value >= s.min && value < s.max) return s.color }
  return '#f1f5f9'
}

// ── GeoJSON sources ───────────────────────────────────────────────────────
const GEOJSON_PROVINSI = [
  'https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia.geojson',
  'https://raw.githubusercontent.com/benkoshy/indonesia/master/indonesia-provinces-simple.geojson',
  'https://raw.githubusercontent.com/rizafahmi/geojson-indonesia/master/prov.json',
]

// GeoJSON kabkota per provinsi — pakai GADM level-2 (per provinsi)
// Format URL: https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-{prov_slug}.geojson
// Fallback: gunakan GeoJSON provinsi yang dipilih itu sendiri (zoom detail)
const GEOJSON_KABKOTA_BASE = 'https://raw.githubusercontent.com/ans-4175/peta-indonesia-geojson/master/'

// Map kode provinsi BPS → slug file GeoJSON kabkota
const KABKOTA_GEOJSON_MAP = {
  '31': 'DKI-Jakarta.geojson',
  '32': 'Jawa-Barat.geojson',
  '33': 'Jawa-Tengah.geojson',
  '34': 'DI-Yogyakarta.geojson',
  '35': 'Jawa-Timur.geojson',
  '36': 'Banten.geojson',
  '11': 'Aceh.geojson',
  '12': 'Sumatera-Utara.geojson',
  '13': 'Sumatera-Barat.geojson',
  '14': 'Riau.geojson',
  '15': 'Jambi.geojson',
  '16': 'Sumatera-Selatan.geojson',
  '17': 'Bengkulu.geojson',
  '18': 'Lampung.geojson',
  '19': 'Bangka-Belitung.geojson',
  '21': 'Kepulauan-Riau.geojson',
  '51': 'Bali.geojson',
  '52': 'Nusa-Tenggara-Barat.geojson',
  '53': 'Nusa-Tenggara-Timur.geojson',
  '61': 'Kalimantan-Barat.geojson',
  '62': 'Kalimantan-Tengah.geojson',
  '63': 'Kalimantan-Selatan.geojson',
  '64': 'Kalimantan-Timur.geojson',
  '65': 'Kalimantan-Utara.geojson',
  '71': 'Sulawesi-Utara.geojson',
  '72': 'Sulawesi-Tengah.geojson',
  '73': 'Sulawesi-Selatan.geojson',
  '74': 'Sulawesi-Tenggara.geojson',
  '75': 'Gorontalo.geojson',
  '76': 'Sulawesi-Barat.geojson',
  '81': 'Maluku.geojson',
  '82': 'Maluku-Utara.geojson',
  '91': 'Papua-Barat.geojson',
  '94': 'Papua.geojson',
}

async function fetchGeoJSON(urls) {
  const list = Array.isArray(urls) ? urls : [urls]
  for (const url of list) {
    try {
      const res = await fetch(url)
      if (res.ok) {
        const data = await res.json()
        if (data?.features?.length) return data
      }
    } catch (_) { /* try next */ }
  }
  return null
}

function normalize(str = '') {
  return str.toLowerCase()
    .replace(/kabupaten /g, 'kab. ')
    .replace(/daerah istimewa /g, 'di ')
    .replace(/daerah khusus ibukota /g, 'dki ')
    .replace(/kepulauan /g, 'kep. ')
    .trim()
}

// ── Provinsi layer ────────────────────────────────────────────────────────
async function renderProvinsiLayer() {
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
      return {
        fillColor:   getColor(val, scale),
        fillOpacity: val > 0 ? 0.85 : 0.3,
        color:       '#ffffff',
        weight:      1.2,
        opacity:     1,
      }
    },
    onEachFeature: (feature, layer) => {
      const raw  = feature.properties.state || feature.properties.name ||
                   feature.properties.NAME_1 || feature.properties.PROVINSI ||
                   feature.properties.Propinsi || 'Unknown'
      const data = props.mapData.find(d => normalize(d.provinsi_nama) === normalize(raw)) || {}
      layer.on({
        mouseover(e) {
          e.target.setStyle({ weight: 2.5, fillOpacity: 1, color: '#15803d' })
          hovered.value = { nama: raw, ...data }
        },
        mouseout(e) {
          geojsonLayer.resetStyle(e.target)
          hovered.value = null
        },
        click() {
          // Drill down ke kabkota
          const prov = props.mapData.find(d => normalize(d.provinsi_nama) === normalize(raw))
          const kode = prov?.provinsi_kode || null
          drillDown(kode, raw, layer)
        },
      })
    },
  }).addTo(leafletMap)
}

// ── Drill down ke kabkota ─────────────────────────────────────────────────
async function drillDown(provinsiKode, provinsiNama, clickedLayer) {
  loading.value = true
  hovered.value = null
  selectedProvinsiKode.value = provinsiKode
  selectedProvinsiNama.value = provinsiNama
  currentLevel.value = 2

  // Zoom ke batas provinsi
  if (clickedLayer) {
    leafletMap.fitBounds(clickedLayer.getBounds(), { padding: [30, 30] })
  }

  // Fetch data kabkota dari API
  try {
    const data = await ReportService.getMapDataKabkota(provinsiKode)
    kabkotaData.value = data || []
  } catch (_) {
    kabkotaData.value = []
  }

  // Load GeoJSON kabkota
  const slug    = provinsiKode ? KABKOTA_GEOJSON_MAP[provinsiKode] : null
  const geoUrl  = slug ? `${GEOJSON_KABKOTA_BASE}${slug}` : null
  const geojson = geoUrl ? await fetchGeoJSON(geoUrl) : null

  if (!geojson) {
    // Fallback: render kabkota sebagai bubble markers jika GeoJSON tidak ada
    renderKabkotaFallback()
    loading.value = false
    return
  }

  renderKabkotaLayer(geojson)
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
      const raw  = feature.properties.KABKOTA || feature.properties.NAME_2 ||
                   feature.properties.name || feature.properties.WADMKK || ''
      const data = lookup[normalize(raw)] || {}
      const val  = data[props.metric] || 0
      return {
        fillColor:   getColor(val, scale),
        fillOpacity: val > 0 ? 0.85 : 0.3,
        color:       '#ffffff',
        weight:      1,
        opacity:     1,
      }
    },
    onEachFeature: (feature, layer) => {
      const raw  = feature.properties.KABKOTA || feature.properties.NAME_2 ||
                   feature.properties.name || feature.properties.WADMKK || 'Unknown'
      const data = kabkotaData.value.find(d => normalize(d.kabkota_nama) === normalize(raw)) || {}
      layer.on({
        mouseover(e) {
          e.target.setStyle({ weight: 2, fillOpacity: 1, color: '#15803d' })
          hovered.value = { nama: raw, ...data }
        },
        mouseout(e) {
          geojsonLayer.resetStyle(e.target)
          hovered.value = null
        },
        click() {
          leafletMap.fitBounds(layer.getBounds(), { padding: [20, 20] })
        },
      })
    },
  }).addTo(leafletMap)
}

// Fallback: jika GeoJSON kabkota tidak tersedia, tampilkan circle markers
function renderKabkotaFallback() {
  const scale = props.metric === 'mustahik' ? mustahikScaleKab : penyaluranScaleKab
  currentLegend.value = legendsKab[props.metric]
  if (geojsonLayer) { geojsonLayer.remove(); geojsonLayer = null }

  // Render sebagai layer group marker
  const markers = L.layerGroup()
  kabkotaData.value.forEach(d => {
    // Koordinat kasar berdasarkan provinsi + urutan (hanya untuk fallback visual)
    const center = leafletMap.getCenter()
    const jitter = (Math.random() - 0.5) * 2
    const circle = L.circleMarker([center.lat + jitter * 0.5, center.lng + jitter], {
      radius:      Math.max(8, Math.min(24, (d.mustahik || 5000) / 3000)),
      fillColor:   getColor(d[props.metric] || 0, scale),
      fillOpacity: 0.85,
      color:       '#ffffff',
      weight:      1.5,
    })
    circle.on({
      mouseover() { hovered.value = { nama: d.kabkota_nama, ...d } },
      mouseout()  { hovered.value = null },
    })
    circle.addTo(markers)
  })
  geojsonLayer = markers
  markers.addTo(leafletMap)
}

// ── Drill up ke provinsi ──────────────────────────────────────────────────
async function drillUp() {
  loading.value = true
  hovered.value = null
  currentLevel.value = 1
  selectedProvinsiKode.value = null
  selectedProvinsiNama.value = ''
  kabkotaData.value = []

  // Reset view Indonesia
  leafletMap.setView([-2.5, 118], 4)
  currentLegend.value = legendsProv[props.metric]
  await renderProvinsiLayer()
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
      maxZoom: 12, subdomains: 'abcd'
    }).addTo(leafletMap)
    await renderProvinsiLayer()
    loading.value = false
  } catch (e) {
    console.error('Map init error', e)
    loading.value = false
    error.value   = true
  }
}

// Watch metric change — re-render layer yang aktif
watch(() => [props.metric, props.mapData], async () => {
  if (!leafletMap || !L) return
  if (currentLevel.value === 2) {
    // Update warna layer kabkota
    const scale = props.metric === 'mustahik' ? mustahikScaleKab : penyaluranScaleKab
    currentLegend.value = legendsKab[props.metric]
    if (geojsonLayer && geojsonLayer.eachLayer) {
      geojsonLayer.eachLayer(layer => {
        if (!layer.feature) return
        const raw  = layer.feature.properties.KABKOTA || layer.feature.properties.NAME_2 ||
                     layer.feature.properties.name || layer.feature.properties.WADMKK || ''
        const data = kabkotaData.value.find(d => normalize(d.kabkota_nama) === normalize(raw)) || {}
        layer.setStyle({ fillColor: getColor(data[props.metric]||0, scale), fillOpacity: data[props.metric] > 0 ? 0.85 : 0.3 })
      })
    }
  } else {
    const scale = props.metric === 'mustahik' ? mustahikScaleProv : penyaluranScaleProv
    currentLegend.value = legendsProv[props.metric]
    if (geojsonLayer && geojsonLayer.eachLayer) {
      geojsonLayer.eachLayer(layer => {
        if (!layer.feature) return
        const raw  = layer.feature.properties.state || layer.feature.properties.name ||
                     layer.feature.properties.NAME_1 || layer.feature.properties.PROVINSI ||
                     layer.feature.properties.Propinsi || ''
        const data = props.mapData.find(d => normalize(d.provinsi_nama) === normalize(raw)) || {}
        layer.setStyle({ fillColor: getColor(data[props.metric]||0, scale), fillOpacity: data[props.metric] > 0 ? 0.85 : 0.3 })
      })
    }
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
</style>
