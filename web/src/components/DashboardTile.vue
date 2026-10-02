<script setup>
// One dashboard tile: caption with the widget title, the device name in a pill, and the widget itself
defineProps({
  widget: Object,  // {title, component} from views/dev/index.js
  dev: Object,     // {name, type, methods, state}
})
</script>

<template>
  <div class="surface-card dash-tile">
    <div class="dev-header">
      <span class="caption">{{ widget.title }}</span>
      <span class="pill" :title="dev.name"><span class="pill-text">{{ dev.name }}</span></span>
    </div>
    <div class="dev-body">
      <component :is="widget.component" :dev="dev"/>
    </div>
  </div>
</template>

<style scoped>
.dash-tile {
  height: 100%;
  overflow: hidden;
}

.pill {
  min-width: 0;
  max-width: 60%;
}

.pill-text {
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
