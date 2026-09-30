import numpy as np
import cv2


class MaskGenerator:
    """Robust binary + soft mask generation from a normalized Grad-CAM /
    attention heatmap. Uses Otsu thresholding, morphological cleanup, and
    connected-component speckle removal."""

    @staticmethod
    def to_binary(heatmap_norm,
                  method='otsu',
                  threshold=0.5,
                  dilate_iters=2,
                  erode_iters=0,
                  kernel_size=3,
                  min_component_ratio=0.005):
        """
        Args:
            heatmap_norm (np.ndarray): float32 [0,1] heatmap, shape (H, W)
            method: 'otsu' (auto) or 'fixed' (uses threshold param)
            threshold: used for 'fixed' method in [0,1]
            dilate_iters / erode_iters: morphological ops on binary mask
            kernel_size: morphological kernel size (odd, >= 1)
            min_component_ratio: drop CCs smaller than this fraction of total pixels
        Returns:
            np.ndarray of uint8 values {0, 255} shape (224, 224)
        """
        if heatmap_norm is None:
            raise ValueError("heatmap_norm is None")
        if heatmap_norm.ndim != 2:
            heatmap_norm = heatmap_norm.squeeze()
            if heatmap_norm.ndim != 2:
                raise ValueError(f"Expected 2D heatmap, got shape {heatmap_norm.shape}")

        heatmap_norm = np.clip(heatmap_norm.astype(np.float32), 0.0, 1.0)
        img = np.uint8(heatmap_norm * 255)
        img = cv2.resize(img, (224, 224), interpolation=cv2.INTER_CUBIC)

        k = int(kernel_size)
        if k % 2 == 0:
            k += 1
        if k < 3:
            k = 3
        kernel = np.ones((k, k), np.uint8)

        if method == 'otsu':
            blur = cv2.GaussianBlur(img, (5, 5), 0)
            _, out = cv2.threshold(blur, 0, 255,
                                     cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            thr = int(max(0, min(255, int(threshold * 255))))
            _, out = cv2.threshold(img, thr, 255, cv2.THRESH_BINARY)

        if erode_iters > 0:
            out = cv2.erode(out, kernel, iterations=erode_iters)
        if dilate_iters > 0:
            out = cv2.dilate(out, kernel, iterations=dilate_iters)

        h, w = out.shape
        total = h * w
        min_pix = max(1, int(min_component_ratio * total))
        num, labels, stats, _ = cv2.connectedComponentsWithStats(out, connectivity=8)
        mask_kept = np.zeros_like(out, dtype=out.dtype)
        for i in range(1, num):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_pix:
                mask_kept[labels == i] = 255
        mask_kept = cv2.morphologyEx(mask_kept, cv2.MORPH_CLOSE, kernel, iterations=1)
        return mask_kept.astype(np.uint8)

    @staticmethod
    def expand_mask(binary_mask_255, border_px=64):
        """Dilate the mask to include a safety border around the manipulated area."""
        if border_px <= 0:
            return (binary_mask_255.copy() if binary_mask_255.dtype == np.uint8
                    else binary_mask_255.astype(np.uint8))
        b = int(border_px)
        k = 2 * b + 1 if b > 0 else 3
        kernel = np.ones((k, k), dtype=np.uint8)
        return cv2.dilate(binary_mask_255.astype(np.uint8), kernel, iterations=1)

    @staticmethod
    def to_soft_mask(binary_mask_255, blur_kernel=15, blur_sigma=5.0):
        """Convert binary {0,255} mask into a float32 [0,1] soft alpha channel
        for Poisson/alpha blending (blurred edges)."""
        b = (binary_mask_255.astype(np.uint8) if binary_mask_255.dtype != np.uint8
             else binary_mask_255)
        k = int(blur_kernel)
        if k % 2 == 0:
            k += 1
        if k < 3:
            k = 3
        blurred = cv2.GaussianBlur(b, (k, k),
                                   sigmaX=float(blur_sigma),
                                   sigmaY=float(blur_sigma))
        blurred = blurred.astype(np.float32) / 255.0
        return np.clip(blurred, 0.0, 1.0).astype(np.float32)
