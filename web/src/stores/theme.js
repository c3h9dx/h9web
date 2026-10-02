import { ref } from 'vue'
import { defineStore } from 'pinia'

// Same key as the inline script in index.html, which applies the theme before the app mounts
export const THEME_STORAGE_KEY = 'h9web-color-theme'
const DARK_CLASS = 'app-dark'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref(document.documentElement.classList.contains(DARK_CLASS) ? 'dark' : 'light')

  const setTheme = (_theme) => {
    theme.value = _theme
    document.documentElement.classList.toggle(DARK_CLASS, _theme === 'dark')
    try {
      localStorage.setItem(THEME_STORAGE_KEY, _theme)
    } catch {
      // storage unavailable (private mode) - theme just won't be remembered
    }
  }

  const toggleTheme = () => setTheme(theme.value === 'dark' ? 'light' : 'dark')

  return { theme, setTheme, toggleTheme }
})
