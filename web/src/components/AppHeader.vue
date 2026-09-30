<script setup>
import {inject, onBeforeUnmount, onMounted, ref} from 'vue'
import Button from 'primevue/button'

import {useSidebarStore} from '@/stores/sidebar.js'
import {useThemeStore} from '@/stores/theme.js'
import XtermVue from "@/components/XtermVue.vue";

const sidebar = useSidebarStore()
const theme = useThemeStore()

const scrolled = ref(false)
const terminalVisible = ref(false)
const xterm = ref(null)

const axios = inject('axios');

async function logout() {
  await axios
      .get('/api/logout', {headers: {'Content-Type': 'application/json'}})
      .then(response => {
        window.location.href = "/"
      })
}

function onScroll() {
  scrolled.value = document.documentElement.scrollTop > 0
}

onMounted(() => document.addEventListener('scroll', onScroll))
onBeforeUnmount(() => document.removeEventListener('scroll', onScroll))

function toggleTerminal() {
  terminalVisible.value = !terminalVisible.value
  if (terminalVisible.value) {
    xterm.value.focus()
  }
}

</script>

<template>
  <header class="app-header" :class="{ scrolled }">
    <Button icon="pi pi-bars" text rounded severity="secondary" aria-label="Toggle sidebar"
            @click="sidebar.toggleVisible()"/>
    <div class="app-header-actions">
      <Button icon="pi pi-code" text rounded severity="secondary" aria-label="Terminal"
              v-tooltip.bottom="'Terminal'" @click="toggleTerminal"/>
      <span class="app-header-divider"/>
      <Button :icon="theme.theme === 'dark' ? 'pi pi-sun' : 'pi pi-moon'" text rounded severity="secondary"
              aria-label="Toggle theme" @click="theme.toggleTheme()"/>
      <Button icon="pi pi-sign-out" text rounded severity="secondary" aria-label="Logout"
              v-tooltip.bottom="'Logout'" @click="logout()"/>
    </div>
  </header>

  <!-- Own panel rather than a PrimeVue Drawer: the terminal must stay mounted so the h9cli session survives closing it -->
  <Transition name="terminal">
    <div v-show="terminalVisible" class="terminal-panel" @keydown.esc="terminalVisible = false">
      <div class="terminal-bar">
        <span>h9cli</span>
        <Button icon="pi pi-times" text rounded size="small" severity="secondary" aria-label="Close terminal"
                @click="terminalVisible = false"/>
      </div>
      <div class="terminal-body">
        <XtermVue ref="xterm"/>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  height: var(--app-header-height);
  padding: 0 1rem;
  margin-bottom: 1.5rem;
  background: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
  transition: box-shadow .15s;
}

.app-header.scrolled {
  box-shadow: 0 2px 6px rgba(0, 0, 0, .08);
}

.app-header-actions {
  display: flex;
  align-items: center;
  gap: .25rem;
  margin-left: auto;
}

.app-header-divider {
  width: 1px;
  height: 1.75rem;
  margin: 0 .5rem;
  background: var(--app-border);
}

.terminal-panel {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1100;
  display: flex;
  flex-direction: column;
  height: 40vh;
  background: #000;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, .3);
}

.terminal-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 .5rem 0 1rem;
  color: #aaa;
  font-size: .85rem;
  border-bottom: 1px solid #222;
}

.terminal-body {
  flex: 1;
  min-height: 0;
  padding: .25rem .5rem;
}

.terminal-enter-active,
.terminal-leave-active {
  transition: transform .2s ease;
}

.terminal-enter-from,
.terminal-leave-to {
  transform: translateY(100%);
}
</style>
