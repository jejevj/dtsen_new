<template>
  <Panel header="Filter" toggleable :collapsed="collapsed" class="mb-4">
    <slot />
    <Divider />
    <div class="flex gap-2 justify-end">
      <Button label="Reset" icon="pi pi-refresh" outlined severity="secondary" size="small" @click="$emit('reset')" />
      <Button label="Terapkan" icon="pi pi-filter" size="small" @click="$emit('apply')" />
    </div>
  </Panel>
</template>

<script setup>
import Panel from 'primevue/panel'
import Button from 'primevue/button'
import Divider from 'primevue/divider'

defineProps({ collapsed: { type: Boolean, default: false } })
defineEmits(['apply', 'reset'])
</script>
