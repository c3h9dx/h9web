<script setup>
import {inject, onMounted, ref} from "vue";
import {CCol, CRow} from "@coreui/vue/dist/esm/components/grid/index.js";
import {CFormInput} from "@coreui/vue/dist/esm/components/form/index.js";
import {CButton} from "@coreui/vue/dist/esm/components/button/index.js";
import {CCard, CCardBody} from "@coreui/vue/dist/esm/components/card/index.js";

const axios = inject('axios');
const toasts = inject('toasts');

const node_columns = [
  {
    key: 'id',
    label: '#',
    // _props: {scope: 'col'},
  },
  {
    key: 'name',
    // _props: {scope: 'col'},
  }
]

const register_columns = [
  {
    key: 'id',
    label: '#',
    // _props: {scope: 'col'},
  },
  {
    key: 'name',
  },
  {
    key: 'size',
    label: 'Size [b]',
  },
  {
    key: 'type',
  },
  {
    key: 'value',
  },
  {
    key: 'action',
  }
]


const nodes = ref([])

const selected_device = ref({registers_list: []})

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
  return reg & (1 << bit)
}

function handleBitChange(reg, bit, value) {
  if (value) {
    reg.val |= (1 << bit);
  } else {
    reg.val &= ~(1 << bit);
  }
}

</script>

<template>
  <CRow>
    <CCol sm="3" class="mb-4">
      <CCard>
        <CCardBody>
          <CButton color="secondary" class="m-1" @click="refreshNodesList()">
            <CIcon icon="cil-loopCircular"/>
            Refresh
          </CButton>
          <CButton color="secondary" class="m-1" @click="discoverNodes()">
            <CIcon icon="cil-search"/>
            Discover
          </CButton>

          <CTable :columns="node_columns" hover>
            <CTableBody>
              <CTableRow v-for="node in nodes" :key="node.id" @click="handleNodeRowClick(node.id)">
                <CTableDataCell>{{ node.id }}</CTableDataCell>
                <CTableDataCell>{{ node.name }}</CTableDataCell>
              </CTableRow>
            </CTableBody>
          </CTable>
        </CCardBody>
      </CCard>
    </CCol>
    <CCol sm="auto">
      <CCard class="mb-4">
        <CCardBody>
          <CRow class="pb-3">
            <CCol class="pl-0">
              <CRow>
                <CCol class="col-3">Node id:</CCol>
                <CCol>{{ selected_device.id }}</CCol>
              </CRow>
              <CRow>
                <CCol class="col-3">Node type:</CCol>
                <CCol>{{ selected_device.type }}</CCol>
              </CRow>
              <CRow>
                <CCol class="col-3">Node name:</CCol>
                <CCol>{{ selected_device.name }}</CCol>
              </CRow>
              <CRow>
                <CCol class="col-3">Node version:</CCol>
                <CCol>
                  {{ selected_device.version_major }}.{{ selected_device.version_minor }}{{ String.fromCharCode(selected_device.hardware_revision) }}
                </CCol>
              </CRow>
              <CRow>
                <CCol class="col-3">Created:</CCol>
                <CCol>{{ selected_device.created_time }}</CCol>
              </CRow>
              <CRow>
                <CCol class="col-3">Last seen:</CCol>
                <CCol>{{ selected_device.last_seen_time }}</CCol>
              </CRow>
              <CRow>
                <CCol class="col-3">Description:</CCol>
                <CCol>{{ selected_device.description }}</CCol>
              </CRow>
            </CCol>
          </CRow>
          <CRow>
            <CCol>
              <CButton color="secondary" class="m-1" @click="nodeReset(selected_device.id)">
                <CIcon icon="cil-xCircle"/>
                Reset
              </CButton>
              <CButton color="secondary" class="m-1" disabled>
                <CIcon icon="cil-memory"/>
                Upload firmware
              </CButton>
            </CCol>
          </CRow>
        </CCardBody>
      </CCard>

      <CCard class="mb-4">
        <CCardBody>
      <CTable :columns="register_columns">
        <CTableBody>
          <template v-for="reg in selected_device.registers_list" :key="reg.id">
            <CTableRow>
              <CTableHeaderCell scope="row" :rowspan="reg.bits_names.length != 0 ? 2 : 1">{{
                  reg.number
                }}
              </CTableHeaderCell>
              <CTableDataCell>{{ reg.name }}</CTableDataCell>
              <CTableDataCell>{{ reg.size }}</CTableDataCell>
              <CTableDataCell>{{ reg.type }}</CTableDataCell>
              <CTableDataCell>
                <CFormInput v-model="reg.val"></CFormInput>
              </CTableDataCell>
              <CTableDataCell>
                <CButtonGroup size="sm">
                  <CButton :disabled="!reg.readable" @click="registerRead(selected_device.id, reg)">Get</CButton>
                  <CButton :disabled="!reg.writable" @click="registerWrite(selected_device.id, reg)">Set</CButton>
                </CButtonGroup>
              </CTableDataCell>

            </CTableRow>
            <CTableRow v-if="reg.bits_names.length != 0">
              <CTableDataCell colspan="5">
                <CButtonGroup size="sm">
                  <CFormCheck
                      :button="{color: 'primary', variant: 'outline'}"
                      :id="'bit_' + index"
                      :label="bit"
                      :text="bit"
                      @change="(event) => handleBitChange(reg, reg.bits_names.length - 1 - index, event.target.checked)"
                      :checked="isBitSet(reg.val, reg.bits_names.length - 1 - index)"
                      v-for="(bit, index) in reg.bits_names.slice().reverse()" :key="index"/>
                </CButtonGroup>
              </CTableDataCell>
            </CTableRow>
          </template>
        </CTableBody>
      </CTable>
        </CCardBody>
      </CCard>
    </CCol>
  </CRow>
</template>

<style scoped>

</style>