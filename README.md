# 🔍 Plag-Check — Full-Stack AI & Web Plagiarism Detection System

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![Node.js](https://img.shields.io/badge/Node.js-43853D?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
[![Express](https://img.shields.io/badge/Express.js-404D59?style=for-the-badge)](https://expressjs.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)

**Plag-Check** is a full-stack, microservice-based content integrity platform that scans natural language, source code, and multi-format documents for web plagiarism using real-time internet search, while simultaneously analyzing text for AI-generated patterns (ChatGPT, Claude, Gemini).



🚀 **Live Demo:** https://ai-plagiarism-web-similarity-detect.vercel.app/

---

## 🌟 Key Features

### 1. 🌐 Live Web Plagiarism Detection
- Crawls and searches live web pages using the **Tavily AI Search Engine**.
- Computes sentence-level matching percentages using **TF-IDF Vectorization** and **Cosine Similarity**.
- Generates interactive sentence highlight cards linking directly to the matched web URLs.

### 2. 🤖 AI-Generated Content Probability Detection
Evaluates text through a 4-pillar NLP heuristic scoring pipeline:
1. **Sentence Burstiness & Uniformity:** Analyzes variance in sentence lengths (LLMs exhibit low variance).
2. **Perplexity Proxy (Lexical Diversity):** Measures unique-to-total word ratios across vocabulary.
3. **AI Keyword Footprint:** Scans for common LLM buzzwords (*delve*, *testament*, *tapestry*, *landscape*, etc.).
4. **Transition Word Density:** Measures formal connective tissue frequency (*moreover*, *furthermore*, *consequently*).

### 3. 💻 Programming Code Similarity Analysis
- Automatically detects programming code vs. natural language.
- Sanitizes comments (`# ...`) and string literals (`"..."`) to focus strictly on structural programming logic.
- Calculates structural similarity matrices using TF-IDF across source code snippets.

### 4. 📄 Document Parsing & Voice Dictation
- **Multi-Format Upload:** Upload and parse `.pdf` (via `pdfjs-dist`), `.docx` (via `mammoth`), and `.txt` files directly on the client side.
- **Voice-to-Text Input:** Dictate text directly in-browser using the native **Web Speech API**.
- **Scan Filters:** Toggle options to automatically exclude quoted text and bibliographies/references.

### 5. 📊 Visual Analytics & PDF Reports
- Interactive **Chart.js** doughnut charts displaying originality vs. similarity breakdowns.
- One-click downloadable **PDF scan reports** generated via `jspdf`.

### 6. 🛡️ Authentication & Scan Persistence (With Graceful Fallback)
- JWT-based authentication with `bcryptjs` password encryption and Google OAuth 2.0 integration (`passport`).
- **Zero-Downtime Fallback:** Plagiarism checks and AI detection run 100% in memory even without a MongoDB instance connected. MongoDB is only required to persist scan history across sessions.

---

## 🏗️ Architecture Overview

The system uses a decoupled **3-tier microservice architecture**:

```text
┌────────────────────────────────┐
│      React.js Frontend         │  (Port 3000)
│   (Upload, Charts, PDF, UI)    │
└───────────────┬────────────────┘
                │ HTTP / REST
┌───────────────▼────────────────┐
│     Node.js / Express API      │  (Port 5000)
│ (Gateway, Auth, Reports, Rate) │
└───────┬────────────────┬───────┘
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────────────────────────┐
│   MongoDB    │  │       FastAPI ML Engine          │  (Port 5001)
│ (Users / DB) │  │  (TF-IDF, NLP, Heuristics, NLTK) │
└──────────────┘  └────────────────┬─────────────────┘
                                   │
                                   ▼
                            ┌──────────────┐
                            │  Tavily API  │ (Live Web Search)
                            └──────────────┘
```

| Service | Stack | Port | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Frontend** | React 19, Framer Motion, Chart.js, Tailwind/CSS | `3000` | UI, Document Parsing, Voice Dictation, PDF Report Export |
| **Backend** | Node.js, Express, Passport, Mongoose, JWT | `5000` | Gateway routing, User Authentication, Report Persistence, Rate Limiting |
| **ML Engine** | Python 3.12, FastAPI, Uvicorn, Scikit-learn, NLTK | `5001` | TF-IDF Vectorization, Cosine Similarity, AI Detection, Live Web Crawl |

---

## 📁 Directory Structure

```text
├── backend/
│   ├── config/             # Passport OAuth & Nodemailer configurations
│   ├── controllers/        # Check and Authentication controllers
│   ├── models/             # Mongoose models (User, Report, ApiKey)
│   ├── routes/             # Express API route handlers
│   ├── .env.example        # Backend environment template
│   ├── package.json        # Backend dependencies
│   └── server.js           # Express API gateway entry point
├── frontend/
│   ├── public/             # Static web assets & icons
│   ├── src/
│   │   ├── components/     # UI components (ResultCard, Console, ProgressBar, etc.)
│   │   ├── context/        # React Auth & Theme contexts
│   │   ├── pages/          # App pages (Home, Results, Upload, History, Login)
│   │   └── services/       # Axios API client
│   ├── package.json        # Frontend dependencies
│   └── vercel.json         # Vercel deployment configuration
├── ml/
│   ├── app.py              # FastAPI service with TF-IDF, NLP & AI heuristics
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # ML service environment template
├── .gitignore              # Git ignore rules
├── package.json            # Root workspace orchestration scripts
└── README.md               # Project documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)
- **MongoDB** *(Optional — core scan features run in guest mode without DB)*

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd "plagcheck fast api"
```

---

### Step 2: Start the ML Service (FastAPI)
```bash
cd ml
pip install -r requirements.txt
cp .env.example .env     # Optional: add your free TAVILY_API_KEY
python app.py
```
*The ML Service runs at `http://127.0.0.1:5001` with Swagger docs available at `http://127.0.0.1:5001/docs`.*

---

### Step 3: Start the Backend Service (Express Gateway)
In a new terminal:
```bash
cd backend
npm install
cp .env.example .env
npm start
```
*The Express Gateway runs at `http://localhost:5000`.*

---

### Step 4: Start the Frontend (React)
In a third terminal:
```bash
cd frontend
npm install
npm start
```
*The React application opens automatically at `http://localhost:3000`.*

---

### ⚡ Workspace Shortcuts (From Project Root)
You can also launch or install services directly from the root folder:

```bash
# Install dependencies across all services
npm run install:all

# Run individual services
npm run start:ml         # Starts FastAPI ML Engine (Port 5001)
npm run start:backend    # Starts Express Gateway (Port 5000)
npm run start:frontend   # Starts React Client (Port 3000)
```

---

## 🔑 Environment Variables Configuration

### Backend (`backend/.env`)
```env
PORT=5000
MONGO_URI=mongodb://localhost:27017/plagiarism-checker
ML_SERVICE_URL=http://127.0.0.1:5001
JWT_SECRET=your_jwt_secret_key
SESSION_SECRET=your_session_secret

# Optional: Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Optional: Email Verification & Password Reset
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password
```

### ML Engine (`ml/.env`)
```env
PORT=5001
# Get a free key at https://tavily.com
TAVILY_API_KEY=your_tavily_api_key_here
```

---

## 📡 API Reference

### ML Service (FastAPI — `http://127.0.0.1:5001`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check endpoint (`{"status": "ok"}`) |
| `GET` | `/docs` | Interactive Swagger UI API documentation |
| `POST` | `/analyze` | Core plagiarism, similarity, and AI detection pipeline |

#### Sample Request Body (`POST /analyze`)
```json
{
  "text": "Machine learning algorithms automatically identify patterns in large datasets.",
  "reference": "Machine learning algorithms can identify patterns in data automatically.",
  "check_ai": true,
  "check_web": true,
  "exclude_quotes": false,
  "exclude_bibliography": false
}
```

#### Sample Response (`200 OK`)
```json
{
  "score": 79.3,
  "word_match": 77.78,
  "sentence_match": 79.95,
  "type_detected": "text",
  "matched_sources": [
    {
      "url": "direct_comparison",
      "title": "Reference Document",
      "similarity_score": 79.3
    }
  ],
  "highlights": [
    {
      "input_sentence": "Machine learning algorithms automatically identify patterns in large datasets.",
      "matched_sentence": "Machine learning algorithms can identify patterns in data automatically.",
      "score": 79.95
    }
  ],
  "summary": "High plagiarism detected! Most content is copied.",
  "ai_score": 12.5
}
```

---

### Backend Gateway (Express — `http://localhost:5000`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/check` | Runs plagiarism scan (calls ML engine) & saves report |
| `GET` | `/api/history` | Retrieves logged-in user scan history (JWT required) |
| `GET` | `/api/report/:id` | Fetches a specific scan report by ID |
| `POST` | `/api/auth/register` | Creates a new user account |
| `POST` | `/api/auth/login` | Authenticates user and returns JWT token |
| `GET` | `/api/auth/me` | Validates JWT token and returns profile data |

---

## 🛡️ Security & Rate Limiting
- **Rate Limiters:** Global limiter (100 req/15 min), check limiter (10 checks/min), and auth limiter (5 attempts/15 min) configured via `express-rate-limit`.
- **Password Security:** Password salting and hashing using `bcryptjs`.
- **CORS Protection:** Configured across all microservices for secure client-server communication.

---

## 📄 License
This project is open-source and licensed under the **ISC License**.
