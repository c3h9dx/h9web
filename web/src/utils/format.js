// Date/time as yyyy-MM-dd HH:mm:ss in the browser's local time zone (h9d sends UTC ISO strings)
export function formatDateTime(value) {
  if (!value) {
    return '---'
  }
  const d = new Date(value)
  if (isNaN(d)) {
    return String(value)
  }
  const p = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
}
