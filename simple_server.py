import os, sys, socket, threading, time

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

LOG = os.path.join(DJANGO_DIR, "server_status.log")
def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        f.flush()

if os.path.exists(LOG):
    os.remove(LOG)

log(f"Start - PID {os.getpid()}")
log(f"CWD: {os.getcwd()}")

try:
    import django
    django.setup()
    log(f"Django {django.get_version()} setup OK")

    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
    log("WSGI app created")

    from wsgiref.simple_server import make_server

    HOST = "127.0.0.1"
    PORT = 8000

    log(f"Calling make_server({HOST}:{PORT}) ...")
    httpd = make_server(HOST, PORT, app)
    log(f"make_server OK. Socket: {httpd.socket.getsockname()}")

    log(f"Now calling serve_forever() ...")
    sys.stdout.flush()

    # Test binding: try to connect to ourselves in a thread
    def _probe():
        time.sleep(2)
        try:
            s = socket.socket()
            s.settimeout(3)
            s.connect((HOST, PORT))
            log(f"SELF-PROBE: connect OK to {HOST}:{PORT}")
            s.sendall(b"GET / HTTP/1.0\r\nHost: localhost\r\n\r\n")
            data = s.recv(4096)
            log(f"SELF-PROBE: got {len(data)} bytes, first 200: {data[:200]!r}")
            s.close()
        except Exception as e:
            log(f"SELF-PROBE FAILED: {e}")

    threading.Thread(target=_probe, daemon=True).start()

    httpd.serve_forever(poll_interval=0.5)

except SystemExit as e:
    log(f"SystemExit: {e.code}")
except Exception as e:
    import traceback
    log(f"EXCEPTION: {type(e).__name__}: {e}")
    log(traceback.format_exc())
finally:
    log("=== SCRIPT EXIT ===")
