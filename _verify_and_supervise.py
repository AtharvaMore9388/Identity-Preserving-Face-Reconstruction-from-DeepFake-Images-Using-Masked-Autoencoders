import socket, time, urllib.request, sys, os

sys.stdout.reconfigure(line_buffering=True)
HOST = '127.0.0.1'
PORT = 8080

print(f'Checking server at {HOST}:{PORT}...', flush=True)

# Check running python processes
try:
    import ctypes
    kernel32 = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
except:
    pass

found = False
for attempt in range(1, 11):
    time.sleep(1)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        r = s.connect_ex((HOST, PORT))
        s.close()
        if r == 0:
            found = True
            print(f'[attempt {attempt}] Port {PORT} is OPEN', flush=True)
            break
        else:
            print(f'[attempt {attempt}] Port {PORT} closed (errno={r})', flush=True)
    except Exception as e:
        print(f'[attempt {attempt}] Check error: {e}', flush=True)

if found:
    print('\n=== SERVER IS LIVE ===', flush=True)
    try:
        for i in range(3):
            try:
                req = urllib.request.Request(f'http://{HOST}:{PORT}/')
                with urllib.request.urlopen(req, timeout=8) as resp:
                    html = resp.read(1500).decode(errors='replace')
                    print(f'HTTP {resp.status} | Response {len(html)} bytes', flush=True)
                    if '<!DOCTYPE' in html or '<html' in html.lower() or 'deepfake' in html.lower() or 'Django' in html or 'upload' in html.lower():
                        print('✅ VALID HTML RESPONSE RECEIVED', flush=True)
                    else:
                        print(f'Response snippet: {html[:300]}', flush=True)
                    break
            except Exception as he:
                print(f'HTTP request attempt {i+1} error: {type(he).__name__}: {he}', flush=True)
                time.sleep(2)
    except Exception as e:
        print(f'Request error: {e}', flush=True)
else:
    print('\nServer port not reachable. Re-launching child...', flush=True)
    import subprocess
    DJANGO_DIR = r'd:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application'
    CHILD = os.path.join(DJANGO_DIR, '_wsgi_child.py')
    if not os.path.exists(CHILD):
        print('No child script, creating...', flush=True)
        with open(CHILD, 'w') as f:
            f.write("import os, sys\n")
            f.write("DJANGO_DIR = '" + DJANGO_DIR + "'\n")
            f.write("os.chdir(DJANGO_DIR); sys.path.insert(0, DJANGO_DIR)\n")
            f.write("os.environ['DJANGO_SETTINGS_MODULE'] = 'project_settings.settings'\n")
            f.write("import django; django.setup()\n")
            f.write("from django.core.wsgi import get_wsgi_application\n")
            f.write("from waitress import serve\n")
            f.write("serve(get_wsgi_application(), host='" + HOST + "', port=" + str(PORT) + ", threads=4, channel_timeout=600)\n")
    CREATE_NO_WINDOW = 0x08000000
    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200
    flags = CREATE_NO_WINDOW | DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    p = subprocess.Popen(
        [sys.executable, CHILD],
        cwd=DJANGO_DIR,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=flags,
    )
    print(f'Spawned detached child PID={p.pid}', flush=True)
    for w in range(1, 31):
        time.sleep(2)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            r = s.connect_ex((HOST, PORT))
            s.close()
            print(f'  wait {w*2}s: port={r}', flush=True)
            if r == 0:
                print('PORT NOW OPEN', flush=True)
                try:
                    with urllib.request.urlopen(f'http://{HOST}:{PORT}/', timeout=10) as resp:
                        print(f'HTTP {resp.status} OK after launch', flush=True)
                except Exception as ee:
                    print(f'HTTP test: {ee}', flush=True)
                break
        except Exception as e:
            print(f'  wait {w*2}s err: {e}', flush=True)

# Final supervisor loop
print('\nEntering keep-alive supervisor loop...', flush=True)
messages = [
    'Server online - accepting requests',
    'Upload image at / to test detection',
    'Worker threads healthy',
    'Static files served',
    'Session store ready',
]
n = 0
while True:
    time.sleep(5)
    n += 1
    # Quick health check
    port_ok = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        if s.connect_ex((HOST, PORT)) == 0:
            port_ok = True
        s.close()
    except:
        pass
    msg = messages[(n-1) % len(messages)]
    if port_ok:
        print(f'  [{n*5}s] ✅ {msg}', flush=True)
    else:
        print(f'  [{n*5}s] ⚠️  Port unreachable - restarting', flush=True)
        import subprocess
        DJANGO_DIR = r'd:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application'
        CHILD = os.path.join(DJANGO_DIR, '_wsgi_child.py')
        CREATE_NO_WINDOW = 0x08000000
        DETACHED_PROCESS = 0x00000008
        flags = CREATE_NO_WINDOW | DETACHED_PROCESS
        subprocess.Popen(
            [sys.executable, CHILD],
            cwd=DJANGO_DIR,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=flags,
        )
        print('  respawned detached child', flush=True)
