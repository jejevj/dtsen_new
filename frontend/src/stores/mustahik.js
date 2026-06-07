import { defineStore } from 'pinia'
import { ref } from 'vue'
import MustahikService from '@/services/mustahik'

export const useMustahikStore = defineStore('mustahik', () => {
  const list = ref([])
  const detail = ref(null)
  const meta = ref({})

  async function fetchList(params) {
    const result = await MustahikService.getList(params)
    list.value = result.data
    meta.value = result.meta
  }

  async function fetchDetail(nikHashed) {
    detail.value = await MustahikService.getDetail(nikHashed)
  }

  return { list, detail, meta, fetchList, fetchDetail }
})
