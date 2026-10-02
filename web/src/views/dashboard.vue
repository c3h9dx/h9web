<script setup>

import {computed, inject, onBeforeUnmount, onMounted, ref} from 'vue'
import {GridLayout} from 'grid-layout-plus'
import Button from 'primevue/button'

import DashboardTile from '@/components/DashboardTile.vue'
import {useEventStream} from '@/composables/useEventStream.js'
import {unknownWidget, widgets} from './dev/index.js'

const axios = inject('axios');
const toasts = inject('toasts');

const layout = ref([])
const devs = ref({})  // name -> {name, type, methods, state}
const loaded = ref(false)
const editing = ref(false)

// A 12 column grid is unreadable on a phone - there the tiles are stacked in grid order instead
const narrowQuery = window.matchMedia('(max-width: 767.98px)')
const narrow = ref(narrowQuery.matches)
const onNarrowChange = (e) => {
  narrow.value = e.matches
  editing.value = false
}
onMounted(() => narrowQuery.addEventListener('change', onNarrowChange))
onBeforeUnmount(() => narrowQuery.removeEventListener('change', onNarrowChange))

const stacked = computed(() => [...layout.value].sort((a, b) => a.y - b.y || a.x - b.x))

function widgetOf(dev_name) {
  return widgets[devs.value[dev_name]?.type] ?? unknownWidget
}

async function loadDashboard() {
  await axios.get('/api/dashboard').then(response => {
    const {layout: l, devs: d} = response.data.response
    devs.value = Object.fromEntries(Object.entries(d).map(([name, dev]) => [name, {name, ...dev}]))
    layout.value = l
  }).catch(function (error) {
    toasts.value.push({
      title: 'Dashboard init',
      content: error
    })
  })
  loaded.value = true
}

// Tiles move only in edit mode, so every layout change there is the user's - save it right away
function onLayoutUpdated() {
  if (!editing.value) {
    return
  }
  axios.post('/api/dashboard', {layout: layout.value}).catch(function (error) {
    toasts.value.push({
      title: 'Dashboard save',
      content: error
    })
  })
}

useEventStream({
  dev: (message) => {
    const dev = devs.value[message.dev_name]
    if (dev) {
      dev.state = {...dev.state, ...message.state}
      // Devices that send several kinds of events tag them with event_name - keep the last one of each kind
      if (message.state?.event_name) {
        dev.events = {...dev.events, [message.state.event_name]: message.state}
      }
    }
  }
})

onMounted(loadDashboard)

</script>

<template>
  <div class="page">
    <div v-if="!narrow" class="toolbar">
      <Button :label="editing ? 'Done' : 'Edit layout'" :icon="editing ? 'pi pi-check' : 'pi pi-pencil'"
              :severity="editing ? undefined : 'secondary'" size="small" @click="editing = !editing"/>
      <span v-if="editing" class="muted">Drag tiles to move them, drag the corner to resize.</span>
    </div>
    <p v-if="loaded && !layout.length" class="muted">h9d reports no devices.</p>
    <div v-if="narrow" class="page">
      <DashboardTile v-for="item in stacked" :key="item.i" :widget="widgetOf(item.i)" :dev="devs[item.i]"/>
    </div>
    <GridLayout v-else v-model:layout="layout" :row-height="30" :is-draggable="editing" :is-resizable="editing"
                :class="{ editing }" @layout-updated="onLayoutUpdated">
      <template #item="{ item }">
        <DashboardTile :widget="widgetOf(item.i)" :dev="devs[item.i]"/>
      </template>
    </GridLayout>
  </div>
</template>

<style scoped>
/* grid-layout-plus keeps a 10px margin around tiles - align the tiles with the page edges */
:deep(.vgl-layout) {
  margin: -10px;
}

/* Edit mode: make tiles look movable and keep clicks from reaching the device controls */
.editing :deep(.dash-tile) {
  cursor: move;
  outline: 2px dashed var(--p-primary-color);
  outline-offset: -2px;
}

.editing :deep(.dev-body) {
  pointer-events: none;
  opacity: .6;
}
</style>
