import {inject} from 'vue'

// Returns callDev(devName, method, params) - invokes an h9d device method through /api/dev.
// Errors are shown as a toast and rethrown, so the caller can roll back its UI state.
export function useDevCall() {
  const axios = inject('axios')
  const toasts = inject('toasts')

  return async function callDev(devName, method, params = {}) {
    try {
      const response = await axios.post('/api/dev/' + devName + '/' + method, params)
      return response.data.response
    } catch (error) {
      toasts.value.push({title: devName + ': ' + method, content: error})
      throw error
    }
  }
}
