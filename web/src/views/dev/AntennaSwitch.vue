<script setup>
import {defineProps, inject, ref} from 'vue'

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
  <CCardHeader>Antenna Switch <small>{{ props.dev_name }}</small></CCardHeader>
  <CCardBody>
    <CButtonGroup size="sm">
      <template v-for="i in 8" :key="i">
        <CButton color="primary" variant="outline" @click="selectAntenna(i)" :active="isAntennaActive(i)">{{ i }}</CButton>
<!--        <CFormCheck :button="{color: 'primary', variant: 'outline'}" :label="i.toString()" :id="dev_name.toString() + '_' + i.toString()" :checked="isAntennaActive(i)" @change="(event) => selectAntenna(i)"/>-->
<!--        <CFormCheck :button="{ color: 'success', variant: 'outline' }" type="radio" name="select_antenna" :label="i.toString()" :value="rr" :id="dev_name.toString() + '_' + i.toString()" :checked="isAntennaActive(i)" @click="selectAntenna(i)"/>-->
      </template>
    </CButtonGroup>
  </CCardBody>
</template>

<style scoped>

</style>