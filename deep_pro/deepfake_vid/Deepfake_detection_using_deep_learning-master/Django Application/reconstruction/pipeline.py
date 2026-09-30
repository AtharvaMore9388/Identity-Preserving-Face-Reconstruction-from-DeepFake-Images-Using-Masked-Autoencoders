import numpy as np
import cv2
import os


class FullReconstructionPipeline:
    """Convenience wrapper that runs the 5-step pipeline:
    1. GradCAM heatmap
    2. Binary + soft masks
    3. Reconstruction (MAE or inpainting fallback)
    4. Poisson / alpha blend
    5. Metrics (if GT provided)"""

    def __init__(self,
                 gradcam_extractor=None,
                 mask_generator=None,
                 blender=None,
                 metrics=None,
                 mae_model=None):
        self.gradcam = gradcam_extractor
        self.maskgen = mask_generator
        self.blender = blender
        self.metrics = metrics
        self.mae = mae_model

    def run(self, face_bgr, cam_normalized, class_idx=0,
            gt_bgr=None, use_mae_if_available=True):
        from .gradcam_extractor import GradCAMExtractor
        from .mask_generator import MaskGenerator
        from .blender import Blender
        from .metrics import ReconstructionMetrics, LPIPSEvaluator
        mg = self.maskgen or MaskGenerator()
        bl = self.blender or Blender()
        rm = self.metrics or ReconstructionMetrics()

        # 1) (already provided as cam_normalized)
        # 2) masks
        binary = mg.to_binary(cam_normalized, method='otsu', dilate_iters=2, min_component_ratio=0.005)
        if np.count_nonzero(binary) < 50:
            binary = mg.to_binary(cam_normalized, method='fixed', threshold=0.5, dilate_iters=3)
        binary = mg.expand_mask(binary, border_px=5)
        soft = mg.to_soft_mask(binary, blur_kernel=15, blur_sigma=5.0)

        # 3) reconstruction placeholder (since MAE training is WIP)
        inpaint_mask = (soft > 0.4).astype(np.uint8) * 255
        inpaint_mask = cv2.GaussianBlur(inpaint_mask, (9, 9), 2)
        reconstructed_bgr = cv2.inpaint(cv2.resize(face_bgr, (224, 224)),
                                         inpaint_mask, 3, cv2.INPAINT_TELEA)

        # 4) blend
        face_224 = cv2.resize(face_bgr, (224, 224))
        result_bgr = bl.combine_blend(face_224, reconstructed_bgr, binary, soft,
                                      poisson_priority=True)

        # 5) metrics
        metrics_out = {}
        if gt_bgr is not None:
            gt_224 = cv2.resize(gt_bgr, (224, 224))
            metrics_out['PSNR_full'] = round(rm.psnr(gt_224, result_bgr), 3)
            metrics_out['SSIM_full'] = round(rm.ssim(gt_224, result_bgr), 4)
            metrics_out['PSNR_masked'] = round(rm.masked_psnr(gt_224, result_bgr, binary), 3)
            metrics_out['SSIM_masked'] = round(rm.masked_ssim(gt_224, result_bgr, binary), 4)
            try:
                lpips_fn = LPIPSEvaluator('cpu')
                metrics_out['LPIPS'] = round(lpips_fn(gt_224, result_bgr), 4)
            except Exception:
                metrics_out['LPIPS'] = 'N/A'
        else:
            metrics_out['note'] = 'No ground truth available'

        return {
            'binary_mask': binary,
            'soft_mask': soft,
            'reconstructed': reconstructed_bgr,
            'blended': result_bgr,
            'method': 'Telea Fallback (MAE in development)',
            'metrics': metrics_out,
        }
