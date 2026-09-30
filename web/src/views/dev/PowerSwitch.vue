<script setup>
import {ref} from 'vue'
import ToggleSwitch from 'primevue/toggleswitch'
import {useDevCall} from '@/composables/useDevCall.js'

const props = defineProps({
  dev: Object
});

const callDev = useDevCall()

// h9d doesn't report the real switch state yet (PowerSwitch::get_dev_state is a stub),
// so the switch shows the last state requested from here.
const on = ref(false)
const busy = ref(false)

async function setPower(value) {
  busy.value = true
  try {
    await callDev(props.dev.name, value ? 'power_on' : 'power_off')
  } catch {
    on.value = !value
  } finally {
    busy.value = false
  }
}

</script>

<template>
  <label class="power-switch">
    <ToggleSwitch v-model="on" :disabled="busy" @update:modelValue="setPower"/>
    Power
  </label>
</template>

<style scoped>
.power-switch {
  display: flex;
  align-items: center;
  gap: .75rem;
  cursor: pointer;
}
</style>
