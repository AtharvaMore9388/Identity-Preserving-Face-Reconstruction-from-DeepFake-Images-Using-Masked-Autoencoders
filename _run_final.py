import os, sys, time, socket, threading, traceback

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
HOST = "127.0.0.1"
PORT = 8000

os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

# DO NOT reconfigure stdout — leave it alone to avoid sandbox crashes.
def out(m):
    try:
        sys.stdout.write(m + "\n")
        sys.stdout.flush()
    except Exception:
        pass

out("=" * 60)
out("  DEEPSHIELD AI — DJANGO WEB SERVER")
out(f"  URL: http://{HOST}:{PORT}/")
out(f"  PID: {os.getpid()}")
out("=" * 60)

def port_free():
    try:
        import re, subprocess
        o = subprocess.check_output(["netstat","-ano"], stderr=subprocess.DEVNULL).decode(errors="replace")
        for line in o.splitlines():
            m = re.search(rf":{PORT}\s+\S+\s+LISTENING\s+(\d+)", line)
            if m:
                try:
                    subprocess.run(["taskkill","/F","/PID",m.group(1)], capture_output=True)
                    out(f"  [cleanup] killed stale PID {m.group(1)} on :{PORT}")
                except: pass
    except Exception as e:
        out(f"  [cleanup] port err: {e}")
port_free()

try:
    import django
    django.setup()
    out("  [init] django.setup OK")
except Exception as e:
    out(f"  [init] FAIL: {e}")
    out(traceback.format_exc())
    sys.exit(1)

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
out("  [init] WSGI app OK")

from waitress.server import create_server
srv = create_server(app, host=HOST, port=PORT, threads=4, channel_timeout=900)
out(f"  [init] waitress server bound to {HOST}:{PORT}")

def server_loop():
    try:
        out("  [init] server entering serve()...")
        srv.run()
    except Exception as e:
        out(f"  [server] crash: {e}")
        out(traceback.format_exc())

t = threading.Thread(target=server_loop, daemon=True)
t.start()
out(f"  [init] server thread launched (TID={t.ident})")

# ========= HEARTBEAT LOOP (critical — prints every 2s forever) =========
port_up = False
n = 0
while True:
    time.sleep(2)
    n += 1
    try:
        s = socket.socket(); s.settimeout(0.5)
        pu = s.connect_ex((HOST, PORT)) == 0
        s.close()
    except:
        pu = False
    if pu and not port_up:
        port_up = True
        out("")
        out("=" * 60)
        out("  SERVER IS UP AND RESPONDING!")
        out(f"  URL:  http://{HOST}:{PORT}/")
        out(f"  URL2: http://localhost:{PORT}/")
        out("=" * 60)
        out("")
        # Do a quick HTTP GET smoke test to confirm Django renders
        try:
            import urllib.request
            req = urllib.request.Request(f"http://{HOST}:{PORT}/", method="GET")
            with urllib.request.urlopen(req, timeout=8) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                title = "N/A"
                if "<title>" in body.lower():
                    import re as _re
                    m = _re.search(r"<title>(.*?)</title>", body, _re.I | _re.S)
                    if m: title = m.group(1).strip()
                markers_found = sum(1 for mk in ["hero-title","upload-zone","navbar","predict","index","Deepfake","DeepShield","deepfake"] if mk.lower() in body.lower())
                out(f"  [smoke-test] GET / -> HTTP {resp.status}  bytes={len(body)}  title={title!r}  markers_hit={markers_found}")
        except Exception as he:
            out(f"  [smoke-test] GET / err: {type(he).__name__}: {he}")
    thr_alive = t.is_alive()
    if not thr_alive:
        out(f"  [HB-{n:>3}] SERVER THREAD DIED! respawning... port={'UP' if pu else 'DOWN'}")
        try:
            t = threading.Thread(target=server_loop, daemon=True)
            t.start()
            out(f"  [supervisor] new server thread TID={t.ident}")
        except Exception as re_:
            out(f"  [supervisor] respawn fail: {re_}")
    elif port_up:
        out(f"  [HB-{n:>3}] OK — port {PORT}:UP  server:alive  serving requests")
    else:
        out(f"  [boot {n*2:>3}s] server thread={thr_alive}  port {PORT}={'UP' if pu else 'DOWN'}")
