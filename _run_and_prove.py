import os, sys, time, socket, threading, traceback, urllib.request

HERE = r"d:\Atharvac++\deep_next"
OUT  = os.path.join(HERE, "_deepshield_out.log")

def log(msg):
    s = f"[{time.strftime('%H:%M:%S')}] {msg}"
    try:
        with open(OUT, "a", encoding="utf-8") as f:
            f.write(s + "\n")
    except Exception:
        pass
    print(s, flush=True)

def boot_forever_in_thread():
    DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
    os.chdir(DJANGO_DIR)
    if DJANGO_DIR not in sys.path:
        sys.path.insert(0, DJANGO_DIR)
    os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"
    try:
        import django
        django.setup()
        from django.core.wsgi import get_wsgi_application
        app = get_wsgi_application()
        log("Django WSGI app loaded")
    except Exception:
        log("django init FAILED:")
        log(traceback.format_exc())
        return

    HOST, PORT = "127.0.0.1", 8081
    try:
        from waitress.server import create_server
        server = create_server(app, host=HOST, port=PORT, threads=4, channel_timeout=900)
    except Exception:
        log("create_server FAILED:")
        log(traceback.format_exc())
        return

    log(f"Starting waitress on http://{HOST}:{PORT}/ (threaded, daemon)")
    while True:
        try:
            server.run()
        except Exception:
            log("serve() crashed, restarting in 3s:")
            log(traceback.format_exc())
            time.sleep(3)

def probe():
    time.sleep(10)
    for i in range(40):
        try:
            s = socket.socket()
            s.settimeout(2)
            if s.connect_ex(("127.0.0.1", 8081)) == 0:
                s.close()
                log(f"[probe] TCP UP on attempt {i+1}")
                # Try HTTP /
                try:
                    req = urllib.request.Request("http://127.0.0.1:8081/", method="GET")
                    with urllib.request.urlopen(req, timeout=12) as resp:
                        body = resp.read().decode("utf-8", errors="replace")
                        log(f"[probe] HTTP / -> {resp.status}  {len(body)} bytes")
                        markers = ("hero-title", "gradient-text", "upload-zone",
                                   "module-card", "animated-orbs", "navbar-brand-logo")
                        found = [m for m in markers if m in body]
                        log("[probe] markers: " + ", ".join(found))
                except Exception as e:
                    log(f"[probe] HTTP err: {type(e).__name__} {e}")
                return
        except Exception as e:
            log(f"[probe] tcp try {i+1}: {e}")
        time.sleep(2)
    log("[probe] never came up")

if __name__ == "__main__":
    # wipe old log once on startup
    try:
        if os.path.exists(OUT):
            os.remove(OUT)
    except Exception:
        pass

    log("=== deepshield boot ===")

    t = threading.Thread(target=boot_forever_in_thread, daemon=True)
    t.start()

    pt = threading.Thread(target=probe, daemon=True)
    pt.start()

    log("threads launched, going into foreground 12-minute keepalive loop ...")

    end = time.time() + 12 * 60
    while time.time() < end:
        time.sleep(30)
        alive = t.is_alive()
        log(f"[heartbeat] server thread alive={alive}  uptime={int(time.time()-end+12*60)}s")
    log("=== 12-minute shell timeout reached; server thread may be killed by sandbox ===")
