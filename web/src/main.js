import { ref, createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import axios from 'axios'
import VueAxios from 'vue-axios'

import VueSSE from 'vue-sse';

import CoreuiVue from '@coreui/vue'
import CIcon from '@coreui/icons-vue'
import { iconsSet as icons } from '@/assets/icons'

const app = createApp(App)

app.use(router)
app.use(createPinia())
app.use(VueAxios, axios)
app.use(VueSSE);
app.use(CoreuiVue)

app.provide('icons', icons)
app.provide('axios', app.config.globalProperties.axios)
app.provide('sse', app.config.globalProperties.$sse)

const toasts = ref([])
app.provide('toasts', toasts)

app.component('CIcon', CIcon)

app.mount('#app')
