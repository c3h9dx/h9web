<script setup>
import {computed, ref} from 'vue'
import ToggleSwitch from 'primevue/toggleswitch'
import {useDevCall} from '@/composables/useDevCall.js'

// Shack control (h9d dev plugin src/devs/shack_ctrl.cc, device type "Shack ctrl"): two outputs of a
// Power switch node, each a relay driving a contactor. The control circuit is supplied RCD -> fuse.
// State: {node_id, rcd, fuse, control_supply, antennas: {relay, contactor, power, manual_override}, christmas_tree: {...},
//         thunder_switch: {node_id, online, pending, connected, disconnected, switching_on, switching_off, manual_move, *_error}}
// The thunder switch (antennas disconnector) is supplied by the antennas output - h9d switches that on when needed.
const props = defineProps({
  dev: Object
});

const callDev = useDevCall()

const OUTPUTS = [
  {key: 'antennas', label: 'Antennas', method: 'antennas_power_supply'},
  {key: 'christmas_tree', label: 'Christmas tree', method: 'christmas_tree_power_supply'},
]

const rcd = computed(() => props.dev.state?.rcd)
const fuse = computed(() => props.dev.state?.fuse)
// control_supply = rcd && fuse; older h9d reports only rcd
const supply = computed(() => props.dev.state?.control_supply ?? rcd.value)

const busy = ref({})
// ToggleSwitch keeps its own value - re-create it when a call fails so it shows the real relay state again
const resetKey = ref(0)

async function setRelay(output, on) {
  busy.value[output.key] = true
  try {
    const node_id = props.dev.state?.node_id
    await callDev(props.dev.name, output.method, node_id ? {on, node_id} : {on})
  } catch {
    resetKey.value++
  } finally {
    busy.value[output.key] = false
  }
}

// --- Thunder switch ---
const ts = computed(() => props.dev.state?.thunder_switch)
const hasThunderSwitch = computed(() => props.dev.methods?.includes('antennas_thunder_switch') || ts.value !== undefined)
const tsMoving = computed(() => !!(ts.value?.switching_on || ts.value?.switching_off))
// While a command waits for the switch to start, show where it is going
const tsTarget = computed(() => ts.value?.pending ? ts.value.pending === 'connect' : !!ts.value?.connected)

const TS_ERRORS = [
  {key: 'limit_switch_error', text: 'limit switch'},
  {key: 'motor_overcurrent_error', text: 'overcurrent'},
  {key: 'motor_undercurrent_error', text: 'undercurrent'},
]
const tsErrors = computed(() => TS_ERRORS.filter((e) => ts.value?.[e.key]))

const tsStatus = computed(() => {
  const t = ts.value
  if (!t) return '---'
  if (t.pending) return (t.pending === 'connect' ? 'connect' : 'disconnect') + ' - waiting for start'
  if (t.switching_on) return 'connecting...'
  if (t.switching_off) return 'disconnecting...'
  if (!t.online) return props.dev.state?.antennas?.power ? 'no data yet' : 'offline (no power)'
  if (t.connected) return 'antennas connected'
  if (t.disconnected) return 'antennas disconnected'
  return 'between positions'
})

async function setThunderSwitch(connect) {
  busy.value.thunder_switch = true
  try {
    const node_id = props.dev.state?.node_id  // the Power switch node, which supplies the thunder switch
    await callDev(props.dev.name, 'antennas_thunder_switch', node_id ? {connect, node_id} : {connect})
  } catch {
    resetKey.value++
  } finally {
    busy.value.thunder_switch = false
  }
}

function statusText(o) {
  if (!o) return '---'
  if (o.power) return 'powered'
  return supply.value === false ? 'no power (control circuit not supplied)' : 'off'
}

</script>

<template>
  <div class="supply" :class="{ off: supply === false }">
    <span class="led" :class="{ on: supply }"/>
    <span class="caption">Control circuit</span>
    <span>{{ supply === undefined ? '---' : supply ? 'supplied' : 'not supplied' }}</span>
  </div>
  <div class="supply-parts">
    <span :class="{ bad: rcd === false }">RCD <b>{{ rcd === undefined ? '---' : rcd ? 'on' : 'off' }}</b></span>
    <span v-if="fuse !== undefined" :class="{ bad: fuse === false }"
          v-tooltip.top="'Mains detected behind the fuse'">Fuse <b>{{ fuse ? 'ok' : 'no mains' }}</b></span>
  </div>

  <template v-for="output in OUTPUTS" :key="output.key">
    <div class="output">
      <span class="led" :class="{ on: dev.state?.[output.key]?.power }"/>
      <div class="output-text">
        <div class="output-name">{{ output.label }}</div>
        <div class="muted output-status">
          {{ statusText(dev.state?.[output.key]) }}
          <span v-if="dev.state?.[output.key]?.manual_override" class="manual"
                v-tooltip.top="'The contactor does not follow the relay - switched manually'">manual</span>
        </div>
      </div>
      <ToggleSwitch :key="output.key + resetKey" :modelValue="!!dev.state?.[output.key]?.relay"
                    :disabled="busy[output.key] || dev.state?.[output.key] === undefined"
                    v-tooltip.left="'Relay'" @update:modelValue="(on) => setRelay(output, on)"/>
    </div>

    <!-- Thunder switch: the antennas disconnector, supplied by the antennas output -->
    <div v-if="output.key === 'antennas' && hasThunderSwitch" class="output sub-output">
      <span class="led" :class="{ on: ts?.connected && ts?.online, moving: tsMoving || ts?.pending }"/>
      <div class="output-text">
        <div class="output-name">Thunder switch</div>
        <div class="muted output-status">
          {{ tsStatus }}
          <span v-if="ts?.manual_move" class="manual" v-tooltip.top="'Moved by hand'">manual</span>
          <span v-for="e in tsErrors" :key="e.key" class="error">{{ e.text }}</span>
        </div>
      </div>
      <ToggleSwitch :key="'ts' + resetKey" :modelValue="tsTarget"
                    :disabled="busy.thunder_switch || tsMoving || supply === false"
                    v-tooltip.left="supply === false ? 'Control circuit not supplied' : 'Connect antennas'"
                    @update:modelValue="setThunderSwitch"/>
    </div>
  </template>
</template>

<style scoped>
.supply {
  display: flex;
  align-items: center;
  gap: .55rem;
  font-size: .85rem;
}

.supply.off {
  color: var(--app-danger);
}

.supply-parts {
  display: flex;
  gap: 1.25rem;
  margin-top: -.35rem;
  padding-left: 1.25rem;
  font-size: .8rem;
  color: var(--app-text-muted);
}

.supply-parts b {
  color: var(--app-text);
}

.supply-parts .bad,
.supply-parts .bad b {
  color: var(--app-danger);
}

.output {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding-top: .65rem;
  border-top: 1px solid var(--app-border);
}

.output-text {
  flex: 1;
  min-width: 0;
}

.output-name {
  font-weight: 600;
}

.output-status {
  display: flex;
  flex-wrap: wrap;
  column-gap: .5rem;
  align-items: center;
  gap: .5rem;
  font-size: .82rem;
}

.sub-output {
  padding-left: 1.25rem;
}

.error {
  padding: 0 .45rem;
  border-radius: 6px;
  background: color-mix(in srgb, var(--p-red-500) 18%, transparent);
  color: var(--p-red-400);
  font-size: .72rem;
  font-weight: 700;
}

.manual {
  padding: 0 .45rem;
  border-radius: 6px;
  background: color-mix(in srgb, var(--p-orange-500) 18%, transparent);
  color: var(--p-orange-400);
  font-size: .72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .05em;
}

.led {
  flex: none;
  width: .7rem;
  height: .7rem;
  border-radius: 50%;
  background: color-mix(in srgb, var(--app-text-muted) 35%, transparent);
}

.led.on {
  background: var(--p-primary-400);
  box-shadow: 0 0 8px var(--p-primary-400);
}

/* thunder switch moving or waiting for its supply */
.led.moving {
  background: var(--p-yellow-400);
  box-shadow: 0 0 8px var(--p-yellow-400);
  animation: blink 1s steps(2, start) infinite;
}

@keyframes blink {
  to {
    opacity: .3;
  }
}
</style>
