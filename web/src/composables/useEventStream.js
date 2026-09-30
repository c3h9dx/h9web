import {inject, onBeforeUnmount, onMounted} from 'vue'

// Subscribes to h9web server-sent events (/api/events) for the lifetime of the calling component.
// handlers: {event name: (data) => ...}, e.g. {frame: addFrame}; data arrives parsed from JSON.
export function useEventStream(handlers) {
  const toasts = inject('toasts')
  let source = null
  let lost = false

  onMounted(() => {
    const filter = Object.keys(handlers).map((e) => 'filter=' + encodeURIComponent(e)).join('&')
    source = new EventSource('/api/events?' + filter, {withCredentials: true})

    for (const [event, handler] of Object.entries(handlers)) {
      source.addEventListener(event, (e) => handler(JSON.parse(e.data)))
    }

    source.addEventListener('open', () => {
      lost = false
    })
    source.addEventListener('error', () => {
      // EventSource reconnects by itself - report the loss once, not on every retry
      if (!lost) {
        lost = true
        toasts.value.push({title: 'Events', content: 'Connection to h9web lost, reconnecting...'})
      }
    })
  })

  onBeforeUnmount(() => {
    source?.close()
  })
}
