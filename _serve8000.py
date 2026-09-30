import os, sys, time, socket, threading, traceback

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
HOST = "127.0.0.1"
PORT = 8000

os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

def out(m):
    try:
        sys.stdout.write(m + "\n")
        sys.stdout.flush()
    except Exception:
        pass

out("=" * 60)
out("  DEEPSHIELD AI - DJANGO SERVER (PORT 8000)")
out(f"  URL: http://{HOST}:{PORT}/")
out(f"  PID: {os.getpid()}")
out("=" * 60)

# === START HEARTBEAT THREAD FIRST TO ENSURE CONSTANT OUTPUT ===
HB = [True, False, False]  # [keep_alive, port_up, server_thread_alive]
def hb_loop():
    n = 0
    while HB[0]:
        time.sleep(1)
        n += 1
        try:
            s = socket.socket(); s.settimeout(0.3)
            pu = s.connect_ex((HOST, PORT)) == 0
            s.close()
        except:
            pu = False
        if pu and not HB[1]:
            HB[1] = True
            out("")
            out("=" * 60)
            out("  SERVER UP — READY FOR REQUESTS!")
            out(f"  Browse:  http://{HOST}:{PORT}/")
            out(f"  Or:      http://localhost:{PORT}/")
            out("=" * 60)
            # Quick HTTP smoke test
            try:
                import urllib.request
                req = urllib.request.Request(f"http://{HOST}:{PORT}/", method="GET")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    body = resp.read().decode(errors="replace")
                    import re as _re
                    tm = _re.search(r"<title>(.*?)</title>", body, _re.I | _re.S)
                    title = tm.group(1).strip() if tm else "(no <title>)"
                    out(f"  [http-smoke] GET / -> {resp.status} OK  bytes={len(body)}  title: {title}")
            except Exception as he:
                out(f"  [http-smoke] {type(he).__name__}: {he}")
            out("")
        out(f"  [HB n={n:>3}] port-{PORT}={'UP' if pu else 'BOOT'}  server-thread={'OK' if HB[2] else 'INIT'}")
hb = threading.Thread(target=hb_loop, daemon=False)
hb.start()
out("  [init] heartbeat thread started — output will flow continuously")

# Cleanup port
try:
    import re, subprocess
    o = subprocess.check_output(["netstat","-ano"], stderr=subprocess.DEVNULL).decode(errors="replace")
    for line in o.splitlines():
        m = re.search(rf":{PORT}\s+\S+\s+LISTENING\s+(\d+)", line)
        if m:
            try:
                subprocess.run(["taskkill","/F","/PID",m.group(1)], capture_output=True)
                out(f"  [init] killed stale :{PORT} PID {m.group(1)}")
            except: pass
except Exception: pass

# Django
try:
    import django
    django.setup()
    out("  [init] django.setup OK")
except Exception as e:
    out(f"  [init] FAIL django.setup: {e}")
    out(traceback.format_exc())
    sys.exit(1)

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
out("  [init] WSGI app OK")

from waitress.server import create_server
srv = create_server(app, host=HOST, port=PORT, threads=4, channel_timeout=900)
out(f"  [init] waitress server created (not yet serving)")

def srv_loop():
    try:
        HB[2] = True
        out("  [init] calling srv.run()... listening for HTTP")
        srv.run()
    except Exception as e:
        out(f"  [server] crashed: {e}")
        out(traceback.format_exc())
    finally:
        HB[2] = False

sthr = threading.Thread(target=srv_loop, daemon=True)
sthr.start()
out("  [init] server thread started — listening for connections soon...")

# Supervisor — keep main alive forever, restart server thread if it dies
while True:
    time.sleep(3)
    if not sthr.is_alive():
        out("  [supervisor] server thread died -> restarting")
        try:
            srv = create_server(app, host=HOST, port=PORT, threads=4, channel_timeout=900)
            sthr = threading.Thread(target=srv_loop, daemon=True)
            sthr.start()
        except Exception as e:
            out(f"  [supervisor] restart fail: {e}")
    HB[2] = sthr.is_alive()
