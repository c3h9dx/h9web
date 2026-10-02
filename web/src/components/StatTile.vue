<script setup>
// Card with a small uppercase label, a big value with its unit and an optional line below.
// Slots: default (below the value), badge (top right).
defineProps({
  label: String,
  value: [String, Number],
  unit: String,
  text: Boolean,  // value is text (e.g. a version string) - smaller font, may wrap
})
</script>

<template>
  <div class="stat-tile">
    <div class="stat-head">
      <span class="caption">{{ label }}</span>
      <slot name="badge"/>
    </div>
    <div class="big-value" :class="{ text }">{{ value ?? '---' }}<span v-if="unit" class="unit">{{ unit }}</span></div>
    <div v-if="$slots.default" class="stat-sub muted">
      <slot/>
    </div>
  </div>
</template>

<style scoped>
.stat-tile {
  display: flex;
  flex-direction: column;
  gap: .55rem;
  min-width: 0;
  padding: 1.15rem 1.25rem;
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: var(--app-radius);
}

.stat-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .5rem;
  min-height: 1.5rem;
}

.big-value.text {
  font-size: 1.2rem;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.stat-sub {
  font-size: .82rem;
}
</style>
