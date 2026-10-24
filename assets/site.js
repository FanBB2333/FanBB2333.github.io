// Hand-drawn outlines for [data-sketch] elements (after the course notebook's sketch.js),
// the paper / chalkboard toggle, copy buttons and "updated 3 days ago" dates.
// Every page load picks new random seeds, so each visit is drawn a little differently;
// the seed is kept per element, so a resize redraws the same strokes.
;(() => {
  const NS = 'http://www.w3.org/2000/svg'
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  let clipCount = 0

  // mulberry32
  function makeRandom(seed) {
    return () => {
      seed = (seed + 0x6d2b79f5) | 0
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed)
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296
    }
  }
  const r1 = (v) => Math.round(v * 10) / 10

  // One wobbly stroke from (x1, y1) to (x2, y2): the ends overshoot a little and the middle bows sideways.
  function stroke(x1, y1, x2, y2, wobble, rand) {
    const jit = (k) => (rand() * 2 - 1) * k
    const len = Math.hypot(x2 - x1, y2 - y1) || 1
    const ux = (x2 - x1) / len, uy = (y2 - y1) / len
    const px = -uy, py = ux
    const o1 = rand() * wobble * 1.8, o2 = rand() * wobble * 1.8
    const ax = x1 - ux * o1 + px * jit(wobble), ay = y1 - uy * o1 + py * jit(wobble)
    const bx = x2 + ux * o2 + px * jit(wobble), by = y2 + uy * o2 + py * jit(wobble)
    const bow = Math.min(len / 80, 1.2) * wobble
    const t1 = 0.3 + jit(0.08), t2 = 0.7 + jit(0.08)
    const b1 = jit(bow), b2 = jit(bow)
    const c1x = ax + (bx - ax) * t1 + px * b1, c1y = ay + (by - ay) * t1 + py * b1
    const c2x = ax + (bx - ax) * t2 + px * b2, c2y = ay + (by - ay) * t2 + py * b2
    return `M${r1(ax)} ${r1(ay)} C${r1(c1x)} ${r1(c1y)} ${r1(c2x)} ${r1(c2y)} ${r1(bx)} ${r1(by)}`
  }

  // Catmull-Rom spline through the points, as cubic Béziers.
  function smooth(p) {
    let d = `M${r1(p[0][0])} ${r1(p[0][1])}`
    for (let i = 0; i < p.length - 1; i++) {
      const p0 = p[i - 1] || p[i], p1 = p[i], p2 = p[i + 1], p3 = p[i + 2] || p2
      d += ` C${r1(p1[0] + (p2[0] - p0[0]) / 6)} ${r1(p1[1] + (p2[1] - p0[1]) / 6)}`
      d += ` ${r1(p2[0] - (p3[0] - p1[0]) / 6)} ${r1(p2[1] - (p3[1] - p1[1]) / 6)} ${r1(p2[0])} ${r1(p2[1])}`
    }
    return d
  }

  // A pen loop around the box that overshoots its start instead of closing neatly.
  function loop(w, h, rand) {
    const cx = w / 2, cy = h / 2, rx = w / 2 + 9, ry = h / 2 + 3
    const start = -Math.PI * (0.6 + rand() * 0.25)
    const sweep = Math.PI * 2 * (1.07 + rand() * 0.06)
    const pts = []
    for (let i = 0; i <= 16; i++) {
      const t = i / 16
      const a = start + sweep * t
      const k = 1 + (rand() * 2 - 1) * 0.045 + t * 0.07
      pts.push([cx + Math.cos(a) * rx * k, cy + Math.sin(a) * ry * k])
    }
    return smooth(pts)
  }

  // Diagonal pencil shading in the L-shaped band below and right of a w×h box.
  function hatch(w, h, ox, oy, rand) {
    const lines = []
    for (let c = Math.min(w, h) - 4; c < w + h + ox + oy + 4; c += 6.5) {
      const top = -2, bottom = h + oy + 2
      lines.push(`M${r1(c - bottom + rand() * 1.2)} ${bottom} L${r1(c - top + rand() * 1.2)} ${top}`)
    }
    const band = `M${w} ${oy} H${w + ox} V${h + oy} H${ox} V${h} H${w} Z`
    return { d: lines.join(' '), band }
  }

  function draw(el) {
    const w = el.offsetWidth, h = el.offsetHeight
    if (!w || !h) return
    if (w === el._w && h === el._h && el._svg) return
    el._w = w
    el._h = h
    el._seed ??= Math.floor(Math.random() * 2 ** 31)
    const rand = makeRandom(el._seed)
    const kind = el.dataset.sketch
    const wobble = parseFloat(el.dataset.sketchWobble) || 1.6
    const shadow = el.hasAttribute('data-sketch-shadow')
    const pad = 16, ox = 9, oy = 10

    const svg = el._svg || document.createElementNS(NS, 'svg')
    const W = w + pad * 2 + (shadow ? ox : 0), H = h + pad * 2 + (shadow ? oy : 0)
    svg.setAttribute('class', 'sketch-svg' + (reduceMotion || el._revealed ? '' : ' animate'))
    svg.setAttribute('aria-hidden', 'true')
    svg.setAttribute('focusable', 'false')
    svg.setAttribute('width', W)
    svg.setAttribute('height', H)
    svg.setAttribute('viewBox', `${-pad} ${-pad} ${W} ${H}`)
    // absolute offsets are measured from the padding box, so step back over the border too
    svg.style.left = `${-pad - el.clientLeft}px`
    svg.style.top = `${-pad - el.clientTop}px`

    let html = ''
    const path = (d, cls, width, delay, dur) =>
      `<path d="${d}" class="${cls}" stroke-width="${width}" pathLength="1" style="--delay:${delay}s;--dur:${dur}s"/>`
    if (shadow) {
      const id = `sketch-clip-${++clipCount}`
      const { d, band } = hatch(w, h, ox, oy, rand)
      html += `<clipPath id="${id}"><path d="${band}"/></clipPath>`
      html += `<g clip-path="url(#${id})">${path(d, 'hatch', 1, 0.9, 0.6)}</g>`
    }
    if (kind === 'circle') {
      html += path(loop(w, h, rand), 'pass-1', 1.7, 0.1, 0.6)
    } else {
      const sides = [[0, 0, w, 0], [w, 0, w, h], [w, h, 0, h], [0, h, 0, 0]]
      const scale = Math.min(1, (w + h) / 900)
      sides.forEach(([x1, y1, x2, y2], i) => {
        html += path(stroke(x1, y1, x2, y2, wobble, rand), 'pass-1', 1.7, i * 0.16 * (0.5 + scale), 0.3)
      })
      sides.forEach(([x1, y1, x2, y2], i) => {
        html += path(stroke(x1, y1, x2, y2, wobble * 0.9, rand), 'pass-2', 1.1, 0.45 + i * 0.12, 0.28)
      })
    }
    svg.innerHTML = html
    if (!el._svg) {
      el.prepend(svg)
      el._svg = svg
    }
  }

  function reveal(el) {
    el._revealed = true
    if (!el._svg) return
    el._svg.getBoundingClientRect() // flush the undrawn state so the transition runs
    el._svg.classList.add('drawn')
  }

  function start() {
    const els = [...document.querySelectorAll('[data-sketch]')]
    const io = 'IntersectionObserver' in window && !reduceMotion
      ? new IntersectionObserver((entries) => {
          for (const e of entries) {
            if (e.isIntersecting) {
              reveal(e.target)
              io.unobserve(e.target)
            }
          }
        }, { threshold: 0.25 })
      : null
    const ro = 'ResizeObserver' in window ? new ResizeObserver((entries) => entries.forEach((e) => draw(e.target))) : null
    for (const el of els) {
      draw(el)
      if (io) io.observe(el)
      else el._revealed = true
      ro?.observe(el)
    }
  }

  // Wait for the webfonts so the first drawing already has the final sizes.
  const fontsReady = document.fonts ? Promise.race([document.fonts.ready, new Promise((r) => setTimeout(r, 1500))]) : Promise.resolve()
  fontsReady.then(start)

  // Paper / chalkboard toggle
  const root = document.documentElement
  const btn = document.getElementById('theme-toggle')
  const label = btn?.querySelector('.theme-label')
  const meta = document.querySelector('meta[name="theme-color"]')
  const dark = window.matchMedia('(prefers-color-scheme: dark)')
  const current = () => root.dataset.theme || (dark.matches ? 'dark' : 'light')
  function sync() {
    const isDark = current() === 'dark'
    if (label) label.textContent = isDark ? 'Paper' : 'Chalkboard'
    btn?.setAttribute('title', isDark ? 'Switch to the paper colors' : 'Switch to the chalkboard colors')
    meta?.setAttribute('content', isDark ? '#1d2a26' : '#f5f2e9')
  }
  btn?.addEventListener('click', () => {
    const next = current() === 'dark' ? 'light' : 'dark'
    root.dataset.theme = next
    try {
      localStorage.setItem('l1ght-home:theme', next)
    } catch {}
    sync()
  })
  dark.addEventListener?.('change', sync)
  sync()

  // Copy buttons next to install commands
  for (const b of document.querySelectorAll('.copy')) {
    b.addEventListener('click', async () => {
      const code = b.previousElementSibling
      try {
        await navigator.clipboard.writeText(code.textContent)
        b.textContent = 'Copied'
        b.dataset.done = ''
      } catch {
        // no clipboard access: select the command so it can be copied by hand
        const range = document.createRange()
        range.selectNodeContents(code)
        getSelection()?.removeAllRanges()
        getSelection()?.addRange(range)
        b.textContent = 'Selected'
      }
      clearTimeout(b._t)
      b._t = setTimeout(() => {
        b.textContent = 'Copy'
        delete b.dataset.done
      }, 1600)
    })
  }

  // <time data-ago datetime="2026-10-13"> -> "2 days ago" (the date itself moves to the tooltip)
  const DAY = 86400000
  function ago(iso) {
    const days = Math.floor((Date.now() - new Date(iso).getTime()) / DAY)
    if (!(days >= 0)) return null
    if (days === 0) return 'today'
    if (days === 1) return 'yesterday'
    if (days < 30) return `${days} days ago`
    const months = Math.round(days / 30.4)
    if (months < 12) return months <= 1 ? 'a month ago' : `${months} months ago`
    const years = Math.round(days / 365)
    return years <= 1 ? 'a year ago' : `${years} years ago`
  }
  for (const t of document.querySelectorAll('time[data-ago]')) {
    const text = ago(t.dateTime)
    if (!text) continue
    t.title = t.dateTime
    t.textContent = text
  }

  // Live star counts from one public GitHub API call (60 per hour per visitor without a token).
  // If it fails or hits the limit, the numbers baked in at build time stay.
  const owner = document.body.dataset.github
  const stars = [...document.querySelectorAll('.star[data-repo]')]
  async function liveStars() {
    const counts = new Map()
    for (let page = 1; page <= 3; page++) {
      const r = await fetch(`https://api.github.com/users/${owner}/repos?per_page=100&page=${page}`)
      if (!r.ok) return
      const batch = await r.json()
      for (const repo of batch) counts.set(repo.name, repo.stargazers_count)
      if (batch.length < 100) break
    }
    let total = 0
    for (const li of stars) {
      const n = counts.get(li.dataset.repo)
      if (n !== undefined) li.textContent = n
      total += Number(li.textContent) || 0
    }
    const sum = document.querySelector('[data-stars-total]')
    if (sum) sum.textContent = total
    const note = document.getElementById('sync-note')
    if (note?.dataset.live) note.textContent = note.dataset.live
  }
  if (owner && stars.length) liveStars().catch(() => {})
})()
