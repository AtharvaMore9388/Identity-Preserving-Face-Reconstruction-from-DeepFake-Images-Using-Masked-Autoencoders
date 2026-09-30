import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import importlib
from importlib.metadata import version as _v

def check(pkg, mod, req=None):
    try:
        importlib.import_module(mod)
        try:
            v = _v(pkg)
        except Exception:
            v = "ok"
        if req and v != req and "ok" != v:
            print(f"MM {pkg:28s} req={req:14s} inst={v}", flush=True)
            return 1, 0
        print(f"OK {pkg:28s} {v}", flush=True)
        return 0, 1
    except Exception:
        print(f"XX {pkg:28s} NOT INSTALLED", flush=True)
        return 1, 0

print("=== PHASE 2: ML / Face ===")
m, o = 0, 0
checks = [
    ("face-recognition","face_recognition","1.3.0"),
    ("face-recognition-models","face_recognition_models","0.3.0"),
    ("dlib","dlib","19.24.2"),
    ("tornado","tornado","6.4.1"),
    ("jinja2","jinja2","3.1.4"),
    ("JupyterLab","jupyterlab","4.2.2"),
    ("notebook","notebook","7.2.1"),
    ("ipython","IPython","8.12.3"),
    ("ipykernel","ipykernel","6.29.4"),
    ("ipywidgets","ipywidgets","8.1.3"),
]
for p in checks:
    a,b = check(*p)
    m += a; o += b
print(f"PHASE2: OK={o} MISMATCH/MISSING={m}", flush=True)
