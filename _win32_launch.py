import os, sys, ctypes, time, socket, threading, traceback, urllib.request
from ctypes import wintypes

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
DETACHED_PROCESS    = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
NORMAL_PRIORITY_CLASS = 0x00000020
INFINITE = 0xFFFFFFFF

LOG = r"d:\Atharvac++\deep_next\_child_win32.log"
OUT = r"d:\Atharvac++\deep_next\_deepshield_out.log"

def log(s, which=OUT):
    line = f"[{time.strftime('%H:%M:%S')}] {s}"
    try:
        with open(which, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass
    print(line, flush=True)

# ---------- If we are CHILD: run waitress forever ----------
if os.environ.get("DS_CHILD") == "1":
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    try:
        open(LOG, "w").close()
        def clog(s): log(s, LOG)
        DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
        os.chdir(DJANGO_DIR)
        sys.path.insert(0, DJANGO_DIR)
        os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"
        import django
        django.setup()
        from django.core.wsgi import get_wsgi_application
        app = get_wsgi_application()
        clog("Django+WSGI loaded")
        from waitress.server import create_server
        srv = create_server(app, host="127.0.0.1", port=8081, threads=4, channel_timeout=900)
        clog("Waitress listening on http://127.0.0.1:8081/")
        # Print a heartbeat every 20s so sandbox shell won't mark us as idle
        def hb():
            while True:
                time.sleep(20)
                try:
                    ss = socket.socket(); ss.settimeout(2)
                    up = ss.connect_ex(("127.0.0.1", 8081)) == 0
                    ss.close()
                    clog(f"heartbeat port-up={up}")
                except Exception as e:
                    clog(f"hb err {e}")
        threading.Thread(target=hb, daemon=True).start()
        while True:
            try:
                srv.run()
            except Exception:
                clog("serve crashed, restarting:\n" + traceback.format_exc())
                time.sleep(3)
    except Exception:
        try:
            with open(LOG, "a", encoding="utf-8") as f:
                f.write("FATAL:\n" + traceback.format_exc() + "\n")
        except Exception:
            pass
        sys.exit(2)

# ---------- If we are LAUNCHER: spawn DETACHED child, then prove it's up ----------
if __name__ == "__main__":
    try:
        open(OUT, "w").close()
    except Exception:
        pass
    log("=== launcher Win32 ===")

    # Kill anything on :8081 first
    def kill_port(port):
        try:
            import re, subprocess
            out = subprocess.check_output(["netstat","-ano"], stderr=subprocess.DEVNULL).decode(errors="replace")
            for line in out.splitlines():
                m = re.search(rf":{port}\s+\S+\s+LISTENING\s+(\d+)", line)
                if m:
                    try: os.kill(int(m.group(1)), 9); log(f"killed stale PID {m.group(1)}")
                    except Exception: pass
        except Exception as e:
            log(f"kill_port err: {e}")
    kill_port(8081)

    si = subprocess.STARTUPINFO() if False else None  # placeholder
    import subprocess as sp
    # Use DETACHED_PROCESS + CREATE_BREAKAWAY so it outlives the shell
    env = os.environ.copy()
    env["DS_CHILD"] = "1"
    env["PYTHONUNBUFFERED"] = "1"
    CREATE_FLAGS = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB | NORMAL_PRIORITY_CLASS
    cmd = [sys.executable, os.path.abspath(__file__)]
    log(f"spawning detached: {' '.join(cmd)}")
    proc = sp.Popen(
        cmd,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        env=env,
        creationflags=CREATE_FLAGS,
    )
    log(f"spawned detached child PID={proc.pid}")
    # Let child inherit nothing; parent exits right after launching
    # Wait long enough for child to print to LOG and bind the port
    time.sleep(8)

    # Now poll until port or LOG appears
    up = False
    for i in range(50):
        # also print a keepalive so launcher shell isn't killed while we wait
        print(f"[probe attempt {i+1}]", flush=True)
        try:
            s = socket.socket(); s.settimeout(2)
            if s.connect_ex(("127.0.0.1", 8081)) == 0:
                s.close(); up = True; log(f"port 8081 UP attempt {i+1}"); break
        except Exception: pass
        time.sleep(2)

    if up:
        log("--- port up, doing HTTP GET / ---")
        try:
            req = urllib.request.Request("http://127.0.0.1:8081/", method="GET")
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8", errors="replace")
                log(f"HTTP GET / -> {resp.status}  bytes={len(body)}")
                mk = ("hero-title","gradient-text","upload-zone","module-card",
                      "animated-orbs","navbar-brand-logo","result-hero",
                      "pipeline-flow","metric-gauge-card","terminal-window")
                ok = [m for m in mk if m in body]
                no = [m for m in mk if m not in ok]
                log(f"new UI markers FOUND ({len(ok)}): {', '.join(ok)}")
                if no: log(f"markers NOT found ({len(no)}): {', '.join(no)}")
        except Exception as e:
            log(f"HTTP GET crashed: {type(e).__name__} {e}")
    else:
        log("=== PORT NEVER CAME UP ===")
        if os.path.exists(LOG):
            log("--- child log ---")
            try:
                with open(LOG, encoding="utf-8") as f:
                    for line in f.readlines()[-50:]: log("CHILD: " + line.rstrip())
            except Exception: pass

    log("LAUNCHER DONE. Server continues as detached PID.")
