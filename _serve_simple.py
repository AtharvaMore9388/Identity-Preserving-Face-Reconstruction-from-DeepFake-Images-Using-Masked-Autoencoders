import os, sys, traceback

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

# Try to kill any previous process on port 8081 / 8080 just in case
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
                sys.stdout.write(f"[boot] killed stale PID {pid} on :{port}\n"); sys.stdout.flush()
    except Exception:
        pass

_try_free(8080)
_try_free(8081)

import django
django.setup()

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()
sys.stdout.write("[boot] Django+WSGI ready\n"); sys.stdout.flush()

from waitress import serve
HOST = "127.0.0.1"
PORT = 8081
sys.stdout.write(f"[boot] DeepShield AI serving on http://{HOST}:{PORT}/\n"); sys.stdout.flush()
try:
    serve(app, host=HOST, port=PORT, threads=4, channel_timeout=900)
except KeyboardInterrupt:
    sys.stdout.write("[boot] stopped by user\n"); sys.stdout.flush()
    sys.exit(0)
except Exception as exc:
    sys.stderr.write("[FATAL] serve() crashed: " + repr(exc) + "\n")
    traceback.print_exc()
    sys.exit(2)

