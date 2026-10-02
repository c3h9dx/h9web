<script setup>
import {computed, inject, onMounted, ref} from "vue";
import Card from 'primevue/card'
import Button from 'primevue/button'
import ButtonGroup from 'primevue/buttongroup'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'

const axios = inject('axios');
const toasts = inject('toasts');

const nodes = ref([])

const selected_device = ref({registers_list: []})
const selected_node = ref(null)

// Registers with named bits get an always-expanded row with a button per bit
const expanded_registers = computed(() =>
    Object.fromEntries(selected_device.value.registers_list
        .filter((reg) => reg.bits_names.length)
        .map((reg) => [reg.number, true])))

async function refreshNodesList() {
  await axios
      .get('/api/nodes')
      .then(response => {
        nodes.value = response.data.response
      }).catch(function (error) {
        toasts.value.push({
          title: 'Refresh nodes',
          content: error
        })
      })
  selected_device.value = {registers_list: []};
  selected_node.value = null;
}

async function discoverNodes() {
  await axios.post('/api/nodes/discover').catch(function (error) {
    toasts.value.push({
      title: 'Nodes discovery',
      content: error
    })
  })
}

async function registerRead(node_id, reg) {
  await axios
      .get('/api/node/' + node_id + '/reg/' + reg.number)
      .then(response => {
        reg.val = response.data.response
      }).catch(function (error) {
        toasts.value.push({
          title: 'Node read register',
          content: error
        })
      })
}

async function registerWrite(node_id, reg) {
  if (reg.type != 'str' && (typeof reg.val === "string")) {
    reg.val = parseInt(reg.val);
  }
  await axios
      .put('/api/node/' + node_id + '/reg/' + reg.number, {value: reg.val}, {headers: {'Content-Type': 'application/json'}})
      .then(response => {
        reg.val = response.data.response
      }).catch(function (error) {
        toasts.value.push({
          title: 'Node write register',
          content: error
        })
      })
}

async function nodeReset(node_id) {
  await axios
      .post('/api/node/' + node_id + '/reset')
      .then(response => {

      }).catch(function (error) {
        toasts.value.push({
          title: 'Node reset',
          content: error
        })
      })
}

onMounted(async () => {
  await refreshNodesList()
})

async function handleNodeRowClick(id) {
  await axios
      .get('/api/node/' + id)
      .then(response => {
        selected_device.value = response.data.response
      }).catch(function (error) {
        toasts.value.push({
          title: 'Node info',
          content: error
        })
      })
}

function isBitSet(reg, bit) {
  return (reg & (1 << bit)) !== 0
}

// bits_names[i] names bit i; shown MSB first
function bitsOf(reg) {
  return reg.bits_names.map((name, bit) => ({name, bit})).reverse()
}

async function handleBitChange(node_id, reg, bit, value) {
  await axios({
    method: value ? 'put' : 'delete',
    url: '/api/node/' + node_id + '/reg/' + reg.number + '/bit/' + bit,
  }).then(async () => {
    // h9d answers set/clear bit with raw bytes, so read the value back in the same form as Get
    await registerRead(node_id, reg)
  }).catch(function (error) {
    toasts.value.push({
      title: value ? 'Node set bit' : 'Node clear bit',
      content: error
    })
  })
}

</script>

<template>
  <div class="page-row nodes-page">
    <Card class="nodes-list">
      <template #content>
        <div class="toolbar">
          <Button label="Refresh" icon="pi pi-refresh" severity="secondary" size="small" @click="refreshNodesList()"/>
          <Button label="Discover" icon="pi pi-search" severity="secondary" size="small" @click="discoverNodes()"/>
        </div>
        <DataTable :value="nodes" dataKey="id" selectionMode="single" v-model:selection="selected_node"
                   @rowSelect="(e) => handleNodeRowClick(e.data.id)" size="small" class="mt">
          <Column field="id" header="#"/>
          <Column field="name" header="Name"/>
        </DataTable>
      </template>
    </Card>
    <div class="page node-details">
      <Card>
        <template #content>
          <dl class="kv">
            <dt>Node id:</dt>
            <dd>{{ selected_device.id }}</dd>
            <dt>Node type:</dt>
            <dd>{{ selected_device.type }}</dd>
            <dt>Node name:</dt>
            <dd>{{ selected_device.name }}</dd>
            <dt>Node version:</dt>
            <dd>
              <template v-if="selected_device.id !== undefined">
                {{ selected_device.version_major }}.{{ selected_device.version_minor }}{{ String.fromCharCode(selected_device.hardware_revision) }}
              </template>
            </dd>
            <dt>Created:</dt>
            <dd>{{ selected_device.created_time }}</dd>
            <dt>Last seen:</dt>
            <dd>{{ selected_device.last_seen_time }}</dd>
            <dt>Description:</dt>
            <dd>{{ selected_device.description }}</dd>
          </dl>
          <div class="toolbar mt">
            <Button label="Reset" icon="pi pi-times-circle" severity="secondary" size="small"
                    :disabled="selected_device.id === undefined" @click="nodeReset(selected_device.id)"/>
            <Button label="Upload firmware" icon="pi pi-microchip" severity="secondary" size="small" disabled/>
          </div>
        </template>
      </Card>

      <Card>
        <template #content>
          <DataTable :value="selected_device.registers_list" dataKey="number" :expandedRows="expanded_registers"
                     size="small">
            <Column field="number" header="#"/>
            <Column header="Name">
              <template #body="{ data: reg }">
                {{ reg.name }}
                <div v-if="reg.description" class="reg-description muted">{{ reg.description }}</div>
              </template>
            </Column>
            <Column field="size" header="Size [B]"/>
            <Column field="type" header="Type"/>
            <Column header="Value">
              <template #body="{ data: reg }">
                <InputText v-model="reg.val" size="small" fluid/>
              </template>
            </Column>
            <Column header="Action">
              <template #body="{ data: reg }">
                <ButtonGroup>
                  <Button label="Get" size="small" severity="secondary" outlined :disabled="!reg.readable"
                          @click="registerRead(selected_device.id, reg)"/>
                  <Button label="Set" size="small" severity="secondary" outlined :disabled="!reg.writable"
                          @click="registerWrite(selected_device.id, reg)"/>
                </ButtonGroup>
              </template>
            </Column>
            <template #expansion="{ data: reg }">
              <ButtonGroup class="bits">
                <Button v-for="b in bitsOf(reg)" :key="b.bit" :label="b.name" size="small"
                        :outlined="!isBitSet(reg.val, b.bit)" :disabled="!reg.writable"
                        :data-bit="reg.number + '.' + b.bit"
                        @click="handleBitChange(selected_device.id, reg, b.bit, !isBitSet(reg.val, b.bit))"/>
              </ButtonGroup>
            </template>
          </DataTable>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.nodes-page > .nodes-list {
  flex: 0 1 18rem;
}

.nodes-page > .node-details {
  flex: 1 1 36rem;
}

.mt {
  margin-top: 1rem;
}

.reg-description {
  font-size: .8rem;
}

.bits {
  flex-wrap: wrap;
}

/* Disabled (read-only register) bits still show their state */
.bits :deep(.p-button:disabled) {
  opacity: .75;
}
</style>
