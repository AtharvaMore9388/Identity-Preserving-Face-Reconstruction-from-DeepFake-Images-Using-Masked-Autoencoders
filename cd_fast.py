import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import importlib
from importlib.metadata import version as _v

def check(pkg, mod, req=None):
    try:
        importlib.import_module(mod)
        try: v = _v(pkg)
        except Exception: v = "ok"
        if req and v != req and v != "ok":
            print(f"MM {pkg:25s} req={req:14s} inst={v}", flush=True)
            return "MISMATCH"
        print(f"OK {pkg:25s} {v}", flush=True)
        return "OK"
    except Exception:
        print(f"XX {pkg:25s} NOT INSTALLED", flush=True)
        return "MISSING"

print("=== CRITICAL ML / FACE PACKAGES ===")
results = []
results.append(check("torch","torch","2.3.1"))
results.append(check("torchvision","torchvision","0.18.1"))
results.append(check("dlib","dlib","19.24.2"))
results.append(check("face-recognition","face_recognition","1.3.0"))
results.append(check("face-recognition-models","face_recognition_models","0.3.0"))
results.append(check("Pillow","PIL","10.3.0"))
results.append(check("matplotlib","matplotlib","3.9.0"))
results.append(check("pandas","pandas","2.2.2"))
results.append(check("waitress","waitress", None))
results.append(check("jinja2","jinja2","3.1.4"))
print("done", flush=True)
