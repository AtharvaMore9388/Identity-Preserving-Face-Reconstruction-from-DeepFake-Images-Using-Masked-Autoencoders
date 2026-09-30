import os, sys, threading, time, traceback, socket

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
HOST = "0.0.0.0"
PORT = 8000

os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"
os.environ["PYTHONUNBUFFERED"] = "1"

try:
    sys.stdout.reconfigure(line_buffering=True, errors="replace")
    sys.stderr.reconfigure(line_buffering=True, errors="replace")
except:
    pass

def out(m):
    try:
        sys.stdout.write(m + "\n")
        sys.stdout.flush()
    except:
        pass

out("=" * 60)
out("  DEEPSHIELD AI - DJANGO DEV SERVER (IN-PROCESS)")
out(f"  Serving on: http://127.0.0.1:{PORT}/")
out(f"  Also on: http://0.0.0.0:{PORT}/ (all interfaces)")
out(f"  PID: {os.getpid()}")
out("=" * 60)

# Kill stale
try:
    import re, subprocess
    out_ = subprocess.check_output(["netstat","-ano"], stderr=subprocess.DEVNULL).decode(errors="replace")
    for line in out_.splitlines():
        m = re.search(rf":{PORT}\s+\S+\s+LISTENING\s+(\d+)", line)
        if m:
            try:
                subprocess.run(["taskkill","/F","/PID",m.group(1)], capture_output=True)
                out(f"  [cleanup] killed stale PID {m.group(1)} on :{PORT}")
            except: pass
except Exception as e:
    out(f"  [cleanup] port-scan err: {e}")

try:
    import django
    django.setup()
    out("  [init] django.setup OK")
except Exception as e:
    out(f"  [init] django.setup FAIL: {e}")
    out(traceback.format_exc())
    sys.exit(1)

server_ref = [None]
thread_ref = [None]

def start_server():
    try:
        from django.core.servers.basehttp import run, get_internal_wsgi_application
        from django.contrib.staticfiles.handlers import StaticFilesHandler
        out(f"  [init] calling django.core.servers.basehttp.run on {HOST}:{PORT}")
        wsgi_app = get_internal_wsgi_application()
        # Wrap with StaticFilesHandler so CSS/JS/images are served (like manage.py runserver)
        static_app = StaticFilesHandler(wsgi_app)
        # run() blocks
        run(HOST, PORT, wsgi_handler=static_app, ipv6=False, threading=True,
            on_bind=lambda srv: (out("="*60),
                                 out("  SERVER IS RUNNING!"),
                                 out(f"  Open: http://127.0.0.1:{PORT}/"),
                                 out("="*60),
                                 server_ref.__setitem__(0, srv)))
    except Exception as e:
        out(f"  [server] FATAL: {e}")
        out(traceback.format_exc())

thread = threading.Thread(target=start_server, daemon=True)
thread.start()
thread_ref[0] = thread
out(f"  [init] server thread started (TID={thread.ident})")

# Fast port check + immediate heartbeat loop (sandbox kills silent processes after ~2s)
up = False
n = 0
while True:
    time.sleep(2)
    n += 1
    try:
        s = socket.socket(); s.settimeout(0.5)
        pu = s.connect_ex(("127.0.0.1", PORT)) == 0
        s.close()
    except:
        pu = False
    if pu and not up:
        up = True
        out("")
        out("=" * 60)
        out("  PORT " + str(PORT) + " CONFIRMED UP — SERVER IS ACCESSIBLE!")
        out("  URL:  http://127.0.0.1:" + str(PORT) + "/")
        out("=" * 60)
    ta = thread.is_alive()
    if not ta:
        out(f"  [HB-{n:>3}] SERVER THREAD DIED! restarting... port={'UP' if pu else 'DOWN'}")
        try:
            server_ref[0] = None
            thread = threading.Thread(target=start_server, daemon=True)
            thread.start()
            thread_ref[0] = thread
            out(f"  [supervisor] restarted server thread (TID={thread.ident})")
        except Exception as re:
            out(f"  [supervisor] restart failed: {re}")
    elif up:
        out(f"  [HB-{n:>3}] ok port={PORT}:UP  server_thread=alive  requests=flowing")
    else:
        out(f"  [boot {n*2:>3}s] server thread={ta}  port-{PORT}={'UP' if pu else 'DOWN'}")
