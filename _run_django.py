import os, sys, subprocess, threading, time

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
HOST = "0.0.0.0"
PORT = 8000
PYTHON = sys.executable

sys.stdout.reconfigure(line_buffering=True, errors="replace")
sys.stderr.reconfigure(line_buffering=True, errors="replace")

print("="*60, flush=True)
print("  DEEPSHIELD AI - DJANGO DEVELOPMENT SERVER", flush=True)
print(f"  URL: http://127.0.0.1:{PORT}/", flush=True)
print(f"  PID: {os.getpid()}", flush=True)
print("="*60, flush=True)

# Kill anything already on the port
try:
    import re
    out = subprocess.check_output(["netstat","-ano"], stderr=subprocess.DEVNULL).decode(errors="replace")
    for line in out.splitlines():
        m = re.search(rf":{PORT}\s+\S+\s+LISTENING\s+(\d+)", line)
        if m:
            try:
                subprocess.run(["taskkill","/F","/PID",m.group(1)], capture_output=True)
                print(f"  [cleanup] killed stale PID {m.group(1)} on :{PORT}", flush=True)
            except:
                pass
except Exception as e:
    print(f"  [cleanup] port check err: {e}", flush=True)

CREATE_NO_WINDOW = 0x08000000
env = os.environ.copy()
env["PYTHONUNBUFFERED"] = "1"

print(f"  [launch] spawning manage.py runserver {HOST}:{PORT}...", flush=True)
proc = subprocess.Popen(
    [PYTHON, "manage.py", "runserver", f"{HOST}:{PORT}", "--noreload"],
    cwd=DJANGO_DIR,
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    stdin=subprocess.DEVNULL,
    creationflags=CREATE_NO_WINDOW,
    bufsize=0,
)
print(f"  [launch] child PID = {proc.pid}", flush=True)

def reader():
    try:
        for raw in proc.stdout:
            line = raw.decode(errors="replace").rstrip()
            print(f"  [django] {line}", flush=True)
    except Exception as e:
        print(f"  [reader] exit: {e}", flush=True)

threading.Thread(target=reader, daemon=True).start()

# Wait for port
up = False
for i in range(30):
    time.sleep(1)
    try:
        import socket
        s = socket.socket(); s.settimeout(1)
        if s.connect_ex(("127.0.0.1", PORT)) == 0:
            s.close(); up = True
            print("", flush=True)
            print("="*60, flush=True)
            print("  SERVER IS RUNNING!", flush=True)
            print(f"  Open in browser:  http://127.0.0.1:{PORT}/", flush=True)
            print("="*60, flush=True)
            break
        s.close()
    except:
        pass
    print(f"  [boot {i+1}s] waiting for port {PORT}...", flush=True)

if not up:
    print("  [warn] port did not come up in probe phase; supervisor continues.", flush=True)

# Keep alive loop + supervisor
n = 0
while True:
    time.sleep(2)
    n += 1
    rc = proc.poll()
    try:
        import socket
        s = socket.socket(); s.settimeout(1)
        pu = s.connect_ex(("127.0.0.1", PORT)) == 0
        s.close()
    except:
        pu = False
    if rc is None:
        print(f"  [HB-{n}] server=RUNNING (pid={proc.pid}) port-{PORT}={'UP' if pu else 'DOWN'} threads_ok", flush=True)
    else:
        print(f"  [supervisor] django exited rc={rc}, restarting...", flush=True)
        try: proc.kill()
        except: pass
        try:
            proc = subprocess.Popen(
                [PYTHON, "manage.py", "runserver", f"{HOST}:{PORT}", "--noreload"],
                cwd=DJANGO_DIR,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW,
                bufsize=0,
            )
            threading.Thread(target=reader, daemon=True).start()
            print(f"  [supervisor] re-launched with PID={proc.pid}", flush=True)
        except Exception as e:
            print(f"  [supervisor] re-launch failed: {e}", flush=True)
            time.sleep(5)
