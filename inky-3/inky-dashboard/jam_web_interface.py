from flask import Flask, request, render_template_string
from modules.spotify_connect import JAM_PATH
import logging

app = Flask(__name__)

HTML = """
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Set Spotify Jam Link</title>
    <style>
      :root {
        --bg: #0f172a;
        --card: #111827;
        --muted: #94a3b8;
        --text: #e5e7eb;
        --accent: #22d3ee;
        --accent2: #a78bfa;
        --success: #34d399;
        --danger: #f87171;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0; min-height: 100vh; display: grid; place-items: center;
        background: radial-gradient(1000px 800px at 10% 10%, rgba(34,211,238,.1), transparent),
                    radial-gradient(900px 700px at 90% 90%, rgba(167,139,250,.1), transparent),
                    var(--bg);
        color: var(--text); font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial;
      }
      .card {
        width: min(520px, 92vw); padding: 28px 24px; border-radius: 16px; background: linear-gradient(180deg, #0b1220 0%, #0b1220ee 100%);
        border: 1px solid #1f2937; box-shadow: 0 20px 60px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.03);
      }
      h1 { font-size: 22px; margin: 0 0 12px; letter-spacing: .2px; }
      p.sub { margin: 0 0 20px; color: var(--muted); font-size: 14px; }
      .actions { display: grid; gap: 12px; margin-top: 10px; }
      .btn {
        appearance: none; border: 0; cursor: pointer; display: inline-flex; align-items: center; justify-content: center;
        gap: 10px; padding: 16px 18px; border-radius: 12px; font-weight: 600; color: #0b1220; font-size: 16px;
        transition: transform .08s ease, box-shadow .2s ease, background .2s ease;
      }
      .btn:active { transform: translateY(1px); }
      .btn-primary {
        background: linear-gradient(135deg, var(--accent), var(--accent2));
        box-shadow: 0 8px 24px rgba(34,211,238,.25), 0 8px 24px rgba(167,139,250,.25);
      }
      .btn-secondary { background: #1f2937; color: var(--text); border: 1px solid #273244; }
      .hint { color: var(--muted); font-size: 13px; text-align: center; }
      .msg { margin-top: 16px; text-align: center; font-weight: 600; }
      .msg.ok { color: var(--success); }
      .msg.err { color: var(--danger); }
      .hidden { display: none; }
      input[type="text"] { width: 100%; padding: 14px 14px; border-radius: 10px; border: 1px solid #273244; background: #0b1220; color: var(--text); font-size: 15px; }
      .divider { height: 1px; background: #1f2937; margin: 12px 0; }
    </style>
  </head>
  <body>
    <div class=\"card\">
      <h1>Spotify Jam link</h1>
      <p class=\"sub\">Paste from clipboard and save with one tap. Works best in modern browsers. If paste access is blocked, use the manual fallback.</p>

      <form id=\"jamForm\" method=\"post\" class=\"hidden\">
        <input id=\"jam_url\" name=\"jam_url\" type=\"text\" autocomplete=\"off\" />
      </form>

      <div class=\"actions\">
        <button id=\"pasteBtn\" class=\"btn btn-primary\" type=\"button\">📋 Paste & Save</button>
        <button id=\"manualBtn\" class=\"btn btn-secondary\" type=\"button\">✍️ Paste Manually</button>
      </div>

      <div id=\"manualWrap\" class=\"hidden\" style=\"margin-top:12px\"> 
        <input id=\"manualInput\" type=\"text\" placeholder=\"Tap here and Paste…\" />
        <div class=\"hint\" style=\"margin-top:8px\">After paste, it will auto-save.</div>
      </div>

      {% if message %}
        <div class=\"msg ok\">{{ message }}</div>
      {% endif %}
    </div>

    <script>
      const jamInput = document.getElementById('jam_url');
      const jamForm = document.getElementById('jamForm');
      const pasteBtn = document.getElementById('pasteBtn');
      const manualBtn = document.getElementById('manualBtn');
      const manualWrap = document.getElementById('manualWrap');
      const manualInput = document.getElementById('manualInput');

      async function pasteAndSave() {
        try {
          if (navigator.clipboard && navigator.clipboard.readText) {
            const text = (await navigator.clipboard.readText())?.trim();
            if (text) {
              jamInput.value = text;
              jamForm.submit();
              return;
            }
          }
          // Fallback: show manual field
          manualWrap.classList.remove('hidden');
          manualInput.focus();
        } catch (e) {
          manualWrap.classList.remove('hidden');
          manualInput.focus();
        }
      }

      // Auto-submit when user pastes into the manual field
      manualInput.addEventListener('paste', (e) => {
        setTimeout(() => {
          const txt = manualInput.value.trim();
          if (txt) {
            jamInput.value = txt;
            jamForm.submit();
          }
        }, 0);
      });

      pasteBtn.addEventListener('click', pasteAndSave);
      manualBtn.addEventListener('click', () => {
        manualWrap.classList.remove('hidden');
        manualInput.focus();
      });
    </script>
  </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    if request.method == "POST":
        jam_url = request.form["jam_url"].strip()
        if jam_url:
            JAM_PATH.write_text(jam_url)
            message = "Jam-link lagret!"
        else:
            message = "Vennligst skriv inn en gyldig lenke."
    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
    app.run(host="0.0.0.0", port=5000)
