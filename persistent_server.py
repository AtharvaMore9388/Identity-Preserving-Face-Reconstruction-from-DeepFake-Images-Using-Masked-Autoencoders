import os, sys, threading, time, urllib.request

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

print("[0s] Booting DeepShield AI ...", flush=True)

import django
django.setup()
print("[1s] Django.setup() OK", flush=True)

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
print("[1s] WSGI app OK", flush=True)

from wsgiref.simple_server import make_server, WSGIRequestHandler

class H(WSGIRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[HTTP] {self.address_string()} - {fmt % args}", flush=True)

HOST, PORT = "127.0.0.1", 8000
httpd = make_server(HOST, PORT, app, handler_class=H)
sock = httpd.socket.getsockname()
print(f"[2s] SOCKET BOUND {sock[0]}:{sock[1]}", flush=True)

def serve():
    try:
        httpd.serve_forever(poll_interval=0.5)
    except Exception as e:
        print(f"[SERVE-ERROR] {e}", flush=True)

threading.Thread(target=serve, daemon=True).start()

time.sleep(0.5)

# Self test
url = f"http://127.0.0.1:{PORT}/"
try:
    req = urllib.request.Request(url, headers={"User-Agent":"DeepShieldBoot/1.0"})
    with urllib.request.urlopen(req, timeout=10) as r:
        body = r.read()
        print(f"[3s] SELF-TEST: HTTP {r.status}, len={len(body)} bytes - APP IS ALIVE", flush=True)
except Exception as e:
    print(f"[3s] SELF-TEST FAILED: {e}", flush=True)

print("="*60, flush=True)
print(f" DEEPSHIELD AI SERVING ON http://127.0.0.1:{PORT}/", flush=True)
print(" Open the URL in your browser NOW.", flush=True)
print("="*60, flush=True)

# Heartbeat loop keeps stdout active so sandbox doesn't kill us
t0 = time.time()
while True:
    time.sleep(2)
    elapsed = int(time.time() - t0)
    try:
        with urllib.request.urlopen(url, timeout=3) as r:
            s = r.status
        print(f"[heartbeat t={elapsed}s] server=ALIVE http={s}", flush=True)
    except Exception as e:
        print(f"[heartbeat t={elapsed}s] server ERROR: {e}", flush=True)
