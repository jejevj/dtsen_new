/**
 * useBaselineRefs
 * - Fetch m_tampilan_dtsen_ref sekali (cache module-level) → resolveValue(fieldKey, raw)
 * - Fetch detail fields per kategori (individu/keluarga) → getDetailFields(kategori)
 */
import { ref } from 'vue'
import api from '@/services/api'

// ── Cache refs (kode → label) ─────────────────────────────────
let _refsLoaded = false
let _refsLoading = false
let _refsListeners = []
const _refMap = {}   // { field_key: { '1': 'Laki-laki', ... } }

async function _loadRefs() {
  if (_refsLoaded) return
  if (_refsLoading) {
    await new Promise(r => _refsListeners.push(r))
    return
  }
  _refsLoading = true
  try {
    const res = await api.get('/tampilan-dtsen')
    const fields = res.data?.data ?? []
    for (const field of fields) {
      if (field.refs?.length) {
        const map = {}
        for (const r of field.refs) map[String(r.ref_value)] = r.ref_label
        _refMap[field.field_key] = map
      }
    }
    _refsLoaded = true
  } catch (e) {
    console.warn('[useBaselineRefs] gagal fetch refs:', e)
  } finally {
    _refsLoading = false
    _refsListeners.forEach(fn => fn())
    _refsListeners = []
  }
}

// ── Cache detail fields per kategori ───────────────────────
const _detailCache = {}  // { 'individu': [...fields], 'keluarga': [...fields] }

async function _loadDetailFields(kategori) {
  if (_detailCache[kategori]) return
  try {
    const res = await api.get('/tampilan-dtsen/detail', { params: { kategori } })
    _detailCache[kategori] = res.data?.data ?? []
  } catch (e) {
    console.warn('[useBaselineRefs] gagal fetch detail fields:', e)
    _detailCache[kategori] = []
  }
}

// ── Composable ───────────────────────────────────────────
export function useBaselineRefs() {
  const ready = ref(_refsLoaded)

  async function init() {
    if (_refsLoaded) { ready.value = true; return }
    await _loadRefs()
    ready.value = true
  }

  /**
   * Resolve nilai mentah ke label dari m_tampilan_dtsen_ref.
   * Jika tidak ada mapping → kembalikan nilai asli.
   */
  function resolveValue(fieldKey, rawValue) {
    if (rawValue === null || rawValue === undefined || rawValue === '') return '-'
    const map = _refMap[fieldKey]
    if (!map) return String(rawValue)
    return map[String(rawValue)] ?? String(rawValue)
  }

  function hasRefs(fieldKey) {
    return Boolean(_refMap[fieldKey])
  }

  /**
   * Ambil daftar field untuk halaman detail (is_detail=1).
   * Dikelompokkan per field_group.
   * @param {'individu'|'keluarga'} kategori
   * @returns {Promise<Array<{group: string, fields: Array}>>}
   */
  async function getDetailFields(kategori) {
    await Promise.all([_loadRefs(), _loadDetailFields(kategori)])
    ready.value = true
    const fields = _detailCache[kategori] ?? []
    // Kelompokkan berdasarkan field_group, pertahankan urutan
    const groups = []
    const groupMap = {}
    for (const f of fields) {
      const g = f.field_group || 'Lainnya'
      if (!groupMap[g]) {
        groupMap[g] = { group: g, fields: [] }
        groups.push(groupMap[g])
      }
      groupMap[g].fields.push(f)
    }
    return groups
  }

  return { ready, init, resolveValue, hasRefs, getDetailFields }
}
