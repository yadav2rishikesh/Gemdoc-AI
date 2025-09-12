# 📄 GEMDOC AI – Document Question Answering with Google Gemini

GEMDOC AI is a smart document assistant that extracts insights from **PDF and DOCX** files.  
Upload a document, ask natural language questions, and get precise answers using **Google Gemini**.

---

## 🚀 Features
✅ Upload **PDF/DOCX** files  
✅ Automatic text extraction & chunking  
✅ Store data in a **FAISS knowledge database**  
✅ Ask natural language questions  
✅ Powered by **Google Gemini API**  
✅ Works for resumes, reports, research papers, contracts, and more  

---

## 🛠️ Tech Stack
- **Backend**: FastAPI, FAISS, SentenceTransformers  
- **Frontend**: ReactJS  
- **LLM**: Google Gemini API  
- **Deployment**: Docker + Docker Compose  

---

## 📂 Project Structure
```

GEMDOC-AI/
│── backend/        # FastAPI backend
│   ├── main.py     # API endpoints
│   ├── Dockerfile  # Backend Docker config
│   └── requirements.txt
│
│── frontend/       # ReactJS frontend
│   ├── src/        # React components
│   └── package.json
│
│── docker-compose.yml
│── README.md
│── .env

````

---

## ⚙️ How to Run Locally

### 🔹 Backend
```bash
# In root folder
docker compose up -d
````

Backend runs at 👉 [http://localhost:8000/docs](http://localhost:8000/docs)

### 🔹 Frontend

```bash
cd frontend
npm install
npm start
```

Frontend runs at 👉 [http://localhost:3000](http://localhost:3000)

---

## 📸 Screenshots 

![Upload Document Screenshot](screenshots/upload.png)
![Query Document Screenshot](screenshots/query.png)

*(Place your images in a folder called `screenshots/` in the repo)*

---

## 🔑 Notes

* Requires a valid **Google Gemini API Key** in `.env` file
* Works best with **English text** documents
* Very large documents may take extra processing time

---

## 👨‍💻 Author

**Rishikesh Yadav**
🚀 Built as a startup demo project

````

---

👉 After pasting this in `README.md`, run:
```bash
git add README.md
git commit -m "Added professional README with features and usage"
git push
````



