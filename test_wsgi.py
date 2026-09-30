import os, sys, traceback, io

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

LOG_FILE = os.path.join(DJANGO_DIR, "wsgiref_server_log.txt")

with open(LOG_FILE, "w", encoding="utf-8") as log:
    def L(msg):
        log.write(str(msg) + "\n")
        log.flush()
        print(msg)

    L(f"Start: {__import__('datetime').datetime.now()}")
    L(f"Python: {sys.version}")

    try:
        import django
        L(f"Django: {django.get_version()}")
        django.setup()
        L("Django.setup() OK")

        from django.core.wsgi import get_wsgi_application
        app = get_wsgi_application()
        L("WSGI app OK")

        # Test that the app responds to a basic request
        L("Testing WSGI with a basic GET / ...")
        from io import BytesIO
        def fake_start_response(status, headers):
            L(f"  Response status: {status}")
            L(f"  Response headers: {headers[:5]}")
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': '8000',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.input': BytesIO(b''),
            'wsgi.errors': sys.stderr,
            'wsgi.version': (1, 0),
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
            'wsgi.url_scheme': 'http',
        }
        result = app(environ, fake_start_response)
        body = b"".join(result)
        L(f"  Response body length: {len(body)} bytes")
        L(f"  First 500 chars: {body[:500].decode(errors='replace')}")
        L("WSGI test passed!")

    except Exception as e:
        L(f"[ERROR] {type(e).__name__}: {e}")
        L(traceback.format_exc())
        sys.exit(1)
