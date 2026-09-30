<script setup>

import {inject, onMounted, ref} from 'vue'
import {GridLayout} from 'grid-layout-plus'
import Button from 'primevue/button'

import {useEventStream} from '@/composables/useEventStream.js'
import {unknownWidget, widgets} from './dev/index.js'

const axios = inject('axios');
const toasts = inject('toasts');

const layout = ref([])
const devs = ref({})  // name -> {name, type, methods, state}
const loaded = ref(false)
const editing = ref(false)

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
    }
  }
})

onMounted(loadDashboard)

</script>

<template>
  <div class="page">
    <div class="toolbar">
      <Button :label="editing ? 'Done' : 'Edit layout'" :icon="editing ? 'pi pi-check' : 'pi pi-pencil'"
              :severity="editing ? undefined : 'secondary'" size="small" @click="editing = !editing"/>
      <span v-if="editing" class="muted">Drag tiles to move them, drag the corner to resize.</span>
    </div>
    <p v-if="loaded && !layout.length" class="muted">h9d reports no devices.</p>
    <GridLayout v-model:layout="layout" :row-height="30" :is-draggable="editing" :is-resizable="editing"
                :class="{ editing }" @layout-updated="onLayoutUpdated">
      <template #item="{ item }">
        <div class="surface-card dash-item">
          <div class="dev-header">{{ widgetOf(item.i).title }} <small>{{ item.i }}</small></div>
          <div class="dev-body">
            <component :is="widgetOf(item.i).component" :dev="devs[item.i]"/>
          </div>
        </div>
      </template>
    </GridLayout>
  </div>
</template>

<style scoped>
.dash-item {
  height: 100%;
  overflow: hidden;
}

/* Edit mode: make tiles look movable and keep clicks from reaching the device controls */
.editing .dash-item {
  cursor: move;
  outline: 2px dashed var(--p-primary-color);
  outline-offset: -2px;
}

.editing .dev-body {
  pointer-events: none;
  opacity: .6;
}
</style>
