<script setup>
import {CContainer} from '@coreui/vue'
import AppFooter from '@/components/AppFooter.vue'
import AppHeader from '@/components/AppHeader.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import {inject} from "vue";
import {CToastBody, CToaster, CToastHeader} from "@coreui/vue/dist/esm/components/toast/index.js";

const toasts = inject('toasts');

const test = {
  "--cui-toast-header-color": "#ff0000",
}

</script>

<template>
  <div>
    <AppSidebar/>
    <div class="wrapper d-flex flex-column min-vh-100">
      <AppHeader/>
      <div class="body flex-grow-1">
        <CContainer xl>
          <router-view/>
        </CContainer>
      </div>
      <AppFooter/>
    </div>

    <CToaster class="p-3" placement="bottom-end">
      <CToast :style="test" v-for="(toast, index) in toasts" visible :key="index" :delay=10000 class="border-0">
        <CCallout color="danger" class="m-0 p-0">
          <CToastHeader closeButton>
            <span class="me-auto fw-bold">{{ toast.title }}</span>
          </CToastHeader>
          <CToastBody>
            {{ toast.content }}
          </CToastBody>
        </CCallout>
      </CToast>
    </CToaster>
  </div>
</template>
