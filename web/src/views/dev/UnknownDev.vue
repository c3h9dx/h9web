<script setup>
defineProps({
  dev: Object
});
</script>

<template>
  <div class="muted">No widget for device type <b>{{ dev.type }}</b></div>
  <div v-if="dev.methods?.length">Methods: {{ dev.methods.join(', ') }}</div>
  <code>{{ JSON.stringify(dev.state) }}</code>
</template>
