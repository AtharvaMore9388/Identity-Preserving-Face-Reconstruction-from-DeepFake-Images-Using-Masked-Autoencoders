import os
import sys
import traceback

DJANGO_DIR = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application"
OUTPUT_FILE = os.path.join(DJANGO_DIR, "debug_run_output.txt")

def log(msg):
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
        f.flush()

if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)

os.chdir(DJANGO_DIR)
sys.path.insert(0, DJANGO_DIR)
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

log(f"Starting: {__import__('datetime').datetime.now()}")

# Check directories
from project_settings.settings import STATIC_ROOT, STATICFILES_DIRS, MEDIA_ROOT, PROJECT_DIR
log(f"PROJECT_DIR: {PROJECT_DIR}  exists: {os.path.exists(PROJECT_DIR)}")
log(f"MEDIA_ROOT: {MEDIA_ROOT}  exists: {os.path.exists(MEDIA_ROOT)}")
log(f"STATIC_ROOT: {STATIC_ROOT}  exists: {os.path.exists(STATIC_ROOT)}")
for d in STATICFILES_DIRS:
    log(f"STATICFILES_DIR: {d}  exists: {os.path.exists(d)}")

# Create MEDIA_ROOT if missing
if not os.path.exists(MEDIA_ROOT):
    try:
        os.makedirs(MEDIA_ROOT)
        log(f"Created MEDIA_ROOT: {MEDIA_ROOT}")
    except Exception as e:
        log(f"Failed to create MEDIA_ROOT: {e}")

try:
    import django
    django.setup()
    log("Django setup OK")

    from django.core.management import call_command
    log("Calling runserver --nostatic on 0.0.0.0:8000 ...")
    call_command('runserver', '0.0.0.0:8000', '--noreload', '--nostatic', verbosity=3)

except SystemExit as e:
    log(f"SystemExit: code={e.code}")
except Exception as e:
    log(f"EXCEPTION: {type(e).__name__}: {e}")
    log(traceback.format_exc())
log("Script finished.")
