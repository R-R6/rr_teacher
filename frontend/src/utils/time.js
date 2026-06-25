export function parseDateTimeString(dateStr) {
  if (!dateStr) return null
  if (dateStr instanceof Date) return dateStr

  const normalized = String(dateStr).trim()
  if (!normalized) return null

  // 带时区的 ISO 串(含 Z、+08:00 等)交给引擎按 UTC 正确换算为本地。
  // 例:'2026-06-06T15:35:10.848662Z' / '2026-06-06T15:35:10+08:00'
  if (/[zZ]$/.test(normalized) || /[+-]\d{2}:\d{2}$/.test(normalized)) {
    return new Date(normalized)
  }

  // 无时区串(后端 naive datetime):用本地时间组件构造,避免:
  //  1) 'YYYY-MM-DD HH:mm:ss' 在 Safari/iOS WebKit 上 new Date() 返回 Invalid Date;
  //  2) 个别引擎把无时区串当 UTC,导致本地读出多 8 小时。
  // 同时兼容空格与 T 两种分隔符。
  const matched = normalized.match(
    /^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?$/
  )
  if (matched) {
    const [, year, month, day, hour, minute, second, fractionRaw = '0'] = matched
    const millisecond = Number((fractionRaw + '000').slice(0, 3))
    return new Date(
      Number(year),
      Number(month) - 1,
      Number(day),
      Number(hour),
      Number(minute),
      Number(second),
      millisecond
    )
  }

  // 其他可被引擎解析的格式(如纯日期、已带时区但未命中上面分支的)
  return new Date(normalized)
}

export function formatRelativeTime(dateStr, now = new Date()) {
  const d = parseDateTimeString(dateStr)
  if (!(d instanceof Date) || Number.isNaN(d.getTime())) return ''

  const diff = now - d
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 2592000000) return `${Math.floor(diff / 86400000)}天前`

  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}
