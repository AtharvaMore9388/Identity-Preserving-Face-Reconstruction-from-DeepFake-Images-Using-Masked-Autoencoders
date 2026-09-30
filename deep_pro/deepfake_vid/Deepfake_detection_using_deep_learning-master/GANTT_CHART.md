# DeepShield AI — Project Gantt Chart & Timeline

**Project:** DeepShield AI — Deepfake Detection & Face Reconstruction  
**Duration:** 4 Months (June – September 2026)  
**Team:** Academic Research Project

---

## Project Gantt Chart

```
PHASE                          JUNE        JULY        AUGUST      SEPTEMBER
                               W1 W2 W3 W4 W1 W2 W3 W4 W1 W2 W3 W4 W1 W2 W3 W4
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 1 — RESEARCH & PLANNING
  Literature Review              ██ ██
  Define Architecture            ██ ██
  Dataset Selection                 ██ ██
  Environment Setup                    ██

PHASE 2 — MODEL DEVELOPMENT
  Data Preprocessing                       ██ ██
  ResNeXt50 Integration                       ██ ██
  LSTM Layer Training                            ██ ██
  Model Evaluation & Tuning                         ██ ██

PHASE 3 — RECONSTRUCTION PIPELINE
  Grad-CAM Implementation                               ██ ██
  Mask Generation (Otsu+CC)                                ██ ██
  NbNet Decoder Integration                                   ██ ██
  Poisson Blending                                               ██

PHASE 4 — WEB APPLICATION
  Django App Setup                                           ██
  Authentication System                                         ██ ██
  Upload & Detection UI                                            ██ ██
  Results & Pipeline UI                                               ██ ██

PHASE 5 — METRICS & VALIDATION
  PSNR / SSIM Implementation                                           ██
  Quality Metrics UI                                                      ██
  End-to-End Testing                                                      ██ ██

PHASE 6 — POLISH & DOCUMENTATION
  UI Responsiveness                                                          ██
  README & Docs                                                              ██ ██
  Performance Testing                                                            ██
  Final Review & Cleanup                                                         ██
```

---

## Milestone Timeline

| # | Milestone | Target Date | Status |
|---|---|---|---|
| M1 | Literature review complete | June Week 2 | ✅ Done |
| M2 | System architecture finalised | June Week 3 | ✅ Done |
| M3 | Datasets preprocessed | July Week 1 | ✅ Done |
| M4 | ResNeXt50 + LSTM model trained (≥ 84% accuracy) | July Week 3 | ✅ Done |
| M5 | Model reaches ≥ 90% accuracy | July Week 4 | ✅ Done |
| M6 | Grad-CAM heatmap working | August Week 1 | ✅ Done |
| M7 | Binary mask generation (Otsu) working | August Week 2 | ✅ Done |
| M8 | NbNet reconstruction producing valid output | August Week 3 | ✅ Done |
| M9 | Poisson blending integrated | August Week 3 | ✅ Done |
| M10 | Django web application running | August Week 4 | ✅ Done |
| M11 | Login/Register authentication working | September Week 1 | ✅ Done |
| M12 | Full pipeline E2E working in UI | September Week 2 | ✅ Done |
| M13 | PSNR/SSIM metrics displayed | September Week 3 | ✅ Done |
| M14 | Responsive design complete | September Week 3 | ✅ Done |
| M15 | Testing & validation complete | September Week 4 | ✅ Done |
| M16 | README & documentation updated | September Week 4 | ✅ Done |

---

## Phase Breakdown

### Phase 1 — Research & Planning (June W1–W4)
- Study deepfake detection literature (FaceForensics++, Celeb-DF papers)
- Review NbNet paper: *"On the Reconstruction of Face Images from Deep Face Templates"* (Mai et al.)
- Select datasets: FaceForensics++, Celeb-DF, DFDC
- Define system architecture: 3-stage pipeline (Detect → Reconstruct → Verify)
- Set up Python 3.10, PyTorch 2.3, CUDA environment

### Phase 2 — Model Development (July W1–W4)
- Preprocess video datasets: frame extraction, face cropping
- Build ResNeXt50 transfer learning backbone (2048-dim feature maps)
- Add LSTM layer for temporal frame consistency
- Train on 6000 videos, achieve **93.59% accuracy** with 100 frames
- Evaluate: Accuracy, Precision, Recall, F1, Confusion Matrix

### Phase 3 — Reconstruction Pipeline (August W1–W3)
- Implement Grad-CAM class activation maps from ResNeXt50 features
- Otsu thresholding + Connected Components for binary mask
- Add fallback for all-white / sparse masks (coverage-based)
- Integrate NbNet de-convolutional decoder for masked inpainting
- Apply Poisson seamless cloning for natural blending

### Phase 4 — Web Application (August W4 – September W2)
- Create Django 5 project with `ml_app`
- Build upload form, session management, pipeline orchestration in `views.py`
- Implement login/register/logout with `auth_views.py`
- Design `predict.html` with 7-step pipeline visualization
- Build `index.html` home page with drag-and-drop upload

### Phase 5 — Metrics & Validation (September W3)
- Implement PSNR and SSIM metrics (full image + masked region)
- Display metrics in circular gauge cards on `predict.html`
- Handle graceful "No Ground Truth" fallback state
- Run full end-to-end integration tests (54 test cases)

### Phase 6 — Polish & Documentation (September W4)
- Ensure mobile/tablet/desktop responsiveness
- Remove LPIPS, DFREC, IAMAE references (update to NbNet)
- Remove all debug/temp/log files
- Write TESTING_REPORT.md and GANTT_CHART.md
- Update README.md with accurate pipeline and setup guide

---

## Effort Distribution

| Phase | Effort | Duration |
|---|---|---|
| Research & Planning | 15% | 4 weeks |
| Model Development | 25% | 4 weeks |
| Reconstruction Pipeline | 20% | 3 weeks |
| Web Application | 25% | 4 weeks |
| Metrics & Validation | 8% | 1 week |
| Polish & Documentation | 7% | 1 week |
| **Total** | **100%** | **~4 months** |

---

## Deliverables

| # | Deliverable | File / Location |
|---|---|---|
| 1 | Trained Model (93.59% accuracy) | `Django Application/models/*.pt` |
| 2 | Django Web Application | `Django Application/` |
| 3 | Reconstruction Pipeline | `Django Application/reconstruction/` |
| 4 | Authentication System | `ml_app/auth_views.py` |
| 5 | Full Frontend UI | `ml_app/templates/predict.html` |
| 6 | Model Training Notebooks | `Model Creation/*.ipynb` |
| 7 | Testing & Validation Report | `TESTING_REPORT.md` |
| 8 | Project Gantt Chart | `GANTT_CHART.md` |
| 9 | Project README | `README.md` |

---

*Gantt chart generated for DeepShield AI v2.5 — September 2026*
