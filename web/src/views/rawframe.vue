<script setup>

import {computed, inject, onBeforeUnmount, onMounted, ref, shallowRef} from "vue";
import Card from 'primevue/card'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import InputGroup from 'primevue/inputgroup'
import InputGroupAddon from 'primevue/inputgroupaddon'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import {useRoute} from 'vue-router'
import {useEventStream} from '@/composables/useEventStream.js'

const axios = inject('axios');
const toasts = inject('toasts');


// Frame types as defined in h9can/include/h9def.h (h9d v0.4)
const frame_type = [
  // --- UNICAST ---
  {value: 0, label: "RES1"},
  {value: 1, label: "PAGE_START"},
  {value: 2, label: "QUIT_BOOTLOADER"},
  {value: 3, label: "PAGE_FILL"},
  {value: 4, label: "RES2"},
  {value: 5, label: "PAGE_FILL_NEXT"},
  {value: 6, label: "PAGE_WRITED"},
  {value: 7, label: "PAGE_FILL_BREAK"},
  {value: 8, label: "COMMAND_ERROR"},
  {value: 9, label: "REG_VALUE"},
  {value: 10, label: "SET_REG"},
  {value: 11, label: "GET_REG"},
  {value: 12, label: "SET_BIT"},
  {value: 13, label: "CLEAR_BIT"},
  {value: 14, label: "NODE_UPGRADE"},
  {value: 15, label: "NODE_RESET"},
  // --- SPECIAL BROADCAST ---
  {value: 16, label: "DISCOVER"},
  {value: 17, label: "GROUP_RESET"},
  // --- BROADCAST ---
  {value: 18, label: "NODE_FAULT"},
  {value: 19, label: "REG_VALUE_BROADCAST"},
  {value: 20, label: "NODE_HEARTBEAT"},
  {value: 21, label: "NODE_INFO"},
  {value: 22, label: "NODE_TURNED_ON"},
  {value: 23, label: "BOOTLOADER_TURNED_ON"},
  {value: 24, label: "NODE_SPECIFIC_BROADCAST0"},
  {value: 25, label: "NODE_SPECIFIC_BROADCAST1"},
  {value: 26, label: "NODE_SPECIFIC_BROADCAST2"},
  {value: 27, label: "NODE_SPECIFIC_BROADCAST3"},
  {value: 28, label: "NODE_SPECIFIC_BROADCAST4"},
  {value: 29, label: "NODE_SPECIFIC_BROADCAST5"},
  {value: 30, label: "NODE_SPECIFIC_BROADCAST6"},
  {value: 31, label: "NODE_SPECIFIC_BROADCAST7"}
];

const frame_flags = [
  {value: 0, label: "SINGLE_FRAME"},
  {value: 1, label: "MULTI_FRAME_FIRST"},
  {value: 2, label: "MULTI_FRAME_MIDDLE"},
  {value: 3, label: "MULTI_FRAME_LAST"}
];

const BROADCAST_TYPE_MIN = 16  // H9FRAME_TYPE_DISCOVER - types from here up are broadcasts
const BROADCAST_ALL_GROUP = 0xffff

const TYPE_MAX = 31
const FLAGS_MAX = 7
const SEQNUM_MAX = 31
const ID_MAX = 255
const GROUP_MAX = 0xffff

function isBroadcast(type) {
  return Number(type) >= BROADCAST_TYPE_MIN
}

function typeLabel(type) {
  const t = frame_type.find((t) => t.value === type)
  return t ? t.label : type
}

function flagsLabel(flags) {
  const f = frame_flags.find((f) => f.value === flags)
  return f ? f.label : flags
}

function groupLabel(group) {
  return group === BROADCAST_ALL_GROUP ? 'ALL' : group
}

const frame = ref({
  type: 11,
  flags: 0,
  seqnum: 0,
  destination_id: 0,
  source_id: 0,
  broadcast_group: 0,
  dlc: 0,
  data: [null, null, null, null, null, null, null, null]
})

const group_all = ref(false)

const is_broadcast = computed(() => isBroadcast(frame.value.type))

// Type picker options, grouped by frame kind
const frame_type_groups = [
  {label: 'Unicast', items: frame_type.filter((t) => !isBroadcast(t.value))},
  {label: 'Broadcast', items: frame_type.filter((t) => isBroadcast(t.value))},
].map((g) => ({...g, items: g.items.map((t) => ({...t, text: t.value + ' ' + t.label}))}))

const raw_frame = ref(false)

// The bus can deliver hundreds of frames per second - rendering each one separately into an ever
// growing table froze the page. Frames are buffered and shown in batches, newest first, and only
// the last MAX_FRAMES are kept. The list is a shallowRef of plain objects: no deep reactivity needed.
const MAX_FRAMES = 500
const FLUSH_MS = 200

const frames = shallowRef([])
const expanded_frames = ref({})
const paused = ref(false)
const received = ref(0)   // all frames since the page was opened (or cleared)

let pending = []          // frames waiting for the next flush (newest last)
let received_count = 0
let flush_timer = null

// Frames have no id of their own - number them as they arrive, for the table's row keys
let frame_key = 0
function addFrame(f) {
  pending.push({...f, _key: frame_key++})
  if (pending.length > MAX_FRAMES) {
    pending.splice(0, pending.length - MAX_FRAMES)
  }
  received_count++
  if (flush_timer === null) {
    flush_timer = setTimeout(flushFrames, FLUSH_MS)
  }
}

function flushFrames() {
  flush_timer = null
  received.value = received_count
  if (paused.value || !pending.length) {
    return
  }
  const next = pending.reverse().concat(frames.value).slice(0, MAX_FRAMES)
  pending = []
  frames.value = next

  // Forget expanded rows that dropped off the list
  const keys = new Set(next.map((f) => f._key))
  for (const key of Object.keys(expanded_frames.value)) {
    if (!keys.has(Number(key))) {
      delete expanded_frames.value[key]
    }
  }
}

function togglePause() {
  paused.value = !paused.value
  if (!paused.value) {
    flushFrames()
  }
}

function clearFrames() {
  pending = []
  frames.value = []
  expanded_frames.value = {}
  received_count = 0
  received.value = 0
}

useEventStream({frame: addFrame})

// /rawframe?dst=<node id> (link from Nodes) pre-fills a unicast frame to that node
const route = useRoute()
const dst = Number(route.query.dst)
if (route.query.dst !== undefined && Number.isInteger(dst) && dst >= 0 && dst <= ID_MAX) {
  if (isBroadcast(frame.value.type)) {
    frame.value.type = 11  // GET_REG
  }
  frame.value.destination_id = dst
}

onMounted(async () => {
  await axios
      .get('/api/frames')
      .then(response => {
        response.data.response.forEach(addFrame)
        flushFrames()
      }).catch(function (error) {
        toasts.value.push({
          title: 'Refresh frames',
          content: error
        })
      })
})

onBeforeUnmount(() => {
  clearTimeout(flush_timer)
})

function clean_frame() {
  frame.value.type = 11;
  frame.value.flags = 0;
  frame.value.seqnum = 0;
  frame.value.destination_id = 0;
  frame.value.source_id = 0;
  frame.value.broadcast_group = 0;
  group_all.value = false;
  frame.value.dlc = 0;
  for (let i = 0; i < 8; i++) {
    frame.value.data[i] = null;
  }
}

// Form inputs give strings - returns the integer, or null when it is not a number in [0, max]
function toInt(value, max) {
  const n = typeof (value) === "number" ? value : parseInt(value)
  return Number.isInteger(n) && n >= 0 && n <= max ? n : null
}

async function send_frame() {
  let i = 0;

  const f = frame.value
  const type = toInt(f.type, TYPE_MAX)

  for (i = 0; i < 8; i++) {
    const tmp = toInt(f.data[i], 255)
    if (tmp === null)
      break;
    f.data[i] = tmp;
  }
  const dlc = i;
  for (; i < 8; i++) {
    f.data[i] = null;
  }

  // h9d picks the fields by frame kind, so send only the ones that apply
  const payload = {type: type, dlc: dlc, data: f.data.slice(0, dlc)}
  if (isBroadcast(type)) {
    payload.broadcast_group = group_all.value ? BROADCAST_ALL_GROUP : toInt(f.broadcast_group, GROUP_MAX)
  } else {
    payload.flags = toInt(f.flags, FLAGS_MAX)
    payload.destination_id = toInt(f.destination_id, ID_MAX)
    if (raw_frame.value)
      payload.seqnum = toInt(f.seqnum, SEQNUM_MAX)
  }
  if (raw_frame.value)
    payload.source_id = toInt(f.source_id, ID_MAX)

  const invalid = Object.keys(payload).filter((k) => payload[k] === null)
  if (invalid.length) {
    toasts.value.push({
      title: 'Send frame',
      content: 'Invalid value: ' + invalid.join(', ')
    })
    return
  }

  await axios.post('/api/frames', {frame: payload, raw: raw_frame.value}, {headers: {'Content-Type': 'application/json'}})
      .catch(function (error) {
        toasts.value.push({
          title: 'Send frame',
          content: error
        })
      })

}


function copyFrame(f) {
  frame.value.type = f.type;
  frame.value.source_id = f.source_id;
  if (isBroadcast(f.type)) {
    group_all.value = f.broadcast_group === BROADCAST_ALL_GROUP;
    frame.value.broadcast_group = group_all.value ? 0 : f.broadcast_group;
  } else {
    frame.value.flags = f.flags;
    frame.value.seqnum = f.seqnum;
    frame.value.destination_id = f.destination_id;
  }
  frame.value.dlc = f.dlc;
  for (let i = 0; i < 8; i++) {
    frame.value.data[i] = i < f.dlc ? f.data[i] : null;
  }
}

function frameDetails(f) {
  const {_key, ...rest} = f
  return JSON.stringify(rest)
}

function originName(origin) {
  return origin.indexOf('@') !== -1 ? origin.substring(0, origin.indexOf('@')) : origin
}

function toggleFrameDetails(f) {
  if (expanded_frames.value[f._key]) {
    delete expanded_frames.value[f._key]
  } else {
    expanded_frames.value[f._key] = true
  }
}

</script>

<template>
  <div class="page">
    <Card>
      <template #content>
        <form class="frame-form" @submit.prevent="send_frame">
          <div class="field">
            <label for="inputType">Type</label>
            <Select inputId="inputType" v-model="frame.type" :options="frame_type_groups" optionGroupLabel="label"
                    optionGroupChildren="items" optionLabel="text" optionValue="value" size="small" scrollHeight="80vh"
                    filter autoFilterFocus resetFilterOnHide filterPlaceholder="Search type"
                    overlayClass="type-select-overlay" class="type-select"/>
          </div>
          <div class="field">
            <label for="inputSource">Source</label>
            <InputText id="inputSource" :disabled="!raw_frame" size="small" maxlength="3" class="num"
                       v-model="frame.source_id"/>
          </div>
          <template v-if="!is_broadcast">
            <div class="field">
              <label for="inputDestination">Destination</label>
              <InputText id="inputDestination" size="small" maxlength="3" class="num" v-model="frame.destination_id"/>
            </div>
            <div class="field">
              <label for="inputFlags">Flags</label>
              <Select inputId="inputFlags" v-model="frame.flags" :options="frame_flags" optionLabel="label"
                      optionValue="value" size="small"/>
            </div>
            <div class="field">
              <label for="inputSeqnum">Seqnum</label>
              <InputText id="inputSeqnum" :disabled="!raw_frame" size="small" maxlength="2" class="num"
                         v-model="frame.seqnum"/>
            </div>
          </template>
          <div v-else class="field">
            <label for="inputGroup" v-tooltip.top="'Broadcast group - node type'">Group</label>
            <InputGroup class="group-input">
              <InputText id="inputGroup" :disabled="group_all" size="small" maxlength="5" v-model="frame.broadcast_group"/>
              <InputGroupAddon>
                <label class="check">
                  <Checkbox inputId="group_all_checkbox" v-model="group_all" binary size="small"/>
                  All
                </label>
              </InputGroupAddon>
            </InputGroup>
          </div>
          <div class="field">
            <label>Data</label>
            <div class="data-inputs">
              <InputText v-for="i in 8" :key="i" :name="'data[' + (i - 1) + ']'" size="small" maxlength="4"
                         v-model="frame.data[i - 1]"/>
            </div>
          </div>
          <div class="form-actions">
            <label class="check" v-tooltip.top="'Allows to set the source (and seqnum for unicast)'">
              <Checkbox inputId="raw_checkbox" v-model="raw_frame" binary/>
              Raw frame
            </label>
            <Button type="button" label="Clean" severity="secondary" @click="clean_frame"/>
            <Button type="submit" label="Send frame"/>
          </div>
        </form>
      </template>
    </Card>
    <Card>
      <template #content>
        <div class="toolbar frames-toolbar">
          <Button :label="paused ? 'Resume' : 'Pause'" :icon="paused ? 'pi pi-play' : 'pi pi-pause'" size="small"
                  :severity="paused ? undefined : 'secondary'" @click="togglePause"/>
          <Button label="Clear" icon="pi pi-trash" size="small" severity="secondary" @click="clearFrames"/>
          <span class="muted">
            {{ received }} received<template v-if="received > MAX_FRAMES">, last {{ MAX_FRAMES }} shown</template>
            <template v-if="paused"> · paused</template>
          </span>
        </div>
        <!-- Plain table, not DataTable: it is re-rendered several times a second under heavy traffic.
             One <tbody> per frame with v-memo, so rows already on screen are not re-rendered. -->
        <div class="frames-scroll">
          <table class="frames">
            <thead>
            <tr>
              <th>Origin</th>
              <th>Src</th>
              <th>Dst / Group</th>
              <th>Type</th>
              <th>Flags</th>
              <th>Seqnum</th>
              <th>Data</th>
              <th>Action</th>
            </tr>
            </thead>
            <tbody v-for="f in frames" :key="f._key" v-memo="[f, !!expanded_frames[f._key]]">
            <tr>
              <td>{{ originName(f.origin) }}</td>
              <td>{{ f.source_id }}</td>
              <td>
                <span v-if="isBroadcast(f.type)" class="group-tag" title="Broadcast group">{{ groupLabel(f.broadcast_group) }}</span>
                <template v-else>{{ f.destination_id }}</template>
              </td>
              <td>{{ typeLabel(f.type) }}</td>
              <td>{{ isBroadcast(f.type) ? '' : flagsLabel(f.flags) }}</td>
              <td>{{ f.seqnum }}</td>
              <td>[ {{ f.data.join(', ') }} ]</td>
              <td class="actions">
                <button type="button" class="row-btn" @click="copyFrame(f)">Copy</button>
                <button type="button" class="row-btn" :class="{ active: expanded_frames[f._key] }"
                        @click="toggleFrameDetails(f)">Details
                </button>
              </td>
            </tr>
            <tr v-if="expanded_frames[f._key]" class="details">
              <td colspan="8">
                <div>
                  <span class="label">Origin: </span>{{ f.origin }}
                </div>
                <div>
                  <span class="label">Frame: </span><code>{{ frameDetails(f) }}</code>
                </div>
              </td>
            </tr>
            </tbody>
          </table>
          <p v-if="!frames.length" class="muted empty">No frames yet.</p>
        </div>
      </template>
    </Card>
  </div>
</template>

<style scoped>
.frame-form {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: flex-start;
}

.field {
  display: flex;
  flex-direction: column;
  gap: .35rem;
}

.field > label {
  font-size: .9rem;
}

.type-select {
  width: 17rem;
}

.num {
  width: 6rem;
}

.group-input {
  width: 11rem;
}

.data-inputs {
  display: flex;
}

.data-inputs .p-inputtext {
  width: 3.2rem;
  border-radius: 0;
}

.data-inputs .p-inputtext:first-child {
  border-radius: 6px 0 0 6px;
}

.data-inputs .p-inputtext:last-child {
  border-radius: 0 6px 6px 0;
}

.data-inputs .p-inputtext + .p-inputtext {
  margin-left: -1px;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: .75rem;
  margin-left: auto;
  align-self: flex-end;
}

.check {
  display: flex;
  align-items: center;
  gap: .4rem;
  cursor: pointer;
}

.label {
  font-weight: 600;
}

.frames-toolbar {
  margin-bottom: .75rem;
}

.frames-scroll {
  max-height: 65vh;
  overflow: auto;
}

.frames {
  width: 100%;
  border-collapse: collapse;
  font-size: .9rem;
  font-variant-numeric: tabular-nums;
}

.frames th {
  position: sticky;
  top: 0;
  z-index: 1;
  padding: .55rem .75rem;
  background: var(--app-surface);
  border-bottom: 1px solid var(--app-border);
  text-align: left;
  font-weight: 600;
  white-space: nowrap;
}

.frames td {
  padding: .4rem .75rem;
  border-bottom: 1px solid var(--app-border);
  white-space: nowrap;
}

.frames tbody:nth-of-type(even) > tr:first-child {
  background: color-mix(in srgb, var(--app-text) 3%, transparent);
}

.frames tr.details td {
  white-space: normal;
}

.group-tag {
  display: inline-block;
  min-width: 1.6rem;
  padding: .05rem .45rem;
  border-radius: 6px;
  background: color-mix(in srgb, var(--p-sky-500) 18%, transparent);
  color: var(--p-sky-400);
  font-size: .8rem;
  font-weight: 700;
  text-align: center;
}

.actions {
  display: flex;
  gap: 1px;
}

.row-btn {
  padding: .25rem .6rem;
  border: none;
  background: color-mix(in srgb, var(--app-text) 8%, transparent);
  color: var(--app-text);
  font: inherit;
  font-size: .8rem;
  cursor: pointer;
}

.row-btn:first-child {
  border-radius: 6px 0 0 6px;
}

.row-btn:last-child {
  border-radius: 0 6px 6px 0;
}

.row-btn:hover,
.row-btn.active {
  background: color-mix(in srgb, var(--app-text) 16%, transparent);
}

.empty {
  margin: 1rem 0 0;
}
</style>

<style>
/* The type list is long (32 types) - compact rows so it fits without scrolling.
   Not scoped: the overlay is teleported to <body>. */
.type-select-overlay .p-select-option {
  padding: .2rem .75rem;
  font-size: .9rem;
}

.type-select-overlay .p-select-option-group {
  padding: .35rem .75rem .15rem;
  font-size: .8rem;
}
</style>
