<script>
import '@xterm/xterm/css/xterm.css'
import {Terminal} from '@xterm/xterm'
import {FitAddon} from '@xterm/addon-fit'
import {Unicode11Addon} from '@xterm/addon-unicode11'
import {AttachAddon} from '@xterm/addon-attach';


export default {
  name: "XtermVue",
  mounted() {
    console.log("mounted")
    // this.$term = new Terminal({allowProposedApi: true, cursorBlink: true, logLevel: 'trace'})
    this.$term = new Terminal({allowProposedApi: true, cursorBlink: true})

    const socket = new WebSocket(`ws://${window.location.host}/api/cli`);

    this.$attachAddon = new AttachAddon(socket, {bidirectional: true, inputUtf8: true});
    this.$fitAddon = new FitAddon()

    this.$term.loadAddon(this.$fitAddon)
    this.$term.loadAddon(this.$attachAddon);
    this.$term.loadAddon(new Unicode11Addon())
    this.$term.unicode.activeVersion = '11'

    this.$term.open(this.$el)
  },

  methods: {
    async focus() {
      console.log("FOCUS")
      await new Promise(r => setTimeout(r, 1000));
      this.$fitAddon.fit()

      // let tmp = this.$fitAddon.proposeDimensions()
      // console.log(tmp)
      // this.$term.resize(tmp.cols, tmp.rows - 2)

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
//display: block;
  height: 100%;
  width: 100%;
}
</style>