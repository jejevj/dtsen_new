/**
 * useViewGuard — View-Only Protection
 *
 * Diaktifkan via VITE_VIEW_ONLY=true di .env
 * Berlaku global saat dipanggil sekali dari main.js
 *
 * Yang dilindungi:
 *  - Klik kanan (contextmenu)
 *  - Text selection (user-select: none via CSS + selectstart event)
 *  - Drag & drop elemen
 *  - Keyboard shortcuts DevTools:
 *      F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C, Ctrl+U (view source)
 *  - DevTools console detection (debugger trap loop)
 *
 * Toast bridge:
 *  Karena composable ini dijalankan sebelum app Vue di-mount,
 *  toast PrimeVue tidak bisa dipanggil langsung.
 *  Solusi: dispatch CustomEvent 'vg:blocked' yang ditangkap oleh App.vue.
 */

function dispatchBlocked(message) {
  window.dispatchEvent(new CustomEvent('vg:blocked', { detail: { message } }))
}

export function initViewGuard() {
  const enabled = import.meta.env.VITE_VIEW_ONLY === 'true'
  if (!enabled) return

  // 1. Disable klik kanan
  document.addEventListener('contextmenu', (e) => {
    e.preventDefault()
    dispatchBlocked('Klik kanan tidak diizinkan pada halaman ini.')
  }, true)

  // 2. Disable text selection via event
  document.addEventListener('selectstart', (e) => {
    e.preventDefault()
  }, true)

  // 3. Disable drag
  document.addEventListener('dragstart', (e) => {
    e.preventDefault()
    dispatchBlocked('Fitur drag tidak diizinkan pada halaman ini.')
  }, true)

  // 4. Inject CSS: user-select none + cursor default pada seluruh halaman
  const style = document.createElement('style')
  style.id = 'view-guard-style'
  style.textContent = `
    *, *::before, *::after {
      -webkit-user-select: none !important;
      -moz-user-select: none !important;
      -ms-user-select: none !important;
      user-select: none !important;
    }
    input, textarea, [contenteditable="true"] {
      -webkit-user-select: text !important;
      user-select: text !important;
    }
  `
  document.head.appendChild(style)

  // 5. Blokir keyboard shortcuts DevTools & View Source
  document.addEventListener('keydown', (e) => {
    const ctrl  = e.ctrlKey || e.metaKey
    const shift = e.shiftKey
    const key   = e.key

    // F12
    if (key === 'F12') {
      e.preventDefault()
      dispatchBlocked('Akses Developer Tools tidak diizinkan.')
      return
    }

    // Ctrl+Shift+I / Ctrl+Shift+J / Ctrl+Shift+C (Chrome DevTools)
    if (ctrl && shift && ['i','I','j','J','c','C'].includes(key)) {
      e.preventDefault()
      dispatchBlocked('Akses Developer Tools tidak diizinkan.')
      return
    }

    // Ctrl+U (View Page Source)
    if (ctrl && ['u','U'].includes(key)) {
      e.preventDefault()
      dispatchBlocked('Melihat sumber halaman tidak diizinkan.')
      return
    }

    // Ctrl+S (Save page)
    if (ctrl && ['s','S'].includes(key)) {
      e.preventDefault()
      dispatchBlocked('Menyimpan halaman tidak diizinkan.')
      return
    }
  }, true)

  // 6. DevTools open detection via debugger trap
  //    Saat DevTools terbuka, debugger statement menyebabkan delay terdeteksi
  //    dan halaman akan ditampilkan overlay peringatan.
  ;(function devtoolsDetect() {
    let devtoolsOpen = false
    const threshold  = 160 // ms

    function check() {
      const start = performance.now()
      // eslint-disable-next-line no-debugger
      debugger
      const delta = performance.now() - start

      if (delta > threshold) {
        if (!devtoolsOpen) {
          devtoolsOpen = true
          dispatchBlocked('Developer Tools terdeteksi terbuka. Tutup untuk melanjutkan.')
          showDevtoolsWarning()
        }
      } else {
        if (devtoolsOpen) {
          devtoolsOpen = false
          hideDevtoolsWarning()
        }
      }
      requestAnimationFrame(check)
    }

    requestAnimationFrame(check)
  })()
}

// ── Overlay peringatan saat DevTools terdeteksi terbuka ───────────────────────
function showDevtoolsWarning() {
  if (document.getElementById('devtools-warning')) return

  const overlay = document.createElement('div')
  overlay.id = 'devtools-warning'
  overlay.style.cssText = [
    'position:fixed', 'inset:0', 'z-index:2147483647',
    'background:rgba(1,105,111,0.97)',
    'display:flex', 'flex-direction:column',
    'align-items:center', 'justify-content:center',
    'font-family:system-ui,sans-serif',
    'color:#fff', 'text-align:center', 'padding:2rem',
  ].join(';')

  overlay.innerHTML = `
    <svg width="56" height="56" viewBox="0 0 24 24" fill="none" style="margin-bottom:1.5rem">
      <circle cx="12" cy="12" r="10" stroke="rgba(255,255,255,0.4)" stroke-width="1.5"/>
      <path d="M12 8v4M12 16h.01" stroke="white" stroke-width="2" stroke-linecap="round"/>
    </svg>
    <h2 style="font-size:1.25rem;font-weight:700;margin:0 0 0.5rem">Akses Dibatasi</h2>
    <p style="font-size:0.9rem;opacity:0.8;max-width:30ch;margin:0">
      Halaman ini tidak dapat diinspeksi.<br>
      Tutup Developer Tools untuk melanjutkan.
    </p>
  `

  document.body.appendChild(overlay)
}

function hideDevtoolsWarning() {
  document.getElementById('devtools-warning')?.remove()
}
