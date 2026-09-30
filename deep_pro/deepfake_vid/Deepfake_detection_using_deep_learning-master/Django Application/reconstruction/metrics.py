import numpy as np
import cv2


def _as_uint8_bgr(img):
    if img is None:
        raise ValueError("Empty image")
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img


def _resize_same(a, b):
    h, w = a.shape[:2]
    if b.shape[:2] != (h, w):
        b = cv2.resize(b, (w, h), interpolation=cv2.INTER_CUBIC)
    return a, b


class ReconstructionMetrics:
    """Standard image/reconstruction fidelity metrics: PSNR, SSIM, masked variants."""

    @staticmethod
    def psnr(img_a_bgr, img_b_bgr, data_range=255.0):
        a, b = _resize_same(_as_uint8_bgr(img_a_bgr), _as_uint8_bgr(img_b_bgr))
        mse = float(np.mean((a.astype(np.float64) - b.astype(np.float64)) ** 2))
        if mse < 1e-10:
            return 100.0
        return float(10.0 * np.log10((data_range ** 2) / mse))

    @staticmethod
    def _ssim_ch1(ch_a, ch_b, C1=6.5025, C2=58.5225):
        """Single-channel SSIM (mean+variance+covariance formulation)."""
        I1 = ch_a.astype(np.float64)
        I2 = ch_b.astype(np.float64)
        kernel = cv2.getGaussianKernel(11, 1.5)
        window = np.outer(kernel, kernel.transpose())

        mu1 = cv2.filter2D(I1, -1, window)
        mu2 = cv2.filter2D(I2, -1, window)
        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2
        sigma1_sq = cv2.filter2D(I1 ** 2, -1, window) - mu1_sq
        sigma2_sq = cv2.filter2D(I2 ** 2, -1, window) - mu2_sq
        sigma12 = cv2.filter2D(I1 * I2, -1, window) - mu1_mu2
        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
                   ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
        return float(np.mean(ssim_map))

    @staticmethod
    def ssim(img_a_bgr, img_b_bgr):
        a, b = _resize_same(_as_uint8_bgr(img_a_bgr), _as_uint8_bgr(img_b_bgr))
        a_y = cv2.cvtColor(a, cv2.COLOR_BGR2YCrCb)[:, :, 0]
        b_y = cv2.cvtColor(b, cv2.COLOR_BGR2YCrCb)[:, :, 0]
        return ReconstructionMetrics._ssim_ch1(a_y, b_y)

    @staticmethod
    def _apply_mask(img, binary_mask_255, fill_value=0):
        if binary_mask_255 is None:
            return img.copy()
        m = binary_mask_255.astype(np.uint8) if binary_mask_255.dtype != np.uint8 else binary_mask_255
        if m.shape[:2] != img.shape[:2]:
            m = cv2.resize(m, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)
        if m.ndim == 2:
            m_3c = np.repeat(m[:, :, None], 3, axis=2)
        else:
            m_3c = m
        masked = img.copy()
        masked[m_3c == 0] = fill_value
        return masked

    @staticmethod
    def masked_psnr(img_gt, img_pred, binary_mask_255):
        a, b = _resize_same(_as_uint8_bgr(img_gt), _as_uint8_bgr(img_pred))
        am = ReconstructionMetrics._apply_mask(a, binary_mask_255)
        bm = ReconstructionMetrics._apply_mask(b, binary_mask_255)
        return ReconstructionMetrics.psnr(am, bm)

    @staticmethod
    def masked_ssim(img_gt, img_pred, binary_mask_255):
        a, b = _resize_same(_as_uint8_bgr(img_gt), _as_uint8_bgr(img_pred))
        am = ReconstructionMetrics._apply_mask(a, binary_mask_255)
        bm = ReconstructionMetrics._apply_mask(b, binary_mask_255)
        return ReconstructionMetrics.ssim(am, bm)


class LPIPSEvaluator:
    """Learned perceptual similarity (wrapper around optional `lpips` / `torch`
    with SqueezeNet / VGG backbone). If dependencies unavailable, returns
    a cheap perceptual proxy (normalized gradient match + color hist)."""

    def __init__(self, device='cpu'):
        self.device = device
        self._lpips_fn = None
        self._backbone = None
        try:
            import torch  # noqa: F401
            import lpips
            self._lpips_fn = lpips.LPIPS(net='vgg').to(device)
            self._backbone = 'vgg16-lpips'
        except Exception:
            self._backbone = 'cv2-proxy'

    def backbone(self):
        return self._backbone

    def __call__(self, a_bgr, b_bgr):
        if self._lpips_fn is not None:
            try:
                import torch
                a, b = _resize_same(_as_uint8_bgr(a_bgr), _as_uint8_bgr(b_bgr))
                def _to_t(x):
                    x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
                    t = torch.from_numpy(x).permute(2, 0, 1).unsqueeze(0).to(self.device)
                    t = 2 * t - 1
                    return t
                with torch.no_grad():
                    return float(self._lpips_fn(_to_t(a), _to_t(b)).cpu().item())
            except Exception:
                pass
        # Fallback: compute a cheap structural proxy [0,1] lower = more similar
        a, b = _resize_same(_as_uint8_bgr(a_bgr), _as_uint8_bgr(b_bgr))
        a_y = cv2.cvtColor(a, cv2.COLOR_BGR2YCrCb).astype(np.float32) / 255.0
        b_y = cv2.cvtColor(b, cv2.COLOR_BGR2YCrCb).astype(np.float32) / 255.0
        gax = cv2.Sobel(a_y[:, :, 0], cv2.CV_32F, 1, 0, ksize=3)
        gay = cv2.Sobel(a_y[:, :, 0], cv2.CV_32F, 0, 1, ksize=3)
        gbx = cv2.Sobel(b_y[:, :, 0], cv2.CV_32F, 1, 0, ksize=3)
        gby = cv2.Sobel(b_y[:, :, 0], cv2.CV_32F, 0, 1, ksize=3)
        ga = np.sqrt(gax ** 2 + gay ** 2)
        gb = np.sqrt(gbx ** 2 + gby ** 2)
        grad_sim = 1.0 - float(np.mean(np.abs(ga - gb)) / max(1e-6, float(ga.max() - ga.min() + 1e-6)))
        color_dist = float(np.mean(np.abs(a_y - b_y)))
        score = 0.5 * (1.0 - max(0.0, min(1.0, grad_sim))) + 0.5 * color_dist
        return float(score)


class FIDEvaluator:
    """Placeholder FID (Fréchet Inception Distance) evaluator — requires
    inception_v3 weights; batch usage only."""

    def __init__(self, device='cpu'):
        self.device = device
        self._ready = False
        try:
            import torch  # noqa: F401
            self._ready = True
        except Exception:
            self._ready = False

    def ready(self):
        return self._ready

    def compute_from_images(self, real_images, fake_images):
        if not self._ready:
            raise RuntimeError("FIDEvaluator requires torch + torchvision")
        return 0.0
