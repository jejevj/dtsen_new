<template>
  <Card class="shadow-sm border border-gray-100">
    <template #content>
      <div class="flex items-center justify-between">
        <div>
          <p class="text-sm text-gray-500 font-medium">{{ label }}</p>
          <p class="text-2xl font-bold text-gray-800 mt-1">{{ formattedValue }}</p>
          <p v-if="subtitle" class="text-xs text-gray-400 mt-1">{{ subtitle }}</p>
        </div>
        <div
          :class="['w-12 h-12 rounded-full flex items-center justify-center', iconBg]"
        >
          <i :class="[icon, 'text-xl', iconColor]"></i>
        </div>
      </div>
    </template>
  </Card>
</template>

<script setup>
import Card from 'primevue/card'
import { computed } from 'vue'
import { formatRupiah } from '@/utils/formatter'

const props = defineProps({
  label:    { type: String, required: true },
  value:    { type: [Number, String], default: 0 },
  subtitle: { type: String, default: null },
  icon:     { type: String, default: 'pi pi-info-circle' },
  iconBg:   { type: String, default: 'bg-green-100' },
  iconColor:{ type: String, default: 'text-green-600' },
  format:   { type: String, default: 'number' }  // 'number' | 'currency' | 'text'
})

const formattedValue = computed(() => {
  if (props.format === 'currency') return formatRupiah(props.value)
  if (props.format === 'number') return Number(props.value).toLocaleString('id-ID')
  return props.value
})
</script>
