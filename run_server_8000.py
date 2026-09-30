import os, sys, traceback

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

LOG_FILE = os.path.join(DJANGO_DIR, "waitress_server_log.txt")
log_f = open(LOG_FILE, "w", encoding="utf-8")

def log(msg, stream=sys.stdout):
    log_f.write(str(msg) + "\n")
    log_f.flush()
    try:
        stream.write(str(msg) + "\n")
        stream.flush()
    except Exception:
        pass

def _try_free(port):
    try:
        import subprocess as _sp
        import re as _re
        out = _sp.check_output(["netstat", "-ano"], stderr=_sp.DEVNULL).decode(errors="replace")
        for line in out.splitlines():
            m = _re.search(rf":{port}\s+\S+\s+LISTENING\s+(\d+)", line)
            if m:
                pid = int(m.group(1))
                os.kill(pid, 9)
                log(f"[boot] killed stale PID {pid} on :{port}")
    except Exception as e:
        log(f"[warn] _try_free({port}): {e}")

_try_free(8000)
_try_free(8080)
_try_free(8081)

import django
django.setup()
log("[boot] Django setup OK")

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
log("[boot] WSGI app created")

from waitress import serve
HOST = "127.0.0.1"
PORT = 8000
log(f"[boot] Calling waitress serve on http://{HOST}:{PORT}/ ...")

try:
    serve(
        app,
        host=HOST,
        port=PORT,
        threads=4,
        channel_timeout=900,
    )
    log("[SERVE RETURNED] This should not happen normally!")
except SystemExit as e:
    log(f"[SystemExit] code={e.code}")
    sys.exit(e.code)
except KeyboardInterrupt:
    log("[boot] stopped by user")
    sys.exit(0)
except Exception as exc:
    log("[FATAL] serve() crashed: " + repr(exc), sys.stderr)
    log(traceback.format_exc(), sys.stderr)
    sys.exit(2)
finally:
    log("[END] Server script exiting")
    log_f.close()
