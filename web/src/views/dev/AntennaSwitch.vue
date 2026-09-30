<script setup>
import {computed, ref} from 'vue'
import Button from 'primevue/button'
import ButtonGroup from 'primevue/buttongroup'
import {useDevCall} from '@/composables/useDevCall.js'

const props = defineProps({
  dev: Object
});

const callDev = useDevCall()

// h9d reports 0 antennas until it has read them from the switch node - offer 8 meanwhile
const DEFAULT_ANTENNAS = 8
const count = computed(() => props.dev.state?.number_of_antenna || DEFAULT_ANTENNAS)
const names = computed(() => props.dev.state?.antennas_name ?? [])

const pending = ref(null)

// The selection shown comes from h9d (dev state events), not from the click
async function selectAntenna(antenna_number) {
  pending.value = antenna_number
  try {
    await callDev(props.dev.name, 'select_antenna', {antenna_number: antenna_number})
  } catch {
    // toast already shown by callDev
  } finally {
    pending.value = null
  }
}

</script>

<template>
  <ButtonGroup class="antennas">
    <Button v-for="i in count" :key="i" :label="i.toString()" size="small"
            :outlined="dev.state?.selected_antenna !== i" :loading="pending === i" :disabled="pending !== null"
            v-tooltip.bottom="names[i - 1]" @click="selectAntenna(i)"/>
  </ButtonGroup>
</template>

<style scoped>
.antennas {
  flex-wrap: wrap;
}
</style>
