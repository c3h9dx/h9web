<script setup>
import {onMounted, ref} from 'vue'
import {useColorModes} from '@coreui/vue'

import {useSidebarStore} from '@/stores/sidebar.js'

const headerClassNames = ref('mb-4 p-0')
const {colorMode, setColorMode} = useColorModes('coreui-free-vue-admin-template-theme')
const sidebar = useSidebarStore()

onMounted(() => {
  document.addEventListener('scroll', () => {
    if (document.documentElement.scrollTop > 0) {
      headerClassNames.value = 'mb-4 p-0 shadow-sm'
    } else {
      headerClassNames.value = 'mb-4 p-0'
    }
  })
})
</script>

<template>
  <CHeader position="sticky" :class="headerClassNames">
    <CContainer class="border-bottom px-4" fluid>
      <CHeaderToggler @click="sidebar.toggleVisible()" style="margin-inline-start: -14px">
        <CIcon icon="cil-menu" size="lg"/>
      </CHeaderToggler>
      <CHeaderNav class="ms-auto">
        <CNavItem>
          <CNavLink href="#">
            <CIcon icon="cil-terminal" size="lg"/>
          </CNavLink>
        </CNavItem>
      </CHeaderNav>
      <CHeaderNav>
        <li class="nav-item py-1">
          <div class="vr h-100 mx-2 text-body text-opacity-75"></div>
        </li>
        <CNavItem>
          <CNavLink href="#">
            <CIcon size="lg" :icon="colorMode === 'light' ? 'cil-moon' : 'cil-sun'"
                   @click="colorMode === 'light' ? setColorMode('dark') : setColorMode('light')"/>
<!--                    <CFormSwitch class="tts" size="lg" id="formSwitchCheckDefault" :checked="colorMode === 'dark'" @click="colorMode === 'light' ? setColorMode('dark') : setColorMode('light')"/>-->
          </CNavLink>
        </CNavItem>
      </CHeaderNav>
    </CContainer>
  </CHeader>
</template>

<style lang="scss" scoped>
$form-switch-checked-color: rgba(#ff00ff, .25);
$form-switch-focus-color: rgba(#ff00ff, .25) !important;
</style>
