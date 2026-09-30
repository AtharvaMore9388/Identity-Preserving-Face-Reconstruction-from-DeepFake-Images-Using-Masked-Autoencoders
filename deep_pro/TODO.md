# Fixed Django Deepfake App - Steps to Complete

## Current Status: Diagnosed import error. Implementing fixes.

1. [x] **Step 0**: Created detailed TODO.md tracking progress.
2. [x] **Step 1**: Verified reconstruction/mae_modules.py (ViT MAE model OK).
3. [x] **Step 2**: Edit ml_app/views.py to fix 'reconstruction' import path using reliable sys.path.insert.
4. [ ] **Step 3**: cd to Django dir (`deepfake_vid/Deepfake_detection_using_deep_learning-master/Django Application`)
5. [ ] **Step 4**: Activate venv_django (`venv_django\Scripts\activate.bat`)
6. [ ] **Step 5**: pip install -r requirements.txt (torch, opencv, dlib etc.)
7. [ ] **Step 6**: python manage.py makemigrations ml_app && python manage.py migrate
8. [ ] **Step 7**: python manage.py check
9. [ ] **Step 8**: python manage.py runserver 0.0.0.0:8000
10. [ ] **Step 9**: Test app at http://localhost:8000 (upload fake/real image/video)

**Next**: After each step confirms success, mark [x] and continue. Server ready after Step 8.
