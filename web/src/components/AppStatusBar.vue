<script setup>
import {computed, inject} from 'vue'
import Button from 'primevue/button'

import {formatNumber, formatUptime, useStatsStore} from '@/stores/stats.js'
import {useSidebarStore} from '@/stores/sidebar.js'
import {useTerminalStore} from '@/stores/terminal.js'
import {useThemeStore} from '@/stores/theme.js'

const statsStore = useStatsStore()
const sidebar = useSidebarStore()
const theme = useThemeStore()
const terminal = useTerminalStore()
const axios = inject('axios');

async function logout() {
  await axios.get('/api/logout').then(() => {
    window.location.href = "/"
  })
}

const items = computed(() => {
  const s = statsStore.stats
  return [
    {label: 'h9web', value: s?.h9web?.version},
    {label: 'h9d', value: s?.h9d?.version},
    {label: 'Uptime', value: s ? formatUptime(s.h9d?.uptime_s) : null},
    {label: 'RX', value: s ? formatNumber(s.h9d?.bus?.received_frames) : null},
    {label: 'TX', value: s ? formatNumber(s.h9d?.bus?.send_frames) : null},
    {label: 'Clients', value: s?.h9d?.tcp_clients?.length},
  ]
})

// OK needs both links: browser -> h9web (event stream) and h9web -> h9d
const status = computed(() => {
  if (!statsStore.streamConnected) {
    return {text: 'h9web offline', ok: false}
  }
  if (!statsStore.h9dConnected) {
    return {text: 'h9d offline', ok: false}
  }
  return {text: 'OK', ok: true}
})
</script>

<template>
  <header class="statusbar">
    <Button icon="pi pi-bars" text rounded size="small" severity="secondary" aria-label="Toggle sidebar"
            @click="sidebar.toggleVisible()"/>
    <div class="statusbar-items">
      <span v-for="item in items" :key="item.label" class="statusbar-item">
        <span class="caption">{{ item.label }}</span>
        <b>{{ item.value ?? '---' }}</b>
      </span>
      <span class="statusbar-item status" :class="{ bad: !status.ok }">
        <span class="dot"/>
        <b>{{ status.text }}</b>
      </span>
    </div>
    <div class="statusbar-actions">
      <Button icon="pi pi-code" text rounded size="small" :severity="terminal.visible ? undefined : 'secondary'"
              aria-label="Terminal" v-tooltip.bottom="'Terminal'" @click="terminal.toggle()"/>
      <Button :icon="theme.theme === 'dark' ? 'pi pi-sun' : 'pi pi-moon'" text rounded size="small"
              severity="secondary" aria-label="Toggle theme" @click="theme.toggleTheme()"/>
      <Button icon="pi pi-sign-out" text rounded size="small" severity="secondary" aria-label="Logout"
              v-tooltip.bottom="'Logout'" @click="logout()"/>
    </div>
  </header>
</template>

<style scoped>
.statusbar {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 1rem;
  height: var(--app-statusbar-height);
  padding: 0 .5rem;
  background: var(--app-bg);
  border-bottom: 1px solid var(--app-border);
  font-size: .8rem;
}

.statusbar-items {
  display: flex;
  align-items: center;
  margin-left: auto;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
}

.statusbar-actions {
  display: flex;
  align-items: center;
  gap: .1rem;
  padding-left: .5rem;
  border-left: 1px solid var(--app-border);
}

.statusbar-item {
  display: flex;
  align-items: baseline;
  gap: .45rem;
  padding: 0 .9rem;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.statusbar-item + .statusbar-item {
  border-left: 1px solid var(--app-border);
}

.statusbar-item .caption {
  font-size: .62rem;
}

.status {
  align-items: center;
  color: var(--app-accent);
}

.status.bad {
  color: var(--app-danger);
}

.dot {
  width: .5rem;
  height: .5rem;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 6px currentColor;
}

/* Narrow screens: keep just the connection status */
@media (max-width: 767.98px) {
  .statusbar-item:not(.status) {
    display: none;
  }
}
</style>
