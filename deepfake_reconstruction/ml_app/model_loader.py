"""
model_loader.py — HuggingFace Hub model downloader for DeepShield AI
Downloads model weights from HuggingFace Hub at startup if not cached locally.

HuggingFace Model Repo: AtharvaMore9388/deepshield-models
"""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
HF_REPO_ID = os.environ.get("HF_MODEL_REPO", "AtharvaMore9388/deepshield-models")
MODELS_DIR = Path(os.environ.get("MODELS_DIR", "/app/models"))
CACHE_DIR  = Path(os.environ.get("HF_CACHE_DIR", "/app/models_cache"))

# All model filenames that live in the HuggingFace repo
MODEL_FILES = [
    # Detection weights
    "model_84_acc_10_frames_final_data.pt",
    "model_87_acc_20_frames_final_data.pt",
    "model_89_acc_40_frames_final_data.pt",
    "model_90_acc_20_frames_FF_data.pt",
    "model_90_acc_60_frames_final_data.pt",
    "model_93_acc_100_frames_celeb_FF_data.pt",
    "model_95_acc_40_frames_FF_data.pt",
    "model_97_acc_60_frames_FF_data.pt",
    "model_97_acc_80_frames_FF_data.pt",
    "model_97_acc_100_frames_FF_data.pt",
    # MAE reconstruction weights
    "mae_pretrain_vit_base.pth",
    "mae_face_pretrain_vit_base.pth",
    "mae_face_visualize_vit_base.pth",
    # IML-ViT localization weights
    "iml-vit_checkpoint.pth",
    "iml-vit_checkpoint_casiav2_20231014.pth",
    "iml-vit_checkpoint_trufor_20231104.pth",
]

# Minimum required models (app can start without optional ones)
REQUIRED_MODELS = [
    "model_97_acc_60_frames_FF_data.pt",   # Best general detector
    "mae_pretrain_vit_base.pth",            # Lightest MAE weight
]


def ensure_models_dir():
    """Create models directory if it doesn't exist."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def download_model(filename: str) -> Path:
    """
    Download a single model file from HuggingFace Hub.
    Returns local path to the downloaded file.
    """
    from huggingface_hub import hf_hub_download

    local_path = MODELS_DIR / filename
    if local_path.exists():
        logger.info(f"[ModelLoader] ✅ Already exists: {filename}")
        return local_path

    logger.info(f"[ModelLoader] ⬇️  Downloading: {filename} from {HF_REPO_ID}")
    try:
        downloaded = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=filename,
            cache_dir=str(CACHE_DIR),
            local_dir=str(MODELS_DIR),
        )
        logger.info(f"[ModelLoader] ✅ Downloaded: {filename}")
        return Path(downloaded)
    except Exception as e:
        logger.error(f"[ModelLoader] ❌ Failed to download {filename}: {e}")
        raise


def download_required_models():
    """
    Download only the minimum required models at startup.
    Call this from Django's AppConfig.ready() or manage.py.
    """
    ensure_models_dir()
    logger.info("[ModelLoader] 🚀 Downloading required models from HuggingFace Hub...")
    for filename in REQUIRED_MODELS:
        try:
            download_model(filename)
        except Exception as e:
            logger.critical(f"[ModelLoader] CRITICAL: Could not get required model {filename}: {e}")
    logger.info("[ModelLoader] ✅ Required models ready.")


def download_all_models():
    """Download ALL model files. Call this for full deployment."""
    ensure_models_dir()
    logger.info("[ModelLoader] 🚀 Downloading ALL models from HuggingFace Hub...")
    for filename in MODEL_FILES:
        try:
            download_model(filename)
        except Exception as e:
            logger.warning(f"[ModelLoader] ⚠️  Skipping {filename}: {e}")
    logger.info("[ModelLoader] ✅ All available models downloaded.")


def get_model_path(filename: str) -> str:
    """
    Get local path to a model file.
    Downloads from HuggingFace Hub if not already present.
    Returns string path compatible with torch.load().
    """
    local_path = MODELS_DIR / filename
    if not local_path.exists():
        local_path = download_model(filename)
    return str(local_path)
