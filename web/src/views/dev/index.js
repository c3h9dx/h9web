import {defineAsyncComponent} from 'vue'

// Dashboard widget for each h9d device type (the "type" in h9d get_devs_list).
// A widget gets one prop, `dev`: {name, type, methods, state, events}
// (events: the last event of each event_name, for devices that tag their events).
export const widgets = {
  PowerSwitch: {
    title: 'Power Switch',
    component: defineAsyncComponent(() => import('./PowerSwitch.vue')),
  },
  AntennaSwitch: {
    title: 'Antenna Switch',
    component: defineAsyncComponent(() => import('./AntennaSwitch.vue')),
  },
  'S-Match': {
    title: 'S-Match ATU',
    component: defineAsyncComponent(() => import('./SMatch.vue')),
  },
}

// For device types without a widget of their own
export const unknownWidget = {
  title: 'Device',
  component: defineAsyncComponent(() => import('./UnknownDev.vue')),
}
