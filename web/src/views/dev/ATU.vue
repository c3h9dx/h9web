<script setup>
import {defineProps} from "vue";
import {CCol, CRow} from "@coreui/vue/dist/esm/components/grid/index.js";

const props = defineProps({
  dev_name: String,
  dev_state: Object
});

const vars = {
  '--cui-progress-bar-transition': "width .1s ease"
}
</script>

<template>
  <CCardHeader>ATU <small>{{ dev_name }}</small></CCardHeader>
  <CCardBody>
    <CRow class="mb-2">
      <CCol>
      PWR: {{ dev_state?.pwr }} W
      <CProgress :style="vars" :value="dev_state?.pwr" color="success" :thin="true"/>
      </CCol>
    </CRow>
    <CRow class="mb-2">
      <CCol>
      SWR: {{ dev_state?.swr / 100 }}
      <CProgress :style="vars" :value="dev_state?.swr ? (dev_state?.swr - 100) * 100 / 899 : 0" color="danger" :thin="true"/>
      <!--    <CProgress :value="10" color="success"/>-->
      <!--    <CFormSwitch size="lg" label="Main power" @click="handleClick" v-model="state"/>-->
      </CCol>
    </CRow>
<!--    <CRow>-->
      <CButton color="primary" variant="outline">Tune</CButton>
<!--    </CRow>-->
  </CCardBody>
</template>

<style scoped>

</style>