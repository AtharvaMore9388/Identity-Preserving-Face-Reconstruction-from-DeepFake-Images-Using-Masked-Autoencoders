
import os, sys, time, socket, threading, traceback
LOG_CHILD = r"d:\Atharvac++\deep_next\_svc_child.log"
def clog(m):
    try:
        with open(LOG_CHILD, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] {m}\n")
    except: pass
try:
    clog("child start pid=" + str(os.getpid()))
    DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
    os.chdir(DJANGO_DIR)
    sys.path.insert(0, DJANGO_DIR)
    os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"
    import django
    django.setup()
    clog("django.setup OK")
    from django.core.wsgi import get_wsgi_application
    app = get_wsgi_application()
    from waitress.server import create_server
    srv = create_server(app, host="127.0.0.1", port=8081, threads=4, channel_timeout=900)
    clog("srv created, calling run()")
    def chb():
        while True:
            time.sleep(10)
            try:
                s = socket.socket(); s.settimeout(1)
                r = s.connect_ex(("127.0.0.1", 8081)) == 0
                s.close()
                clog(f"child-hb port-up={r}")
            except: pass
    threading.Thread(target=chb, daemon=True).start()
    srv.run()
except Exception as e:
    clog("FATAL: " + str(e))
    clog(traceback.format_exc())
    sys.exit(1)
