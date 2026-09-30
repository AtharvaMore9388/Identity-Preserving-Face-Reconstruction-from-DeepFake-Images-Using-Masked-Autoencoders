import os, sys, subprocess

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
CREATE_BREAKAWAY_FROM_JOB = 0x01000000
NORMAL_PRIORITY_CLASS = 0x00000020
FLAGS = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP | CREATE_BREAKAWAY_FROM_JOB | NORMAL_PRIORITY_CLASS

PORT = 8000
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

proc = subprocess.Popen(
    [sys.executable, "-u", TARGET],
    cwd=os.path.dirname(TARGET),
    env=env,
    creationflags=FLAGS,
)
print(f"FIRED PID={proc.pid} PORT={PORT} (CREATE_BREAKAWAY_FROM_JOB)")
print(f"URL: http://127.0.0.1:{PORT}/")
print("Launcher exiting now — child survives independently.")
sys.stdout.flush()
sys.exit(0)
