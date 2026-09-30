import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import importlib
from importlib.metadata import version as _v

def chk(pkg, mod, req=None):
    try:
        importlib.import_module(mod)
        try: v = _v(pkg)
        except Exception: v = "ok"
        if req and v != req and v != "ok":
            print(f"MM {pkg} req={req} inst={v}", flush=True)
        else:
            print(f"OK {pkg} {v}", flush=True)
    except Exception as e:
        print(f"XX {pkg} MISSING ({type(e).__name__})", flush=True)

chk("torch","torch","2.3.1")
chk("torchvision","torchvision","0.18.1")
