<script setup>

import {inject, onMounted, ref} from "vue";
import Card from 'primevue/card'
import {useEventStream} from '@/composables/useEventStream.js'

const axios = inject('axios');
const toasts = inject('toasts');

const last_stats = ref({})

useEventStream({
  stats: (message) => {
    last_stats.value = message
  }
})

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
  <div class="page">
    <div class="page-row">
      <Card>
        <template #title>h9d</template>
        <template #content>
          <dl class="kv">
            <dt>Version:</dt>
            <dd>{{ last_stats?.h9d?.version || '---' }}</dd>
            <dt>Commit:</dt>
            <dd>{{ last_stats?.h9d?.commit || '---' }}</dd>
            <dt>Uptime:</dt>
            <dd>{{ last_stats?.h9d?.uptime || '---' }}</dd>
          </dl>
        </template>
      </Card>
      <Card>
        <template #title>h9web</template>
        <template #content>
          <dl class="kv">
            <dt>Version:</dt>
            <dd>{{ last_stats?.h9web?.version || '---' }}</dd>
          </dl>
        </template>
      </Card>
    </div>
    <div class="page-row">
      <Card>
        <template #title>Bus</template>
        <template #content>
          <dl class="kv">
            <dt>Received frames:</dt>
            <dd>{{ last_stats?.h9d?.bus?.received_frames || '---' }}</dd>
            <dt>Send frames:</dt>
            <dd>{{ last_stats?.h9d?.bus?.send_frames || '---' }}</dd>
          </dl>
          <div v-for="(endpoint, name) in last_stats?.h9d?.bus?.endpoints" :key="name" class="list-item">
            <div class="list-item-title">{{ name }}</div>
            <dl class="kv">
              <dt>Received frames:</dt>
              <dd>{{ endpoint.received_frames }}</dd>
              <dt>Received frames per s:</dt>
              <dd>{{ endpoint.received_frames_per_s }} f/s</dd>
              <dt>Send frames:</dt>
              <dd>{{ endpoint.send_frames }}</dd>
              <dt>Send frames per s:</dt>
              <dd>{{ endpoint.send_frames_per_s }} f/s</dd>
            </dl>
          </div>
        </template>
      </Card>
      <Card>
        <template #title>TCP</template>
        <template #content>
          <div v-for="client in last_stats?.h9d?.tcp_clients" :key="client.id" class="list-item">
            <dl class="kv">
              <dt>Entity:</dt>
              <dd>{{ client.entity || '---' }}</dd>
              <dt>Remote:</dt>
              <dd>{{ client.remote_address }}:{{ client.remote_port }}</dd>
              <dt>Connected at:</dt>
              <dd>{{ (new Date(client.connection_time)).toLocaleString() }}</dd>
              <dt>Authenticated:</dt>
              <dd>{{ client.authenticated ? 'Yes' : 'No' }}</dd>
              <dt>Frame subscription:</dt>
              <dd>{{ client.frame_subscription ? 'Yes' : 'No' }}</dd>
              <dt>Dev subscription:</dt>
              <dd>{{ client.dev_subscription ? 'Yes' : 'No' }}</dd>
            </dl>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<style scoped>
.list-item {
  padding: .75rem 0;
  border-top: 1px solid var(--app-border);
}

.list-item:first-child {
  border-top: none;
  padding-top: 0;
}

.kv + .list-item {
  margin-top: .75rem;
  border-top: 1px solid var(--app-border);
  padding-top: .75rem;
}

.list-item-title {
  font-weight: 600;
  margin-bottom: .25rem;
}
</style>
