import sys, os, time
sys.path.insert(0, r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application")
os.environ["DJANGO_SETTINGS_MODULE"] = "project_settings.settings"

LOG = r"d:\Atharvac++\deep_next\_full_check.log"
def L(s):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("[%H:%M:%S] ") + s + "\n")
    except: pass

try: open(LOG, "w").close()
except: pass

L("=== DEP + INTEGRITY CHECK START ===")

results = {}

def CHECK(name, fn):
    try:
        L(f"[TEST] {name} ...")
        result = fn()
        L(f"[PASS] {name}: {result}")
        results[name] = ("OK", result)
    except Exception as e:
        L(f"[FAIL] {name}: {e}")
        import traceback
        L(traceback.format_exc())
        results[name] = ("FAIL", str(e))

# ---------- 1. Core libraries ----------
def chk_django():
    import django
    return django.get_version()
CHECK("1. Django", chk_django)

def chk_numpy():
    import numpy as np
    return np.__version__
CHECK("2. NumPy", chk_numpy)

def chk_cv2():
    import cv2
    return cv2.__version__
CHECK("3. OpenCV", chk_cv2)

def chk_pil():
    from PIL import Image
    return Image.__version__
CHECK("4. Pillow", chk_pil)

def chk_matplotlib():
    import matplotlib
    return matplotlib.__version__
CHECK("5. Matplotlib", chk_matplotlib)

def chk_sklearn():
    import sklearn
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix
    return sklearn.__version__
CHECK("6. Scikit-learn", chk_sklearn)

# ---------- 2. ML libraries (slow, might timeout) ----------
def chk_torch():
    import torch
    v = torch.__version__
    cuda = torch.cuda.is_available()
    return f"{v} CUDA={cuda}"
CHECK("7. PyTorch", chk_torch)

def chk_torchvision():
    import torchvision
    from torchvision import transforms, models
    return torchvision.__version__
CHECK("8. TorchVision", chk_torchvision)

# ---------- 3. Face libraries ----------
def chk_dlib():
    import dlib
    v = getattr(dlib, '__version__', 'compiled')
    return v
CHECK("9. dlib", chk_dlib)

def chk_face_rec():
    import face_recognition
    return "available"
CHECK("10. face_recognition", chk_face_rec)

# ---------- 4. Server ----------
def chk_waitress():
    import waitress
    return "available"
CHECK("11. Waitress WSGI", chk_waitress)

# ---------- 5. Optional ----------
def chk_lpips():
    import lpips
    return "available"
CHECK("12. LPIPS (optional)", chk_lpips)

def chk_scipy():
    import scipy
    return scipy.__version__
CHECK("13. SciPy (optional)", chk_scipy)

def chk_pandas():
    import pandas
    return pandas.__version__
CHECK("14. Pandas (optional)", chk_pandas)

# ---------- 6. Django setup + DB ----------
def chk_django_setup():
    import django
    django.setup()
    from django.conf import settings
    return f"DEBUG={settings.DEBUG} DB={settings.DATABASES['default']['ENGINE']}"
CHECK("15. Django.setup()", chk_django_setup)

def chk_db_migrate():
    import django
    django.setup()
    from django.core.management import call_command
    from io import StringIO
    out = StringIO()
    call_command('showmigrations', stdout=out, verbosity=0)
    txt = out.getvalue()
    applied = txt.count('[X]')
    pending = txt.count('[ ]')
    return f"applied={applied} pending={pending}"
CHECK("16. DB Migrations", chk_db_migrate)

def chk_django_check():
    import django
    django.setup()
    from django.core.management import call_command
    from io import StringIO, stderr
    out = StringIO()
    err = StringIO()
    try:
        call_command('check', stdout=out, stderr=err, verbosity=1)
        return "PASS"
    except SystemExit as e:
        return "ISSUE: " + err.getvalue()[:200]
CHECK("17. Django System Check", chk_django_check)

# ---------- 7. Models exist ----------
def chk_model_files():
    import os
    mdir = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application\models"
    files = [f for f in os.listdir(mdir) if f.endswith('.pt') or f.endswith('.pth')]
    sizes = {f: os.path.getsize(os.path.join(mdir, f)) for f in files}
    summary = ", ".join(f"{f}({s//1024//1024}MB)" for f,s in sizes.items())
    return f"{len(files)} model files: {summary[:200]}"
CHECK("18. ML Model Files", chk_model_files)

# ---------- 8. Reconstruction module imports ----------
def chk_reconstruction():
    from reconstruction import (
        GradCAMExtractor, MaskGenerator, Blender,
        ReconstructionMetrics, LPIPSEvaluator, FullReconstructionPipeline,
        MAEFaceReconstruction, IdentityLoss,
    )
    return "all 8 classes imported"
CHECK("19. Reconstruction module", chk_reconstruction)

def chk_mask_generator():
    import numpy as np
    from reconstruction.mask_generator import MaskGenerator
    h = np.random.rand(100, 100).astype(np.float32)
    b = MaskGenerator.to_binary(h, method='otsu')
    s = MaskGenerator.to_soft_mask(b)
    e = MaskGenerator.expand_mask(b, border_px=5)
    return f"binary={b.shape} dtype={b.dtype}, soft={s.shape}, expanded={e.shape}"
CHECK("20. MaskGenerator smoke test", chk_mask_generator)

def chk_blender():
    import numpy as np
    from reconstruction.blender import Blender
    a = (np.random.rand(224, 224, 3) * 255).astype(np.uint8)
    b = (np.random.rand(224, 224, 3) * 255).astype(np.uint8)
    mask = np.zeros((224, 224), dtype=np.uint8)
    mask[80:144, 80:144] = 255
    soft = mask.astype(np.float32) / 255.0
    r = Blender.combine_blend(a, b, mask, soft, poisson_priority=False)
    return f"output shape={r.shape} dtype={r.dtype}"
CHECK("21. Blender smoke test", chk_blender)

def chk_metrics():
    import numpy as np
    from reconstruction.metrics import ReconstructionMetrics
    a = (np.random.rand(100, 100, 3) * 255).astype(np.uint8)
    b = a.copy()
    psnr = ReconstructionMetrics.psnr(a, b)
    ssim = ReconstructionMetrics.ssim(a, b)
    return f"PSNR(identical)={psnr:.2f} SSIM(identical)={ssim:.4f}"
CHECK("22. Metrics smoke test (PSNR/SSIM)", chk_metrics)

# ---------- 9. URL / app config ----------
def chk_urls():
    import django
    django.setup()
    from django.urls import get_resolver
    r = get_resolver()
    patterns = []
    def collect(resolver, prefix=''):
        for p in resolver.url_patterns:
            name = getattr(p, 'name', None)
            if name:
                patterns.append(prefix + str(p.pattern) + " -> " + name)
    collect(r)
    return f"{len(patterns)} named URLs: " + ", ".join(patterns[:5])
CHECK("23. URL Resolver", chk_urls)

# ---------- Summary ----------
L("")
L("=" * 50)
L("SUMMARY")
L("=" * 50)
ok = sum(1 for v in results.values() if v[0] == "OK")
fa = sum(1 for v in results.values() if v[0] == "FAIL")
L(f"TOTAL: {len(results)} | PASS: {ok} | FAIL: {fa}")
if fa > 0:
    L("FAILED TESTS:")
    for k, (s, v) in results.items():
        if s == "FAIL":
            L(f"  - {k}: {v[:300]}")
else:
    L(">>> ALL CHECKS PASSED! Project is ready to run.")
L("=" * 50)
L("CHECK COMPLETE")
sys.exit(0 if fa == 0 else 1)
