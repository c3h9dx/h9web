<script setup>
import {computed} from "vue";
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'
import {useDevCall} from '@/composables/useDevCall.js'

const props = defineProps({
  dev: Object
});

const callDev = useDevCall()

// pwr [W] and swr [x100] arrive with dev state events from h9d (atu.cc)
const pwr = computed(() => props.dev.state?.pwr)
const swr = computed(() => props.dev.state?.swr === undefined ? undefined : props.dev.state.swr / 100)

// SWR 1.0 - 10.0 mapped onto the bar
const swrPercent = computed(() => swr.value === undefined ? 0 : Math.min(100, (swr.value - 1) * 100 / 9))

const canTune = computed(() => props.dev.methods?.includes('tune'))

</script>

<template>
  <div>
    PWR: {{ pwr ?? '---' }} W
    <ProgressBar class="meter meter-pwr" :value="Math.min(100, pwr ?? 0)" :showValue="false"/>
  </div>
  <div>
    SWR: {{ swr === undefined ? '---' : swr.toFixed(2) }}
    <ProgressBar class="meter meter-swr" :value="swrPercent" :showValue="false"/>
  </div>
  <div v-if="canTune">
    <Button label="Tune" outlined size="small" @click="callDev(dev.name, 'tune').catch(() => {})"/>
  </div>
</template>

<style scoped>
.meter {
  height: .3rem;
  margin-top: .25rem;
}

.meter :deep(.p-progressbar-value) {
  transition: width .1s ease;
}

.meter-pwr {
  --p-progressbar-value-background: var(--p-green-500);
}

.meter-swr {
  --p-progressbar-value-background: var(--p-red-500);
}
</style>
