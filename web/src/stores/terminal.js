import {ref} from 'vue'
import {defineStore} from 'pinia'

// Visibility of the h9cli terminal panel (components/AppTerminal.vue), opened from the sidebar
export const useTerminalStore = defineStore('terminal', () => {
  const visible = ref(false)

  const toggle = () => {
    visible.value = !visible.value
  }

  return {visible, toggle}
})
