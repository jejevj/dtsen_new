<template>
  <div
    style="position:relative;width:100%;border-radius:12px;overflow:hidden;background:#f0fdf4;"
    :style="{ height: height }"
  >
    <!-- Loading -->
    <div
      v-if="loading"
      style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#f8fafc;z-index:10;gap:12px;"
    >
      <div class="map-spinner"></div>
      <span style="font-size:13px;color:#64748b;font-family:Inter,sans-serif;">Memuat peta Indonesia...</span>
    </div>

    <!-- Error -->
    <div
      v-if="error"
      style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;background:#fef2f2;z-index:10;gap:8px;"
    >
      <i class="pi pi-exclamation-triangle" style="font-size:28px;color:#ef4444;"></i>
      <span style="font-size:13px;color:#dc2626;font-family:Inter,sans-serif;">Gagal memuat peta. Coba refresh halaman.</span>
    </div>

    <!-- Map -->
    <div ref="mapRef" style="width:100%;height:100%;"></div>

    <!-- Legend -->
    <div
      v-if="!loading"
      style="position:absolute;bottom:16px;right:16px;background:white;border-radius:10px;box-shadow:0 2px 8px rgba(0,0,0,0.12);padding:12px 14px;z-index:1000;min-width:140px;"
    >
      <p style="font-size:11px;font-weight:700;color:#374151;margin:0 0 8px;text-transform:uppercase;letter-spacing:0.05em;">
        {{ metric === 'mustahik' ? 'Jml. Mustahik' : 'Penyaluran' }}
      </p>
      <div v-for="step in currentLegend" :key="step.label" style="display:flex;align-items:center;gap:7px;margin-bottom:5px;">
        <div :style="{ width:'14px', height:'10px', borderRadius:'3px', background:step.color, flexShrink:0 }"></div>
        <span style="font-size:11px;color:#6b7280;">{{ step.label }}</span>
      </div>
    </div>

    <!-- Hover Tooltip -->
    <div
      v-if="hovered"
      style="position:absolute;top:16px;left:16px;background:white;border-radius:10px;box-shadow:0 4px 16px rgba(0,0,0,0.12);padding:14px;z-index:1000;min-width:190px;"
    >
      <p style="font-size:13px;font-weight:700;color:#1e293b;margin:0 0 10px;border-bottom:1px solid #f1f5f9;padding-bottom:8px;">{{ hovered.nama }}</p>
      <div style="display:flex;flex-direction:column;gap:6px;">
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:12px;color:#64748b;display:flex;align-items:center;gap:5px;">
            <i class="pi pi-users" style="font-size:10px;color:#3b82f6;"></i> Mustahik
          </span>
          <span style="font-size:12px;font-weight:600;color:#1e293b;">{{ (hovered.mustahik||0).toLocaleString('id-ID') }}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:12px;color:#64748b;display:flex;align-items:center;gap:5px;">
            <i class="pi pi-wallet" style="font-size:10px;color:#16a34a;"></i> Penyaluran
          </span>
          <span style="font-size:12px;font-weight:600;color:#15803d;">{{ formatRupiah(hovered.penyaluran||0) }}</span>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span style="font-size:12px;color:#64748b;display:flex;align-items:center;gap:5px;">
            <i class="pi pi-building" style="font-size:10px;color:#7c3aed;"></i> LAZ Aktif
          </span>
          <span style="font-size:12px;font-weight:600;color:#1e293b;">{{ hovered.laz_count||0 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { formatRupiah } from '@/utils/formatter'

const props = defineProps({
  mapData: { type: Array,  default: () => [] },
  height:  { type: String, default: '480px' },
  metric:  { type: String, default: 'mustahik' }
})

const mapRef  = ref(null)
const loading = ref(true)
const error   = ref(false)
const hovered = ref(null)
let L           = null
let leafletMap  = null
let geojsonLayer = null

// ── Color scales ──────────────────────────────────────────
const mustahikScale = [
  { min: 0,       max: 30000,   color: '#dcfce7' },
  { min: 30000,   max: 80000,   color: '#86efac' },
  { min: 80000,   max: 150000,  color: '#4ade80' },
  { min: 150000,  max: 300000,  color: '#16a34a' },
  { min: 300000,  max: Infinity,color: '#14532d' },
]
const penyaluranScale = [
  { min: 0,            max: 100e9,   color: '#dbeafe' },
  { min: 100e9,        max: 300e9,   color: '#93c5fd' },
  { min: 300e9,        max: 600e9,   color: '#3b82f6' },
  { min: 600e9,        max: 1000e9,  color: '#1d4ed8' },
  { min: 1000e9,       max: Infinity,color: '#1e3a8a' },
]

const mustahikLegend = [
  { color:'#dcfce7', label:'< 30 rb' },
  { color:'#86efac', label:'30–80 rb' },
  { color:'#4ade80', label:'80–150 rb' },
  { color:'#16a34a', label:'150–300 rb' },
  { color:'#14532d', label:'> 300 rb' },
]
const penyaluranLegend = [
  { color:'#dbeafe', label:'< 100 M' },
  { color:'#93c5fd', label:'100–300 M' },
  { color:'#3b82f6', label:'300–600 M' },
  { color:'#1d4ed8', label:'600 M–1 T' },
  { color:'#1e3a8a', label:'> 1 T' },
]

const currentLegend = ref(mustahikLegend)

function getColor(value, scale) {
  for (const s of scale) {
    if (value >= s.min && value < s.max) return s.color
  }
  return '#f1f5f9'
}

// ── GeoJSON CDN sources (fallback chain) ──────────────────
const GEOJSON_SOURCES = [
  'https://raw.githubusercontent.com/wahyukmr/indonesia-geojson/main/indonesia-province.geojson',
  'https://raw.githubusercontent.com/ans-4175/peta-indonesia-geojson/master/indonesia-peta.geojson',
  'https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia.geojson',
]

async function fetchGeoJSON() {
  for (const url of GEOJSON_SOURCES) {
    try {
      const res = await fetch(url)
      if (res.ok) return await res.json()
    } catch (_) { /* try next */ }
  }
  throw new Error('All GeoJSON sources failed')
}

// ── Province name normalization ───────────────────────────
function normalize(str = '') {
  return str.toLowerCase()
    .replace(/daerah istimewa /g, 'di ')
    .replace(/daerah khusus ibukota /g, 'dki ')
    .replace(/kepulauan /g, 'kep. ')
    .replace(/\bpapua barat daya\b/, 'papua barat daya')
    .trim()
}

// ── Build data lookup ─────────────────────────────────────
function buildLookup() {
  const map = {}
  props.mapData.forEach(d => {
    if (d.provinsi_nama) map[normalize(d.provinsi_nama)] = d
  })
  return map
}

// ── Init Leaflet ──────────────────────────────────────────
async function initMap() {
  try {
    L = (await import('leaflet')).default || (await import('leaflet'))
    await import('leaflet/dist/leaflet.css')

    leafletMap = L.map(mapRef.value, {
      center: [-2.5, 118],
      zoom: 4,
      zoomControl: false,
      scrollWheelZoom: false,
      attributionControl: false,
      dragging: true,
    })

    // Zoom top-right
    L.control.zoom({ position: 'topright' }).addTo(leafletMap)

    // Light basemap
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
      maxZoom: 12, subdomains: 'abcd'
    }).addTo(leafletMap)

    await renderLayer()
    loading.value = false
  } catch (e) {
    console.error('Map init error', e)
    loading.value = false
    error.value   = true
  }
}

async function renderLayer() {
  const geojson = await fetchGeoJSON()
  const lookup  = buildLookup()
  const scale   = props.metric === 'mustahik' ? mustahikScale : penyaluranScale
  currentLegend.value = props.metric === 'mustahik' ? mustahikLegend : penyaluranLegend

  if (geojsonLayer) { geojsonLayer.remove(); geojsonLayer = null }

  geojsonLayer = L.geoJSON(geojson, {
    style: (feature) => {
      const raw  = feature.properties.state || feature.properties.name ||
                   feature.properties.NAME_1 || feature.properties.PROVINSI || ''
      const data = lookup[normalize(raw)] || {}
      const val  = data[props.metric] || 0
      return {
        fillColor:   getColor(val, scale),
        fillOpacity: val > 0 ? 0.85 : 0.25,
        color:    '#ffffff',
        weight:   1.2,
        opacity:  1,
      }
    },
    onEachFeature: (feature, layer) => {
      const raw  = feature.properties.state || feature.properties.name ||
                   feature.properties.NAME_1 || feature.properties.PROVINSI || 'Unknown'
      const data = props.mapData.find(d =>
        normalize(d.provinsi_nama) === normalize(raw)
      ) || {}

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
          leafletMap.fitBounds(layer.getBounds(), { padding: [20, 20] })
        },
      })
    },
  }).addTo(leafletMap)
}

// Re-render when metric or data changes
watch(() => [props.metric, props.mapData], async () => {
  if (!leafletMap || !L) return
  const scale = props.metric === 'mustahik' ? mustahikScale : penyaluranScale
  currentLegend.value = props.metric === 'mustahik' ? mustahikLegend : penyaluranLegend
  if (geojsonLayer) {
    geojsonLayer.eachLayer(layer => {
      const feat = layer.feature
      const raw  = feat?.properties?.state || feat?.properties?.name ||
                   feat?.properties?.NAME_1 || feat?.properties?.PROVINSI || ''
      const data = props.mapData.find(d => normalize(d.provinsi_nama) === normalize(raw)) || {}
      const val  = data[props.metric] || 0
      layer.setStyle({
        fillColor:   getColor(val, scale),
        fillOpacity: val > 0 ? 0.85 : 0.25,
      })
    })
  }
}, { deep: true })

onMounted(initMap)
onUnmounted(() => { if (leafletMap) { leafletMap.remove(); leafletMap = null } })
</script>

<style scoped>
.map-spinner {
  width: 36px; height: 36px;
  border: 3px solid #dcfce7;
  border-top-color: #16a34a;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
