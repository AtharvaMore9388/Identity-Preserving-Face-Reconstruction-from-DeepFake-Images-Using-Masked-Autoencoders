import numpy as np
import cv2


class Blender:
    """Blend reconstructed inpainted regions into the original authentic image,
    preserving authentic pixels and using Poisson seamless cloning for the
    reconstructed masked region. Alpha-blend fallback if Poisson fails."""

    @staticmethod
    def alpha_blend(original_bgr, reconstructed_bgr, soft_mask_f32):
        """Alpha blend using soft_mask as alpha channel. Shape: (224,224,3) or
        broadcastable. soft_mask is float [0,1] single-channel."""
        a = soft_mask_f32.astype(np.float32)
        if a.ndim == 2:
            a = np.repeat(a[:, :, None], 3, axis=2)
        orig = original_bgr.astype(np.float32)
        rec = reconstructed_bgr.astype(np.float32)
        out = (1.0 - a) * orig + a * rec
        return np.clip(out, 0, 255).astype(np.uint8)

    @staticmethod
    def poisson_blend(original_bgr, reconstructed_bgr, binary_mask_255,
                      poisson_flags=None):
        """Attempt cv2.seamlessClone with MIXED_CLONE over the bounding rect
        of the masked region, centered on the mask's centroid."""
        try:
            binary = binary_mask_255.astype(np.uint8) if binary_mask_255.dtype != np.uint8 else binary_mask_255
            if cv2.countNonZero(binary) < 4:
                return original_bgr.copy()
            ys, xs = np.where(binary > 0)
            cx = int(np.mean(xs))
            cy = int(np.mean(ys))
            h, w = original_bgr.shape[:2]
            cx = np.clip(cx, 0, w - 1)
            cy = np.clip(cy, 0, h - 1)
            if poisson_flags is None:
                poisson_flags = cv2.NORMAL_CLONE
            result, _ = cv2.seamlessClone(
                reconstructed_bgr,
                original_bgr,
                binary,
                (cx, cy),
                poisson_flags,
            )
            return np.clip(result, 0, 255).astype(np.uint8)
        except Exception:
            return None

    @staticmethod
    def combine_blend(original_bgr, reconstructed_bgr, binary_mask_255,
                      soft_mask_f32, poisson_priority=True):
        """Replaces authentic pixels with original_bgr, then runs Poisson blend
        on the reconstructed region. Falls back to alpha blend on error."""
        # Step 1: replace only masked pixels in reconstructed image with original
        mask_bool = binary_mask_255 > 127
        if mask_bool.ndim == 2:
            mask_bool_3c = np.repeat(mask_bool[:, :, None], 3, axis=2)
        else:
            mask_bool_3c = mask_bool

        region_only = original_bgr.copy()
        region_only[mask_bool_3c] = reconstructed_bgr[mask_bool_3c]

        if not poisson_priority:
            return Blender.alpha_blend(original_bgr, region_only, soft_mask_f32)

        poisson = Blender.poisson_blend(
            original_bgr, region_only, binary_mask_255, cv2.MIXED_CLONE
        )
        if poisson is not None:
            return poisson
        return Blender.alpha_blend(original_bgr, region_only, soft_mask_f32)
