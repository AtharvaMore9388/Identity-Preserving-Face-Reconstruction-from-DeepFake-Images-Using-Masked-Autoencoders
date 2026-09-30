import socket, urllib.request, sys, os, time

HOST, PORT = "127.0.0.1", 8081
P = r"d:\Atharvac++\deep_next\_server_keep.log"

def log(msg):
    with open(P, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg, flush=True)

log(f"=== verify @ {time.ctime()} ===")

up = False
for i in range(8):
    try:
        s = socket.socket()
        s.settimeout(2)
        r = s.connect_ex((HOST, PORT))
        s.close()
        if r == 0:
            up = True
            log(f"TCP :{PORT} UP (attempt {i+1})")
            break
    except Exception as e:
        log(f"tcp try {i+1}: {e}")
    time.sleep(2)

if not up:
    log(f"TCP DOWN after 8 attempts. Launching...")
    DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
    os.chdir(DJANGO_DIR)
    sys.path.insert(0, DJANGO_DIR)
    os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"
    import django
    django.setup()
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
    log("django+wsgi loaded — will detach waitress via thread")
    from waitress.server import create_server
    server = create_server(app, host=HOST, port=PORT, threads=4, channel_timeout=900)
    import threading
    t = threading.Thread(target=server.run, daemon=True)
    t.start()
    log(f"thread launched, will now sleep 12s then verify HTTP")
    time.sleep(12)
    up = True

if up:
    try:
        req = urllib.request.Request(f"http://{HOST}:{PORT}/", method="GET")
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = resp.read().decode("utf-8", errors="replace")
            log(f"HTTP GET / -> {resp.status}  bytes={len(data)}")
            for marker in ("hero-title", "gradient-text", "upload-zone", "module-card",
                           "animated-orbs", "navbar-brand-logo", "result-hero",
                           "pipeline-flow", "metric-gauge-card", "terminal-window"):
                if marker in data:
                    log(f"  marker OK: {marker}")
    except Exception as e:
        log(f"HTTP GET failed: {type(e).__name__} {e}")

log("=== END ===")
