<script setup>

import {onBeforeMount} from 'vue'
import {RouterView} from 'vue-router'

import {useThemeStore} from '@/stores/theme.js'

const theme = useThemeStore()

onBeforeMount(() => {
  // ?theme=dark|light in the URL overrides the remembered theme
  const urlParams = new URLSearchParams(window.location.href.split('?')[1])
  const urlTheme = urlParams.get('theme')

  if (urlTheme === 'dark' || urlTheme === 'light') {
    theme.setTheme(urlTheme)
  }
})
</script>

<template>
  <router-view/>
</template>
