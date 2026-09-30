import os, sys, subprocess, time

SERVER_SCRIPT = r"d:\Atharvac++\deep_next\wsgiref_server.py"
DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
LOG_FILE = os.path.join(DJANGO_DIR, "wsgiref_launcher_log.txt")
PID_FILE = os.path.join(DJANGO_DIR, "wsgiref_server.pid")

with open(LOG_FILE, "w", encoding="utf-8") as log:
    def L(msg):
        log.write(str(msg) + "\n")
        log.flush()
        print(msg)

    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

    cmd = [sys.executable, SERVER_SCRIPT]
    L(f"Launching: {' '.join(cmd)}")

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=DJANGO_DIR,
            close_fds=True,
            creationflags=creationflags,
        )
        L(f"Launched launcher PID: {proc.pid}")
        with open(PID_FILE, "w") as pf:
            pf.write(str(proc.pid))
    except Exception as e:
        L(f"ERROR: {e}")
        import traceback
        traceback.print_exc(file=log)
        sys.exit(1)

    L(f"Waiting 6s for server to start...")
    time.sleep(6)

    # Read server log
    SRV_LOG = os.path.join(DJANGO_DIR, "wsgiref_server_log.txt")
    if os.path.exists(SRV_LOG):
        L("\n=== Server log ===")
        with open(SRV_LOG, "r", encoding="utf-8") as f:
            L(f.read())
    else:
        L(f"\n[warn] Server log not found at {SRV_LOG}")

    # Check port
    L("\n=== Checking port 8000 ===")
    try:
        out = subprocess.check_output(["netstat", "-ano"], stderr=subprocess.DEVNULL).decode(errors="replace")
        for line in out.splitlines():
            if ":8000" in line and "LISTENING" in line:
                L(f"  LISTENING: {line.strip()}")
    except Exception as e:
        L(f"  netstat check failed: {e}")
