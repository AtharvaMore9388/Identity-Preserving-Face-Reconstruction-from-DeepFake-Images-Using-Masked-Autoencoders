import sys, importlib

REQUIRED = [
    ('Django', 'django', '5.x'),
    ('numpy', 'numpy', '1.26.4'),
    ('opencv-python', 'cv2', '4.x'),
    ('torch', 'torch', '2.3.x'),
    ('torchvision', 'torchvision', '0.18.x'),
    ('Pillow', 'PIL', '10.x'),
    ('matplotlib', 'matplotlib', '3.x'),
    ('face-recognition', 'face_recognition', '1.3.x'),
    ('dlib', 'dlib', '19.24.x'),
    ('scikit-learn', 'sklearn', 'any'),
    ('waitress', 'waitress', 'any'),
    ('lpips', 'lpips', 'optional'),
    ('scipy', 'scipy', 'optional'),
    ('pandas', 'pandas', 'optional'),
    ('timm', 'timm', 'optional'),
]

print('='*60)
print('  DEEPFAKE DETECTION APP - DEPENDENCY CHECK')
print('='*60)
print(f'Python: {sys.version}')
print(f'Platform: {sys.platform}')
print()

ok, warn, fail = [], [], []
for pkg_name, mod_name, ver_req in REQUIRED:
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
        print(f'  [OK]   {pkg_name:<20} -> {mod_name:<18} ver={ver}')
        ok.append((pkg_name, ver))
    except ImportError as e:
        if ver_req == 'optional':
            print(f'  [WARN] {pkg_name:<20} -> NOT INSTALLED (optional)')
            warn.append((pkg_name, str(e)))
        else:
            print(f'  [FAIL] {pkg_name:<20} -> NOT INSTALLED: {e}')
            fail.append((pkg_name, str(e)))

print()
print('='*60)
print(f'  SUMMARY: OK={len(ok)}  WARN={len(warn)}  FAIL={len(fail)}')
print('='*60)
if fail:
    print('MISSING CRITICAL PACKAGES:')
    for p,e in fail: print(f'  - {p}: {e}')
    print()
    print('TO INSTALL: pip install ' + ' '.join(p for p,_ in fail))
if warn:
    print()
    print('OPTIONAL (missing advanced features):')
    for p,e in warn: print(f'  - {p}: {e}')
if not fail:
    print()
    print('>>> ALL CRITICAL DEPENDENCIES ARE INSTALLED!')
print()

print('-'*60)
print('  ADDITIONAL CHECKS')
print('-'*60)

try:
    import torch
    cuda_ok = torch.cuda.is_available()
    print(f'  CUDA available: {cuda_ok}')
    if cuda_ok:
        print(f'  CUDA device: {torch.cuda.get_device_name(0)}')
        print(f'  CUDA version: {torch.version.cuda}')
    else:
        print(f'  (CPU mode will be used - slower inference)')
except Exception as e:
    print(f'  CUDA check failed: {e}')
print()

try:
    import numpy as np
    import cv2
    print(f'  NumPy: {np.__version__}')
    print(f'  OpenCV: {cv2.__version__}')
    a = np.zeros((10,10,3), dtype=np.uint8)
    b = cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
    print(f'  NumPy+OpenCV compat test: OK')
except Exception as e:
    print(f'  NumPy/OpenCV compat test FAILED: {e}')
print()

try:
    import dlib
    v = getattr(dlib, '__version__', 'compiled')
    print(f'  dlib: OK (ver={v})')
except Exception as e:
    print(f'  dlib: FAIL - {e}')

try:
    import face_recognition
    print(f'  face_recognition: OK')
except Exception as e:
    print(f'  face_recognition: FAIL - {e}')

try:
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    print(f'  sklearn.metrics (classification metrics): OK')
except Exception as e:
    print(f'  sklearn.metrics: FAIL - {e}')

try:
    import waitress
    print(f'  waitress (WSGI server): OK')
except Exception as e:
    print(f'  waitress: FAIL - {e}')

print()
print('='*60)
sys.exit(0 if not fail else 1)
