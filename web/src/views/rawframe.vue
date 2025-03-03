<script setup>

import {CCardBody} from "@coreui/vue/dist/esm/components/card/index.js";
import {CCol, CRow} from "@coreui/vue/dist/esm/components/grid/index.js";
import {inject, onBeforeUnmount, onMounted, ref} from "vue";
import {CButton} from "@coreui/vue/dist/cjs/components/button/index.js";

const axios = inject('axios');
const toasts = inject('toasts');
const sse = inject('sse')

let sseClient

const frame_priority = [
  {value: 0, label: "H"},
  {value: 1, label: "L"}
];

const frame_type = [
  {value: 0, label: "NOP"},
  {value: 1, label: "PAGE_START"},
  {value: 2, label: "QUIT_BOOTLOADER"},
  {value: 3, label: "PAGE_FILL"},
  {value: 4, label: "BOOTLOADER_TURNED_ON"},
  {value: 5, label: "PAGE_FILL_NEXT"},
  {value: 6, label: "PAGE_WRITED"},
  {value: 7, label: "PAGE_FILL_BREAK"},
  {value: 8, label: "SET_REG"},
  {value: 9, label: "GET_REG"},
  {value: 10, label: "SET_BIT"},
  {value: 11, label: "CLEAR_BIT"},
  {value: 12, label: "TOGGLE_BIT"},
  {value: 13, label: "NODE_UPGRADE"},
  {value: 14, label: "NODE_RESET"},
  {value: 15, label: "DISCOVER"},
  {value: 16, label: "REG_EXTERNALLY_CHANGED"},
  {value: 17, label: "REG_INTERNALLY_CHANGED"},
  {value: 18, label: "REG_VALUE_BROADCAST"},
  {value: 19, label: "REG_VALUE"},
  {value: 20, label: "ERROR"},
  {value: 21, label: "NODE_HEARTBEAT"},
  {value: 22, label: "NODE_INFO"},
  {value: 23, label: "NODE_TURNED_ON"},
  {value: 24, label: "NODE_SPECIFIC_BULK0"},
  {value: 25, label: "NODE_SPECIFIC_BULK1"},
  {value: 26, label: "NODE_SPECIFIC_BULK2"},
  {value: 27, label: "NODE_SPECIFIC_BULK3"},
  {value: 28, label: "NODE_SPECIFIC_BULK4"},
  {value: 29, label: "NODE_SPECIFIC_BULK5"},
  {value: 30, label: "NODE_SPECIFIC_BULK6"},
  {value: 31, label: "NODE_SPECIFIC_BULK7"}
];

const frame = ref({
  priority: 1,
  type: 0,
  seqnum: 0,
  destination_id: 0,
  source_id: 0,
  dlc: 0,
  data: [null, null, null, null, null, null, null, null]
})

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
    key: 'destination_id',
    label: 'Dst',
    // _props: {scope: 'col'},
  },
  {
    key: 'priority',
    // _props: {scope: 'col'},
  },
  {
    key: 'type',
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
  frame.value.priority = 1;
  frame.value.type = 0;
  frame.value.seqnum = 0;
  frame.value.destination_id = 0;
  frame.value.source_id = 0;
  frame.value.dlc = 0;
  for (let i = 0; i < 8; i++) {
    frame.value.data[i] = null;
  }
}

async function send_frame() {
  let i = 0;
  console.log(frame.value);

  if (typeof (frame.value.priority) === "string") {
    let tmp = parseInt(JSON.parse(JSON.stringify(frame.value.priority)))
    if (!isNaN(tmp) && tmp >= 0 && tmp <= 1) {
      frame.value.priority = tmp;
    } else {
      frame.value.priority = null;
    }
  }

  if (typeof (frame.value.type) === "string") {
    let tmp = parseInt(JSON.parse(JSON.stringify(frame.value.type)))
    if (!isNaN(tmp) && tmp >= 0 && tmp < 32) {
      frame.value.type = tmp;
    } else {
      frame.value.type = null;
    }
  }

  if (typeof (frame.value.seqnum) === "string") {
    let tmp = parseInt(JSON.parse(JSON.stringify(frame.value.seqnum)))
    if (!isNaN(tmp) && tmp >= 0 && tmp < 32) {
      frame.value.seqnum = tmp;
    } else {
      frame.value.seqnum = null;
    }
  }

  if (typeof (frame.value.destination_id) === "string") {
    let tmp = parseInt(JSON.parse(JSON.stringify(frame.value.destination_id)))
    if (!isNaN(tmp) && tmp >= 0 && tmp < 512) {
      frame.value.destination_id = tmp;
    } else {
      frame.value.destination_id = null;
    }
  }

  if (typeof (frame.value.source_id) === "string") {
    let tmp = parseInt(JSON.parse(JSON.stringify(frame.value.source_id)))
    if (!isNaN(tmp) && tmp >= 0 && tmp < 511) {
      frame.value.source_id = tmp;
    } else {
      frame.value.source_id = null;
    }
  }

  for (i = 0; i < 8; i++) {
    if (typeof (frame.value.data[i]) === "string") {
      let tmp = parseInt(JSON.parse(JSON.stringify(frame.value.data[i])))
      if (!isNaN(tmp)) {
        frame.value.data[i] = tmp;
      } else {
        frame.value.data[i] = null;
      }
    }
    if (typeof (frame.value.data[i]) !== "number")
      break;
  }
  frame.value.dlc = i;
  for (; i < 8; i++) {
    frame.value.data[i] = null;
  }

  let t = JSON.parse(JSON.stringify(frame.value)) //deep copy 🤦

  console.log("try send")

  await axios.post('/api/frames', {frame: t, raw: raw_frame.value}, {headers: {'Content-Type': 'application/json'}})
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
  frame.value.priority = f.priority;
  frame.value.type = f.type;
  frame.value.seqnum = f.seqnum;
  frame.value.destination_id = f.destination_id;
  frame.value.source_id = f.source_id;
  frame.value.dlc = f.dlc;
  for (let i = 0; i < 8; i++) {
    frame.value.data[i] = f.data[i];
  }
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
                <CFormLabel for="inputPriority">Priority</CFormLabel>
                <CFormSelect id="inputPriority" size="sm" :options="frame_priority"
                             v-model="frame.priority"></CFormSelect>
              </CCol>
              <CCol class="col-auto">
                <CFormLabel for="inputType">Type</CFormLabel>
                <CFormSelect id="inputType" size="sm" :options="frame_type" v-model="frame.type"></CFormSelect>
              </CCol>
              <CCol class="col-auto">
                <CFormLabel for="inputSeqnum">Seqnum</CFormLabel>
                <CFormInput id="inputSeqnum" :disabled="!raw_frame" size="sm" maxlength="2" style="max-width: 10ch;"
                            v-model="frame.seqnum"></CFormInput>
              </CCol>
              <CCol class="col-auto">
                <CFormLabel for="inputSource">Source</CFormLabel>
                <CFormInput id="inputSource" :disabled="!raw_frame" size="sm" maxlength="3" style="max-width: 10ch;"
                            v-model="frame.source_id"></CFormInput>
              </CCol>
              <CCol class="col-auto">
                <CFormLabel for="inputDestination">Destination</CFormLabel>
                <CFormInput id="inputDestination" size="sm" maxlength="3" style="max-width: 10ch;"
                            v-model="frame.destination_id"></CFormInput>
              </CCol>
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
                <label for="raw_checkbox" title="Allows to set the seqnum and source">
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
                  <CTableDataCell>{{ f.destination_id }}</CTableDataCell>
                  <CTableDataCell>{{ f.priority == 0 ? 'H' : 'L' }}</CTableDataCell>
                  <CTableDataCell>{{ frame_type.find((frame) => frame.value === f.type).label }}</CTableDataCell>
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