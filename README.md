# Intelligent Quote Search

This project is an intelligent quote/document search app supporting PDF and Excel uploads, OCR (English/Chinese), and robust fuzzy search. It features a Next.js frontend and a FastAPI backend with PaddleOCR, pdfplumber, and more.

---

## Features
- Upload and search PDF and Excel files
- Convert Excel to PDF for unified search
- OCR for images and scanned documents (English & Chinese)
- Robust fuzzy/partial search for both English and Chinese (including long product names)
- Drag-and-drop upload, text/image search, and card-style results

---

## Tech Stack
- **Frontend:** Next.js (React), Tailwind CSS
- **Backend:** FastAPI (Python), PaddleOCR, pdfplumber, openpyxl, Sentence Transformers/OpenAI embeddings
- **OCR:** PaddleOCR (English & Chinese)
- **PDF/Excel:** pdfplumber, openpyxl, PyMuPDF (fitz)
- **Fuzzy Search:** Custom logic for English/Chinese, difflib, character overlap

---

## How to Initialize & Run

### 1. Clone the Repository
```sh
git clone https://github.com/nikhil2004-blip/finder.git
cd finder
```

### 2. Backend Setup
```sh
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
# Or: source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
```

#### Start Backend (in background)
```sh
uvicorn app.main:app --reload
```

#### Stop Backend (find and kill process)
- On Windows:
  1. Find the process:
     ```sh
     netstat -ano | findstr :8000
     ```
  2. Kill the process:
     ```sh
     taskkill /PID <pid> /F
     ```
- On Linux/Mac:
  ```sh
  lsof -i :8000
  kill <pid>
  ```

### 3. Frontend Setup
```sh
cd ../frontend
npm install
npm run dev
```

#### Stop Frontend
- Press `Ctrl+C` in the terminal running `npm run dev`.

---

## Website Description
This app allows you to upload PDF and Excel files, search them using text or image input, and get robust results even for scanned or image-based documents. It supports both English and Chinese, and is designed for real-world business/product document search.

---

## Repository
[https://github.com/nikhil2004-blip/finder](https://github.com/nikhil2004-blip/finder)

---

## Contact / Issues
Open an issue on GitHub for support or feature requests. 