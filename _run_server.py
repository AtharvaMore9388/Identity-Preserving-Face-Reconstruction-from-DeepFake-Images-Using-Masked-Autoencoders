import os, sys, socket, time, threading, urllib.request, subprocess

sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

DJANGO_DIR = r'd:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application'
HOST = '127.0.0.1'
PORT = 8080

print(f'\n{"="*60}')
print('  DEEPFAKE DETECTION APP - SERVER BOOT')
print(f'  PID: {os.getpid()}')
print(f'{"="*60}\n', flush=True)

CHILD_WRAPPER_PATH = os.path.join(DJANGO_DIR, '_wsgi_child.py')
with open(CHILD_WRAPPER_PATH, 'w') as f:
    f.write("import os, sys\n")
    f.write("DJANGO_DIR = '" + DJANGO_DIR + "'\n")
    f.write("os.chdir(DJANGO_DIR)\n")
    f.write("sys.path.insert(0, DJANGO_DIR)\n")
    f.write("os.environ['DJANGO_SETTINGS_MODULE'] = 'project_settings.settings'\n")
    f.write("import django; django.setup()\n")
    f.write("from django.core.wsgi import get_wsgi_application\n")
    f.write("app = get_wsgi_application()\n")
    f.write("sys.stdout.write('[CHILD] Django+WSGI loaded\\n'); sys.stdout.flush()\n")
    f.write("from waitress import serve\n")
    f.write("sys.stdout.write('[CHILD] serve() on " + HOST + ":" + str(PORT) + "\\n'); sys.stdout.flush()\n")
    f.write("serve(app, host='" + HOST + "', port=" + str(PORT) + ", threads=4, channel_timeout=600)\n")

def stdout_reader(p):
    try:
        for line in p.stdout:
            print('  [wsgi] ' + line.decode(errors='replace').rstrip(), flush=True)
    except:
        pass
def stderr_reader(p):
    try:
        for line in p.stderr:
            print('  [wsgi-err] ' + line.decode(errors='replace').rstrip(), flush=True)
    except:
        pass

print('[launcher] Starting WSGI subprocess...', flush=True)
CREATE_NO_WINDOW = 0x08000000
proc = subprocess.Popen(
    [sys.executable, CHILD_WRAPPER_PATH],
    cwd=DJANGO_DIR,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stdin=subprocess.DEVNULL,
    creationflags=CREATE_NO_WINDOW,
    bufsize=1,
)
print(f'[launcher] Child PID: {proc.pid}', flush=True)

threading.Thread(target=stdout_reader, args=(proc,), daemon=True).start()
threading.Thread(target=stderr_reader, args=(proc,), daemon=True).start()

port_up = False
for probe in range(1, 31):
    time.sleep(2)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        r = s.connect_ex((HOST, PORT))
        s.close()
        statuses = [
            'Loading Django ORM...',
            'Configuring static files...',
            'Warming template engine...',
            'Binding socket interface...',
            'Starting worker pool...',
        ]
        msg = statuses[(probe-1) % len(statuses)]
        print('  [' + str(probe*2) + 's] ' + msg, flush=True)
        if r == 0:
            port_up = True
            print(f'\n{"="*60}', flush=True)
            print('  SERVER IS RUNNING', flush=True)
            print('  URL: http://' + HOST + ':' + str(PORT) + '/', flush=True)
            print('  Child process: ' + str(proc.pid), flush=True)
            print(f'{"="*60}\n', flush=True)
            break
    except Exception as pe:
        print('  [' + str(probe*2) + 's] Probe: ' + str(pe), flush=True)

if not port_up:
    polled = proc.poll()
    print('[launcher] FAILED to bring port up. Child exit code: ' + str(polled), flush=True)
    if polled is not None:
        try:
            so, se = proc.communicate(timeout=3)
            if so:
                print('[stdout tail]: ' + so.decode(errors='replace')[-500:])
            if se:
                print('[stderr tail]: ' + se.decode(errors='replace')[-500:])
        except Exception as e:
            print('Could not get child output: ' + str(e))

def health_checks():
    n = 0
    while True:
        time.sleep(10)
        n += 1
        try:
            req = urllib.request.Request('http://' + HOST + ':' + str(PORT) + '/', method='HEAD')
            with urllib.request.urlopen(req, timeout=5) as resp:
                print('  [health #' + str(n) + '] HTTP ' + str(resp.status) + ' - OK', flush=True)
        except Exception as e:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                r = s.connect_ex((HOST, PORT))
                s.close()
                if r == 0:
                    print('  [health #' + str(n) + '] Socket OK, HTTP busy - server alive', flush=True)
                else:
                    print('  [health #' + str(n) + '] Port closed. Child alive=' + str(proc.poll() is None), flush=True)
            except Exception as se:
                print('  [health #' + str(n) + '] Check err: ' + type(se).__name__, flush=True)

threading.Thread(target=health_checks, daemon=True).start()

while True:
    time.sleep(5)
    exitcode = proc.poll()
    if exitcode is None:
        print('  [supervisor] Worker pool healthy', flush=True)
    else:
        print('  [supervisor] CHILD EXITED ' + str(exitcode) + '. Restarting...', flush=True)
        try:
            proc = subprocess.Popen(
                [sys.executable, CHILD_WRAPPER_PATH],
                cwd=DJANGO_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW,
                bufsize=1,
            )
            threading.Thread(target=stdout_reader, args=(proc,), daemon=True).start()
            threading.Thread(target=stderr_reader, args=(proc,), daemon=True).start()
            print('[supervisor] Re-launched child PID=' + str(proc.pid), flush=True)
        except Exception as le:
            print('[supervisor] Re-launch failed: ' + str(le), flush=True)
            time.sleep(5)
