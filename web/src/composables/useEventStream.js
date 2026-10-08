import {onBeforeUnmount, onMounted, ref} from 'vue'

// EventSource reconnects by itself only after network errors. When a retry gets a non-200 answer
// (e.g. 502 from a proxy while h9web restarts) it gives up for good - then we reconnect after these delays [ms].
const RECONNECT_DELAYS = [1000, 2000, 5000, 10000]

// Subscribes to h9web server-sent events (/api/events) for the lifetime of the calling component.
// handlers: {event name: (data) => ...}, e.g. {frame: addFrame}; data arrives parsed from JSON.
// Returns `connected` (ref) - false while the stream is down.
export function useEventStream(handlers) {
  const connected = ref(false)
  const filter = Object.keys(handlers).map((e) => 'filter=' + encodeURIComponent(e)).join('&')
  let source = null
  let reconnects = 0
  let reconnectTimer = null
  let stopped = false

  function connect() {
    reconnectTimer = null
    source = new EventSource('/api/events?' + filter, {withCredentials: true})

    for (const [event, handler] of Object.entries(handlers)) {
      source.addEventListener(event, (e) => handler(JSON.parse(e.data)))
    }

    source.addEventListener('open', () => {
      connected.value = true
      reconnects = 0
    })
    source.addEventListener('error', () => {
      connected.value = false
      if (source.readyState === EventSource.CLOSED && !stopped && reconnectTimer === null) {
        const delay = RECONNECT_DELAYS[Math.min(reconnects, RECONNECT_DELAYS.length - 1)]
        reconnects++
        reconnectTimer = setTimeout(connect, delay)
      }
    })
  }

  onMounted(connect)

  onBeforeUnmount(() => {
    stopped = true
    clearTimeout(reconnectTimer)
    source?.close()
  })

  return {connected}
}
