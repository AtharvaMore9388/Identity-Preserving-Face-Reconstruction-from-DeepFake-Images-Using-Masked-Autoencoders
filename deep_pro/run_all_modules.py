import torch
import cv2
import numpy as np
import os
from reconstruction.mae_modules import MAEFaceReconstruction, IdentityLoss
from torchvision import transforms

import sys

def run_all_modules():
    print("--- Starting Pipeline: Run All Modules ---")
    sys.stdout.flush()
    try:
        print("Implementation based on:")
        print("1. DFREC (arXiv:2412.07260v2, Mar 2025)")
        print("2. FRG2D with Residual Outlook Attention (ACM Trans. 2025)")
        sys.stdout.flush()
        
        # Paths
        base_path = r"c:\Users\Acer\Downloads\deep_pro\deepfake_vid\Deepfake_detection_using_deep_learning-master\Django Application\uploaded_images"
        image_path = os.path.join(base_path, "uploaded_file_1770921109_cropped_face.png")
        
        print(f"Checking for image at: {image_path}")
        sys.stdout.flush()
        if not os.path.exists(image_path):
            print(f"Error: Image not found at {image_path}")
            sys.stdout.flush()
            return

        # 1. Module 1: Identity Segmentation (Simulated)
        print("Module 1: Generating Identity Segmentation Map (Simulated)...")
        sys.stdout.flush()
        original_img = cv2.imread(image_path)
        if original_img is None:
            print(f"Error: Failed to load image at {image_path}")
            sys.stdout.flush()
            return
        original_img = cv2.resize(original_img, (224, 224))
        
        # Simulate a manipulation map (mask) where 1 is fake and 0 is real
        mask = np.zeros((224, 224, 1), dtype=np.float32)
        mask[120:180, 70:150, 0] = 1.0 # Simulated fake region
        
        # Convert to Tensors
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.ToTensor(),
        ])
        
        img_tensor = transform(cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)).unsqueeze(0) # (1, 3, 224, 224)
        mask_tensor = torch.from_numpy(mask).permute(2, 0, 1).unsqueeze(0) # (1, 1, 224, 224)
        
        # 2. Module 2 & 3 & 4: MAE Architecture
        print("Module 2: Identity-Aware Patching & Masking...")
        print("Module 3: Feature Extraction (SIRM Encoder)...")
        print("Module 4: Reconstruction (TIRM Decoder)...")
        sys.stdout.flush()
        
        model = MAEFaceReconstruction(img_size=224, patch_size=16)
        model.eval()
        
        print("Running model inference...")
        sys.stdout.flush()
        with torch.no_grad():
            reconstructed_tensor = model(img_tensor, mask_tensor)
        print("Model inference complete.")
        sys.stdout.flush()
        
        # 3. Identity Alignment Verification
        print("Identity Alignment: Calculating Identity Loss...")
        sys.stdout.flush()
        identity_loss_fn = IdentityLoss()
        loss = identity_loss_fn(reconstructed_tensor, img_tensor)
        
        # 4. Results
        print("\n--- Pipeline Results ---")
        print(f"Input Image: {os.path.basename(image_path)}")
        print(f"Masked Pixels (Fake Region): {int(mask_tensor.sum().item())}")
        print(f"Reconstructed Image Shape: {reconstructed_tensor.shape}")
        print(f"Identity Loss (Alignment): {loss.item():.4f}")
        print("\nPipeline execution completed successfully.")
        sys.stdout.flush()
    except Exception as e:
        print(f"\nCRITICAL ERROR in pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.stdout.flush()

if __name__ == "__main__":
    print("SCRIPT START")
    run_all_modules()
    print("SCRIPT END")
