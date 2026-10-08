<script setup>
import {computed, inject, onMounted, ref} from "vue";
import {RouterLink, useRoute} from 'vue-router'
import Card from 'primevue/card'
import Button from 'primevue/button'
import ButtonGroup from 'primevue/buttongroup'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import InputText from 'primevue/inputtext'
import Tag from 'primevue/tag'

import {formatDateTime} from '@/utils/format.js'

const axios = inject('axios');
const toasts = inject('toasts');
const route = useRoute()

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
  // /nodes?node=<id> (e.g. a link from Devs) opens that node
  const id = Number(route.query.node)
  if (route.query.node !== undefined && !isNaN(id)) {
    selected_node.value = nodes.value.find((n) => n.id === id) ?? null
    await handleNodeRowClick(id)
  }
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

// Node info as sent by h9d get_node_info (h9can/include/h9def.h)
const RESET_REASONS = ['unknown', 'power on', 'watchdog', 'brown-out', 'external reset', 'software']
const NODE_FLAG_RESET_REASON_MASK = 0x0007
const NODE_FLAG_BL_PRESENT = 0x0008
const NODE_FLAG_BL_MISMATCH = 0x0010
const NODE_FLAG_DEFAULT_ID = 0x0020
const NODE_FLAG_CAN_ERROR_WARNING = 0x0040
const NODE_FLAG_CAN_TX_FRAME_LOSS = 0x0080
const NODE_FLAG_CAN_RX_FRAME_LOSS = 0x0100

const node_loaded = computed(() => selected_device.value.id !== undefined)

const node_version = computed(() => {
  const d = selected_device.value
  return [d.version_major, d.version_minor, d.version_patch].map((v) => v ?? 0).join('.')
})

// PCB revision letter + BOM revision number, e.g. A0
const pcb_revision = computed(() => {
  const d = selected_device.value
  const pcb = d.hardware_revision >= 0x20 ? String.fromCharCode(d.hardware_revision) : '?'
  return pcb + (d.bom_revision ?? '')
})

const reset_reason = computed(() => {
  const d = selected_device.value
  const reason = d.reset_reason ?? (d.flags & NODE_FLAG_RESET_REASON_MASK)
  return RESET_REASONS[reason] ?? `unknown (${reason})`
})

// Bootloader state and CAN problems reported in the node flags
const node_flags = computed(() => {
  const flags = selected_device.value.flags ?? 0
  const tags = []
  if (flags & NODE_FLAG_BL_PRESENT) {
    tags.push(flags & NODE_FLAG_BL_MISMATCH
        ? {text: 'bootloader mismatch', severity: 'danger'}
        : {text: 'bootloader', severity: 'secondary'})
  } else {
    tags.push({text: 'no bootloader', severity: 'secondary'})
  }
  if (flags & NODE_FLAG_DEFAULT_ID) tags.push({text: 'default id', severity: 'warn'})
  if (flags & NODE_FLAG_CAN_ERROR_WARNING) tags.push({text: 'CAN error warning', severity: 'warn'})
  if (flags & NODE_FLAG_CAN_TX_FRAME_LOSS) tags.push({text: 'CAN TX frame loss', severity: 'danger'})
  if (flags & NODE_FLAG_CAN_RX_FRAME_LOSS) tags.push({text: 'CAN RX frame loss', severity: 'danger'})
  return tags
})

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
            <dd>
              <RouterLink v-if="node_loaded" :to="{ path: '/rawframe', query: { dst: selected_device.id } }"
                          class="node-link" v-tooltip.top="'Send a frame to this node'">
                {{ selected_device.id }}
              </RouterLink>
            </dd>
            <dt>Node type:</dt>
            <dd>{{ selected_device.type }}</dd>
            <dt>Node name:</dt>
            <dd>{{ selected_device.name }}</dd>
            <dt>Firmware version:</dt>
            <dd>{{ node_loaded ? node_version : '' }}</dd>
            <dt>PCB revision:</dt>
            <dd>{{ node_loaded ? pcb_revision : '' }}</dd>
            <dt>Reset reason:</dt>
            <dd>{{ node_loaded ? reset_reason : '' }}</dd>
            <dt>Flags:</dt>
            <dd class="flags">
              <template v-if="node_loaded">
                <Tag v-for="t in node_flags" :key="t.text" :value="t.text" :severity="t.severity"/>
              </template>
            </dd>
            <dt>Created:</dt>
            <dd>{{ node_loaded ? formatDateTime(selected_device.created_time) : '' }}</dd>
            <dt>Last seen:</dt>
            <dd>{{ node_loaded ? formatDateTime(selected_device.last_seen_time) : '' }}</dd>
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

.node-link {
  color: var(--app-accent);
  font-weight: 600;
  text-decoration: none;
}

.node-link:hover {
  text-decoration: underline;
}

.flags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .35rem;
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
