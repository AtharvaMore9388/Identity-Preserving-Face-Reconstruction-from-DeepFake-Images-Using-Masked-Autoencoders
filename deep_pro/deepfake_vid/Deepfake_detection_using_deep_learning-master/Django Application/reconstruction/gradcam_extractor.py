import numpy as np
import cv2


class GradCAMExtractor:
    """Grad-CAM extraction helper. Produces a normalized 2D activation map from
    feature maps and last linear-layer weights."""

    def __init__(self, model=None, target_layer=None):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        self._hooked = False

    def _hook(self, module, input, output):
        self.activations = output.detach().cpu().numpy()

    def _grad_hook(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach().cpu().numpy()

    def register(self):
        if self.model is None or self.target_layer is None:
            return
        self.target_layer.register_forward_hook(self._hook)
        self.target_layer.register_full_backward_hook(self._grad_hook)
        self._hooked = True

    @staticmethod
    def from_linear(fmap, weight_softmax, class_idx):
        """Compute Grad-CAM map offline from a pre-computed feature map and
        classifier weight matrix (no backprop required)."""
        # fmap shape: (nc, H, W)  or  (bs, nc, H, W)
        if fmap.ndim == 4:
            fmap = fmap[0]
        nc, h, w = fmap.shape
        weights = weight_softmax[class_idx, :]  # (nc,)
        cam = np.tensordot(weights, fmap, axes=(0, 0))  # (h, w)
        cam = cam - cam.min()
        cam_max = cam.max()
        if cam_max > 0:
            cam = cam / cam_max
        return cam.astype(np.float32)
