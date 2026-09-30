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
      <RouterLink to="/">
        <svg class="sidebar-logo" :viewBox="'0 0 ' + logo[0]" height="32" v-html="logo[1]"/>
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
  background: var(--app-sidebar-bg);
  color: var(--app-sidebar-text);
}

.sidebar-brand {
  display: flex;
  align-items: center;
  height: var(--app-header-height);
  padding: 0 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, .1);
}

.sidebar-brand a {
  display: flex;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: .15rem;
  padding: .5rem;
  overflow-y: auto;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: .85rem;
  padding: .7rem 1rem;
  border-radius: 6px;
  color: inherit;
  text-decoration: none;
}

.sidebar-link:hover {
  color: #fff;
  background: rgba(255, 255, 255, .05);
}

.sidebar-link.active {
  color: #fff;
  background: var(--app-sidebar-active-bg);
}

.sidebar-link i {
  font-size: 1.1rem;
  width: 1.25rem;
  text-align: center;
}
</style>
