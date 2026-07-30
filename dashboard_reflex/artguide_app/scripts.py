"""Small vanilla-JS helpers: live camera viewfinder and the custom audio player.

Camera helpers are parameterised by a video element id because the mobile and
desktop layouts both render (one hidden via CSS breakpoints) and would
otherwise collide on a shared id.
"""


# getUserMedia only exists in a secure context, so on a plain http:// page
# `navigator.mediaDevices` is undefined and the camera can never start -- the
# viewfinder just reports NotSupported. The origin answers on both http and
# https (Cloudflare does not redirect), and typing the bare domain on a phone
# lands on http, which is why this only ever bit mobile visitors. Redirect
# before anything else runs. localhost is itself a secure context and is
# excluded so `reflex run` keeps working over http.
FORCE_HTTPS = """
(function () {
  if (location.protocol !== 'http:') return;
  const h = location.hostname;
  if (h === 'localhost' || h === '127.0.0.1' || h === '::1' || h === '0.0.0.0') return;
  location.replace('https://' + location.host + location.pathname + location.search + location.hash);
})();
"""


def start_camera_script(
    video_id: str, auto: bool = False, visible_check_id: str | None = None
) -> str:
    """Start the rear-facing camera into the given <video id>.

    Resolves "" on success, otherwise the DOMException name (e.g.
    NotAllowedError, NotFoundError) so the UI can explain what went wrong.
    Note the browser only prompts once per origin: after a denial getUserMedia
    rejects immediately, which is why the refusal message has to tell the user
    to re-enable it from the address bar themselves.

    `auto=True` is for triggering the camera without a click (e.g. on page
    mount). The mobile and desktop viewfinders share the same DOM regardless
    of viewport (CSS just hides one), so an unconditional auto-start would
    also prompt desktop visitors for camera access too. Check `visible_check_id`
    (a breakpoint-controlled ancestor) rather than the video element itself:
    the video's own wrapper is hidden via `camera_on`-driven CSS, which is
    exactly false while we're trying to auto-start it, so it can't be used as
    the visibility signal. Resolves 'Skip' when hidden, which the caller must
    treat as a no-op.
    """
    check_id = visible_check_id or video_id
    skip_if_hidden = f"""
  const vis = document.getElementById('{check_id}');
  if (!vis || vis.offsetParent === null) return 'Skip';
""" if auto else ""
    return f"""
(async () => {{
  const v = document.getElementById('{video_id}');
  if (!v) return 'NoElement';
  {skip_if_hidden}
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
    return 'NotSupported';
  }}
  try {{
    // Release any previous stream so a retry gets a fresh one.
    if (v.__agStream) {{
      v.__agStream.getTracks().forEach(t => t.stop());
      v.__agStream = null;
    }}
    const stream = await navigator.mediaDevices.getUserMedia({{
      video: {{ facingMode: {{ ideal: 'environment' }} }}, audio: false
    }});
    v.__agStream = stream;
    v.srcObject = stream;
    await v.play();
    return '';
  }} catch (e) {{
    return (e && e.name) ? e.name : 'Error';
  }}
}})()
"""


def capture_script(video_id: str) -> str:
    """Grab a still frame, stop the stream, hand the data URL back to the State."""
    return f"""
(() => {{
  const v = document.getElementById('{video_id}');
  if (!v || !v.videoWidth) return '';
  const c = document.createElement('canvas');
  c.width = v.videoWidth;
  c.height = v.videoHeight;
  c.getContext('2d').drawImage(v, 0, 0);
  const data = c.toDataURL('image/jpeg', 0.9);
  if (v.__agStream) {{
    v.__agStream.getTracks().forEach(t => t.stop());
    v.__agStream = null;
  }}
  v.srcObject = null;
  return data;
}})()
"""


def stop_camera_script(video_id: str) -> str:
    return f"""
(() => {{
  const v = document.getElementById('{video_id}');
  if (v && v.__agStream) {{
    v.__agStream.getTracks().forEach(t => t.stop());
    v.__agStream = null;
  }}
  if (v) v.srcObject = null;
}})()
"""


def click_file_input_script(upload_id: str) -> str:
    """Programmatically open the native file picker for an rx.upload zone.

    Used instead of the upload zone's own click-to-open behaviour so that
    "choose file" and "use camera" can be two unambiguous, independent
    controls instead of both sharing one big clickable area.
    """
    return f"""
(() => {{
  const root = document.getElementById('{upload_id}');
  const input = root && root.querySelector('input[type=file]');
  if (input) input.click();
}})()
"""


# Custom audio player: play/pause toggle, remaining time, progress across the
# bars. Scoped per `.ag-player` container (via closest/querySelector) rather
# than global ids, since a hidden duplicate instance always exists on the
# other breakpoint (mobile vs desktop) and a global getElementById would
# silently grab the wrong — possibly invisible — one.
AUDIO_PLAYER = """
(function () {
  if (window.__agAudioInit) return;
  window.__agAudioInit = true;

  const fmt = (t) => {
    if (!isFinite(t) || t < 0) t = 0;
    const m = Math.floor(t / 60), s = Math.floor(t % 60);
    return m + ':' + String(s).padStart(2, '0');
  };

  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.ag-play');
    if (!btn) return;
    const root = btn.closest('.ag-player');
    const a = root && root.querySelector('audio');
    if (!a) return;
    a.paused ? a.play() : a.pause();
  });

  setInterval(() => {
    document.querySelectorAll('.ag-player').forEach((root) => {
      const a = root.querySelector('audio');
      if (!a) return;
      const dur = a.duration || 0, cur = a.currentTime || 0;

      const time = root.querySelector('.ag-time');
      if (time) time.textContent = fmt(dur ? dur - cur : 0);

      const tri = root.querySelector('.ag-tri');
      const pause = root.querySelector('.ag-pause');
      if (tri && pause) {
        tri.style.display = a.paused ? 'block' : 'none';
        pause.style.display = a.paused ? 'none' : 'flex';
      }

      const bars = root.querySelectorAll('.ag-bars > span');
      const wrap = root.querySelector('.ag-bars');
      if (wrap) wrap.classList.toggle('playing', !a.paused);

      const p = dur ? cur / dur : 0;
      bars.forEach((b, i) => {
        b.style.background = (i / bars.length) <= p
          ? (i % 3 === 2 ? '#c8341f' : '#1a1a1a')
          : 'rgba(0,0,0,.28)';
      });
    });
  }, 150);
})();
"""


# Scroll-reveal: fade/slide sections in, draw label underlines, subtle parallax.
# Re-scans on DOM mutations so it survives Reflex re-renders (e.g. language switch).
REVEAL = """
(function () {
  if (window.__agRevealInit) return;
  window.__agRevealInit = true;

  const SEL = '[data-r], [data-r-stagger], [data-clip], .reveal-lines';

  // Deterministic scroll-position check rather than IntersectionObserver: a
  // missed callback would leave a section stuck at opacity 0 forever.
  function reveal() {
    const vh = window.innerHeight;
    document.querySelectorAll(SEL).forEach((el) => {
      if (el.classList.contains('in')) return;
      const r = el.getBoundingClientRect();
      // Visible, or already scrolled past (covers fast scrolling and anchors).
      if (r.top < vh * 0.92 && r.bottom > -vh) el.classList.add('in');
    });
  }

  function parallax() {
    const vh = window.innerHeight;
    document.querySelectorAll('.prlx').forEach((el) => {
      const k = parseFloat(el.dataset.prlx || '.06');
      const r = el.getBoundingClientRect();
      const mid = r.top + r.height / 2 - vh / 2;
      el.style.transform = 'translate3d(0,' + (-mid * k).toFixed(1) + 'px,0)';
    });
  }

  let ticking = false;
  function onFrame() {
    ticking = false;
    reveal();
    parallax();
  }
  function schedule() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(onFrame);
  }

  schedule();
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule, { passive: true });
  new MutationObserver(schedule).observe(document.body, {
    childList: true, subtree: true,
  });
  // Safety net: never leave content invisible if something above misfires.
  setTimeout(() => document.querySelectorAll(SEL).forEach((el) => {
    const r = el.getBoundingClientRect();
    if (r.top < window.innerHeight) el.classList.add('in');
  }), 1200);
})();
"""
