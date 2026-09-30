import os, sys

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

LOG_FILE = os.path.join(DJANGO_DIR, "wsgiref_server_log.txt")
PID_FILE = os.path.join(DJANGO_DIR, "wsgiref_server.pid")

import django
django.setup()

from django.core.wsgi import get_wsgi_application
app = get_wsgi_application()

from wsgiref.simple_server import make_server, WSGIRequestHandler

class QuietHandler(WSGIRequestHandler):
    def log_message(self, format, *args):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("[%s] %s\n" % (self.log_date_time_string(), format % args))
            f.flush()

HOST = "0.0.0.0"
PORT = 8000

with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write(f"[start] Starting wsgiref server on http://{HOST}:{PORT}/\n")
    f.write(f"[start] PID: {os.getpid()}\n")
    f.flush()

with open(PID_FILE, "w") as f:
    f.write(str(os.getpid()))

try:
    httpd = make_server(HOST, PORT, app, handler_class=QuietHandler)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[ready] Serving on http://{HOST}:{PORT}/ (PID {os.getpid()})\n")
        f.flush()
    sys.stdout.write(f"[READY] wsgiref serving on http://{HOST}:{PORT}/ (PID {os.getpid()})\n")
    sys.stdout.flush()
    httpd.serve_forever()
except KeyboardInterrupt:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("[stop] KeyboardInterrupt\n")
    sys.exit(0)
except Exception as e:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[ERROR] {type(e).__name__}: {e}\n")
        import traceback
        traceback.print_exc(file=f)
    sys.exit(1)
