import { ref, computed } from 'vue'

export function usePagination(fetchFn) {
  const page = ref(1)
  const perPage = ref(20)
  const total = ref(0)
  const pages = ref(0)
  const loading = ref(false)

  const totalPages = computed(() => pages.value)

  async function load(params = {}) {
    loading.value = true
    try {
      const result = await fetchFn({ ...params, page: page.value, per_page: perPage.value })
      total.value = result.meta?.total || 0
      pages.value = result.meta?.pages || 0
      return result.data
    } finally {
      loading.value = false
    }
  }

  function goTo(p) {
    page.value = p
  }

  return { page, perPage, total, totalPages, loading, load, goTo }
}
