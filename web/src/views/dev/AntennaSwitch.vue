<script setup>
import {computed, ref} from 'vue'
import {useDevCall} from '@/composables/useDevCall.js'

// Antenna switch (h9d dev plugin src/devs/antenna_switch.cc, device type "Antenna switch").
// State: {node_id, antennas: [{number, name}], antenna (0 = all off), antenna_name, overcurrent, undercurrent}
// One button per antenna - a single click selects it. Renaming and the antennas number are set in Devs.
const props = defineProps({
  dev: Object
});

const callDev = useDevCall()

const antennas = computed(() => props.dev.state?.antennas ?? [])
const selected = computed(() => props.dev.state?.antenna)
const pending = ref(null)   // antenna number being selected

async function select(number) {
  if (pending.value !== null) {
    return
  }
  pending.value = number
  try {
    const node_id = props.dev.state?.node_id
    // the shown selection follows the state events from h9d, not the click
    await callDev(props.dev.name, 'select_antenna', node_id ? {antenna: number, node_id} : {antenna: number})
  } catch {
    // toast already shown by callDev
  } finally {
    pending.value = null
  }
}

</script>

<template>
  <div v-if="dev.state?.overcurrent" class="alert bad"
       v-tooltip.top="'Overcurrent protection switched the antennas off - select an antenna to reset it'">
    <i class="pi pi-bolt"/> Overcurrent - antennas off
  </div>
  <div v-else-if="dev.state?.undercurrent" class="alert warn"
       v-tooltip.top="'The selected antenna draws less current than expected - relay disconnected or burnt?'">
    <i class="pi pi-exclamation-triangle"/> Undercurrent on antenna {{ selected }}
  </div>

  <div class="antennas">
    <button v-for="a in antennas" :key="a.number" type="button" class="antenna"
            :class="{ active: selected === a.number, pending: pending === a.number }"
            :disabled="pending !== null" :title="a.name || 'Antenna ' + a.number" @click="select(a.number)">
      <span class="number">{{ a.number }}</span>
      <span class="name">{{ a.name || '&nbsp;' }}</span>
    </button>
    <button type="button" class="antenna off" :class="{ active: selected === 0, pending: pending === 0 }"
            :disabled="pending !== null" title="All antennas off" @click="select(0)">
      <span class="number"><i class="pi pi-power-off"/></span>
      <span class="name">Off</span>
    </button>
  </div>
  <p v-if="!antennas.length" class="muted no-antennas">The switch has not reported its antennas yet.</p>
</template>

<style scoped>
.antennas {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(3.6rem, 1fr));
  gap: .45rem;
}

.antenna {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: .1rem;
  min-width: 0;
  padding: .45rem .25rem;
  border: 1px solid var(--app-border);
  border-radius: 10px;
  background: color-mix(in srgb, var(--app-text) 4%, transparent);
  color: var(--app-text);
  font: inherit;
  cursor: pointer;
  transition: background .12s, border-color .12s, box-shadow .12s;
}

.antenna:hover:not(:disabled) {
  border-color: color-mix(in srgb, var(--app-accent) 60%, transparent);
}

.antenna:disabled {
  cursor: progress;
}

.antenna .number {
  font-size: 1.25rem;
  font-weight: 700;
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
}

.antenna .name {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: .72rem;
  color: var(--app-text-muted);
}

.antenna.active {
  border-color: var(--app-accent);
  background: var(--app-accent-soft);
  color: var(--app-accent);
  box-shadow: 0 0 10px color-mix(in srgb, var(--app-accent) 30%, transparent);
}

.antenna.active .name {
  color: var(--app-accent);
}

.antenna.off.active {
  border-color: var(--app-text-muted);
  background: color-mix(in srgb, var(--app-text) 10%, transparent);
  color: var(--app-text);
  box-shadow: none;
}

.antenna.pending {
  border-color: var(--p-yellow-400);
  animation: pulse .8s ease-in-out infinite alternate;
}

@keyframes pulse {
  to {
    background: color-mix(in srgb, var(--p-yellow-400) 18%, transparent);
  }
}

.alert {
  display: flex;
  align-items: center;
  gap: .5rem;
  padding: .4rem .7rem;
  border-radius: 8px;
  font-size: .82rem;
  font-weight: 600;
}

.alert.bad {
  background: color-mix(in srgb, var(--p-red-500) 16%, transparent);
  color: var(--p-red-400);
}

.alert.warn {
  background: color-mix(in srgb, var(--p-orange-500) 16%, transparent);
  color: var(--p-orange-400);
}

.no-antennas {
  margin: 0;
  font-size: .85rem;
}
</style>
