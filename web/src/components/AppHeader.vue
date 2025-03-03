<script setup>
import {inject, nextTick, onMounted, ref} from 'vue'
import {useColorModes} from '@coreui/vue'

import {useSidebarStore} from '@/stores/sidebar.js'
import XtermVue from "@/components/XtermVue.vue";

const headerClassNames = ref('mb-4 p-0')
const {colorMode, setColorMode} = useColorModes('coreui-free-vue-admin-template-theme')
const sidebar = useSidebarStore()

const visibleBottom = ref(false)

const axios = inject('axios');

async function logout() {
  await axios
      .get('/api/logout', {headers: {'Content-Type': 'application/json'}})
      .then(response => {
        console.log("try redirect")
        window.location.href = "/"
      })
}

onMounted(() => {
  document.addEventListener('scroll', () => {
    if (document.documentElement.scrollTop > 0) {
      headerClassNames.value = 'mb-4 p-0 shadow-sm'
    } else {
      headerClassNames.value = 'mb-4 p-0'
    }
  })
})

const offcanvas_style = {
"--cui-offcanvas-bg": "black"
}

const xterm = ref(null)

function do_focus() {
  xterm.value.focus()
}

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
            <CIcon icon="cil-terminal" size="lg" @click="() => { visibleBottom = !visibleBottom }"/>
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
        <CNavItem>
          <CNavLink href="#">
            <CIcon size="lg" icon="cil-accountLogout" @click="logout()"/>
          </CNavLink>

        </CNavItem>
      </CHeaderNav>
    </CContainer>
  </CHeader>

  <COffcanvas :style="offcanvas_style" placement="bottom" :visible="visibleBottom" @hide="() => { visibleBottom = !visibleBottom }" @show="do_focus" :keyboard="false" aria-labelledby="CLI" aria-describedby="dialog1Desc">
<!--    <COffcanvasHeader style="height: 1px">-->
<!--      <COffcanvasTitle>CLI</COffcanvasTitle>-->
<!--      <CCloseButton class="text-reset" @click="() => { visibleBottom = false }"/>-->
<!--    </COffcanvasHeader>-->
    <XtermVue ref="xterm"/>
  </COffcanvas>

</template>

<style lang="scss" scoped>

$form-switch-checked-color: rgba(#ff00ff, .25);
$form-switch-focus-color: rgba(#ff00ff, .25) !important;
</style>
