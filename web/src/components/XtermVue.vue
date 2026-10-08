<script>
import '@xterm/xterm/css/xterm.css'
import {Terminal} from '@xterm/xterm'
import {FitAddon} from '@xterm/addon-fit'
import {Unicode11Addon} from '@xterm/addon-unicode11'
import {AttachAddon} from '@xterm/addon-attach';

// Reconnect delays [ms] after the websocket to h9web drops (h9web restarted, network...).
// A restart of h9cli itself is handled by h9web and keeps the websocket open.
const RECONNECT_DELAYS = [1000, 2000, 5000, 10000]

export default {
  name: "XtermVue",
  mounted() {
    this.$term = new Terminal({allowProposedApi: true, cursorBlink: true})
    this.$fitAddon = new FitAddon()

    this.$term.loadAddon(this.$fitAddon)
    this.$term.loadAddon(new Unicode11Addon())
    this.$term.unicode.activeVersion = '11'

    this.$term.open(this.$el)

    this.$reconnects = 0
    this.$destroyed = false
    this.connect()
  },

  beforeUnmount() {
    this.$destroyed = true
    clearTimeout(this.$reconnectTimer)
    this.$socket?.close()
    this.$term.dispose()
  },

  methods: {
    connect() {
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const socket = new WebSocket(`${protocol}://${window.location.host}/api/cli`)
      this.$socket = socket

      this.$attachAddon?.dispose()
      this.$attachAddon = new AttachAddon(socket, {bidirectional: true, inputUtf8: true})
      this.$term.loadAddon(this.$attachAddon)

      socket.addEventListener('open', () => {
        this.$reconnects = 0
      })
      socket.addEventListener('close', () => {
        if (this.$destroyed || socket !== this.$socket) {
          return
        }
        const delay = RECONNECT_DELAYS[Math.min(this.$reconnects, RECONNECT_DELAYS.length - 1)]
        this.$reconnects++
        this.$term.write(`\r\n\x1b[33m[connection to h9web lost - reconnecting in ${delay / 1000} s]\x1b[0m\r\n`)
        this.$reconnectTimer = setTimeout(() => this.connect(), delay)
      })
    },

    async focus() {
      await new Promise(r => setTimeout(r, 1000));
      this.$fitAddon.fit()
      this.$term.focus()
    }
  }
}
</script>

<template>
  <div class="xterm"/>
</template>

<style scoped>
.xterm {
  /* display: block; */
  height: 100%;
  width: 100%;
}
</style>
