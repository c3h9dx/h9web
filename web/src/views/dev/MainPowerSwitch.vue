<script setup>
import {defineProps, inject, ref} from 'vue'
import ToggleSwitch from 'primevue/toggleswitch'

const axios = inject('axios');
const toasts = inject('toasts');

const props = defineProps({
  dev_name: String,
  dev_state: Object
});

const state = ref(false)

async function handleChange(checked) {
  if (checked) {
    await axios.post('/api/dev/' + props.dev_name + '/power_on')
        .then(response => {
        }).catch(function (error) {
          state.value = false
          toasts.value.push({
            title: 'Switch',
            content: error
          })
        })
  }
  else {
    await axios.post('/api/dev/' + props.dev_name + '/power_off')
        .then(response => {
        }).catch(function (error) {
          state.value = true
          toasts.value.push({
            title: 'Switch',
            content: error
          })
        })
  }
}

</script>

<template>
  <div class="dev-header">Main Power <small>{{ dev_name }}</small></div>
  <div class="dev-body">
    <label class="power-switch">
      <ToggleSwitch v-model="state" @update:modelValue="handleChange"/>
      Main power
    </label>
  </div>
</template>

<style scoped>
.power-switch {
  display: flex;
  align-items: center;
  gap: .75rem;
  cursor: pointer;
}
</style>