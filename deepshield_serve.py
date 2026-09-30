import os, sys, threading, time, signal

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

print("="*60, flush=True)
print(f" DEEPSHIELD AI - DEEPFAKE DETECTION SERVER", flush=True)
print("="*60, flush=True)
print(f"[boot] PID: {os.getpid()}", flush=True)
print(f"[boot] CWD: {os.getcwd()}", flush=True)

import django
django.setup()
print(f"[boot] Django {django.get_version()} setup OK", flush=True)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
print(f"[boot] WSGI application created", flush=True)

from wsgiref.simple_server import make_server, WSGIRequestHandler

class LoggedHandler(WSGIRequestHandler):
    def log_message(self, fmt, *args):
        msg = fmt % args
        print(f"[http] {self.address_string()} - {msg}", flush=True)

HOST = "127.0.0.1"
PORT = 8000
httpd = None

def run_server():
    global httpd
    try:
        print(f"[boot] make_server({HOST}:{PORT}) ...", flush=True)
        httpd = make_server(HOST, PORT, application, handler_class=LoggedHandler)
        sock = httpd.socket.getsockname()
        print(f"[boot] SOCKET BOUND: {sock[0]}:{sock[1]}", flush=True)
        print("="*60, flush=True)
        print(f"  DEEPSHIELD AI SERVING ON:", flush=True)
        print(f"    http://127.0.0.1:{PORT}/", flush=True)
        print(f"    http://localhost:{PORT}/", flush=True)
        print(f"  (bound to {HOST}:{PORT})", flush=True)
        print("="*60, flush=True)
        httpd.serve_forever(poll_interval=0.5)
    except Exception as e:
        import traceback
        print(f"[server-error] {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        raise

t = threading.Thread(target=run_server, daemon=True)
t.start()

# Wait for server to be ready
for _ in range(30):
    time.sleep(0.2)
    if httpd is not None:
        break

import urllib.request
def _selftest():
    time.sleep(2)
    try:
        url = f"http://127.0.0.1:{PORT}/"
        print(f"[selftest] GET {url} ...", flush=True)
        req = urllib.request.Request(url, headers={"User-Agent": "DeepShieldSelfTest/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read()
            print(f"[selftest] OK: HTTP {resp.status}, len={len(body)} bytes", flush=True)
    except Exception as e:
        print(f"[selftest] FAILED: {type(e).__name__}: {e}", flush=True)

threading.Thread(target=_selftest, daemon=True).start()

# Main thread keeps printing heartbeats to keep process alive
tick = 0
try:
    while True:
        time.sleep(2)
        tick += 1
        alive = t.is_alive()
        print(f"[heartbeat] t={tick*2}s  server_thread={'ALIVE' if alive else 'DEAD'}", flush=True)
        if not alive:
            print("[FATAL] Server thread died! Exiting.", flush=True)
            break
except KeyboardInterrupt:
    print("\n[shutdown] KeyboardInterrupt", flush=True)
finally:
    try:
        if httpd:
            httpd.shutdown()
            httpd.server_close()
    except Exception:
        pass
    print("[shutdown] Goodbye.", flush=True)
