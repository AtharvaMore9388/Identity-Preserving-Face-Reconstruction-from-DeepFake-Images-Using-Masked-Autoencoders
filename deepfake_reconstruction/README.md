# DeepFake Identity Recovery & Reconstruction System
### *Identity-Preserving Face Reconstruction from DeepFake Images Using Masked Autoencoders (MAE)*

---

## 📌 Project Overview
This project presents an end-to-end framework for detecting manipulated facial media (DeepFakes) and recovering the original, authentic facial identity. Built upon state-of-the-art deep learning architectures, the system integrates:

1. **Temporal/Spatial DeepFake Detection**: ResNet/Inception-based feature extractors evaluating video frames and image inputs with fine-grained probability scores.
2. **Grad-CAM Localization**: Gradient-weighted Class Activation Mapping that pinpoints exact manipulated regions on the face without requiring ground-truth manipulation masks.
3. **Identity-Aware Masked Autoencoder (MAE)**: Vision Transformer (ViT) encoder-decoder trained to reconstruct authentic facial features in the identified fake areas while strictly preserving original identity and facial geometry.
4. **Poisson & Seamless Blending**: Seamless integration of reconstructed authentic facial patches back into the original image context.
5. **Interactive Web Dashboard**: Full-featured Django web application with drag-and-drop video/image inference, real-time visual explanations, Grad-CAM heatmaps, metrics calculation (PSNR, SSIM, LPIPS), and comparative before/after visualization.

---

## 📁 Simplified Project Structure
```
deepfake_reconstruction/
├── manage.py                     # Django management CLI
├── START_SERVER.bat              # 1-Click launcher for Windows
├── requirements.txt              # Project dependencies
├── README.md                     # Documentation and Guide instructions
├── db.sqlite3                    # SQLite database
│
├── project_settings/             # Application configuration
│   ├── settings.py               # Django settings (clean paths)
│   ├── urls.py                   # Master URL routing
│   ├── wsgi.py                   # WSGI deployment entry point
│   └── asgi.py                   # ASGI entry point
│
├── ml_app/                       # Main Web Application & Inference Pipeline
│   ├── views.py                  # Prediction view, Grad-CAM & MAE pipeline
│   ├── models.py                 # Django ORM models
│   ├── model_loader.py           # Pretrained model loader
│   ├── auth_views.py             # User authentication views
│   ├── forms.py                  # Upload forms
│   ├── urls.py                   # Route definitions
│   └── templates/                # Frontend HTML templates
│
├── reconstruction/               # MAE & Restoration Engine
│   ├── __init__.py               # Unified exports
│   ├── mae_modules.py            # ViT MAE architecture & identity-aware masking
│   └── gradcam_pipeline.py       # Grad-CAM, MaskGenerator, Poisson Blender & Metrics
│
├── models/                       # Pre-trained deep learning weights (.pt / .pth)
├── static/                       # CSS, JS, Bootstrap, and Face-API models
├── templates/                    # Base layout templates (base.html, nav-bar, footer)
├── uploaded_images/              # Processed image cache
├── uploaded_videos/              # Video upload cache
│
└── notebooks/                    # Training and exploratory Jupyter notebooks
    ├── Model_and_train_csv.ipynb
    ├── Predict.ipynb
    ├── preprocessing.ipynb
    └── metadata/
```

---

## 🚀 How to Run the Project

### Option A: 1-Click Launch (Recommended for Windows)
Simply double-click:
```
START_SERVER.bat
```
Then open your web browser at: **`http://127.0.0.1:8000/`**

### Option B: Manual Command Line Execution
1. Open terminal / command prompt in this directory:
   ```bash
   cd deepfake_reconstruction
   ```
2. (Optional) Activate your Python 3.10 virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Django development server:
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
5. Open your browser and navigate to: **`http://127.0.0.1:8000/`**

---

## 🧪 Testing the Application
1. **Login/Register**: Use the built-in authentication or log in as guest.
2. **Upload Media**: Upload any facial image or video (.mp4, .jpg, .png).
3. **Detection Results**:
   - Classification: REAL or FAKE with confidence percentage.
   - Grad-CAM Heatmap: Highlighting manipulated regions.
   - Reconstruction Preview: Identity-preserving MAE output.
   - Quality Metrics: PSNR, SSIM, and restoration scores.

---

## 👥 Authors & Academic Context
- **Project Title**: Identity-Preserving Face Reconstruction from DeepFake Images Using Masked Autoencoders
- **Domain**: Computer Vision, Deep Learning, Digital Forensics
