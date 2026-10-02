<script setup>
import {computed, ref} from "vue";
import Button from 'primevue/button'
import {useDevCall} from '@/composables/useDevCall.js'

// S-Match ATU (h9d dev plugin src/devs/smatch.cc, device type "S-Match")
const props = defineProps({
  dev: Object
});

const callDev = useDevCall()

// Full scale of the power bargraphs [W]
const POWER_SCALE_W = 100
// SWR bargraph range: 1.0 (empty) - SWR_SCALE (full)
const SWR_SCALE = 3

// Bargraphs follow only the "power" events: {event_name: "power", fwd, ref, pep [W], freq [kHz], node_id}.
// Before the first event the state from get_dev_status is used if it holds a power reading.
const power = computed(() => props.dev.events?.power
    ?? (props.dev.state?.event_name === 'power' ? props.dev.state : undefined))

const fwd = computed(() => power.value?.fwd)
const ref_ = computed(() => power.value?.ref)
const pep = computed(() => power.value?.pep)

// SWR from forward / reflected power: (1 + G) / (1 - G), G = sqrt(ref / fwd)
const swr = computed(() => {
  if (!fwd.value || ref_.value == null) {
    return undefined
  }
  const g = Math.sqrt(ref_.value / fwd.value)
  return g >= 1 ? Infinity : (1 + g) / (1 - g)
})

const freqMHz = computed(() => power.value?.freq ? (power.value.freq / 1000).toFixed(3) : undefined)

function powerPercent(w) {
  return Math.min(100, Math.max(0, (w ?? 0) * 100 / POWER_SCALE_W))
}

const swrPercent = computed(() => swr.value === undefined ? 0 : Math.min(100, (swr.value - 1) * 100 / (SWR_SCALE - 1)))
const swrLevel = computed(() => swr.value === undefined || swr.value < 1.5 ? 'good' : swr.value < 2 ? 'warn' : 'bad')

function fmt(value, digits = 1) {
  return value == null ? '---' : value.toFixed(digits)
}

const canTune = computed(() => props.dev.methods?.includes('tune'))
const tuning = ref(false)

async function tune() {
  tuning.value = true
  try {
    // Without node_id h9d tunes the node it last heard from - pass ours, as h9d may not have heard any yet
    const node_id = power.value?.node_id ?? props.dev.state?.node_id
    await callDev(props.dev.name, 'tune', node_id ? {node_id} : {})
  } catch {
    // toast already shown by callDev
  } finally {
    tuning.value = false
  }
}

</script>

<template>
  <div class="readings">
    <div>
      <div class="caption">Forward</div>
      <div class="big-value">{{ fmt(fwd) }}<span class="unit">W</span></div>
      <div class="bar"><div class="bar-value fwd" :style="{ width: powerPercent(fwd) + '%' }"/></div>
    </div>
    <div>
      <div class="caption">Reflected</div>
      <div class="big-value">{{ fmt(ref_) }}<span class="unit">W</span></div>
      <div class="bar"><div class="bar-value ref" :style="{ width: powerPercent(ref_) + '%' }"/></div>
    </div>
    <div>
      <div class="caption">SWR</div>
      <div class="big-value">{{ swr === Infinity ? '∞' : fmt(swr, 2) }}</div>
      <div class="bar"><div class="bar-value swr" :class="swrLevel" :style="{ width: swrPercent + '%' }"/></div>
    </div>
  </div>
  <div class="footer">
    <span class="muted">PEP <b>{{ fmt(pep) }}</b> W</span>
    <span class="muted"><b>{{ freqMHz ?? '---' }}</b> MHz</span>
    <Button v-if="canTune" label="Tune" icon="pi pi-sliders-h" size="small" outlined :loading="tuning"
            class="tune" @click="tune"/>
  </div>
</template>

<style scoped>
.readings {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
}

.readings .big-value {
  font-size: 1.55rem;
  white-space: nowrap;
}

.bar {
  height: .45rem;
  margin-top: .5rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--app-text-muted) 18%, transparent);
  overflow: hidden;
}

.bar-value {
  height: 100%;
  border-radius: inherit;
  transition: width .15s ease;
}

.fwd {
  background: var(--p-primary-500);
}

.ref {
  background: var(--p-orange-500);
}

.swr.good {
  background: var(--p-primary-500);
}

.swr.warn {
  background: var(--p-yellow-500);
}

.swr.bad {
  background: var(--p-red-500);
}

.footer {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: .5rem 1.25rem;
  font-size: .85rem;
  font-variant-numeric: tabular-nums;
}

.footer b {
  color: var(--app-text);
}

.tune {
  margin-left: auto;
}
</style>
