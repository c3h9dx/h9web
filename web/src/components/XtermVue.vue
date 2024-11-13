<script>
import '@xterm/xterm/css/xterm.css'
import {Terminal} from '@xterm/xterm'
import {FitAddon} from '@xterm/addon-fit'
// import {WebLinksAddon} from 'xterm-addon-web-links'
import {Unicode11Addon} from '@xterm/addon-unicode11'

export default {
  name: "XtermVue",
  mounted() {
    this.$term = new Terminal({allowProposedApi: true, logLevel: 'trace'})
    // this.$term = new Terminal({allowProposedApi: true})
    // this.$term.allowProposedApi = true

    this.$fitAddon = new FitAddon()
    this.$term.loadAddon(this.$fitAddon)
    // this.$term.loadAddon(new WebLinksAddon())
    this.$term.loadAddon(new Unicode11Addon())
    this.$term.unicode.activeVersion = '11'

    this.$term.open(this.$el)
    this.$fitAddon.fit()
    this.$term.onTitleChange((title) => this.$emit('title-change', title))
  },

  methods: {
    fit() {
      this.$fitAddon.fit()
    },
    focus() {
      this.$term.focus()
    },
    blur() {
      this.$term.blur()
    },
    paste(data) {
      this.$term.paste(data)
    }
  }
}
</script>

<template>
    <div class="xterm" />
</template>

<style scoped>
.xterm {
  height: 100%;
  width: 100%;
}
</style>