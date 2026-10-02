<script setup>
import {ref, watch} from 'vue'
import Button from 'primevue/button'

import XtermVue from '@/components/XtermVue.vue'
import {useTerminalStore} from '@/stores/terminal.js'

const terminal = useTerminalStore()
const xterm = ref(null)

watch(() => terminal.visible, (visible) => {
  if (visible) {
    xterm.value.focus()
  }
})
</script>

<template>
  <!-- Own panel rather than a PrimeVue Drawer: the terminal must stay mounted so the h9cli session survives closing it -->
  <Transition name="terminal">
    <div v-show="terminal.visible" class="terminal-panel" @keydown.esc="terminal.visible = false">
      <div class="terminal-bar">
        <span class="caption">h9cli</span>
        <Button icon="pi pi-times" text rounded size="small" severity="secondary" aria-label="Close terminal"
                @click="terminal.visible = false"/>
      </div>
      <div class="terminal-body">
        <XtermVue ref="xterm"/>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
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
  border-top: 1px solid #272b31;
  box-shadow: 0 -4px 16px rgba(0, 0, 0, .3);
}

.terminal-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 .5rem 0 1rem;
  border-bottom: 1px solid #1c1f24;
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
