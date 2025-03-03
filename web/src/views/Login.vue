<script setup>
import {inject, ref} from "vue";

const axios = inject('axios');

const user = ref("")
const password = ref("")
async function handleLoginClick() {
  await axios
      .post('/api/login', {user: user.value, password: password.value}, {headers: {'Content-Type': 'application/json'}})
      .then(response => {
        console.log(response.data.response)
        window.location.href = "/"
      })
}

</script>
<template>
  <div class="wrapper min-vh-100 d-flex flex-row align-items-center">
    <CContainer>
      <CRow class="justify-content-center">
        <CCol :md="4">
          <CCardGroup>
            <CCard class="p-4" style="width: 44%">
              <CCardBody>
                <CForm>
                  <h1>Login</h1>
                  <p class="text-body-secondary">Sign In to your account</p>
                  <CInputGroup class="mb-3">
                    <CInputGroupText>
                      <CIcon icon="cil-user" />
                    </CInputGroupText>
                    <CFormInput placeholder="Username" autocomplete="username" v-model="user"/>
                  </CInputGroup>
                  <CInputGroup class="mb-4">
                    <CInputGroupText>
                      <CIcon icon="cil-lock-locked" />
                    </CInputGroupText>
                    <CFormInput type="password" placeholder="Password" autocomplete="current-password" v-model="password"/>
                  </CInputGroup>
                  <CRow>
                    <CCol :xs="6">
                      <CButton color="primary" class="px-4" @click="handleLoginClick()"> Login </CButton>
                    </CCol>
                    <CCol :xs="6" class="text-right">
                      <CPopover content="Unfortunately, I can't help you. &#128523;" placement="bottom">
                        <template #toggler="{ id, on }">
                          <CButton color="link" class="px-0" v-on="on">Forgot password?</CButton>
                        </template>
                      </CPopover>
                    </CCol>
                  </CRow>
                </CForm>
              </CCardBody>
            </CCard>
          </CCardGroup>
        </CCol>
      </CRow>
    </CContainer>
  </div>
</template>
<script setup>
</script>