/**
 * useBaselineRefs
 * Fetch m_tampilan_dtsen_ref sekali, cache di module scope,
 * lalu sediakan helper resolveValue(fieldKey, rawValue) → label string.
 */
import { ref } from 'vue'
import { fetchTampilanDtsen } from '@/services/tampilanDtsenService'

// Module-level cache agar tidak re-fetch tiap komponen mount
let _loaded = false
let _loading = false
let _listeners = []

// Map: field_key → Map(ref_value → ref_label)
// Contoh: { jenis_kelamin: { '1': 'Laki-laki', '2': 'Perempuan' } }
const _refMap = {}

async function _loadOnce() {
  if (_loaded) return
  if (_loading) {
    // tunggu yang sedang berjalan
    await new Promise(resolve => _listeners.push(resolve))
    return
  }
  _loading = true
  try {
    const fields = await fetchTampilanDtsen()
    for (const field of fields) {
      if (field.refs && field.refs.length > 0) {
        const map = {}
        for (const r of field.refs) {
          // simpan dengan String() agar lookup selalu konsisten
          map[String(r.ref_value)] = r.ref_label
        }
        _refMap[field.field_key] = map
      }
    }
    _loaded = true
  } catch (e) {
    console.warn('[useBaselineRefs] gagal fetch tampilan-dtsen:', e)
  } finally {
    _loading = false
    _listeners.forEach(fn => fn())
    _listeners = []
  }
}

export function useBaselineRefs() {
  const ready = ref(_loaded)

  async function init() {
    if (_loaded) {
      ready.value = true
      return
    }
    await _loadOnce()
    ready.value = true
  }

  /**
   * Resolve nilai mentah ke label.
   * Jika tidak ada mapping → kembalikan nilai asli.
   * @param {string} fieldKey  - e.g. 'jenis_kelamin'
   * @param {*}      rawValue  - e.g. 1, '1', '2'
   * @returns {string}
   */
  function resolveValue(fieldKey, rawValue) {
    if (rawValue === null || rawValue === undefined || rawValue === '') return '-'
    const map = _refMap[fieldKey]
    if (!map) return String(rawValue)
    return map[String(rawValue)] ?? String(rawValue)
  }

  /**
   * Apakah field ini punya mapping refs?
   */
  function hasRefs(fieldKey) {
    return Boolean(_refMap[fieldKey])
  }

  return { ready, init, resolveValue, hasRefs }
}
