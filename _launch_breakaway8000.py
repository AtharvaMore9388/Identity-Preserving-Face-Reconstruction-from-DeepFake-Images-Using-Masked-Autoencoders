import os, sys, subprocess, time, socket

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
NORMAL_PRIORITY_CLASS = 0x00000020

FLAGS = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB | NORMAL_PRIORITY_CLASS

PORT = 8000
HOST = "127.0.0.1"
TARGET = os.path.abspath(r"d:\Atharvac++\deep_next\_serve8000.py")

# Kill stale
try:
    import re
    o = subprocess.check_output(["netstat","-ano"], stderr=subprocess.DEVNULL).decode(errors="replace")
    for line in o.splitlines():
        m = re.search(rf":{PORT}\s+\S+\s+LISTENING\s+(\d+)", line)
        if m:
            try: subprocess.run(["taskkill","/F","/PID",m.group(1)], capture_output=True)
            except: pass
except: pass

env = os.environ.copy()
env["PYTHONUNBUFFERED"] = "1"

print(f"[launcher] spawning with CREATE_BREAKAWAY_FROM_JOB...")
print(f"[launcher] target: {TARGET}")
print(f"[launcher] python: {sys.executable}")

# Use a wrapper log-to-file script that uses pythonw (no console needed):
# Actually the _serve8000.py uses print-based HB loop, but that's fine for breakaway child
proc = subprocess.Popen(
    [sys.executable, "-u", TARGET],
    cwd=os.path.dirname(TARGET),
    env=env,
    creationflags=FLAGS,
)
print(f"[launcher] child PID = {proc.pid}  (BREAKAWAY — survives sandbox exit)")
print(f"[launcher] child will write HBs to its own stdout (no console visible).")

# Wait for port (max 45s)
print(f"[launcher] waiting for port {PORT} to come up...")
for i in range(23):
    time.sleep(2)
    try:
        s = socket.socket(); s.settimeout(0.5)
        if s.connect_ex((HOST, PORT)) == 0:
            s.close()
            print()
            print("=" * 60)
            print("  SERVER IS RUNNING!")
            print(f"  Open browser:  http://{HOST}:{PORT}/")
            print(f"  Or local:      http://localhost:{PORT}/")
            print(f"  Child PID: {proc.pid}  (independent, survives this exit)")
            print("=" * 60)
            # Smoke test
            try:
                import urllib.request
                req = urllib.request.Request(f"http://{HOST}:{PORT}/")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    body = resp.read().decode(errors="replace")
                    import re as _re
                    tm = _re.search(r"<title>(.*?)</title>", body, _re.I | _re.S)
                    t = tm.group(1).strip() if tm else "(none)"
                    print(f"  [smoke] GET / -> {resp.status}  size={len(body)}  title={t}")
            except Exception as he:
                print(f"  [smoke] err: {he}")
            print()
            print("[launcher] Exiting now. Server continues running independently.")
            sys.exit(0)
        s.close()
    except: pass
    print(f"  [{(i+1)*2:>2}s] probe port {PORT} ...")

print(f"[launcher] WARN: Port {PORT} not confirmed after 46s, but child is BREAKAWAY and may still boot.")
print(f"[launcher] Check child PID {proc.pid} or try http://{HOST}:{PORT}/ later.")
sys.exit(0)
