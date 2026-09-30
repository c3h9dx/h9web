<script setup>
import {inject, ref} from "vue";
import Card from 'primevue/card'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import Popover from 'primevue/popover'

const axios = inject('axios');

const user = ref("")
const password = ref("")
const forgotPopover = ref(null)

async function handleLoginClick() {
  await axios
      .post('/api/login', {user: user.value, password: password.value}, {headers: {'Content-Type': 'application/json'}})
      .then(response => {
        window.location.href = "/"
      })
}

</script>
<template>
  <div class="login-page">
    <Card class="login-card">
      <template #content>
        <form class="login-form" @submit.prevent="handleLoginClick()">
          <div>
            <h1>Login</h1>
            <p class="muted">Sign In to your account</p>
          </div>
          <InputGroup>
            <InputGroupAddon><i class="pi pi-user"/></InputGroupAddon>
            <InputText placeholder="Username" autocomplete="username" v-model="user"/>
          </InputGroup>
          <InputGroup>
            <InputGroupAddon><i class="pi pi-lock"/></InputGroupAddon>
            <InputText type="password" placeholder="Password" autocomplete="current-password" v-model="password"/>
          </InputGroup>
          <div class="login-actions">
            <Button type="submit" label="Login"/>
            <Button type="button" label="Forgot password?" link @click="(e) => forgotPopover.toggle(e)"/>
            <Popover ref="forgotPopover">Unfortunately, I can't help you. &#128523;</Popover>
          </div>
        </form>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1rem;
}

.login-card {
  width: 100%;
  max-width: 26rem;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
}

.login-form p {
  margin: 0;
}

.login-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
