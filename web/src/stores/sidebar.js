import { ref } from 'vue'
import { defineStore } from 'pinia'

// Must match the breakpoint in layouts/DefaultLayout.vue
const WIDE_SCREEN = '(min-width: 992px)'

export const useSidebarStore = defineStore('sidebar', () => {
  // null = default for the screen size: shown on wide screens, hidden on narrow ones
  const visible = ref(null)

  const toggleVisible = (value) => {
    const current = visible.value ?? window.matchMedia(WIDE_SCREEN).matches
    visible.value = value !== undefined ? value : !current
  }

  return { visible, toggleVisible }
})
