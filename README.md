# 🔍 Plag-Check — Full-Stack AI & Web Plagiarism Detection System

Plag-Check is a full-stack, microservice-based text analysis platform that scans text, code, and documents for plagiarized content across the live internet, and evaluates text for AI-generated patterns (ChatGPT, Claude, Gemini).

---

## ✨ Features & Capabilities

- 🌐 **Live Web Plagiarism Engine**:
  - Crawls and searches the live internet using the **Tavily AI Search Engine**.
  - Ranks matching sources and returns direct **source URLs**, page titles, and similarity percentages.
  - Sentence-level granularity: Highlights exact matching sentences with their corresponding web sources.

- 🤖 **AI Content Probability Detector**:
  - Evaluates text using 4 NLP heuristics to detect LLM-authored text:
    1. **Sentence Burstiness & Uniformity**: Analyzes sentence length variance.
    2. **Perplexity Proxy**: Measures lexical diversity and unique-to-total word ratios.
    3. **AI Keyword Scanner**: Identifies common LLM buzzwords and phrase structures.
    4. **Transition Word Density**: Evaluates connective word frequencies.

- 💻 **Programming Code Similarity Detector**:
  - Automatically identifies code vs. natural language.
  - Sanitizes comments (`# ...`) and string literals (`"..."`) to focus on structural code logic.
  - Computes structural similarity using TF-IDF vectorization.

- 📄 **Multi-Format Document Parsing**:
  - Upload `.pdf`, `.docx`, and `.txt` files.
  - Parsed directly on the client side using `pdfjs-dist` (PDFs) and `mammoth` (Word documents).

- 🎙️ **Voice-to-Text Input**:
  - Dictate text or reference passages using browser-native **Web Speech API** (`SpeechRecognition`).

- 📊 **Visual Analytics & PDF Export**:
  - Interactive **Chart.js** doughnut charts showing originality vs. similarity breakdowns.
  - One-click downloadable **PDF scan reports** generated via `jspdf`.

- 🛡️ **Authentication & History (Optional)**:
  - JWT-based authentication with `bcryptjs` password encryption.
  - Persistent scan history stored in MongoDB.
  - Graceful fallback: Plagiarism and AI scans work 100% even without MongoDB connected.

---

## 🏗️ System Architecture

Plag-Check uses a **3-tier decoupled microservice architecture**:

```text
┌─────────────────────────┐
│     React Frontend      │  (Port 3000)
│   (Upload, Charts, UI)  │
└────────────┬────────────┘
             │ HTTP / REST
┌────────────▼────────────┐
│   Node / Express API    │  (Port 5000)
│ (Auth, Reports, Gateway)│
└──────┬─────────────┬────┘
       │             │
       ▼             ▼
┌─────────────┐ ┌───────────────────────────┐
│   MongoDB   │ │    FastAPI ML Service     │  (Port 5001)
│ (User / DB) │ │ (TF-IDF, NLP, Heuristics) │
└─────────────┘ └─────────────┬─────────────┘
                              │
                              ▼
                       ┌──────────────┐
                       │  Tavily API  │ (Live Web Search)
                       └──────────────┘
```

| Service | Technology | Port | Responsibilities |
| :--- | :--- | :--- | :--- |
| **Frontend** | React, Tailwind, Chart.js | `3000` | UI, Document Parsing, Voice Dictation, PDF Export |
| **Backend** | Node.js, Express, Mongoose | `5000` | Gateway, Authentication, MongoDB Persistence, Rate Limiting |
| **ML Engine** | Python, FastAPI, Uvicorn, Scikit-learn, NLTK | `5001` | TF-IDF Vectorization, Cosine Similarity, AI Detection Heuristics, Web Crawling |

---

## 📁 Project Structure

```text
├── backend/                # Node.js Express API gateway
│   ├── config/             # Passport & Email configurations
│   ├── controllers/        # Check & Auth controllers
│   ├── models/             # Mongoose schemas (User, Report, ApiKey)
│   ├── routes/             # Express API routes
│   ├── .env.example        # Backend environment variables template
│   ├── package.json        # Backend dependencies
│   └── server.js           # Express server entry point
├── frontend/               # React client application
│   ├── public/             # Static public assets
│   ├── src/                # React source code (components, pages, services)
│   ├── package.json        # Frontend dependencies
│   └── vercel.json         # Vercel deployment config
├── ml/                     # Python FastAPI NLP & ML microservice
│   ├── app.py              # FastAPI application & NLP pipelines
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # ML environment variables template
├── .gitignore              # Git ignore rules
├── package.json            # Root workspace orchestration scripts
└── README.md               # Documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** (v18+)
- **Python** (v3.10+)
- **MongoDB** *(Optional — service functions without MongoDB via memory fallback)*

---

### 1. Start the ML Service (FastAPI)

```bash
cd ml
pip install -r requirements.txt
cp .env.example .env     # Optional: add your TAVILY_API_KEY
python app.py
```
*ML Service will be running at `http://127.0.0.1:5001` with interactive API docs at `http://127.0.0.1:5001/docs`.*

---

### 2. Start the Backend Service (Node/Express)

```bash
cd backend
npm install
cp .env.example .env
npm start
```
*Backend API will be running at `http://localhost:5000`.*

---

### 3. Start the Frontend (React)

```bash
cd frontend
npm install
npm start
```
*Frontend will open automatically at `http://localhost:3000`.*

---

### ⚡ Shortcut (From Project Root)

You can install all dependencies and start individual services from the root folder:

```bash
# Install all dependencies
npm run install:all

# Start individual services in separate terminals
npm run start:ml         # Python FastAPI (Port 5001)
npm run start:backend    # Express (Port 5000)
npm run start:frontend   # React (Port 3000)
```

---

## 🔑 Environment Variables

### Backend (`backend/.env`)

```env
PORT=5000
MONGO_URI=mongodb://localhost:27017/plagiarism-checker
ML_SERVICE_URL=http://127.0.0.1:5001
JWT_SECRET=your_jwt_secret_key
SESSION_SECRET=your_session_secret
```

### ML Engine (`ml/.env`)

```env
PORT=5001
TAVILY_API_KEY=your_tavily_api_key_here
```

---

## 📡 API Endpoints

### ML Service (FastAPI — Port 5001)

- `GET /health` — Health check endpoint.
- `GET /docs` — Interactive OpenAPI (Swagger) documentation.
- `POST /analyze` — Core plagiarism, similarity, and AI evaluation pipeline.

### Backend Gateway (Express — Port 5000)

- `POST /api/check` — Runs plagiarism check (calls ML service) and saves report to MongoDB.
- `GET /api/history` — Fetches user's previous scan reports (auth required).
- `POST /api/auth/register` — Creates user account.
- `POST /api/auth/login` — Authenticates user and returns JWT token.

---

## 📄 License

This project is licensed under the ISC License.
