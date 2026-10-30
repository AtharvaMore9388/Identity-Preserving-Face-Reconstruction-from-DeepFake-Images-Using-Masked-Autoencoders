"""
Grad-CAM Based Inpainting Pipeline for Deepfake Restoration

Modules:
1. GradCAMExtractor: Proper gradient-weighted class activation mapping
2. MaskGenerator: Advanced binary mask generation with Otsu, morphology, CC analysis
3. UNetInpainter: U-Net reconstruction model
4. Blender: Poisson & alpha blending for seamless integration
5. ReconstructionMetrics: PSNR, SSIM, LPIPS, FID evaluation
"""

import os
import sys
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import defaultdict
from typing import Tuple, Optional, List, Dict

# ============================================================
# MODULE 1: GRAD-CAM EXTRACTOR (Proper gradient-based CAM)
# ============================================================

class GradCAMExtractor:
    """
    Grad-CAM: Gradient-weighted Class Activation Mapping
    Computes gradients of target class w.r.t. final conv feature maps,
    weights them by global average-pooled gradients, and produces a heatmap.
    """

    def __init__(self, model: nn.Module, target_layer: Optional[str] = None):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._register_hooks()

    def _register_hooks(self):
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        def forward_hook(module, input, output):
            self.activations = output

        target_module = None
        if self.target_layer:
            for name, module in self.model.named_modules():
                if name == self.target_layer:
                    target_module = module
                    break
        if target_module is None:
            # Auto-find last conv layer in the feature extractor
            if hasattr(self.model, 'model') and isinstance(self.model.model, nn.Sequential):
                for i in range(len(self.model.model) - 1, -1, -1):
                    if isinstance(self.model.model[i], nn.Conv2d) or \
                       isinstance(self.model.model[i], nn.Sequential):
                        target_module = self.model.model[i]
                        break
            if target_module is None:
                for name, module in self.model.named_modules():
                    if isinstance(module, nn.Conv2d):
                        target_module = module
        if target_module is None:
            raise ValueError("Could not find target conv layer for Grad-CAM")

        target_module.register_forward_hook(forward_hook)
        target_module.register_full_backward_hook(backward_hook)

    def generate(self, input_tensor: torch.Tensor, target_class: Optional[int] = None,
                 resize_to: Optional[Tuple[int, int]] = None) -> np.ndarray:
        """
        input_tensor: (1, C, H, W) or (1, seq, C, H, W) for sequential models
        Returns: Normalized heatmap in [0, 1], shape (H, W)
        """
        self.model.eval()
        device = next(self.model.parameters()).device

        # Handle sequential input (for ResNeXt+LSTM model in views.py)
        is_sequential = (input_tensor.dim() == 5)
        x = input_tensor.to(device)
        x.requires_grad = True

        self.model.zero_grad()
        fmap, logits = self.model(x)

        if target_class is None:
            target_class = torch.argmax(logits, dim=1).item()

        # Compute gradient of target class score w.r.t. activations
        one_hot = torch.zeros_like(logits)
        one_hot[0, target_class] = 1.0
        score = torch.sum(logits * one_hot)
        score.backward(retain_graph=True)

        if self.gradients is None or self.activations is None:
            # Fallback: use stored fmap + weight method
            return self._fallback_cam(fmap, logits, target_class, resize_to)

        # Grad-CAM: weight = global average pool of gradients
        grads = self.gradients  # (B, C_fm, H_fm, W_fm)
        activs = self.activations.detach()
        if grads.dim() > 4:
            grads = grads.view(-1, grads.shape[-3], grads.shape[-2], grads.shape[-1])
            activs = activs.view(-1, activs.shape[-3], activs.shape[-2], activs.shape[-1])

        weights = torch.mean(grads, dim=(2, 3), keepdim=True)  # (B, C_fm, 1, 1)
        cam = torch.sum(weights * activs, dim=1)  # (B, H_fm, W_fm)
        cam = torch.clamp(cam, min=0)  # ReLU

        cam_np = cam[0].detach().cpu().numpy()
        if cam_np.max() > 0:
            cam_np = cam_np - cam_np.min()
            cam_np = cam_np / (cam_np.max() + 1e-8)

        if resize_to:
            cam_np = cv2.resize(cam_np, resize_to)

        return cam_np

    def _fallback_cam(self, fmap, logits, target_class, resize_to):
        """Fallback: weight-based CAM (used when hooks don't fire on complex models)"""
        import numpy as np
        weight_softmax = None
        for name, param in self.model.named_parameters():
            if 'linear1.weight' in name:
                weight_softmax = param.detach().cpu().numpy()
                break
        if weight_softmax is None:
            # Approximate with random weights
            bz, nc, h, w = fmap.shape
            cam_np = np.mean(fmap[-1].detach().cpu().numpy(), axis=0)
        else:
            idx = target_class
            bz, nc, h, w = fmap.shape
            cam_np = np.dot(fmap[-1].detach().cpu().numpy().reshape((nc, h * w)).T,
                           weight_softmax[idx, :].T)
            cam_np = cam_np.reshape(h, w)
        cam_np = cam_np - cam_np.min()
        cam_np = cam_np / (cam_np.max() + 1e-8)
        if resize_to:
            cam_np = cv2.resize(cam_np, resize_to)
        return cam_np

    def generate_heatmap_overlay(self, image_bgr: np.ndarray, cam: np.ndarray,
                                 alpha: float = 0.5, beta: float = 0.5) -> np.ndarray:
        """Overlay heatmap on image. image_bgr: (H,W,3) uint8 BGR, cam: (H,W) float32 [0,1]"""
        h, w = image_bgr.shape[:2]
        cam_rs = cv2.resize(cam, (w, h))
        cam_uint8 = np.uint8(255 * cam_rs)
        heatmap = cv2.applyColorMap(cam_uint8, cv2.COLORMAP_JET)
        overlay = cv2.addWeighted(heatmap, alpha, image_bgr, beta, 0)
        return overlay


# ============================================================
# MODULE 2: BINARY MASK GENERATOR (Otsu + Morphology + CC)
# ============================================================

class MaskGenerator:
    """
    Converts Grad-CAM heatmap into a clean binary mask identifying manipulated pixels.
    Steps: Otsu thresholding -> morphological cleanup -> connected component filtering
    """

    @staticmethod
    def to_binary(heatmap: np.ndarray, method: str = 'otsu',
                  threshold: float = 0.5, dilate_iters: int = 2,
                  erode_iters: int = 0, min_component_ratio: float = 0.005,
                  kernel_size: int = 5) -> np.ndarray:
        """
        heatmap: (H, W) float in [0, 1] or uint8 [0,255]
        Returns: (H, W) uint8 binary mask (0/255)
        """
        if heatmap.max() <= 1.0:
            hm_uint8 = (heatmap * 255).astype(np.uint8)
        else:
            hm_uint8 = heatmap.astype(np.uint8)

        if method == 'otsu':
            _, binary = cv2.threshold(hm_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == 'adaptive':
            binary = cv2.adaptiveThreshold(hm_uint8, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY, 11, 2)
        elif method == 'fixed':
            t_val = int(threshold * 255) if threshold <= 1.0 else int(threshold)
            _, binary = cv2.threshold(hm_uint8, t_val, 255, cv2.THRESH_BINARY)
        else:
            t_val = int(threshold * 255) if threshold <= 1.0 else int(threshold)
            _, binary = cv2.threshold(hm_uint8, t_val, 255, cv2.THRESH_BINARY)

        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        if erode_iters > 0:
            binary = cv2.erode(binary, kernel, iterations=erode_iters)
        if dilate_iters > 0:
            binary = cv2.dilate(binary, kernel, iterations=dilate_iters)

        # Close operation to fill small holes
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        # Open operation to remove small speckles
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # Connected Component filtering: keep only largest significant regions
        h, w = binary.shape[:2]
        min_pixels = int(h * w * min_component_ratio)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        if num_labels > 1:
            areas = stats[1:, cv2.CC_STAT_AREA]
            valid_labels = [i + 1 for i, a in enumerate(areas) if a >= min_pixels]
            clean_mask = np.zeros_like(binary)
            for lbl in valid_labels:
                clean_mask[labels == lbl] = 255
            binary = clean_mask

        # Final dilate to expand mask slightly for border coverage
        binary = cv2.dilate(binary, kernel, iterations=1)
        return binary

    @staticmethod
    def to_soft_mask(binary_mask: np.ndarray, blur_kernel: int = 15,
                     blur_sigma: float = 5.0) -> np.ndarray:
        """Convert hard binary mask to soft float mask in [0,1] using Gaussian blur."""
        if binary_mask.max() > 1:
            mask_f = binary_mask.astype(np.float32) / 255.0
        else:
            mask_f = binary_mask.astype(np.float32)
        k = max(3, blur_kernel)
        if k % 2 == 0:
            k += 1
        soft = cv2.GaussianBlur(mask_f, (k, k), blur_sigma)
        soft = np.clip(soft, 0.0, 1.0)
        return soft

    @staticmethod
    def expand_mask(binary_mask: np.ndarray, border_px: int = 10) -> np.ndarray:
        """Expand mask by border_px pixels to cover manipulation edges."""
        kernel = np.ones((border_px * 2 + 1, border_px * 2 + 1), np.uint8)
        return cv2.dilate(binary_mask, kernel, iterations=1)

    @staticmethod
    def get_bbox(mask: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Return (x, y, w, h) bounding box of non-zero region, or None if empty."""
        coords = cv2.findNonZero(mask)
        if coords is None:
            return None
        return cv2.boundingRect(coords)


# ============================================================
# MODULE 3: U-NET INPAINTER (Alternative reconstruction model)
# ============================================================

class DoubleConv(nn.Module):
    def __init__(self, in_ch: int, out_ch: int, mid_ch: int = None):
        super().__init__()
        if mid_ch is None:
            mid_ch = out_ch
        self.conv = nn.Sequential(
            nn.Conv2d(in_ch, mid_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(mid_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(mid_ch, out_ch, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.conv(x)


class Down(nn.Module):
    def __init__(self, in_ch: int, out_ch: int):
        super().__init__()
        self.pool = nn.MaxPool2d(2)
        self.conv = DoubleConv(in_ch, out_ch)

    def forward(self, x):
        return self.conv(self.pool(x))


class Up(nn.Module):
    def __init__(self, in_ch: int, skip_ch: int, out_ch: int, bilinear: bool = True):
        super().__init__()
        if bilinear:
            self.up = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        else:
            self.up = nn.ConvTranspose2d(in_ch, in_ch // 2, 2, stride=2)
        self.conv = DoubleConv(in_ch // 2 + skip_ch, out_ch, in_ch // 2 + skip_ch)

    def forward(self, x, skip):
        x = self.up(x)
        diffY = skip.size(2) - x.size(2)
        diffX = skip.size(3) - x.size(3)
        x = F.pad(x, [diffX // 2, diffX - diffX // 2, diffY // 2, diffY - diffY // 2])
        x = torch.cat([skip, x], dim=1)
        return self.conv(x)


class UNetInpainter(nn.Module):
    """
    U-Net for inpainting: takes (image, mask) concatenated as 4-channel input.
    Reconstructs only the masked region. Image range: [0, 1].
    """

    def __init__(self, in_channels: int = 4, out_channels: int = 3,
                 base_dim: int = 64, bilinear: bool = True):
        super().__init__()
        self.in_conv = DoubleConv(in_channels, base_dim)
        self.down1 = Down(base_dim, base_dim * 2)
        self.down2 = Down(base_dim * 2, base_dim * 4)
        self.down3 = Down(base_dim * 4, base_dim * 8)
        factor = 2 if bilinear else 1
        self.down4 = Down(base_dim * 8, base_dim * 16 // factor)
        self.up1 = Up(base_dim * 16, base_dim * 8, base_dim * 8 // factor, bilinear)
        self.up2 = Up(base_dim * 8, base_dim * 4, base_dim * 4 // factor, bilinear)
        self.up3 = Up(base_dim * 4, base_dim * 2, base_dim * 2 // factor, bilinear)
        self.up4 = Up(base_dim * 2, base_dim, base_dim, bilinear)
        self.out_conv = nn.Conv2d(base_dim, out_channels, kernel_size=1)

    def forward(self, image: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """
        image: (B, 3, H, W) in [0, 1]
        mask:  (B, 1, H, W) in {0, 1}
        Returns: (B, 3, H, W) in [0, 1]
        """
        # Corrupt input: set masked pixels to 0 (or noise)
        corrupted = image * (1.0 - mask)
        x = torch.cat([corrupted, mask], dim=1)
        x1 = self.in_conv(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        return torch.sigmoid(self.out_conv(x))


class PartialConv2d(nn.Module):
    """Partial Convolution for inpainting (Liu et al. 2018)."""

    def __init__(self, in_ch: int, out_ch: int, kernel_size: int,
                 stride: int = 1, padding: int = 0, dilation: int = 1,
                 groups: int = 1, bias: bool = True):
        super().__init__()
        self.conv = nn.Conv2d(in_ch, out_ch, kernel_size, stride, padding, dilation, groups, bias=False)
        self.mask_conv = nn.Conv2d(in_ch, out_ch, kernel_size, stride, padding, dilation, groups, bias=False)
        torch.nn.init.constant_(self.mask_conv.weight, 1.0)
        for p in self.mask_conv.parameters():
            p.requires_grad = False
        self.bias = nn.Parameter(torch.zeros(out_ch), requires_grad=bias)
        self.kernel_size = kernel_size
        self.stride = stride
        self.padding = padding

    def forward(self, x, mask):
        with torch.no_grad():
            updated_mask = self.mask_conv(mask)
            mask_ratio = self.kernel_size ** 2 / (updated_mask + 1e-8)
            updated_mask = torch.clamp(updated_mask, 0, 1)
            mask_ratio = mask_ratio * updated_mask
        x = self.conv(x * mask)
        x = x * mask_ratio
        x = x + self.bias.view(1, -1, 1, 1)
        return x, updated_mask


# ============================================================
# MODULE 4: BLENDER (Poisson + improved alpha blending)
# ============================================================

class Blender:
    """Blend reconstructed region with original image seamlessly."""

    @staticmethod
    def alpha_blend(original_bgr: np.ndarray, reconstructed_bgr: np.ndarray,
                    soft_mask: np.ndarray) -> np.ndarray:
        """
        Alpha blending using soft mask.
        original_bgr, reconstructed_bgr: (H,W,3) uint8 BGR or float [0,1]
        soft_mask: (H,W) float [0,1]
        Returns uint8 BGR.
        """
        orig_f = original_bgr.astype(np.float32)
        rec_f = reconstructed_bgr.astype(np.float32)
        if orig_f.max() > 1.0:
            orig_f /= 255.0
            rec_f /= 255.0
        mask_3c = np.repeat(soft_mask[..., None], 3, axis=2)
        blended = rec_f * mask_3c + orig_f * (1.0 - mask_3c)
        return (np.clip(blended, 0.0, 1.0) * 255).astype(np.uint8)

    @staticmethod
    def poisson_blend(original_bgr: np.ndarray, reconstructed_bgr: np.ndarray,
                      binary_mask: np.ndarray, center: Optional[Tuple[int, int]] = None,
                      mode: int = cv2.MIXED_CLONE) -> np.ndarray:
        """
        Poisson blending (seamlessClone in OpenCV).
        binary_mask: (H,W) uint8 (0 or 255)
        center: (x, y) center of mask in destination. If None, use bbox center.
        """
        h, w = original_bgr.shape[:2]
        if binary_mask.max() <= 1:
            mask = (binary_mask * 255).astype(np.uint8)
        else:
            mask = binary_mask.astype(np.uint8)

        # Ensure mask has 3 channels for seamlessClone
        if mask.ndim == 2:
            mask_3c = np.repeat(mask[..., None], 3, axis=2)
        else:
            mask_3c = mask

        if center is None:
            coords = cv2.findNonZero(mask)
            if coords is None:
                return original_bgr.copy()
            bx, by, bw, bh = cv2.boundingRect(coords)
            cx = bx + bw // 2
            cy = by + bh // 2
        else:
            cx, cy = center

        try:
            # Ensure center is inside image bounds
            cx = np.clip(cx, 1, w - 2)
            cy = np.clip(cy, 1, h - 2)
            result = cv2.seamlessClone(reconstructed_bgr, original_bgr,
                                       mask_3c, (cx, cy), mode)
            return result
        except Exception as e:
            # Fallback to alpha blend
            print(f"[Poisson fallback] {e}")
            soft = MaskGenerator.to_soft_mask(mask, blur_kernel=15, blur_sigma=5)
            return Blender.alpha_blend(original_bgr, reconstructed_bgr, soft)

    @staticmethod
    def combine_blend(original_bgr: np.ndarray, reconstructed_bgr: np.ndarray,
                      binary_mask: np.ndarray, soft_mask: np.ndarray,
                      poisson_priority: bool = True) -> np.ndarray:
        """Try Poisson first, fall back to alpha blend."""
        if poisson_priority and np.count_nonzero(binary_mask) > 100:
            result = Blender.poisson_blend(original_bgr, reconstructed_bgr, binary_mask)
            # Validate result (poisson can return black in edge cases)
            if result.mean() > 5:
                return result
        return Blender.alpha_blend(original_bgr, reconstructed_bgr, soft_mask)


# ============================================================
# MODULE 5: RECONSTRUCTION QUALITY METRICS
# ============================================================

class ReconstructionMetrics:
    """
    Evaluate reconstruction quality against ground truth.
    Metrics: PSNR, SSIM, LPIPS, FID (perceptual).
    """

    @staticmethod
    def psnr(original: np.ndarray, reconstructed: np.ndarray,
             data_range: float = 255.0) -> float:
        """Peak Signal-to-Noise Ratio (higher = better)."""
        orig = original.astype(np.float64)
        rec = reconstructed.astype(np.float64)
        if orig.max() <= 1.0 and rec.max() <= 1.0:
            orig *= 255.0
            rec *= 255.0
            data_range = 255.0
        mse = np.mean((orig - rec) ** 2)
        if mse == 0:
            return float('inf')
        return 20.0 * np.log10(data_range / np.sqrt(mse))

    @staticmethod
    def ssim(original: np.ndarray, reconstructed: np.ndarray,
             window_size: int = 11, sigma: float = 1.5,
             data_range: float = 255.0) -> float:
        """Structural Similarity Index (closer to 1 = better). Uses luminance/contrast/structure."""
        orig = original.astype(np.float64)
        rec = reconstructed.astype(np.float64)
        if orig.max() <= 1.0 and rec.max() <= 1.0:
            orig *= 255.0
            rec *= 255.0
            data_range = 255.0

        def _ssim_single(ch1, ch2):
            C1 = (0.01 * data_range) ** 2
            C2 = (0.03 * data_range) ** 2
            kernel = cv2.getGaussianKernel(window_size, sigma)
            kernel = kernel @ kernel.T
            mu1 = cv2.filter2D(ch1, -1, kernel)
            mu2 = cv2.filter2D(ch2, -1, kernel)
            mu1_sq = mu1 * mu1
            mu2_sq = mu2 * mu2
            mu1_mu2 = mu1 * mu2
            sigma1_sq = cv2.filter2D(ch1 * ch1, -1, kernel) - mu1_sq
            sigma2_sq = cv2.filter2D(ch2 * ch2, -1, kernel) - mu2_sq
            sigma12 = cv2.filter2D(ch1 * ch2, -1, kernel) - mu1_mu2
            num = (2 * mu1_mu2 + C1) * (2 * sigma12 + C2)
            den = (mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2)
            return np.mean(num / den)

        if orig.ndim == 2:
            return _ssim_single(orig, rec)
        scores = []
        for c in range(orig.shape[2]):
            scores.append(_ssim_single(orig[..., c], rec[..., c]))
        return float(np.mean(scores))

    @staticmethod
    def masked_psnr(original: np.ndarray, reconstructed: np.ndarray,
                    mask: np.ndarray, data_range: float = 255.0) -> float:
        """PSNR computed only inside the masked (reconstructed) region."""
        orig = original.astype(np.float64)
        rec = reconstructed.astype(np.float64)
        if orig.max() <= 1.0 and rec.max() <= 1.0:
            orig *= 255.0
            rec *= 255.0
            data_range = 255.0
        if mask.max() <= 1:
            mask_b = mask > 0.5
        else:
            mask_b = mask > 127
        if mask_b.ndim == 2:
            mask_b3 = np.repeat(mask_b[..., None], 3, axis=0 if orig.ndim == 2 else 2)
        else:
            mask_b3 = mask_b
        if not np.any(mask_b3):
            return ReconstructionMetrics.psnr(original, reconstructed, data_range)
        diff = (orig - rec) ** 2
        mse = np.mean(diff[mask_b3])
        if mse == 0:
            return float('inf')
        return 20.0 * np.log10(data_range / np.sqrt(mse))

    @staticmethod
    def masked_ssim(original: np.ndarray, reconstructed: np.ndarray,
                    mask: np.ndarray) -> float:
        """SSIM computed only inside masked region."""
        if mask.max() <= 1:
            mask_b = mask > 0.5
        else:
            mask_b = mask > 127
        if not np.any(mask_b):
            return ReconstructionMetrics.ssim(original, reconstructed)
        coords = np.where(mask_b)
        ymin, ymax = max(0, coords[0].min() - 5), min(original.shape[0], coords[0].max() + 6)
        xmin, xmax = max(0, coords[1].min() - 5), min(original.shape[1], coords[1].max() + 6)
        return ReconstructionMetrics.ssim(
            original[ymin:ymax, xmin:xmax],
            reconstructed[ymin:ymax, xmin:xmax]
        )


class LPIPSEvaluator:
    """
    LPIPS: Learned Perceptual Image Patch Similarity (lower = better).
    Uses torchvision's pre-trained SqueezeNet features as a lightweight approximation
    if the official lpips package is not installed.
    """

    def __init__(self, device: str = 'cpu'):
        self.device = device
        self.model = None
        self.use_official = False
        try:
            import lpips
            self.model = lpips.LPIPS(net='vgg').to(device)
            self.use_official = True
            print("[LPIPS] Using official lpips library (VGG backbone).")
        except ImportError:
            print("[LPIPS] lpips not installed. Using torchvision feature approximation.")
            self._init_fallback()

    def _init_fallback(self):
        from torchvision import models
        vgg = models.vgg16(weights='DEFAULT').features
        # Use specific layer outputs similar to LPIPS
        self.layers = [3, 8, 15, 22]  # relu1_2, relu2_2, relu3_3, relu4_3
        self.extractor = nn.Sequential(*list(vgg.children())[:max(self.layers) + 1]).eval()
        for p in self.extractor.parameters():
            p.requires_grad = False
        self.extractor = self.extractor.to(self.device)
        self.weights = [1.0 / (2 ** i) for i in range(len(self.layers))]
        self.mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(self.device)
        self.std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(self.device)

    def __call__(self, image_a: np.ndarray, image_b: np.ndarray) -> float:
        """
        image_a, image_b: (H,W,3) uint8 BGR or float [0,1]
        Returns: LPIPS distance (float, lower is better).
        """
        a = self._to_tensor(image_a)
        b = self._to_tensor(image_b)
        a = a.to(self.device)
        b = b.to(self.device)
        if self.use_official:
            with torch.no_grad():
                d = self.model(a, b)
            return float(d.mean().item())
        return self._fallback_lpips(a, b)

    def _to_tensor(self, img: np.ndarray) -> torch.Tensor:
        f = img.astype(np.float32)
        if f.max() > 1.0:
            f /= 255.0
        # BGR -> RGB
        rgb = f[..., ::-1]
        t = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0)
        return t

    def _fallback_lpips(self, a, b):
        with torch.no_grad():
            a_n = (a - self.mean) / self.std
            b_n = (b - self.mean) / self.std
            total = 0.0
            x_a = a_n
            x_b = b_n
            layer_idx = 0
            target_idx = 0
            for module in self.extractor:
                x_a = module(x_a)
                x_b = module(x_b)
                if layer_idx == self.layers[target_idx]:
                    # Normalize each feature map
                    fa = F.normalize(x_a, dim=1)
                    fb = F.normalize(x_b, dim=1)
                    d = ((fa - fb) ** 2).mean(dim=[2, 3])
                    total += self.weights[target_idx] * d.mean().item()
                    target_idx += 1
                    if target_idx >= len(self.layers):
                        break
                layer_idx += 1
            return float(total)


class FIDEvaluator:
    """
    Approximate FID (Fréchet Inception Distance) using VGG features.
    Official FID requires InceptionV3; this uses VGG16 as a lightweight substitute.
    Lower score = more similar distributions.
    """

    def __init__(self, device: str = 'cpu'):
        self.device = device
        from torchvision import models
        vgg = models.vgg16(weights='DEFAULT')
        self.feature_extractor = nn.Sequential(*list(vgg.classifier.children())[:-1])
        self.full_vgg = vgg.features.to(device).eval()
        self.classifier_feat = self.feature_extractor.to(device).eval()
        self.avgpool = vgg.avgpool.to(device).eval()
        for p in list(self.full_vgg.parameters()) + list(self.classifier_feat.parameters()):
            p.requires_grad = False
        self.mean_t = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1).to(device)
        self.std_t = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1).to(device)

    @staticmethod
    def _calculate_frechet(mu1, sigma1, mu2, sigma2, eps: float = 1e-6):
        diff = mu1 - mu2
        covmean, _ = FIDEvaluator._sqrtm(sigma1 @ sigma2, eps)
        if not np.isfinite(covmean).all():
            offset = np.eye(sigma1.shape[0]) * eps
            covmean, _ = FIDEvaluator._sqrtm((sigma1 + offset) @ (sigma2 + offset), eps)
        tr_covmean = np.trace(covmean)
        return float(diff @ diff + np.trace(sigma1) + np.trace(sigma2) - 2 * tr_covmean)

    @staticmethod
    def _sqrtm(A, eps=1e-10):
        s, v = np.linalg.eigh(A)
        s = np.clip(s, eps, None)
        return (v * np.sqrt(s)) @ v.T, None

    def _extract_features(self, images: List[np.ndarray]) -> np.ndarray:
        feats = []
        for img in images:
            f = img.astype(np.float32)
            if f.max() > 1.0:
                f /= 255.0
            rgb = f[..., ::-1]
            t = torch.from_numpy(rgb).permute(2, 0, 1).unsqueeze(0).to(self.device)
            t = (t - self.mean_t) / self.std_t
            with torch.no_grad():
                fmap = self.full_vgg(t)
                pooled = self.avgpool(fmap).flatten(1)
                fc = self.classifier_feat(pooled)
            feats.append(fc.cpu().numpy().reshape(-1))
        return np.array(feats)

    def __call__(self, images_a: List[np.ndarray], images_b: List[np.ndarray]) -> float:
        """Compute FID between two sets of images (lists of HxWx3 arrays)."""
        fa = self._extract_features(images_a)
        fb = self._extract_features(images_b)
        mu1, sigma1 = fa.mean(axis=0), np.cov(fa, rowvar=False)
        mu2, sigma2 = fb.mean(axis=0), np.cov(fb, rowvar=False)
        return self._calculate_frechet(mu1, sigma1, mu2, sigma2)


# ============================================================
# END-TO-END PIPELINE (Convenience orchestration)
# ============================================================

class FullReconstructionPipeline:
    """
    Orchestrates the full flow:
    image + classifier -> Grad-CAM -> Binary Mask -> Reconstruction Model
          -> Blending -> Metrics (if GT available)
    """

    def __init__(self, classifier_model: nn.Module,
                 reconstruction_model: nn.Module,
                 device: str = 'cpu'):
        self.classifier = classifier_model.to(device)
        self.reconstructor = reconstruction_model.to(device)
        self.device = device
        self.gradcam = GradCAMExtractor(classifier_model)

    def run(self, face_image_bgr: np.ndarray, input_tensor: torch.Tensor,
            prediction_class: int, ground_truth_bgr: Optional[np.ndarray] = None,
            use_mae: bool = True) -> Dict:
        """
        face_image_bgr: (H,W,3) uint8 BGR cropped face
        input_tensor: the transformed tensor fed to the classifier (for Grad-CAM)
        prediction_class: 0 = fake, 1 = real (only run if FAKE)
        ground_truth_bgr: optional original authentic image for metrics
        Returns dict with keys: binary_mask, soft_mask, cam_heatmap,
                               reconstructed_img, blended_result, metrics
        """
        h, w = face_image_bgr.shape[:2]
        target_size = (224, 224)
        face_resized = cv2.resize(face_image_bgr, target_size)

        # 1. Grad-CAM
        cam = self.gradcam.generate(input_tensor, target_class=prediction_class,
                                    resize_to=target_size)
        heatmap_overlay = self.gradcam.generate_heatmap_overlay(face_resized, cam)

        # 2. Binary Mask (Otsu + Morphology + CC)
        binary_mask = MaskGenerator.to_binary(cam, method='otsu', dilate_iters=2)
        binary_mask = cv2.resize(binary_mask, target_size, interpolation=cv2.INTER_NEAREST)
        if np.count_nonzero(binary_mask) == 0:
            # Fallback if Otsu gave empty result: use 0.5 threshold
            binary_mask = MaskGenerator.to_binary(cam, method='fixed',
                                                  threshold=0.5, dilate_iters=3)
        binary_mask = MaskGenerator.expand_mask(binary_mask, border_px=5)
        soft_mask = MaskGenerator.to_soft_mask(binary_mask, blur_kernel=15, blur_sigma=5)

        # 3. Prepare tensors for reconstructor
        face_rgb = cv2.cvtColor(face_resized, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        img_t = torch.from_numpy(face_rgb).permute(2, 0, 1).unsqueeze(0).to(self.device)
        mask_t = torch.from_numpy((binary_mask > 127).astype(np.float32)).unsqueeze(0).unsqueeze(0).to(self.device)

        # 4. Reconstruction
        self.reconstructor.eval()
        with torch.no_grad():
            if use_mae:
                rec_t = self.reconstructor(img_t, mask_t)
            else:
                # U-Net / Partial Conv path
                rec_t = self.reconstructor(img_t, mask_t)
        rec_np = rec_t.squeeze(0).permute(1, 2, 0).cpu().numpy()
        rec_np = np.clip(rec_np, 0.0, 1.0)
        rec_bgr = cv2.cvtColor((rec_np * 255).astype(np.uint8), cv2.COLOR_RGB2BGR)

        # 4b. Keep authentic pixels: reconstruct ONLY where mask says
        authentic = face_resized.copy()
        mask_b = binary_mask > 127
        if mask_b.ndim == 2:
            mask_b3 = np.repeat(mask_b[..., None], 3, axis=2)
        else:
            mask_b3 = mask_b
        region_only_bgr = authentic.copy()
        region_only_bgr[mask_b3] = rec_bgr[mask_b3]

        # 5. Blending
        blended_bgr = Blender.combine_blend(face_resized, region_only_bgr,
                                            binary_mask, soft_mask,
                                            poisson_priority=True)

        # 6. Metrics (if GT provided)
        metrics = {}
        if ground_truth_bgr is not None:
            gt = cv2.resize(ground_truth_bgr, target_size)
            metrics['PSNR_full'] = ReconstructionMetrics.psnr(gt, blended_bgr)
            metrics['SSIM_full'] = ReconstructionMetrics.ssim(gt, blended_bgr)
            metrics['PSNR_masked'] = ReconstructionMetrics.masked_psnr(gt, blended_bgr, binary_mask)
            metrics['SSIM_masked'] = ReconstructionMetrics.masked_ssim(gt, blended_bgr, binary_mask)

            try:
                lpips_fn = LPIPSEvaluator(self.device)
                metrics['LPIPS'] = lpips_fn(gt, blended_bgr)
            except Exception as e:
                metrics['LPIPS_error'] = str(e)

        return {
            'cam': cam,
            'heatmap_overlay': heatmap_overlay,
            'binary_mask': binary_mask,
            'soft_mask': soft_mask,
            'reconstruction_raw': rec_bgr,
            'region_only': region_only_bgr,
            'blended_result': blended_bgr,
            'metrics': metrics
        }
