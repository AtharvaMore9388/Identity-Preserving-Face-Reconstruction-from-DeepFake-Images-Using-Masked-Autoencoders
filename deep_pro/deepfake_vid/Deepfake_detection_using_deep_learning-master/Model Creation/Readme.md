# Model Creation — Training Your Own Deepfake Detector

This directory contains Jupyter notebooks for preprocessing datasets, training the ResNeXt50 + LSTM model, and running predictions with your custom weights.

> **Recommended:** Use [Google Colab](https://colab.research.google.com/) for free GPU access during training.

---

## 📂 Directory Contents

```
Model Creation/
├── preprocessing.ipynb       ← Extract & crop face frames from videos
├── Model_and_train_csv.ipynb ← Train ResNeXt50 + LSTM on preprocessed data
├── Predict.ipynb             ← Run inference on new videos
├── Helpers/                  ← Utility scripts (CSV conversion, file ops)
└── labels/                   ← Global metadata CSV for dataset labels
```

---

## Step 1 — Preprocessing (`preprocessing.ipynb`)

1. Load a video dataset (FaceForensics++, Celeb-DF, or DFDC)
2. Split each video into individual frames
3. Detect and crop the face region from each frame using `face_recognition`
4. Save the face-cropped frames/videos to disk

---

## Step 2 — Model Training (`Model_and_train_csv.ipynb`)

1. Load preprocessed face videos and labels from a CSV file
2. Build the model:
   - **ResNeXt50** (pretrained on ImageNet) → 2048-dim spatial feature maps
   - **LSTM** (1 layer, hidden dim 2048) → temporal consistency across frames
   - **Linear + Softmax** → binary classification (REAL / FAKE)
3. Split data into train/test sets
4. Train with cross-entropy loss and save the best checkpoint as a `.pt` file

---

## Step 3 — Prediction (`Predict.ipynb`)

1. Load any saved `.pt` model checkpoint
2. Run inference on new unseen video/image files
3. Output: predicted label (REAL / FAKE) + confidence score

---

## 📊 Pre-trained Model Results

| Model File | Videos | Frames | Accuracy |
|---|---|---|---|
| `model_84_acc_10_frames_final_data.pt` | 6000 | 10 | **84.21%** |
| `model_87_acc_20_frames_final_data.pt` | 6000 | 20 | **87.79%** |
| `model_89_acc_40_frames_final_data.pt` | 6000 | 40 | **89.35%** |
| `model_90_acc_60_frames_final_data.pt` | 6000 | 60 | **90.59%** |
| `model_91_acc_80_frames_final_data.pt` | 6000 | 80 | **91.50%** |
| `model_93_acc_100_frames_final_data.pt` | 6000 | 100 | **93.59%** |

> Download pre-trained models: [Google Drive](https://drive.google.com/drive/folders/1UX8jXUXyEjhLLZ38tcgOwGsZ6XFSLDJ-?usp=sharing)

---

## 🗄️ Datasets

| Dataset | Link |
|---|---|
| FaceForensics++ | [GitHub](https://github.com/ondyari/FaceForensics) |
| Celeb-DF | [GitHub](https://github.com/yuezunli/celeb-deepfakeforensics) |
| Deepfake Detection Challenge | [Kaggle](https://www.kaggle.com/c/deepfake-detection-challenge/data) |

### Preprocessed Data (ready to use)

| Dataset | Type | Google Drive |
|---|---|---|
| Celeb-DF | Fake | [Link](https://drive.google.com/drive/folders/1SxCb_Wr7N4Wsc-uvjUl0i-6PpwYmwN65?usp=sharing) |
| Celeb-DF | Real | [Link](https://drive.google.com/drive/folders/1g97v9JoD3pCKA2TxHe8ZLRe4buX2siCQ?usp=sharing) |
| FaceForensics++ | Real + Fake | [Link](https://drive.google.com/drive/folders/1VIIWRLs6VBXRYKODgeOU7i6votLPPxT0?usp=sharing) |
| DFDC | Fake | [Link](https://drive.google.com/drive/folders/1yz3DBeFJvZ_QzWsyY7EwBNm7fx4MiOfF?usp=sharing) |
| DFDC | Real | [Link](https://drive.google.com/drive/folders/1wN3ZOd0WihthEeH__Lmj_ENhoXJN6U11?usp=sharing) |

> Labels for all datasets: `labels/Global_metadata.csv`

---

## 🔧 Helper Scripts (`Helpers/`)

Utility scripts for common data preparation tasks:
- Convert JSON label files to CSV format
- Copy files between directories in bulk
- Remove audio-altered files from the DFDC dataset
