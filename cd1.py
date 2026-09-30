import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import importlib
from importlib.metadata import version as _v, PackageNotFoundError

def check(pkg, mod, req=None, label=""):
    lbl = label or pkg
    try:
        importlib.import_module(mod)
        try:
            v = _v(pkg)
        except Exception:
            v = "ok"
        if req and v != req and "ok" != v:
            print(f"MM {lbl:28s} req={req:14s} inst={v}", flush=True)
            return 1, 0
        print(f"OK {lbl:28s} {v}", flush=True)
        return 0, 1
    except Exception:
        print(f"XX {lbl:28s} NOT INSTALLED", flush=True)
        return 1, 0

print("=== PHASE 1 ===")
m, o = 0, 0
checks = [
    ("Django","django","5.0.6"),
    ("numpy","numpy","1.26.4"),
    ("opencv-python","cv2","4.10.0.84"),
    ("torch","torch","2.3.1"),
    ("torchvision","torchvision","0.18.1"),
    ("Pillow","PIL","10.3.0"),
    ("pandas","pandas","2.2.2"),
    ("matplotlib","matplotlib","3.9.0"),
    ("PyYAML","yaml","6.0.1"),
    ("requests","requests","2.32.3"),
]
for p in checks:
    a,b = check(*p)
    m += a; o += b
print(f"PHASE1: OK={o} MISMATCH/MISSING={m}")
sys.stdout.flush()
