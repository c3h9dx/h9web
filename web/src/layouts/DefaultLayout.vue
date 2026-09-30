<script setup>
import {inject, watch} from "vue";
import Toast from 'primevue/toast'
import {useToast} from 'primevue/usetoast'

import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import {useSidebarStore} from '@/stores/sidebar.js'

const sidebar = useSidebarStore()

// Views report errors by pushing {title, content} into the shared `toasts` array (see main.js);
// show each one as a PrimeVue toast and empty the queue.
const toasts = inject('toasts');
const toast = useToast()

watch(() => toasts.value.length, () => {
  for (const t of toasts.value.splice(0)) {
    toast.add({severity: 'error', summary: t.title, detail: String(t.content), life: 10000})
  }
})

</script>

<template>
  <div class="layout" :class="{ 'sidebar-hidden': sidebar.visible === false, 'sidebar-open': sidebar.visible === true }">
    <div class="layout-sidebar">
      <AppSidebar/>
    </div>
    <div class="layout-backdrop" @click="sidebar.toggleVisible(false)"/>
    <div class="layout-main">
      <AppHeader/>
      <main class="layout-content">
        <router-view/>
      </main>
    </div>
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
  max-width: 1320px;
  margin: 0 auto;
  padding: 0 1rem 2rem;
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
    background: rgba(0, 0, 0, .4);
  }
}
</style>
