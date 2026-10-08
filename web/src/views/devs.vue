<script setup>
import {computed, inject, onMounted, ref} from "vue";
import {RouterLink, useRoute, useRouter} from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Tag from 'primevue/tag'

import {useEventStream} from '@/composables/useEventStream.js'
import {useDevCall} from '@/composables/useDevCall.js'

const axios = inject('axios');
const toasts = inject('toasts');
const route = useRoute()
const router = useRouter()
const callDev = useDevCall()

const devs = ref([])          // [{name, type}] from h9d get_devs_list
const selected_row = ref(null)
const selected = ref(null)    // {description, state} of the selected device
const loading = ref(false)

const description = computed(() => selected.value?.description)

// Current state as rows; nested values are shown as JSON
const state_rows = computed(() => {
  const state = selected.value?.state
  if (state === null || typeof state !== 'object') {
    return []
  }
  return Object.entries(state).map(([key, value]) => ({
    key,
    value: value !== null && typeof value === 'object' ? JSON.stringify(value) : String(value),
  }))
})

// Per method: params typed by the user (JSON object), last result or error, busy flag
const method_params = ref({})
const method_results = ref({})
const method_busy = ref({})

async function refreshDevsList() {
  await axios.get('/api/devs').then(response => {
    devs.value = response.data.response
  }).catch(function (error) {
    toasts.value.push({
      title: 'Refresh devs',
      content: error
    })
  })
}

async function selectDev(name) {
  loading.value = true
  method_params.value = {}
  method_results.value = {}
  await axios.get('/api/dev/' + encodeURIComponent(name)).then(response => {
    selected.value = response.data.response
  }).catch(function (error) {
    selected.value = null
    toasts.value.push({
      title: 'Dev info',
      content: error
    })
  })
  loading.value = false
  router.replace({query: {dev: name}})
}

async function callMethod(method) {
  const name = description.value.dev_name
  let params = {}
  const text = (method_params.value[method] ?? '').trim()
  if (text) {
    try {
      params = JSON.parse(text)
    } catch {
      method_results.value[method] = {error: 'Parameters must be JSON, e.g. {"node_id": 200}'}
      return
    }
  }

  method_busy.value[method] = true
  try {
    const result = await callDev(name, method, params)
    method_results.value[method] = {result: JSON.stringify(result)}
  } catch (error) {
    method_results.value[method] = {error: error.response?.data?.error?.message ?? String(error)}
  } finally {
    method_busy.value[method] = false
  }
}

// Live state of the selected device
useEventStream({
  dev: (message) => {
    if (selected.value && message.dev_name === description.value?.dev_name) {
      selected.value.state = {...(selected.value.state ?? {}), ...message.state}
    }
  }
})

onMounted(async () => {
  await refreshDevsList()
  // /devs?dev=<name> keeps the selection on reload
  const name = route.query.dev
  if (name && devs.value.some((d) => d.name === name)) {
    selected_row.value = devs.value.find((d) => d.name === name)
    await selectDev(name)
  }
})

function cpuSeconds(value) {
  return value == null ? '---' : value.toFixed(3) + ' s'
}

</script>

<template>
  <div class="page-row devs-page">
    <Card class="devs-list">
      <template #content>
        <div class="toolbar">
          <Button label="Refresh" icon="pi pi-refresh" severity="secondary" size="small" @click="refreshDevsList()"/>
        </div>
        <DataTable :value="devs" dataKey="name" selectionMode="single" v-model:selection="selected_row"
                   @rowSelect="(e) => selectDev(e.data.name)" size="small" class="mt">
          <Column field="name" header="Name"/>
          <Column field="type" header="Type"/>
        </DataTable>
        <p v-if="!devs.length" class="muted mt">h9d reports no devices.</p>
      </template>
    </Card>

    <div class="page dev-details">
      <Card>
        <template #content>
          <p v-if="!description" class="muted no-margin">Select a device.</p>
          <dl v-else class="kv">
            <dt>Name:</dt>
            <dd>{{ description.dev_name }}</dd>
            <dt>Type:</dt>
            <dd>{{ description.dev_type }}</dd>
            <dt>Plugin version:</dt>
            <dd>{{ description.dev_version ?? '---' }}</dd>
            <dt>Node types:</dt>
            <dd>{{ description.dev_node_types?.length ? description.dev_node_types.join(', ') : '---' }}</dd>
            <dt>Related nodes:</dt>
            <dd class="nodes">
              <RouterLink v-for="id in description.dev_related_nodes" :key="id" :to="{ path: '/nodes', query: { node: id } }"
                          v-tooltip.top="'Open in Nodes'">
                <Tag :value="String(id)"/>
              </RouterLink>
              <span v-if="!description.dev_related_nodes?.length" class="muted">none</span>
            </dd>
            <dt>CPU usage:</dt>
            <dd>
              {{ cpuSeconds(description.dev_cpu_usage?.total) }}
              <span class="muted">(user {{ cpuSeconds(description.dev_cpu_usage?.user) }},
                system {{ cpuSeconds(description.dev_cpu_usage?.system) }})</span>
            </dd>
          </dl>
          <div v-if="description" class="toolbar mt">
            <Button label="Reload" icon="pi pi-refresh" severity="secondary" size="small" :loading="loading"
                    @click="selectDev(description.dev_name)"/>
          </div>
        </template>
      </Card>

      <Card v-if="description">
        <template #title><span class="caption">State</span></template>
        <template #content>
          <DataTable v-if="state_rows.length" :value="state_rows" dataKey="key" size="small">
            <Column field="key" header="Key"/>
            <Column header="Value">
              <template #body="{ data: row }"><code>{{ row.value }}</code></template>
            </Column>
          </DataTable>
          <p v-else class="muted no-margin">No state reported.</p>
        </template>
      </Card>

      <Card v-if="description">
        <template #title><span class="caption">Methods</span></template>
        <template #content>
          <div v-for="method in description.dev_methods" :key="method" class="method">
            <code class="method-name">{{ method }}</code>
            <InputText v-model="method_params[method]" size="small" placeholder='params, e.g. {"node_id": 200}'
                       class="method-params" @keydown.enter="callMethod(method)"/>
            <Button label="Call" icon="pi pi-play" size="small" :loading="method_busy[method]"
                    @click="callMethod(method)"/>
            <div v-if="method_results[method]" class="method-result"
                 :class="{ error: method_results[method].error }">
              {{ method_results[method].error ?? method_results[method].result }}
            </div>
          </div>
          <p v-if="!description.dev_methods?.length" class="muted no-margin">The device has no methods.</p>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.devs-page > .devs-list {
  flex: 0 1 18rem;
}

.devs-page > .dev-details {
  flex: 1 1 36rem;
}

.mt {
  margin-top: 1rem;
}

.no-margin {
  margin: 0;
}

.nodes {
  display: flex;
  flex-wrap: wrap;
  gap: .35rem;
}

.method {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .5rem .75rem;
  padding: .6rem 0;
}

.method + .method {
  border-top: 1px solid var(--app-border);
}

.method-name {
  min-width: 6rem;
  font-size: .95rem;
  font-weight: 600;
}

.method-params {
  flex: 1 1 14rem;
  font-family: ui-monospace, monospace;
}

.method-result {
  flex-basis: 100%;
  font-family: ui-monospace, monospace;
  font-size: .85rem;
  color: var(--app-accent);
  word-break: break-all;
}

.method-result.error {
  color: var(--app-danger);
}
</style>
