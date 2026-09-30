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

print("=== PHASE 4: GCP + Misc ===")
m, o = 0, 0
checks = [
    ("MarkupSafe","markupsafe","2.1.5"),
    ("mistune","mistune","3.0.2"),
    ("nbconvert","nbconvert","7.16.4"),
    ("nbformat","nbformat","5.10.4"),
    ("packaging","packaging","24.1"),
    ("pyasn1","pyasn1","0.6.0"),
    ("pyasn1-modules","pyasn1_modules","0.4.0"),
    ("pycodestyle","pycodestyle","2.12.0"),
    ("Pygments","pygments","2.18.0"),
    ("pyparsing","pyparsing","3.1.2"),
    ("pyrsistent","pyrsistent","0.20.0"),
    ("python-dateutil","dateutil","2.9.0"),
    ("pywinpty","winpty", None),  # placeholder, won't import
    ("pyzmq","zmq","26.0.3"),
    ("rsa","rsa","4.9"),
    ("s3transfer","s3transfer","0.10.2"),
    ("Send2Trash","send2trash","1.8.3"),
    ("six","six","1.16.0"),
    ("soupsieve","soupsieve","2.5"),
    ("sqlparse","sqlparse","0.5.0"),
    ("terminado","terminado","0.18.1"),
    ("testpath","testpath","0.6.0"),
    ("toml","toml","0.10.2"),
    ("toolz","toolz","0.12.1"),
    ("traitlets","traitlets","5.14.3"),
    ("tzlocal","tzlocal","5.2"),
    ("uritemplate","uritemplate","4.1.1"),
    ("urllib3","urllib3","2.2.2"),
    ("validators","validators","0.28.3"),
    ("watchdog","watchdog","4.0.1"),
    ("wcwidth","wcwidth","0.2.13"),
    ("webencodings","webencodings","0.5.1"),
    ("widgetsnbextension","widgetsnbextension","4.0.11"),
    ("google-api-core","google.api_core","2.19.1"),
    ("google-api-python-client","googleapiclient","2.134.0"),
    ("google-auth","google.auth","2.30.0"),
    ("google-auth-httplib2","google_auth_httplib2","0.2.0"),
    ("googleapis-common-protos","google.api","1.63.2"),
]
for p in checks:
    a,b = check(*p)
    m += a; o += b
print(f"PHASE4: OK={o} MISMATCH/MISSING={m}", flush=True)
