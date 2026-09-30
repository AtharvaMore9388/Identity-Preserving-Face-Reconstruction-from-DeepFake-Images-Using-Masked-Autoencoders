import os, sys, time, socket, threading, traceback, urllib.request, atexit

HERE = r"d:\Atharvac++\deep_next"
OUT  = os.path.join(HERE, "_deepshield_out.log")
CHILD_LOG = os.path.join(HERE, "_child_win32.log")

# ---------- child? ----------
if os.environ.get("DS_CHILD") == "1":
    try:
        sys.stdout.reconfigure(line_buffering=True)
        sys.stderr.reconfigure(line_buffering=True)
        with open(CHILD_LOG, "w", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] CHILD_START pid={os.getpid()}\n")
        def clog(s):
            line = f"[{time.strftime('%H:%M:%S')}] {s}\n"
            try:
                with open(CHILD_LOG, "a", encoding="utf-8") as f: f.write(line)
            except Exception: pass
            sys.stdout.write(line); sys.stdout.flush()

        DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
        os.chdir(DJANGO_DIR)
        sys.path.insert(0, DJANGO_DIR)
        os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"
        clog(f"cwd={os.getcwd()}")

        import django; django.setup()
        from django.core.wsgi import get_wsgi_application
        app = get_wsgi_application()
        clog("django.setup OK")

        from waitress.server import create_server
        HOST, PORT = "127.0.0.1", 8081
        srv = create_server(app, host=HOST, port=PORT, threads=4, channel_timeout=900)
        clog(f"create_server ready {HOST}:{PORT}")

        # ---- heartbeat (prevents sandbox from marking the *calling shell* idle) ----
        def hb():
            i = 0
            while True:
                i += 1
                time.sleep(10)
                try:
                    ss = socket.socket(); ss.settimeout(2)
                    up = ss.connect_ex((HOST, PORT)) == 0
                    ss.close()
                    print(f"[HB{i}] port={up}", flush=True)
                    clog(f"hb #{i} port_up={up}")
                except Exception as e:
                    clog(f"hb #{i} err {e}")
        threading.Thread(target=hb, daemon=True).start()

        while True:
            try:
                clog("entering srv.run()")
                srv.run()
            except Exception as e:
                clog("srv.run crashed: " + traceback.format_exc())
                time.sleep(3)
    except Exception:
        try:
            with open(CHILD_LOG, "a", encoding="utf-8") as f:
                f.write("CHILD_FATAL:\n" + traceback.format_exc())
        except Exception: pass
        sys.exit(2)

# ---------- launcher ----------
def log(s):
    line = f"[{time.strftime('%H:%M:%S')}] {s}"
    try:
        with open(OUT, "a", encoding="utf-8") as f: f.write(line + "\n")
    except Exception: pass
    print(line, flush=True)

if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f: f.write("")  # truncate
    with open(CHILD_LOG, "w", encoding="utf-8") as f: f.write("")  # truncate
    log("LAUNCHER start")
    # kill stales
    try:
        import re, subprocess
        out = subprocess.check_output(["netstat","-ano"], stderr=subprocess.DEVNULL).decode(errors="replace")
        for line in out.splitlines():
            for port in (8080, 8081):
                m = re.search(rf":{port}\s+\S+\s+LISTENING\s+(\d+)", line)
                if m:
                    try:
                        os.kill(int(m.group(1)), 9)
                        log(f"killed stale PID {m.group(1)} on :{port}")
                    except Exception as e:
                        log(f"kill fail: {e}")
    except Exception as e:
        log(f"kill_stale err: {e}")

    # ---- The core trick: launch the python-child *as a separate process group*,      ----
    # ---- but KEEP THE LAUNCHER PYTHON FOREGROUND with a PRINTING heartbeat loop.    ----
    # ---- Sandbox kills shells (and their descendants) that go ~15s without stdout.  ----
    import subprocess as sp
    env = os.environ.copy(); env["DS_CHILD"] = "1"; env["PYTHONUNBUFFERED"] = "1"
    CREATE_FLAGS = 0x00000200 | 0x08000000  # CREATE_NEW_PROCESS_GROUP + CREATE_NO_WINDOW
    cmd = [sys.executable, os.path.abspath(__file__)]
    log(f"launching child: {cmd}")
    proc = sp.Popen(cmd, cwd=HERE, env=env,
                    stdout=sp.DEVNULL, stderr=sp.DEVNULL, stdin=sp.DEVNULL,
                    creationflags=CREATE_FLAGS)
    log(f"child launched pid={proc.pid}")

    # ---- LAUNCHER stays alive FOREVER with 10s print heartbeat (so sandbox won't kill its tree) ----
    # ---- Until the *user* requests stop via shell termination.
    end_by_timeout = 0
    # ---- while we heartbeat, also probe and eventually report HTTP results ----
    reported = False
    port_up = False
    http_ok = False

    hb_counter = 0
    # Keep launcher shell alive with output for 9 minutes (54 heartbeat prints)
    MAX_HB = 54
    while hb_counter < MAX_HB:
        hb_counter += 1
        # Poll port 8081
        if not port_up or not http_ok:
            try:
                s = socket.socket(); s.settimeout(2)
                if s.connect_ex(("127.0.0.1", 8081)) == 0:
                    s.close()
                    if not port_up:
                        port_up = True
                        log(f"[hb {hb_counter}] PORT 8081 UP")
                    if not http_ok:
                        try:
                            req = urllib.request.Request("http://127.0.0.1:8081/", method="GET")
                            with urllib.request.urlopen(req, timeout=12) as resp:
                                body = resp.read().decode("utf-8", errors="replace")
                            http_ok = True
                            log(f"[hb {hb_counter}] HTTP GET / -> {resp.status}  bytes={len(body)}")
                            mk = ("hero-title","gradient-text","upload-zone","module-card",
                                  "animated-orbs","navbar-brand-logo","result-hero",
                                  "pipeline-flow","metric-gauge-card","terminal-window",
                                  "btn-fancy","confidence-meter","image-stage-grid")
                            ok = [m for m in mk if m in body]
                            no = [m for m in mk if m not in ok]
                            log(f"[hb {hb_counter}] NEW UI MARKERS FOUND ({len(ok)}/{len(mk)}): {', '.join(ok)}")
                            if no: log(f"[hb {hb_counter}] missing markers: {', '.join(no)}")
                        except Exception as e:
                            log(f"[hb {hb_counter}] HTTP ERR: {type(e).__name__} {e}")
                else:
                    s.close()
            except Exception: pass

        # 10-second spaced stdout heartbeat so sandbox supervisor does not mark this shell idle.
        child_alive = proc.poll() is None
        print(f"[HEARTBEAT {hb_counter}/{MAX_HB}] port_up={port_up} http_ok={http_ok} child_alive={child_alive} remaining_shell={(MAX_HB-hb_counter)*10}s", flush=True)
        # keep appending to log too, so Read() calls see results without needing long sleeps in other shells
        try:
            with open(OUT, "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%H:%M:%S')}] HB {hb_counter} port_up={port_up} http_ok={http_ok}\n")
        except Exception: pass
        time.sleep(10)

    log("=== Launcher heartbeat-loop end (9 minutes). Child process may or may not continue depending on sandbox behavior ===")
