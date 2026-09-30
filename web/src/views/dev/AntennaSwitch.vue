<script setup>
import {defineProps, inject, ref} from 'vue'
import Button from 'primevue/button'
import ButtonGroup from 'primevue/buttongroup'

const axios = inject('axios');
const toasts = inject('toasts');

const props = defineProps({
  dev_name: String,
  dev_state: Object
});

async function selectAntenna(antenna_number) {
  console.log("select", antenna_number)
  await axios.post('/api/dev/' + props.dev_name + '/select_antenna', {'antenna_number': antenna_number}, {headers: {'Content-Type': 'application/json'}})
      .then(response => {
        props.dev_state.selected_antenna = 0
      }).catch(function (error) {
        props.dev_state.selected_antenna = 0
        toasts.value.push({
          title: 'Switch',
          content: error
        })
      })
}

function isAntennaActive(antenna_number) {
  return props.dev_state?.selected_antenna === antenna_number
}

</script>

<template>
  <div class="dev-header">Antenna Switch <small>{{ props.dev_name }}</small></div>
  <div class="dev-body">
    <ButtonGroup>
      <Button v-for="i in 8" :key="i" :label="i.toString()" size="small" :outlined="!isAntennaActive(i)"
              @click="selectAntenna(i)"/>
    </ButtonGroup>
  </div>
</template>

<style scoped>

</style>