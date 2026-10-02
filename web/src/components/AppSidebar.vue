<script setup>
import {RouterLink} from 'vue-router'

import {logo} from '@/assets/logo'
import nav from '@/router/nav.js'
import {useSidebarStore} from '@/stores/sidebar.js'

const sidebar = useSidebarStore()

function onNavigate(navigate) {
  navigate()
  // On narrow screens the sidebar overlays the page - close it after picking a page
  if (!window.matchMedia('(min-width: 992px)').matches) {
    sidebar.toggleVisible(false)
  }
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <RouterLink to="/" class="brand-link">
        <svg class="brand-logo" :viewBox="'0 0 ' + logo[0]" height="30" v-html="logo[1]"/>
        <span class="brand-text">
          <b>h9web</b>
          <small>h9 bus control</small>
        </span>
      </RouterLink>
    </div>

    <nav class="sidebar-nav">
      <RouterLink v-for="item in nav" :key="item.to" :to="item.to" custom v-slot="{ href, navigate, isActive }">
        <a :href="href" class="sidebar-link" :class="{ active: isActive }" @click.prevent="onNavigate(navigate)">
          <i :class="item.icon"/>
          <span>{{ item.name }}</span>
        </a>
      </RouterLink>
    </nav>
  </aside>
</template>

<style scoped>
.sidebar {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--app-bg);
  border-right: 1px solid var(--app-border);
}

.sidebar-brand {
  padding: 1.1rem 1.25rem;
}

.brand-link {
  display: flex;
  align-items: center;
  gap: .7rem;
  color: var(--app-text);
  text-decoration: none;
}

/* The logo is drawn in white - on the light theme show it on a dark badge */
.brand-logo {
  flex: none;
  padding: .25rem;
  border-radius: 8px;
  background: #16181c;
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.15;
}

.brand-text b {
  font-size: 1.05rem;
  letter-spacing: .02em;
}

.brand-text small {
  font-size: .7rem;
  color: var(--app-text-muted);
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: .2rem;
  padding: .75rem;
  border-top: 1px solid var(--app-border);
  overflow-y: auto;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: .85rem;
  padding: .65rem .9rem;
  border-radius: 10px;
  color: var(--app-text-muted);
  font-weight: 600;
  text-decoration: none;
  transition: background .12s, color .12s;
}

.sidebar-link:hover {
  color: var(--app-text);
  background: color-mix(in srgb, var(--app-text) 5%, transparent);
}

.sidebar-link.active {
  color: var(--app-accent);
  background: var(--app-accent-soft);
}

.sidebar-link i {
  font-size: 1.05rem;
  width: 1.25rem;
  text-align: center;
}
</style>
