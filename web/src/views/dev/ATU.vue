<script setup>
import {defineProps} from "vue";
import Button from 'primevue/button'
import ProgressBar from 'primevue/progressbar'

const props = defineProps({
  dev_name: String,
  dev_state: Object
});
</script>

<template>
  <div class="dev-header">ATU <small>{{ dev_name }}</small></div>
  <div class="dev-body">
    <div>
      PWR: {{ dev_state?.pwr }} W
      <ProgressBar class="meter meter-pwr" :value="dev_state?.pwr" :showValue="false"/>
    </div>
    <div>
      SWR: {{ dev_state?.swr / 100 }}
      <ProgressBar class="meter meter-swr" :value="dev_state?.swr ? (dev_state?.swr - 100) * 100 / 899 : 0" :showValue="false"/>
    </div>
    <div>
      <Button label="Tune" outlined size="small"/>
    </div>
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
