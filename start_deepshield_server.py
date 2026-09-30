import os, sys, threading, time, urllib.request

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"
os.environ["PYTHONUNBUFFERED"] = "1"

LOG = os.path.join(DJANGO_DIR, "final_server.log")
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        f.flush()
    try:
        print(msg, flush=True)
    except Exception:
        pass

if os.path.exists(LOG):
    os.remove(LOG)

log(f"=== DEEPSHIELD AI SERVER STARTING ===")
log(f"PID: {os.getpid()}  CWD: {os.getcwd()}")
log(f"Python: {sys.version.splitlines()[0]}")

import django
log(f"Django module: {django.__file__}")
django.setup()
log(f"Django.setup() OK  version={django.get_version()}")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
log("WSGI application created")

def self_test(HOST, PORT):
    time.sleep(3)
    url = f"http://{HOST if HOST != '0.0.0.0' else '127.0.0.1'}:{PORT}/"
    try:
        log(f"[self-test] GET {url} ...")
        req = urllib.request.Request(url, headers={"User-Agent": "SelfTest/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            body = resp.read()
            log(f"[self-test] OK: status={resp.status}, type={resp.headers.get('Content-Type')}, len={len(body)}")
            log(f"[self-test] Title snippet: {body[body.find(b'<title'):body.find(b'</title>')+100].decode(errors='replace')[:200]}")
    except Exception as e:
        log(f"[self-test] FAILED: {type(e).__name__}: {e}")

from wsgiref.simple_server import make_server

HOST = "0.0.0.0"
PORT = 8000

log(f"Binding server to http://{HOST}:{PORT}/ ...")
httpd = make_server(HOST, PORT, application)
sockname = httpd.socket.getsockname()
log(f"SERVER BOUND: socket={sockname}")

threading.Thread(target=self_test, args=(HOST, PORT), daemon=True).start()

log(f"{'='*60}")
log(f"DEEPSHIELD AI DEEPFAKE DETECTION SERVER IS RUNNING:")
log(f"    http://127.0.0.1:{PORT}/")
log(f"    http://localhost:{PORT}/")
log(f"    http://0.0.0.0:{PORT}/")
log(f"Press Ctrl+C to stop.")
log(f"{'='*60}")

sys.stdout.flush()
sys.stderr.flush()

try:
    httpd.serve_forever(poll_interval=1.0)
except KeyboardInterrupt:
    log("Server stopped by user (KeyboardInterrupt)")
except Exception as e:
    import traceback
    log(f"SERVER ERROR: {type(e).__name__}: {e}")
    log(traceback.format_exc())
finally:
    try:
        httpd.server_close()
    except Exception:
        pass
    log("=== SERVER EXIT ===")
