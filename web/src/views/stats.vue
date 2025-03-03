<script setup>

import {inject, onMounted, ref} from "vue";
import {CCol, CRow} from "@coreui/vue/dist/cjs/components/grid/index.js";
import {CCard, CCardBody} from "@coreui/vue/dist/cjs/components/card/index.js";
import {CCardHeader} from "@coreui/vue/dist/esm/components/card/index.js";

const axios = inject('axios');
const toasts = inject('toasts');
const sse = inject('sse')

const last_stats = ref({})
let sseClient

onMounted(async () => {
  await axios
      .get('/api/stats')
      .then(response => {
        last_stats.value = response.data.response
      }).catch(function (error) {
        toasts.value.push({
          title: 'Refresh stats',
          content: error
        })
      })

  sseClient = sse.create({
    format: 'json',
    url: '/api/events?filter=stats',
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

  sseClient.on('stats', (message, lastEventId) => {
    console.warn('Received a message w/o an event!', message, lastEventId);

    last_stats.value = message;
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

// {
//   "h9web": {
//   "version": "0.0.0"
// },
//   "h9d": {
//   "version": "0.3.1",
//       "commit": "g4f1c43e",
//       "uptime": "13 days 1 hours 22 minutes 21seconds",
//       "bus": {
//     "received_frames": 6820,
//         "send_frames": 172,
//         "endpoints": {
//       "can0": {
//         "received_frames_per_s": 0.0,
//             "send_frames_per_s": 0.0,
//             "received_frames": 6646,
//             "send_frames": 346
//       },
//       "udp0": {
//         "received_frames_per_s": 0.0,
//             "send_frames_per_s": 0.0,
//             "received_frames": 0,
//             "send_frames": 6992
//       },
//       "vcan": {
//         "received_frames_per_s": 0.0,
//             "send_frames_per_s": 0.0,
//             "received_frames": 174,
//             "send_frames": 6818
//       }
//     }
//   }
// }
// }

</script>

<template>
  <CRow class="mb-4">
    <CCol>
      <CCard>
        <CCardHeader>h9d</CCardHeader>
        <CCardBody>
          <CRow>
            <CCol class="col-2">Version:</CCol>
            <CCol>{{ last_stats?.h9d?.version || '---'}}</CCol>
          </CRow>
          <CRow>
            <CCol class="col-2">Commit:</CCol>
            <CCol>{{ last_stats?.h9d?.commit || '---'}}</CCol>
          </CRow>
          <CRow>
            <CCol class="col-2">Uptime:</CCol>
            <CCol>{{ last_stats?.h9d?.uptime || '---'}}</CCol>
          </CRow>
        </CCardBody>
      </CCard>
    </CCol>
    <CCol>
      <CCard>
        <CCardHeader>h9web</CCardHeader>
        <CCardBody>
          <CRow>
            <CCol class="col-2">Version:</CCol>
            <CCol>{{ last_stats?.h9web?.version || '---'}}</CCol>
          </CRow>
        </CCardBody>
      </CCard>
    </CCol>
  </CRow>
  <CRow>
    <CCol>
      <CCard>
        <CCardHeader>Bus</CCardHeader>
        <CCardBody>
          <CRow>
            <CCol class="col-3">Received frames:</CCol>
            <CCol>{{ last_stats?.h9d?.bus?.received_frames || '---'}}</CCol>
          </CRow>
          <CRow>
            <CCol class="col-3">Send frames:</CCol>
            <CCol>{{ last_stats?.h9d?.bus?.send_frames || '---'}}</CCol>
          </CRow>
        </CCardBody>
        <CListGroup flush>
          <CListGroupItem v-for="(endpoint,name) in last_stats?.h9d?.bus?.endpoints">
            <CRow>
              <CCol class="col-3">{{ name }}:</CCol>
              <CCol class="col-4">Received frames:</CCol>
              <CCol>{{ endpoint.received_frames}}</CCol>
            </CRow>
            <CRow>
              <CCol class="col-3"></CCol>
              <CCol class="col-4">Received frames per s:</CCol>
              <CCol>{{ endpoint.received_frames_per_s}} f/s</CCol>
            </CRow>
            <CRow>
              <CCol class="col-3"></CCol>
              <CCol class="col-4">Send frames:</CCol>
              <CCol>{{ endpoint.send_frames}}</CCol>
            </CRow>
            <CRow>
              <CCol class="col-3"></CCol>
              <CCol class="col-4">Send frames per s:</CCol>
              <CCol>{{ endpoint.send_frames_per_s}} f/s</CCol>
            </CRow>
          </CListGroupItem>
        </CListGroup>
      </CCard>
    </CCol>
    <CCol>
      <CCard>
        <CCardHeader>TCP</CCardHeader>
        <CListGroup flush>
          <CListGroupItem v-for="client in last_stats?.h9d?.tcp_clients">
            <CRow>
              <CCol class="col-4">Entity:</CCol>
              <CCol>{{ client.entity || '---'}}</CCol>
            </CRow>
            <CRow>
              <CCol class="col-4">Remote:</CCol>
              <CCol>{{ client.remote_address }}:{{ client.remote_port }}</CCol>
            </CRow>
            <CRow>
              <CCol class="col-4">Connected at:</CCol>
              <CCol>{{ (new Date(client.connection_time)).toLocaleString() }}</CCol>
            </CRow>
            <CRow>
              <CCol class="col-4">Authenticated:</CCol>
              <CCol>{{ client.authenticated ? 'Yes' : 'No'}}</CCol>
            </CRow>
            <CRow>
              <CCol class="col-4">Frame subscription:</CCol>
              <CCol>{{ client.frame_subscription ? 'Yes' : 'No'}}</CCol>
            </CRow>
            <CRow>
              <CCol class="col-4">Dev subscription:</CCol>
              <CCol>{{ client.dev_subscription ? 'Yes' : 'No'}}</CCol>
            </CRow>
          </CListGroupItem>
        </CListGroup>
      </CCard>
    </CCol>
  </CRow>
</template>

<style scoped>

</style>