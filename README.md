# 📝 Optical Mark Recognition (OMR) - Bubble Sheet Exam Evaluator

This project is a **Python + OpenCV** implementation of an Optical Mark Recognition (OMR) system that scans bubble sheet exams, detects filled answers, grades them, and displays the result directly on the sheet.

It works for both:
- Pre-scanned / photographed exam sheet images
- Live webcam feeds

---

## ✨ Features
- Automatically detects the answer sheet and grade box.
- Corrects perspective (top-down view) for accurate bubble detection.
- Splits the sheet into question boxes and counts marked answers.
- Compares detected answers to a predefined answer key.
- Calculates the score and overlays it on the sheet.
- Displays each processing step for debugging.
- Saves graded sheets as images.

---

## 📂 Project Structure
```
.
├── assets/
│   └── 1.jpg                 # Sample bubble sheet image
├── main.py                   # Main OMR processing script
├── utlis.py                  # Helper functions for image processing
├── Scanned/                  # Folder for saving graded sheets
└── README.md                 # Project documentation
```

---

## 🔧 Requirements
- Python 3.x
- [OpenCV](https://pypi.org/project/opencv-python/)
- [NumPy](https://pypi.org/project/numpy/)

Install dependencies:
```bash
pip install opencv-python numpy
```

---

## ⚙️ Configuration
Edit **`main.py`** to set your parameters:
```python
webCamFeed = False               # True for webcam input, False for image
pathImage = "assets/1.jpg"       # Path to exam sheet image
heightImg = 700                  # Processing image height
widthImg = 700                   # Processing image width
questions = 5                    # Number of questions
choices = 5                      # Choices per question
ans = [1, 2, 0, 2, 4]            # Correct answer indices
```

---

## ▶️ Usage

### 1. Run with an Image
Place your image in the **assets** folder, then run:
```bash
python main.py
```

### 2. Run with Webcam
Set:
```python
webCamFeed = True
```
Then:
```bash
python main.py
```

---

## ⌨️ Controls
- **`q`** → Quit the program
- **`s`** → Save graded result in `Scanned/ResultImage.jpg`

---

## 📸 Output Example
**Grading Visualization:**
- ✅ **Green circles** → Correct answers
- ❌ **Red circles** → Incorrect answers (with correct answer shown in small green circle)
- 📊 Score displayed in the grade box.

---

## 🧠 How It Works
**Main Processing Steps:**
1. **Image Acquisition** – From webcam or image file.
2. **Preprocessing** – Grayscale conversion, Gaussian blur, Canny edge detection.
3. **Contour Detection** – Find the two largest rectangles:
   - Main answer sheet
   - Grade display area
4. **Perspective Transformation** – Warp both rectangles for a clean top-down view.
5. **Thresholding & Box Splitting** – Convert to binary, split into `questions × choices` boxes.
6. **Answer Detection** – Count non-zero pixels to determine marked choice.
7. **Grading** – Compare with `ans` array and calculate score.
8. **Overlay Results** – Draw marks for answers and score, warp back, merge with original.

---

## 📦 Helper Functions (utlis.py)
- **`stackImages(imgArray, scale, labels=[])`** → Stacks images into one display window.
- **`reorder(myPoints)`** → Reorders corner points for consistent warping.
- **`rectContour(contours)`** → Finds rectangular contours sorted by area.
- **`getCornerPoints(cont)`** → Gets four corner points of a contour.
- **`splitBoxes(img)`** → Splits the warped image into boxes.
- **`drawGrid(img, questions=5, choices=5)`** → Draws a debug grid.
- **`showAnswers(img, myIndex, grading, ans, questions=5, choices=5)`** → Marks correct/incorrect answers.

---

## 📌 Notes
- Ensure good lighting and image clarity.
- Adjust parameters (`heightImg`, `widthImg`, thresholds) for different sheet formats.
- Defaults assume 5 questions × 5 choices; change in both `main.py` and `splitBoxes()` for other layouts.
