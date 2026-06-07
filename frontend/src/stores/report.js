import { defineStore } from 'pinia'
import { ref } from 'vue'
import ReportService from '@/services/report'

export const useReportStore = defineStore('report', () => {
  const summary = ref(null)
  const genderData = ref(null)
  const bidangData = ref([])
  const timeseriesData = ref([])
  const desilData = ref({})

  async function fetchAll(params = {}) {
    const [s, g, b, t, d] = await Promise.all([
      ReportService.getSummary(params),
      ReportService.getByGender(params),
      ReportService.getByBidang(params),
      ReportService.getTimeseries(params),
      ReportService.getDesilSummary(params)
    ])
    summary.value = s
    genderData.value = g
    bidangData.value = b
    timeseriesData.value = t
    desilData.value = d
  }

  return { summary, genderData, bidangData, timeseriesData, desilData, fetchAll }
})
