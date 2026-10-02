import { ref, createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import axios from 'axios'

import PrimeVue from 'primevue/config'
import ToastService from 'primevue/toastservice'
import Tooltip from 'primevue/tooltip'
import Aura from '@primeuix/themes/aura'
import { definePreset } from '@primeuix/themes'
import 'primeicons/primeicons.css'

import './styles/style.css'

// Green accent on near-black graphite surfaces (dark is the default theme, see index.html)
const H9Preset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '{emerald.50}',
      100: '{emerald.100}',
      200: '{emerald.200}',
      300: '{emerald.300}',
      400: '{emerald.400}',
      500: '{emerald.500}',
      600: '{emerald.600}',
      700: '{emerald.700}',
      800: '{emerald.800}',
      900: '{emerald.900}',
      950: '{emerald.950}',
    },
    colorScheme: {
      dark: {
        surface: {
          0: '#ffffff',
          50: '#f3f4f6',
          100: '#e4e6ea',
          200: '#c7cbd1',
          300: '#9aa0a8',
          400: '#6e747d',
          500: '#4c5159',
          600: '#353940',
          700: '#272b31',
          800: '#1c1f24',
          900: '#16181c',
          950: '#0e1013',
        },
      },
    },
  },
})

const app = createApp(App)

app.use(router)
app.use(createPinia())
app.use(PrimeVue, {
  theme: {
    preset: H9Preset,
    options: {
      // Toggled on <html> by the theme store (see stores/theme.js and index.html)
      darkModeSelector: '.app-dark',
    },
  },
})
app.use(ToastService)
app.directive('tooltip', Tooltip)

app.provide('axios', axios)

const toasts = ref([])
app.provide('toasts', toasts)

app.mount('#app')
