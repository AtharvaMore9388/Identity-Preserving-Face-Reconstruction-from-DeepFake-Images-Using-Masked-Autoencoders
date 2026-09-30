import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
import importlib
from importlib.metadata import version as _v

def check(pkg, mod, req=None, label=""):
    lbl = label or pkg
    try:
        importlib.import_module(mod)
        try:
            v = _v(pkg)
        except Exception:
            v = "ok"
        if req and v != req and "ok" != v:
            print(f"MM {lbl:30s} req={req:14s} inst={v}", flush=True)
            return 1, 0
        print(f"OK {lbl:30s} {v}", flush=True)
        return 0, 1
    except Exception:
        print(f"XX {lbl:30s} NOT INSTALLED", flush=True)
        return 1, 0

print("=== PHASE 3: Google Cloud / AWS / Utils ===")
m, o = 0, 0
checks = [
    ("altair","altair","5.3.0"),
    ("asgiref","asgiref","3.8.1"),
    ("astor","astor","0.8.1"),
    ("attrs","attrs","23.2.0"),
    ("base58","base58","2.1.1"),
    ("bleach","bleach","6.1.0"),
    ("blinker","blinker","1.8.2"),
    ("cachetools","cachetools","5.3.3"),
    ("certifi","certifi","2024.6.2"),
    ("chardet","chardet","5.2.0"),
    ("click","click","8.1.7"),
    ("colorama","colorama","0.4.6"),
    ("cycler","cycler","0.12.1"),
    ("decorator","decorator","5.1.1"),
    ("defusedxml","defusedxml","0.7.1"),
    ("docutils","docutils","0.21.2"),
    ("httplib2","httplib2","0.22.0"),
    ("idna","idna","3.7"),
    ("jsonschema","jsonschema","4.22.0"),
    ("kiwisolver","kiwisolver","1.4.5"),
]
for p in checks:
    a,b = check(*p)
    m += a; o += b
print(f"PHASE3: OK={o} MISMATCH/MISSING={m}", flush=True)
