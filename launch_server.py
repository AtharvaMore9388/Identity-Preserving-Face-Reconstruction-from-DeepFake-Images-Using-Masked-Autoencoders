import os, sys, subprocess, time

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)

LOG_FILE = os.path.join(DJANGO_DIR, "runserver_output.log")
PID_FILE = os.path.join(DJANGO_DIR, "runserver.pid")

with open(LOG_FILE, "w") as log:
    log.write(f"Launcher start: {time.ctime()}\n")
    log.write(f"CWD: {os.getcwd()}\n")
    log.flush()

    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    creationflags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

    cmd = [
        sys.executable,
        "manage.py",
        "runserver",
        "0.0.0.0:8000",
        "--noreload",
    ]

    log.write(f"Running: {' '.join(cmd)}\n")
    log.flush()

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=DJANGO_DIR,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            close_fds=True,
            creationflags=creationflags,
        )
        with open(PID_FILE, "w") as pf:
            pf.write(str(proc.pid))
        log.write(f"Launched PID: {proc.pid}\n")
        log.flush()
        print(f"[OK] Launched Django runserver on 0.0.0.0:8000 (PID {proc.pid})")
        print(f"     Log: {LOG_FILE}")
        print(f"     PID file: {PID_FILE}")
        time.sleep(3)
    except Exception as e:
        log.write(f"ERROR launching: {type(e).__name__}: {e}\n")
        log.flush()
        import traceback
        traceback.print_exc(file=log)
        print(f"[FAIL] {e}")
        sys.exit(1)
