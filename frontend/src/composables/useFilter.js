import { reactive, watch } from 'vue'

export function useFilter(initialFilters = {}) {
  const filters = reactive({ ...initialFilters })

  function resetFilters() {
    Object.keys(filters).forEach((key) => {
      filters[key] = initialFilters[key] ?? null
    })
  }

  function getActiveFilters() {
    return Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v !== null && v !== '' && v !== undefined)
    )
  }

  return { filters, resetFilters, getActiveFilters }
}
