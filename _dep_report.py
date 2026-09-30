import sys, importlib, time, os

LOG = r"d:\Atharvac++\deep_next\_dep_report.log"

def log(s):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(s + "\n")
    print(s, flush=True)

try: open(LOG, "w").close()
except: pass

REQUIRED = [
    ('Django', 'django'),
    ('numpy', 'numpy'),
    ('opencv-python', 'cv2'),
    ('torch', 'torch'),
    ('torchvision', 'torchvision'),
    ('Pillow', 'PIL'),
    ('matplotlib', 'matplotlib'),
    ('face-recognition', 'face_recognition'),
    ('dlib', 'dlib'),
    ('scikit-learn', 'sklearn'),
    ('waitress', 'waitress'),
    ('lpips', 'lpips'),
    ('scipy', 'scipy'),
    ('pandas', 'pandas'),
    ('timm', 'timm'),
]

log("="*60)
log("  DEEPFAKE DETECTION - DEPENDENCY REPORT")
log("  " + time.strftime("%Y-%m-%d %H:%M:%S"))
log("="*60)
log(f"Python: {sys.version}")
log(f"Platform: {sys.platform}")
log(f"Executable: {sys.executable}")
log("")

ok, warn, fail = [], [], []
CRITICAL = {'Django','numpy','opencv-python','torch','torchvision','Pillow','face-recognition','dlib','scikit-learn','waitress'}

for pkg_name, mod_name in REQUIRED:
    is_optional = pkg_name not in CRITICAL
    t0 = time.time()
    try:
        mod = importlib.import_module(mod_name)
        ver = getattr(mod, '__version__', 'N/A')
        if mod_name == 'PIL':
            from PIL import Image
            ver = getattr(Image, '__version__', ver)
        if mod_name == 'cv2':
            ver = getattr(mod, '__version__', ver)
        if mod_name == 'sklearn':
            import sklearn
            ver = getattr(sklearn, '__version__', ver)
        if mod_name == 'face_recognition':
            ver = 'installed'
        dt = time.time() - t0
        log(f"  [OK]   {pkg_name:<20} ver={ver:<12} ({dt:.1f}s)")
        ok.append((pkg_name, ver))
    except Exception as e:
        dt = time.time() - t0
        if is_optional:
            log(f"  [WARN] {pkg_name:<20} NOT INSTALLED (optional, {dt:.1f}s)")
            warn.append((pkg_name, str(e)))
        else:
            log(f"  [FAIL] {pkg_name:<20} NOT INSTALLED - {e} ({dt:.1f}s)")
            fail.append((pkg_name, str(e)))

log("")
log("="*60)
log(f"  SUMMARY: OK={len(ok)}  WARN={len(warn)}  FAIL={len(fail)}")
log("="*60)

if fail:
    log("")
    log("*** MISSING CRITICAL PACKAGES - MUST INSTALL ***")
    for p,e in fail:
        log(f"  - {p}: {e}")
    log("")
    log("Install command:")
    log("  pip install " + " ".join(p for p,_ in fail))
else:
    log("")
    log(">>> ALL CRITICAL DEPENDENCIES ARE INSTALLED!")

if warn:
    log("")
    log("Optional packages missing (some features reduced):")
    for p,e in warn:
        log(f"  - {p}: {e}")

log("")
log("-"*60)
log("  ENVIRONMENT DETAILS")
log("-"*60)

try:
    import torch
    log(f"  PyTorch: {torch.__version__}")
    cuda = torch.cuda.is_available()
    log(f"  CUDA available: {cuda}")
    if cuda:
        log(f"  CUDA device: {torch.cuda.get_device_name(0)}")
        log(f"  CUDA version: {torch.version.cuda}")
        log(f"  cuDNN version: {torch.backends.cudnn.version()}")
    else:
        log("  (Running on CPU - inference will be slower)")
except Exception as e:
    log(f"  Torch/CUDA check: FAIL - {e}")

try:
    import numpy as np
    import cv2
    log(f"  NumPy: {np.__version__}")
    log(f"  OpenCV: {cv2.__version__}")
    a = np.zeros((10,10,3), dtype=np.uint8)
    b = cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
    log(f"  NumPy<->OpenCV compat: PASS")
except Exception as e:
    log(f"  NumPy/OpenCV test: FAIL - {e}")

try:
    import dlib
    v = getattr(dlib, '__version__', 'built')
    log(f"  dlib: OK (ver={v})")
    try:
        log(f"  dlib DLIB_USE_CUDA: {dlib.DLIB_USE_CUDA}")
    except: pass
except Exception as e:
    log(f"  dlib: FAIL - {e}")

try:
    import face_recognition
    log(f"  face_recognition: OK")
except Exception as e:
    log(f"  face_recognition: FAIL - {e}")

try:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    log(f"  sklearn.metrics: OK")
except Exception as e:
    log(f"  sklearn.metrics: FAIL - {e}")

try:
    import waitress
    log(f"  waitress WSGI: OK")
except Exception as e:
    log(f"  waitress: FAIL - {e}")

log("")
log("="*60)
log("  REPORT COMPLETE. Exit: " + ("0 (all good)" if not fail else "1 (issues found)"))
log("="*60)
sys.exit(0 if not fail else 1)
