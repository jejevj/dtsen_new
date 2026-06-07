<template>
  <div class="relative w-full rounded-xl overflow-hidden" :style="{ height: height }">
    <!-- Loading overlay -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-gray-50 z-10">
      <ProgressSpinner style="width:50px;height:50px" />
    </div>

    <!-- Map container -->
    <div ref="mapRef" class="w-full h-full"></div>

    <!-- Legend -->
    <div class="absolute bottom-4 right-4 bg-white rounded-lg shadow-md p-3 z-10">
      <p class="text-xs font-semibold text-gray-600 mb-2">Jumlah Mustahik</p>
      <div class="flex flex-col gap-1">
        <div v-for="step in legend" :key="step.label" class="flex items-center gap-2">
          <div class="w-4 h-3 rounded-sm" :style="{ backgroundColor: step.color }"></div>
          <span class="text-xs text-gray-500">{{ step.label }}</span>
        </div>
      </div>
    </div>

    <!-- Tooltip -->
    <div
      v-if="hoveredProvince"
      class="absolute top-4 left-4 bg-white rounded-lg shadow-lg p-3 z-10 min-w-48"
    >
      <p class="font-semibold text-sm text-gray-800">{{ hoveredProvince.nama }}</p>
      <div class="mt-2 space-y-1">
        <div class="flex justify-between gap-4 text-xs">
          <span class="text-gray-500">Mustahik</span>
          <span class="font-medium text-gray-800">{{ hoveredProvince.mustahik?.toLocaleString('id-ID') || '0' }}</span>
        </div>
        <div class="flex justify-between gap-4 text-xs">
          <span class="text-gray-500">Penyaluran</span>
          <span class="font-medium text-green-600">{{ formatRupiah(hoveredProvince.penyaluran || 0) }}</span>
        </div>
        <div class="flex justify-between gap-4 text-xs">
          <span class="text-gray-500">LAZ Aktif</span>
          <span class="font-medium text-gray-800">{{ hoveredProvince.laz_count || 0 }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import ProgressSpinner from 'primevue/progressspinner'
import { formatRupiah } from '@/utils/formatter'

const props = defineProps({
  mapData:  { type: Array,  default: () => [] },  // [{ provinsi_kode, provinsi_nama, mustahik, penyaluran, laz_count }]
  height:   { type: String, default: '480px' },
  metric:   { type: String, default: 'mustahik' }  // 'mustahik' | 'penyaluran'
})

const mapRef         = ref(null)
const loading        = ref(true)
const hoveredProvince = ref(null)
let leafletMap       = null
let geojsonLayer     = null

// Color scale (light → dark green)
const colorStops = ['#dcfce7', '#86efac', '#4ade80', '#16a34a', '#14532d']
const legend = [
  { color: colorStops[0], label: '< 1.000' },
  { color: colorStops[1], label: '1.000 – 10.000' },
  { color: colorStops[2], label: '10.000 – 50.000' },
  { color: colorStops[3], label: '50.000 – 100.000' },
  { color: colorStops[4], label: '> 100.000' },
]

function getColor(value) {
  if (!value || value < 1000)   return colorStops[0]
  if (value < 10000)  return colorStops[1]
  if (value < 50000)  return colorStops[2]
  if (value < 100000) return colorStops[3]
  return colorStops[4]
}

async function initMap() {
  const L = await import('leaflet')
  await import('leaflet/dist/leaflet.css')

  leafletMap = L.map(mapRef.value, {
    center: [-2.5, 118],
    zoom: 4,
    zoomControl: true,
    scrollWheelZoom: false,
    attributionControl: false
  })

  // Tile layer (light)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    maxZoom: 10
  }).addTo(leafletMap)

  await loadGeoJSON(L)
  loading.value = false
}

async function loadGeoJSON(L) {
  try {
    // Load Indonesia provinces GeoJSON from public CDN
    const res = await fetch('https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-en.geojson')
    const geojson = await res.json()

    // Build lookup map by province name
    const dataMap = {}
    props.mapData.forEach(d => {
      dataMap[d.provinsi_nama?.toLowerCase()] = d
    })

    if (geojsonLayer) geojsonLayer.remove()

    geojsonLayer = L.geoJSON(geojson, {
      style: (feature) => {
        const name  = feature.properties.state?.toLowerCase() || feature.properties.name?.toLowerCase()
        const data  = dataMap[name]
        const value = data?.[props.metric] || 0
        return {
          fillColor: getColor(value),
          weight: 1,
          opacity: 1,
          color: '#ffffff',
          fillOpacity: 0.85
        }
      },
      onEachFeature: (feature, layer) => {
        const name = feature.properties.state || feature.properties.name
        const data = props.mapData.find(d =>
          d.provinsi_nama?.toLowerCase() === name?.toLowerCase()
        )
        layer.on({
          mouseover: (e) => {
            e.target.setStyle({ weight: 2, fillOpacity: 1 })
            hoveredProvince.value = {
              nama: name,
              mustahik: data?.mustahik || 0,
              penyaluran: data?.penyaluran || 0,
              laz_count: data?.laz_count || 0
            }
          },
          mouseout: (e) => {
            geojsonLayer.resetStyle(e.target)
            hoveredProvince.value = null
          }
        })
      }
    }).addTo(leafletMap)
  } catch (e) {
    console.error('Failed to load GeoJSON', e)
  }
}

watch(() => props.mapData, () => {
  if (leafletMap) {
    import('leaflet').then(L => loadGeoJSON(L))
  }
}, { deep: true })

onMounted(initMap)
onUnmounted(() => { if (leafletMap) leafletMap.remove() })
</script>
