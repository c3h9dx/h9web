import {onBeforeUnmount, onMounted, ref} from 'vue'

// Subscribes to h9web server-sent events (/api/events) for the lifetime of the calling component.
// handlers: {event name: (data) => ...}, e.g. {frame: addFrame}; data arrives parsed from JSON.
// Returns `connected` (ref) - false while the stream is down; EventSource reconnects by itself.
export function useEventStream(handlers) {
  const connected = ref(false)
  let source = null

  onMounted(() => {
    const filter = Object.keys(handlers).map((e) => 'filter=' + encodeURIComponent(e)).join('&')
    source = new EventSource('/api/events?' + filter, {withCredentials: true})

    for (const [event, handler] of Object.entries(handlers)) {
      source.addEventListener(event, (e) => handler(JSON.parse(e.data)))
    }

    source.addEventListener('open', () => {
      connected.value = true
    })
    source.addEventListener('error', () => {
      connected.value = false
    })
  })

  onBeforeUnmount(() => {
    source?.close()
  })

  return {connected}
}
