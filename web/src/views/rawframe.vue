<script setup>

import {CCardBody} from "@coreui/vue/dist/esm/components/card/index.js";
import {CCol, CRow} from "@coreui/vue/dist/esm/components/grid/index.js";
import {computed, inject, onBeforeUnmount, onMounted, ref} from "vue";
import {CButton} from "@coreui/vue/dist/cjs/components/button/index.js";

const axios = inject('axios');
const toasts = inject('toasts');
const sse = inject('sse')

let sseClient

// Frame types as defined in h9can/include/h9def.h (h9d v0.4)
const frame_type = [
  // --- UNICAST ---
  {value: 0, label: "RES1"},
  {value: 1, label: "PAGE_START"},
  {value: 2, label: "QUIT_BOOTLOADER"},
  {value: 3, label: "PAGE_FILL"},
  {value: 4, label: "RES2"},
  {value: 5, label: "PAGE_FILL_NEXT"},
  {value: 6, label: "PAGE_WRITED"},
  {value: 7, label: "PAGE_FILL_BREAK"},
  {value: 8, label: "COMMAND_ERROR"},
  {value: 9, label: "REG_VALUE"},
  {value: 10, label: "SET_REG"},
  {value: 11, label: "GET_REG"},
  {value: 12, label: "SET_BIT"},
  {value: 13, label: "CLEAR_BIT"},
  {value: 14, label: "NODE_UPGRADE"},
  {value: 15, label: "NODE_RESET"},
  // --- SPECIAL BROADCAST ---
  {value: 16, label: "DISCOVER"},
  {value: 17, label: "GROUP_RESET"},
  // --- BROADCAST ---
  {value: 18, label: "NODE_FAULT"},
  {value: 19, label: "REG_VALUE_BROADCAST"},
  {value: 20, label: "NODE_HEARTBEAT"},
  {value: 21, label: "NODE_INFO"},
  {value: 22, label: "NODE_TURNED_ON"},
  {value: 23, label: "BOOTLOADER_TURNED_ON"},
  {value: 24, label: "NODE_SPECIFIC_BROADCAST0"},
  {value: 25, label: "NODE_SPECIFIC_BROADCAST1"},
  {value: 26, label: "NODE_SPECIFIC_BROADCAST2"},
  {value: 27, label: "NODE_SPECIFIC_BROADCAST3"},
  {value: 28, label: "NODE_SPECIFIC_BROADCAST4"},
  {value: 29, label: "NODE_SPECIFIC_BROADCAST5"},
  {value: 30, label: "NODE_SPECIFIC_BROADCAST6"},
  {value: 31, label: "NODE_SPECIFIC_BROADCAST7"}
];

const frame_flags = [
  {value: 0, label: "SINGLE_FRAME"},
  {value: 1, label: "MULTI_FRAME_FIRST"},
  {value: 2, label: "MULTI_FRAME_MIDDLE"},
  {value: 3, label: "MULTI_FRAME_LAST"}
];

const BROADCAST_TYPE_MIN = 16  // H9FRAME_TYPE_DISCOVER - types from here up are broadcasts
const BROADCAST_ALL_GROUP = 0xffff

const TYPE_MAX = 31
const FLAGS_MAX = 7
const SEQNUM_MAX = 31
const ID_MAX = 255
const GROUP_MAX = 0xffff

function isBroadcast(type) {
  return Number(type) >= BROADCAST_TYPE_MIN
}

function typeLabel(type) {
  const t = frame_type.find((t) => t.value === type)
  return t ? t.label : type
}

function flagsLabel(flags) {
  const f = frame_flags.find((f) => f.value === flags)
  return f ? f.label : flags
}

function groupLabel(group) {
  return group === BROADCAST_ALL_GROUP ? 'ALL' : group
}

const frame = ref({
  type: 11,
  flags: 0,
  seqnum: 0,
  destination_id: 0,
  source_id: 0,
  broadcast_group: 0,
  dlc: 0,
  data: [null, null, null, null, null, null, null, null]
})

const group_all = ref(false)

const is_broadcast = computed(() => isBroadcast(frame.value.type))

const frames_columns = [
  {
    key: 'origin',
    // _props: {scope: 'col'},
  },
  {
    key: 'source_id',
    label: 'Src',
    // _props: {scope: 'col'},
  },
  {
    key: 'destination',
    label: 'Dst / Group',
    // _props: {scope: 'col'},
  },
  {
    key: 'type',
    // _props: {scope: 'col'},
  },
  {
    key: 'flags',
    // _props: {scope: 'col'},
  },
  {
    key: 'seqnum',
    // _props: {scope: 'col'},
  },
  {
    key: 'data',
    // _props: {scope: 'col'},
  },
  {
    label: 'Action',
    // _props: {scope: 'col'},
  }
]

const raw_frame = ref(false)

const frames = ref([])

onMounted(async () => {
  await axios
      .get('/api/frames')
      .then(response => {
        frames.value = response.data.response
      }).catch(function (error) {
        toasts.value.push({
          title: 'Refresh nodes',
          content: error
        })
      })

  sseClient = sse.create({
    format: 'json',
    url: '/api/events?filter=frame',
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

  sseClient.on('frame', (message, lastEventId) => {
    console.warn('Received a message w/o an event!', message, lastEventId);
    frames.value.push(message)
  });

  sseClient.on('error', (e) => {
    console.error('lost connection or failed to parse!', e);
    toasts.value.push({
      title: 'SSE error',
      content: e
    })
    // If this error is due to an unexpected disconnection, EventSource will
    // automatically attempt to reconnect indefinitely. You will _not_ need to
    // re-add your handlers.
  });

})

function clean_frame() {
  frame.value.type = 11;
  frame.value.flags = 0;
  frame.value.seqnum = 0;
  frame.value.destination_id = 0;
  frame.value.source_id = 0;
  frame.value.broadcast_group = 0;
  group_all.value = false;
  frame.value.dlc = 0;
  for (let i = 0; i < 8; i++) {
    frame.value.data[i] = null;
  }
}

// Form inputs give strings - returns the integer, or null when it is not a number in [0, max]
function toInt(value, max) {
  const n = typeof (value) === "number" ? value : parseInt(value)
  return Number.isInteger(n) && n >= 0 && n <= max ? n : null
}

async function send_frame() {
  let i = 0;

  const f = frame.value
  const type = toInt(f.type, TYPE_MAX)

  for (i = 0; i < 8; i++) {
    const tmp = toInt(f.data[i], 255)
    if (tmp === null)
      break;
    f.data[i] = tmp;
  }
  const dlc = i;
  for (; i < 8; i++) {
    f.data[i] = null;
  }

  // h9d picks the fields by frame kind, so send only the ones that apply
  const payload = {type: type, dlc: dlc, data: f.data.slice(0, dlc)}
  if (isBroadcast(type)) {
    payload.broadcast_group = group_all.value ? BROADCAST_ALL_GROUP : toInt(f.broadcast_group, GROUP_MAX)
  } else {
    payload.flags = toInt(f.flags, FLAGS_MAX)
    payload.destination_id = toInt(f.destination_id, ID_MAX)
    if (raw_frame.value)
      payload.seqnum = toInt(f.seqnum, SEQNUM_MAX)
  }
  if (raw_frame.value)
    payload.source_id = toInt(f.source_id, ID_MAX)

  const invalid = Object.keys(payload).filter((k) => payload[k] === null)
  if (invalid.length) {
    toasts.value.push({
      title: 'Send frame',
      content: 'Invalid value: ' + invalid.join(', ')
    })
    return
  }

  await axios.post('/api/frames', {frame: payload, raw: raw_frame.value}, {headers: {'Content-Type': 'application/json'}})
      .catch(function (error) {
        toasts.value.push({
          title: 'Send frame',
          content: error
        })
      })

}

onBeforeUnmount(() => {
  console.error('Disconnecting!');
  sseClient.disconnect()
})

function copyFrame(f) {
  frame.value.type = f.type;
  frame.value.source_id = f.source_id;
  if (isBroadcast(f.type)) {
    group_all.value = f.broadcast_group === BROADCAST_ALL_GROUP;
    frame.value.broadcast_group = group_all.value ? 0 : f.broadcast_group;
  } else {
    frame.value.flags = f.flags;
    frame.value.seqnum = f.seqnum;
    frame.value.destination_id = f.destination_id;
  }
  frame.value.dlc = f.dlc;
  for (let i = 0; i < 8; i++) {
    frame.value.data[i] = i < f.dlc ? f.data[i] : null;
  }
}

function frameDetails(f) {
  const {visible, ...rest} = f
  return JSON.stringify(rest)
}

function toggleFrameDetailsVisibility(item) {
  item.visible = !item.visible;
}

</script>

<template>
    <CRow><CCol sm="auto">
      <CCard class="mb-3">
        <CCardBody>
          <!--      <CForm class="row g-3">-->
          <CForm>
            <CRow class="mb-3">
              <!--      <div class="row align-items-center justify-content-center">-->
              <CCol class="col-auto">
                <CFormLabel for="inputType">Type</CFormLabel>
                <CFormSelect id="inputType" size="sm" v-model.number="frame.type">
                  <optgroup label="Unicast">
                    <option v-for="t in frame_type.filter((t) => !isBroadcast(t.value))" :key="t.value" :value="t.value">
                      {{ t.value }} {{ t.label }}
                    </option>
                  </optgroup>
                  <optgroup label="Broadcast">
                    <option v-for="t in frame_type.filter((t) => isBroadcast(t.value))" :key="t.value" :value="t.value">
                      {{ t.value }} {{ t.label }}
                    </option>
                  </optgroup>
                </CFormSelect>
              </CCol>
              <CCol class="col-auto">
                <CFormLabel for="inputSource">Source</CFormLabel>
                <CFormInput id="inputSource" :disabled="!raw_frame" size="sm" maxlength="3" style="max-width: 10ch;"
                            v-model="frame.source_id"></CFormInput>
              </CCol>
              <template v-if="!is_broadcast">
                <CCol class="col-auto">
                  <CFormLabel for="inputDestination">Destination</CFormLabel>
                  <CFormInput id="inputDestination" size="sm" maxlength="3" style="max-width: 10ch;"
                              v-model="frame.destination_id"></CFormInput>
                </CCol>
                <CCol class="col-auto">
                  <CFormLabel for="inputFlags">Flags</CFormLabel>
                  <CFormSelect id="inputFlags" size="sm" :options="frame_flags" v-model.number="frame.flags"></CFormSelect>
                </CCol>
                <CCol class="col-auto">
                  <CFormLabel for="inputSeqnum">Seqnum</CFormLabel>
                  <CFormInput id="inputSeqnum" :disabled="!raw_frame" size="sm" maxlength="2" style="max-width: 10ch;"
                              v-model="frame.seqnum"></CFormInput>
                </CCol>
              </template>
              <template v-else>
                <CCol class="col-auto">
                  <CFormLabel for="inputGroup" title="Broadcast group - node type">Group</CFormLabel>
                  <CInputGroup size="sm">
                    <CFormInput id="inputGroup" :disabled="group_all" maxlength="5" style="max-width: 10ch;"
                                v-model="frame.broadcast_group"></CFormInput>
                    <CInputGroupText>
                      <CFormCheck id="group_all_checkbox" label="All" v-model="group_all"/>
                    </CInputGroupText>
                  </CInputGroup>
                </CCol>
              </template>
              <CCol class="col-auto">
                <CFormLabel for="inputData">Data</CFormLabel>
                <fieldset id="inputData">
                  <CInputGroup>
                    <CFormInput name="data[0]" size="sm" maxlength="4" style="max-width: 5ch;"
                                v-model="frame.data[0]"></CFormInput>
                    <CFormInput name="data[1]" size="sm" maxlength="4" style="max-width: 5ch;"
                                v-model="frame.data[1]"></CFormInput>
                    <CFormInput name="data[2]" size="sm" maxlength="4" style="max-width: 5ch;"
                                v-model="frame.data[2]"></CFormInput>
                    <CFormInput name="data[3]" size="sm" maxlength="4" style="max-width: 5ch;"
                                v-model="frame.data[3]"></CFormInput>
                    <CFormInput name="data[4]" size="sm" maxlength="4" style="max-width: 5ch;"
                                v-model="frame.data[4]"></CFormInput>
                    <CFormInput name="data[5]" size="sm" maxlength="4" style="max-width: 5ch;"
                                v-model="frame.data[5]"></CFormInput>
                    <CFormInput name="data[6]" size="sm" maxlength="4" style="max-width: 5ch;"
                                v-model="frame.data[6]"></CFormInput>
                    <CFormInput name="data[7]" size="sm" maxlength="4" style="max-width: 5ch;"
                                v-model="frame.data[7]"></CFormInput>
                  </CInputGroup>
                </fieldset>
              </CCol>
            </CRow>
            <CRow class="justify-content-end  ">
              <CCol class="col-auto mt-1 mt-2 gap-2 d-md-flex">
                <!--      {% module xsrf_form_html() %}-->
                <label for="raw_checkbox" title="Allows to set the source (and seqnum for unicast)">
                  <CFormCheck id="raw_checkbox" label="Raw frame" v-model="raw_frame"/>
                </label>
              </CCol>
              <CCol class="col-auto d-md-flex">
                <CButton class="m-1" color="secondary" @click="clean_frame">Clean</CButton>
                <CButton class="m-1" color="secondary" @click="send_frame">Send frame</CButton>
              </CCol>
            </CRow>
          </CForm>
        </CCardBody>
      </CCard>
      <CCard class="mb-3">
        <CCardBody>
          <CTable :columns="frames_columns"  striped>
            <CTableBody>
              <template v-for="f in frames" :key="f.id">
                <CTableRow>
                  <CTableDataCell>
                    {{ f.origin.indexOf('@') !== -1 ? f.origin.substring(0, f.origin.indexOf('@')) : f.origin }}
                  </CTableDataCell>
                  <CTableDataCell>{{ f.source_id }}</CTableDataCell>
                  <CTableDataCell>
                    <CBadge v-if="isBroadcast(f.type)" color="info" title="Broadcast group">
                      {{ groupLabel(f.broadcast_group) }}
                    </CBadge>
                    <template v-else>{{ f.destination_id }}</template>
                  </CTableDataCell>
                  <CTableDataCell>{{ typeLabel(f.type) }}</CTableDataCell>
                  <CTableDataCell>{{ isBroadcast(f.type) ? '' : flagsLabel(f.flags) }}</CTableDataCell>
                  <CTableDataCell>{{ f.seqnum }}</CTableDataCell>
                  <CTableDataCell>{{ f.data }}</CTableDataCell>
                  <CTableDataCell>
                    <CButtonGroup size="sm">
                      <CButton color="secondary" @click="copyFrame(f)">Copy</CButton>
                      <CButton color="secondary" @click="toggleFrameDetailsVisibility(f)">Details</CButton>
                    </CButtonGroup>
                  </CTableDataCell>
                </CTableRow>
                <CTableRow colspan="8"/>
                <CTableRow>
                  <CTableDataCell v-show="f.visible" colspan="8">
                    <div>
                      <span class="fw-bold">Origin: </span>{{ f.origin }}
                    </div>
                    <div>
                      <span class="fw-bold">Frame: </span><code>{{ frameDetails(f) }}</code>
                    </div>
                  </CTableDataCell>
                </CTableRow>
              </template>
            </CTableBody>
          </CTable>
        </CCardBody>
      </CCard>
    </CCol></CRow>
</template>

<style scoped>

</style>