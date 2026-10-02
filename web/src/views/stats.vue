<script setup>

import {computed} from "vue";

import {formatNumber, formatUptime, useStatsStore} from '@/stores/stats.js'

// Kept up to date by the layout (stats server-sent events)
const statsStore = useStatsStore()
const h9d = computed(() => statsStore.stats?.h9d)
const h9web = computed(() => statsStore.stats?.h9web)

function yesNo(value) {
  return value ? 'Yes' : 'No'
}

</script>

<template>
  <div class="page">
    <div class="page-row">
      <section class="surface-card stats-card">
        <div class="caption">h9d</div>
        <dl class="kv">
          <dt>Version</dt>
          <dd>{{ h9d?.version || '---' }}</dd>
          <dt>Commit</dt>
          <dd>{{ h9d?.commit || '---' }}</dd>
          <dt>Uptime</dt>
          <dd>{{ formatUptime(h9d?.uptime_s) }}</dd>
        </dl>
      </section>
      <section class="surface-card stats-card">
        <div class="caption">h9web</div>
        <dl class="kv">
          <dt>Version</dt>
          <dd>{{ h9web?.version || '---' }}</dd>
        </dl>
      </section>
    </div>

    <div class="page-row">
      <section class="surface-card stats-card">
        <div class="caption">Bus</div>
        <div class="totals">
          <div>
            <div class="caption">Received frames</div>
            <div class="big-value">{{ formatNumber(h9d?.bus?.received_frames) }}</div>
          </div>
          <div>
            <div class="caption">Send frames</div>
            <div class="big-value">{{ formatNumber(h9d?.bus?.send_frames) }}</div>
          </div>
        </div>
        <div v-for="(endpoint, name) in h9d?.bus?.endpoints" :key="name" class="list-item">
          <div class="list-item-title">{{ name }}</div>
          <dl class="kv">
            <dt>Received frames</dt>
            <dd>{{ formatNumber(endpoint.received_frames) }}</dd>
            <dt>Received frames per s</dt>
            <dd>{{ formatNumber(endpoint.received_frames_per_s, 1) }} f/s</dd>
            <dt>Send frames</dt>
            <dd>{{ formatNumber(endpoint.send_frames) }}</dd>
            <dt>Send frames per s</dt>
            <dd>{{ formatNumber(endpoint.send_frames_per_s, 1) }} f/s</dd>
          </dl>
        </div>
      </section>

      <section class="surface-card stats-card">
        <div class="caption">TCP</div>
        <div v-for="client in h9d?.tcp_clients" :key="client.id" class="list-item">
          <div class="list-item-title">{{ client.entity || '---' }}</div>
          <dl class="kv">
            <dt>Remote</dt>
            <dd>{{ client.remote_address }}:{{ client.remote_port }}</dd>
            <dt>Connected at</dt>
            <dd>{{ (new Date(client.connection_time)).toLocaleString() }}</dd>
            <dt>Authenticated</dt>
            <dd>{{ yesNo(client.authenticated) }}</dd>
            <dt>Frame subscription</dt>
            <dd>{{ yesNo(client.frame_subscription) }}</dd>
            <dt>Dev subscription</dt>
            <dd>{{ yesNo(client.dev_subscription) }}</dd>
          </dl>
        </div>
        <p v-if="!h9d?.tcp_clients?.length" class="muted">No clients.</p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.stats-card {
  display: flex;
  flex-direction: column;
  gap: .9rem;
  padding: 1.15rem 1.25rem;
}

.totals {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem 2.5rem;
}

.totals .caption {
  margin-bottom: .25rem;
}

.list-item {
  padding-top: .9rem;
  border-top: 1px solid var(--app-border);
}

.caption + .list-item {
  padding-top: 0;
  border-top: none;
}

.list-item-title {
  margin-bottom: .35rem;
  font-weight: 700;
}

.kv dd {
  font-variant-numeric: tabular-nums;
}
</style>
