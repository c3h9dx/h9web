<script setup>
import {inject, onMounted, watch} from "vue";
import {useRoute} from 'vue-router'
import Toast from 'primevue/toast'
import {useToast} from 'primevue/usetoast'

import AppSidebar from '@/components/AppSidebar.vue'
import AppStatusBar from '@/components/AppStatusBar.vue'
import AppTerminal from '@/components/AppTerminal.vue'
import {useEventStream} from '@/composables/useEventStream.js'
import {useSidebarStore} from '@/stores/sidebar.js'
import {useStatsStore} from '@/stores/stats.js'

const route = useRoute()
const sidebar = useSidebarStore()
const statsStore = useStatsStore()
const axios = inject('axios');

// Views report errors by pushing {title, content} into the shared `toasts` array (see main.js);
// show each one as a PrimeVue toast and empty the queue.
const toasts = inject('toasts');
const toast = useToast()

watch(() => toasts.value.length, () => {
  for (const t of toasts.value.splice(0)) {
    toast.add({severity: 'error', summary: t.title, detail: String(t.content), life: 10000})
  }
})

// Stats feed the status bar on every page, so they are subscribed here once
const {connected} = useEventStream({
  stats: (message) => {
    statsStore.stats = message
  }
})
watch(connected, (value) => {
  statsStore.streamConnected = value
})

onMounted(() => {
  axios.get('/api/stats').then((response) => {
    statsStore.stats = response.data.response
  }).catch(() => {
    // the status bar shows the connection state
  })
})

</script>

<template>
  <div class="layout" :class="{ 'sidebar-hidden': sidebar.visible === false, 'sidebar-open': sidebar.visible === true }">
    <div class="layout-sidebar">
      <AppSidebar/>
    </div>
    <div class="layout-backdrop" @click="sidebar.toggleVisible(false)"/>
    <div class="layout-main">
      <AppStatusBar/>
      <main class="layout-content">
        <h1 class="page-title">{{ route.name }}</h1>
        <router-view/>
      </main>
    </div>
    <AppTerminal/>
    <Toast position="bottom-right"/>
  </div>
</template>

<style scoped>
.layout-sidebar {
  position: fixed;
  top: 0;
  bottom: 0;
  left: 0;
  z-index: 20;
  width: var(--app-sidebar-width);
  transition: transform .2s ease;
}

.layout-main {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  transition: margin-left .2s ease;
}

.layout-content {
  flex: 1;
  width: 100%;
  max-width: 1240px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

.layout-backdrop {
  display: none;
}

/* Wide screens: sidebar shown next to the content unless the user hid it */
@media (min-width: 992px) {
  .layout-main {
    margin-left: var(--app-sidebar-width);
  }

  .sidebar-hidden .layout-sidebar {
    transform: translateX(-100%);
  }

  .sidebar-hidden .layout-main {
    margin-left: 0;
  }
}

/* Narrow screens: sidebar hidden, opened as an overlay */
@media (max-width: 991.98px) {
  .layout:not(.sidebar-open) .layout-sidebar {
    transform: translateX(-100%);
  }

  .sidebar-open .layout-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 15;
    background: rgba(0, 0, 0, .5);
  }

  .layout-content {
    padding: 1.25rem 1rem 2rem;
  }
}
</style>
