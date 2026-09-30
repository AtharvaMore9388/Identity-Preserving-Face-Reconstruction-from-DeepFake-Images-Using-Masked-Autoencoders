import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)

# Quick inline dependency check - prints immediately
import importlib
from importlib.metadata import version as _v, PackageNotFoundError

CHECK = [
    ("Django", "django", "5.0.6"),
    ("numpy", "numpy", "1.26.4"),
    ("opencv-python", "cv2", "4.10.0.84"),
    ("torch", "torch", "2.3.1"),
    ("torchvision", "torchvision", "0.18.1"),
    ("Pillow", "PIL", "10.3.0"),
    ("face-recognition", "face_recognition", "1.3.0"),
    ("dlib", "dlib", "19.24.2"),
    ("pandas", "pandas", "2.2.2"),
    ("matplotlib", "matplotlib", "3.9.0"),
    ("tensorflow / keras", None, None),
    ("waitress", "waitress", None),
]

print("="*80, flush=True)
print("CORE DEPENDENCY CHECK (CRITICAL FOR DEEPFAKE DETECTION APP)", flush=True)
print(f"Python {sys.version.splitlines()[0]}", flush=True)
print("="*80, flush=True)

missing = []
mismatch = []
ok = []

for pkg, mod, req in CHECK:
    if mod is None:
        try:
            import tensorflow
            ver = getattr(tensorflow, "__version__", "unknown")
            print(f"  ✅ {pkg:25s} TF installed: {ver}", flush=True)
            ok.append(pkg)
        except Exception:
            try:
                import keras
                ver = getattr(keras, "__version__", "unknown")
                print(f"  ✅ keras installed: {ver}", flush=True)
                ok.append(pkg)
            except Exception:
                print(f"  ⚠️  tensorflow/keras (optional) — NOT INSTALLED", flush=True)
                missing.append(pkg)
        continue

    try:
        m = importlib.import_module(mod)
    except Exception:
        if req:
            print(f"  ❌ {pkg:25s} required=={req}  —  **NOT INSTALLED**", flush=True)
        else:
            print(f"  ❌ {pkg:25s} NOT INSTALLED", flush=True)
        missing.append(pkg)
        continue

    try:
        v = _v(pkg)
    except PackageNotFoundError:
        v = getattr(m, "__version__", "unknown")
    except Exception:
        v = getattr(m, "__version__", "unknown")

    if req and v != req and "unknown" not in v.lower():
        print(f"  ⚠️  {pkg:25s} required=={req}, installed: {v}  (MISMATCH)", flush=True)
        mismatch.append((pkg, req, v))
    else:
        print(f"  ✅ {pkg:25s} installed: {v}", flush=True)
        ok.append(pkg)

print("", flush=True)
print("-"*80, flush=True)
print(f"SUMMARY: OK={len(ok)}  MISMATCH={len(mismatch)}  MISSING={len(missing)}", flush=True)
if missing:
    print(f"MISSING packages: {', '.join(missing)}", flush=True)
if mismatch:
    print(f"MISMATCH packages: {', '.join(x[0] for x in mismatch)}", flush=True)
print("="*80, flush=True)
