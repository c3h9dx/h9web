import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import axios from 'axios'
import VueAxios from 'vue-axios'

import CoreuiVue from '@coreui/vue'
import CIcon from '@coreui/icons-vue'
import { iconsSet as icons } from '@/assets/icons'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(VueAxios, axios)
app.use(CoreuiVue)

app.provide('axios', app.config.globalProperties.axios)
app.provide('icons', icons)

app.component('CIcon', CIcon)

app.mount('#app')
