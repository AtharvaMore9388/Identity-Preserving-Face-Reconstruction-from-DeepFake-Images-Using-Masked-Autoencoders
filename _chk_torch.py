import os, sys, time
LOG = r"d:\Atharvac++\deep_next\_torch_check.log"
def L(s):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("[%H:%M:%S] ") + s + "\n")
try: open(LOG, "w").close()
except: pass
try:
    L("Importing torch...")
    import torch
    L(f"torch OK: " + torch.__version__)
    L(f"CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        L(f"CUDA device: {torch.cuda.get_device_name(0)}")
        L(f"CUDA version: {torch.version.cuda}")
    x = torch.rand(3, 3)
    L(f"torch smoke test OK, tensor shape = {x.shape}")
except Exception as e:
    L(f"torch FAIL: {e}")
try:
    L("Importing torchvision...")
    import torchvision
    from torchvision import transforms, models
    L(f"torchvision OK: {torchvision.__version__}")
    m = models.resnet18(weights=None)
    L(f"resnet18 build OK")
except Exception as e:
    L(f"torchvision FAIL: {e}")
L("DONE")
