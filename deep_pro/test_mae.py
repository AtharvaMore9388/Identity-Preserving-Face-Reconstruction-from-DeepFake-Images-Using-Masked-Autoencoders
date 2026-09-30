import torch
from reconstruction.mae_modules import MAEFaceReconstruction, IdentityLoss
import numpy as np

def test_mae_reconstruction():
    # 1. Setup parameters
    img_size = 224
    patch_size = 16
    batch_size = 2
    
    # 2. Create dummy input image (B, 3, 224, 224)
    image = torch.randn(batch_size, 3, img_size, img_size)
    
    # 3. Create dummy segmentation mask (B, 1, 224, 224)
    # Let's mask a square region in the middle for the first image
    mask = torch.zeros(batch_size, 1, img_size, img_size)
    mask[0, 0, 80:144, 80:144] = 1.0 # Masked region
    
    # For the second image, let's mask a different region
    mask[1, 0, 10:100, 10:100] = 1.0
    
    # 4. Initialize MAE model
    model = MAEFaceReconstruction(img_size=img_size, patch_size=patch_size)
    model.eval()
    
    # 5. Run forward pass
    with torch.no_grad():
        reconstructed_image = model(image, mask)
    
    # 6. Verify Identity Loss
    identity_loss_fn = IdentityLoss()
    loss = identity_loss_fn(reconstructed_image, image)
    print(f"Identity Loss: {loss.item()}")
    
    # 7. Verify output shape
    print(f"Input image shape: {image.shape}")
    print(f"Mask shape: {mask.shape}")
    print(f"Reconstructed image shape: {reconstructed_image.shape}")
    
    assert reconstructed_image.shape == image.shape, f"Output shape {reconstructed_image.shape} does not match input shape {image.shape}"
    print("Test passed: Output shape is correct.")

if __name__ == "__main__":
    print("Starting MAE test...")
    test_mae_reconstruction()
