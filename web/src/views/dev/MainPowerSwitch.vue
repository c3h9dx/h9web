<script setup>
import {defineProps, inject, ref} from 'vue'

const axios = inject('axios');
const toasts = inject('toasts');

const props = defineProps({
  dev_name: String,
  dev_state: Object
});

const state = ref(false)

async function handleClick(event) {
  if (event.target.checked) {
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
  <CCardHeader>Main Power <small>{{ dev_name }}</small></CCardHeader>
  <CCardBody>
    <CFormSwitch size="lg" label="Main power" @click="handleClick" v-model="state"/>
  </CCardBody>
</template>

<style scoped>

</style>