import {computed, ref} from 'vue'
import {defineStore} from 'pinia'

// h9d / h9web statistics (/api/stats), kept up to date by layouts/DefaultLayout.vue
// from the `stats` server-sent events; read by the status bar and the Stats view.
export const useStatsStore = defineStore('stats', () => {
  const stats = ref(null)
  const streamConnected = ref(false)

  // h9web reports no uptime while it has no connection to h9d
  const h9dConnected = computed(() => stats.value?.h9d?.uptime_s != null)

  return {stats, streamConnected, h9dConnected}
})

export function formatUptime(seconds) {
  if (seconds == null) {
    return '---'
  }
  const d = Math.floor(seconds / 86400)
  const h = Math.floor(seconds % 86400 / 3600)
  const m = Math.floor(seconds % 3600 / 60)
  return (d ? d + 'd ' : '') + (d || h ? h + 'h ' : '') + m + 'm'
}

export function formatNumber(value, digits = 0) {
  if (value == null) {
    return '---'
  }
  return value.toLocaleString(undefined, {minimumFractionDigits: digits, maximumFractionDigits: digits})
}
