print("Testing imports...")
try:
    import torch
    print("torch imported")
    import cv2
    print("cv2 imported")
    import numpy as np
    print("numpy imported")
    from torchvision import transforms
    print("torchvision imported")
    from reconstruction.mae_modules import MAEFaceReconstruction, IdentityLoss
    print("reconstruction.mae_modules imported")
    print("All imports successful")
except Exception as e:
    print(f"Import failed: {e}")
    import traceback
    traceback.print_exc()
