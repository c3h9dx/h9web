<script setup>

import {defineAsyncComponent, inject, onMounted, reactive, ref} from 'vue'
import {GridLayout} from 'grid-layout-plus'

const axios = inject('axios');
const toasts = inject('toasts');
const sse = inject('sse')

let sseClient

const components = {}
const loadComponents = async () => {
  const modules = import.meta.glob('./dev/*.vue');

  for (const path in modules) {
    const name = path.match(/\/([^/]+)\.vue$/)[1];
    components[name] = defineAsyncComponent(modules[path]);
  }
};

loadComponents();

const layout = ref([])
const devs_state = ref({})

function updateDevState(target, updates) {
  for (const key in updates) {
    if (updates.hasOwnProperty(key)) {
      if (typeof updates[key] === 'object' && updates[key] !== null && typeof target[key] === 'object' && target[key] !== null) {
        updateDevState(target[key], updates[key]);
      } else {
        target[key] = updates[key];
      }
    }
  }
}

function saveLayout(l) {
  if (l.length) {
    axios.post('/api/dashboard', {'layout': l}, {headers: {'Content-Type': 'application/json'}}).then(response => {
    }).catch(function (error) {
      toasts.value.push({
        title: 'Dashboard save',
        content: error
      })
    })
  }
}

onMounted(async () => {
  axios.get('/api/dashboard').then(response => {
    for (const l in response.data.response) {
      let tmp = {}
      tmp[l.i] = {}
      updateDevState(devs_state.value, tmp)
    }
    layout.value = response.data.response
  }).catch(function (error) {
    toasts.value.push({
      title: 'Dashboard init',
      content: error
    })
  })

  sseClient = sse.create({
    format: 'json',
    url: '/api/events?filter=dev',
    withCredentials: true,
  })

  sseClient.connect().then(sse => {
    console.log('We\'re connected!');
  }).catch((error) => {
    toasts.value.push({
      title: 'SSE connect',
      content: error
    })
    console.error('Failed make initial connection:', error)
  });

  sseClient.on('dev', (message, lastEventId) => {
    console.warn('Received a message w/o an event!', message, lastEventId);
    let tmp = {}
    tmp[message.dev_name] = message.state
    updateDevState(devs_state.value, tmp)
    console.log(tmp)
    console.log(devs_state.value)
    // last_stats.value = message;
  });

  sseClient.on('error', (e) => {
    console.error('lost connection or failed to parse!', e);
    toasts.value.push({
      title: 'SSE error',
      content: e
    })
  });
})

</script>

<template>
  <div>
    <GridLayout v-model:layout="layout" :row-height="30" class="h-75" @layout-updated="saveLayout">
      <template #item="{ item }">
        <CCard class="h-100" style="overflow: hidden;">
          <component :is="components[item.component]" :dev_name="item.i" :dev_state="devs_state[item.i]"/>
        </CCard>
      </template>
    </GridLayout>
  </div>
</template>
