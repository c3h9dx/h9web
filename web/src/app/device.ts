export interface Device {
  id: number;
  name: string;
}

export interface DevRegister {
  number: number;
  name: string;
  type: string;
  size: number;
  readable: boolean;
  writable: boolean;
  bits_names: string[];
  description: string;
  value: number|number[]|string|undefined;
}

export interface DeviceInfo {
  id: number;
  type: number,
  version_major: number,
  version_minor: number,
  version_patch: number,
  name: string,
  created_time: number,
  last_seen_time: number,
  description: string,
  registers_list: DevRegister[]
}
