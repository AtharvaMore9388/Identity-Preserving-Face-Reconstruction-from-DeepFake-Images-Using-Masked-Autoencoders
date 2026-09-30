import importlib
import sys
import os
import re
from importlib.metadata import version as _get_version, PackageNotFoundError

REQ_FILE = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application\requirements.txt"
OUT_FILE = r"d:\Atharvac++\deep_next\dependency_check.txt"

lines_out = []

def P(msg=""):
    lines_out.append(msg)

def safe_import(modname, pkgname):
    try:
        mod = importlib.import_module(modname)
    except Exception:
        return None, None
    try:
        v = _get_version(pkgname)
        return mod, v
    except PackageNotFoundError:
        return mod, getattr(mod, "__version__", "unknown")
    except Exception:
        return mod, getattr(mod, "__version__", "unknown")

IMPORT_MAP = {
    "opencv-python": "cv2",
    "face-recognition": "face_recognition",
    "face-recognition-models": None,
    "pyyaml": "yaml",
    "pillow": "PIL",
    "torch": "torch",
    "torchvision": "torchvision",
    "pywinpty": None,
    "enum-compat": "enum_compat",
    "google-auth": "google.auth",
    "google-auth-httplib2": "google_auth_httplib2",
    "google-api-core": "google.api_core",
    "google-api-python-client": "googleapiclient",
    "googleapis-common-protos": "google.api",
    "pyasn1-modules": "pyasn1_modules",
    "prompt-toolkit": "prompt_toolkit",
    "ipython-genutils": "IPython_genutils",
    "python-dateutil": "dateutil",
    "send2trash": "send2trash",
    "jupyter-client": "jupyter_client",
    "jupyter-core": "jupyter_core",
    "jupyterlab": None,
    "jupyterlab-server": "jupyterlab_server",
    "notebook": None,
    "pydeck": "pydeck",
    "dlib": "dlib",
    "cmake": None,
    "watchdog": "watchdog",
    "pathtools": "pathtools",
    "s3transfer": "s3transfer",
    "cachetools": "cachetools",
    "base58": "base58",
    "tornado": "tornado",
    "pyzmq": "zmq",
    "terminado": "terminado",
    "prometheus-client": "prometheus_client",
    "validators": "validators",
    "widgetsnbextension": None,
    "pywin32": None,
    "pytz": "pytz",
}

P("="*90)
P(f"DEPENDENCY CHECK REPORT  ({__import__('datetime').datetime.now()})")
P(f"Python: {sys.version.splitlines()[0]}")
P(f"Executable: {sys.executable}")
P("="*90)
P("")

counts = {"OK": 0, "MISMATCH": 0, "MISSING": 0, "INFO": 0}

with open(REQ_FILE, "r", encoding="utf-8") as f:
    lines = f.read().splitlines()

for line in lines:
    raw = line.strip()
    if not raw or raw.startswith("#"):
        P(f"   {raw}")
        continue

    m = re.match(r"^([A-Za-z0-9_.\-]+)\s*(===|==|>=|<=|>|<|~=)?\s*([A-Za-z0-9_.\-+]+)?", raw)
    if not m:
        P(f"   [SKIP] Cannot parse: {raw}")
        continue
    pkg = m.group(1)
    op = m.group(2) or ""
    req_v = m.group(3) or ""

    key = pkg.lower()
    mod_name = IMPORT_MAP.get(key)
    if mod_name is None and key not in IMPORT_MAP:
        mod_name = key.lower().replace("-", "_").replace(".", "_")

    if mod_name is None:
        counts["INFO"] += 1
        P(f" ℹ️  [INFO   ] {pkg:30s} CLI/data-only package (not importable)")
        continue

    mod, inst_v = safe_import(mod_name, pkg)
    if mod is None:
        counts["MISSING"] += 1
        if req_v:
            P(f" ❌ [MISSING] {pkg:30s} required {op}{req_v}  —  **NOT INSTALLED**")
        else:
            P(f" ❌ [MISSING] {pkg:30s} **NOT INSTALLED**")
        continue

    status = "OK"
    marker = "✅"
    note = f"installed {inst_v}"
    if req_v and op in ("==", "==="):
        if inst_v != req_v and "unknown" not in inst_v.lower():
            status = "MISMATCH"
            marker = "⚠️ "
            note = f"required {op}{req_v}, installed {inst_v}"
            counts["MISMATCH"] += 1
        else:
            counts["OK"] += 1
    else:
        counts["OK"] += 1

    P(f" {marker} [{status:7s}] {pkg:30s} {note}")

P("")
P("="*90)
P("SUMMARY:")
for k in ("OK", "MISMATCH", "MISSING", "INFO"):
    P(f"  {k:10s} : {counts.get(k, 0)}")
P("="*90)

with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(lines_out) + "\n")

print("\n".join(lines_out))
print()
print(f"Report saved to: {OUT_FILE}")
