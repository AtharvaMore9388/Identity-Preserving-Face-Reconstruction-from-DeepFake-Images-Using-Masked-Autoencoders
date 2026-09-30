import urllib.request, socket, sys

OUT_FILE = r"d:\Atharvac++\deep_next\check_server_result.txt"
with open(OUT_FILE, "w", encoding="utf-8") as f:
    def P(m):
        f.write(str(m) + "\n")
        f.flush()

    P("=== Process check ===")
    try:
        import subprocess
        out = subprocess.check_output(["tasklist", "/FI", "PID eq 20344", "/FO", "CSV"]).decode(errors="replace")
        for line in out.strip().splitlines():
            P(line)
    except Exception as e:
        P(f"tasklist failed: {e}")

    P("\n=== Port 8000 check ===")
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect(("127.0.0.1", 8000))
        P(f"CONNECT OK to 127.0.0.1:8000")
        s.close()
    except Exception as e:
        P(f"Connect failed: {e}")

    P("\n=== HTTP GET / ===")
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/")
        with urllib.request.urlopen(req, timeout=10) as resp:
            P(f"Status: {resp.status}")
            P(f"Content-Type: {resp.headers.get('Content-Type')}")
            body = resp.read()
            P(f"Body length: {len(body)} bytes")
            P(f"First 500 chars:")
            P(body[:500].decode(errors="replace"))
    except Exception as e:
        P(f"HTTP FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc(file=f)

    P("\n=== Server status log ===")
    SRV_LOG = r"d:\Atharvac++\deep_next\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application\server_status.log"
    try:
        with open(SRV_LOG, "r", encoding="utf-8") as sf:
            P(sf.read())
    except Exception as e:
        P(f"Failed to read server log: {e}")
