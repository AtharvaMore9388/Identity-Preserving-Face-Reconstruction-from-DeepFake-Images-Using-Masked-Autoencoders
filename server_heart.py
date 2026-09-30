import os, sys, threading, time

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

LOG = os.path.join(DJANGO_DIR, "server_status.log")
HEART = os.path.join(DJANGO_DIR, "heartbeat.txt")

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
if os.path.exists(HEART):
    os.remove(HEART)

log(f"BOOT - PID {os.getpid()}")
log(f"argv: {sys.argv}")

import django
django.setup()
log(f"Django {django.get_version()} OK")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
log("WSGI OK")

def heartbeat():
    while True:
        try:
            with open(HEART, "w") as f:
                f.write(f"alive PID={os.getpid()} time={time.time()}\n")
        except Exception:
            pass
        time.sleep(2)

threading.Thread(target=heartbeat, daemon=True).start()

HOST = os.environ.get("SRV_HOST", "127.0.0.1")
PORT = int(os.environ.get("SRV_PORT", "8000"))

from wsgiref.simple_server import make_server

class LoggedHandler(__import__('wsgiref.simple_server', fromlist=['WSGIRequestHandler']).WSGIRequestHandler):
    def log_message(self, fmt, *args):
        try:
            log(f"REQ: {fmt % args}")
        except Exception:
            pass

log(f"make_server({HOST}:{PORT}) ...")
httpd = make_server(HOST, PORT, app, handler_class=LoggedHandler)
log(f"SOCKET BOUND: {httpd.socket.getsockname()}")
log(f"SERVE_FOREVER starting now.")

try:
    httpd.serve_forever(poll_interval=0.5)
except KeyboardInterrupt:
    log("KeyboardInterrupt - stopping")
except Exception as e:
    import traceback
    log(f"SERVE ERROR: {e}")
    log(traceback.format_exc())
finally:
    log("=== END ===")
