# DeepShield AI — Deepfake Detection & Face Reconstruction

> **ResNeXt50 + LSTM · Grad-CAM · NbNet Decoder · Poisson Blending**

A full-stack deepfake detection system with a Django web application. Uploads a facial image, classifies it as **REAL** or **FAKE**, and if fake — reconstructs the authentic face using a multi-stage inpainting pipeline.

> 📖 **Detailed Model & Weights Documentation:** See [README2.md](README2.md) for full documentation of all detection models, reconstruction models (MAE, U-Net, IML-ViT), file implementations, and weight locations.

---

## 📁 Project Structure

```
Deepfake_detection_using_deep_learning-master/
├── Django Application/      ← Main web application (Django)
│   ├── ml_app/              ← Core detection & reconstruction app
│   ├── reconstruction/      ← Grad-CAM, mask generation, NbNet, metrics
│   ├── models/              ← Trained .pt model files
│   ├── static/              ← CSS, JS, Bootstrap assets
│   ├── templates/           ← Global base, navbar, footer HTML
│   ├── requirements.txt     ← Python dependencies
│   └── manage.py
│
└── Model Creation/          ← Jupyter notebooks for training your own model
    ├── preprocessing.ipynb
    ├── Model_and_train_csv.ipynb
    ├── Predict.ipynb
    └── labels/
```

---

## 🚀 Features

| Module | Technology | Status |
|---|---|---|
| Deepfake Detection | ResNeXt50 + LSTM | ✅ Active |
| Grad-CAM Heatmap | Class Activation Maps | ✅ Active |
| Binary Mask Generation | Otsu Thresholding + Connected Components | ✅ Active |
| Soft Mask | Gaussian Blur | ✅ Active |
| Face Reconstruction | NbNet de-convolutional decoder | ✅ Active |
| Seamless Blending | Poisson Cloning (OpenCV) | ✅ Active |
| Quality Metrics | PSNR · SSIM (Full & Masked region) | ✅ Active |
| User Authentication | Django Auth (Login / Register) | ✅ Active |

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- CUDA-capable GPU (optional; CPU fallback supported)

### 1. Clone the repository

```bash
git clone https://github.com/your-repo/deepshield-ai.git
cd "deepshield-ai/Django Application"
```

### 2. Create a virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download trained models

Place your `.pt` model files in the `models/` directory.  
Pre-trained models available:

| Model File | Frames | Accuracy |
|---|---|---|
| `model_84_acc_10_frames_final_data.pt` | 10 | 84.21% |
| `model_87_acc_20_frames_final_data.pt` | 20 | 87.79% |
| `model_89_acc_40_frames_final_data.pt` | 40 | 89.35% |
| `model_90_acc_60_frames_final_data.pt` | 60 | 90.59% |
| `model_91_acc_80_frames_final_data.pt` | 80 | 91.50% |
| `model_93_acc_100_frames_final_data.pt` | 100 | 93.59% |

> Download from [Google Drive](https://drive.google.com/drive/folders/1UX8jXUXyEjhLLZ38tcgOwGsZ6XFSLDJ-?usp=sharing)

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Run the development server

```bash
python manage.py runserver 0.0.0.0:8000
```

Open `http://localhost:8000` in your browser.

---

## 🧠 Detection & Reconstruction Pipeline

```
Upload Image
    │
    ▼
Face Detection (face_recognition)
    │
    ▼
Preprocessing (224×224, ImageNet normalization)
    │
    ▼
ResNeXt50 Feature Extraction → LSTM → Softmax → REAL / FAKE
    │                            │
    │ (if FAKE)                  └─ Confidence Score
    ▼
Grad-CAM Heatmap (class activation visualization)
    │
    ▼
Otsu Threshold + Connected Components → Binary Mask
    │
    ▼
Gaussian Soft Mask
    │
    ▼
NbNet Decoder (de-convolutional inpainting)
    │
    ▼
Poisson Seamless Cloning → Final Reconstructed Image
    │
    ▼
Quality Metrics: PSNR · SSIM (Full image + Masked region)
```

---

## 📊 Reconstruction Quality Metrics

When a ground-truth reference image is available, the system automatically computes:

- **PSNR** — Peak Signal-to-Noise Ratio (full image & masked region)
- **SSIM** — Structural Similarity Index (full image & masked region)

To enable metrics: place a reference image at `uploaded_images/real/real_test.jpg`,  
or include the word **`real`** in your uploaded image filename.

---

## 🗄️ Datasets Used for Training

- [FaceForensics++](https://github.com/ondyari/FaceForensics)
- [Celeb-DF](https://github.com/yuezunli/celeb-deepfakeforensics)
- [Deepfake Detection Challenge (DFDC)](https://www.kaggle.com/c/deepfake-detection-challenge/data)

### Preprocessed Data (Google Drive)

| Dataset | Type | Link |
|---|---|---|
| Celeb-DF | Fake | [Download](https://drive.google.com/drive/folders/1SxCb_Wr7N4Wsc-uvjUl0i-6PpwYmwN65?usp=sharing) |
| Celeb-DF | Real | [Download](https://drive.google.com/drive/folders/1g97v9JoD3pCKA2TxHe8ZLRe4buX2siCQ?usp=sharing) |
| FaceForensics++ | Real + Fake | [Download](https://drive.google.com/drive/folders/1VIIWRLs6VBXRYKODgeOU7i6votLPPxT0?usp=sharing) |
| DFDC | Fake | [Download](https://drive.google.com/drive/folders/1yz3DBeFJvZ_QzWsyY7EwBNm7fx4MiOfF?usp=sharing) |
| DFDC | Real | [Download](https://drive.google.com/drive/folders/1wN3ZOd0WihthEeH__Lmj_ENhoXJN6U11?usp=sharing) |

> Labels: `/labels/Global_metadata.csv`

---

## 🏋️ Training Your Own Model

See [`Model Creation/Readme.md`](Model%20Creation/Readme.md) for step-by-step instructions on:
1. Preprocessing video datasets
2. Training the ResNeXt50 + LSTM model
3. Running predictions with your custom weights

---

## 🔒 Authentication

The app includes a full login/registration system:
- Register a new account at `/auth/register/`
- Login at `/auth/login/`
- All analysis pages require authentication

---

## 📱 Responsive Design

The web interface is fully responsive and works on:
- **Desktop** — Full pipeline visualization with side-by-side comparisons
- **Tablet** — Adaptive grid layout
- **Mobile** — Horizontally scrollable pipeline cards

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.0, Python 3.10 |
| ML Framework | PyTorch 2.3, TorchVision |
| CV Library | OpenCV, face_recognition (dlib) |
| Frontend | Bootstrap 5, Vanilla CSS, Font Awesome 6 |
| Database | SQLite (development) |

---

## 📄 License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

This project is licensed under the GNU General Public License v3.0.
