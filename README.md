# ✈️ TravelTrack Pro

**TravelTrack Pro** is a modern, premium, and feature-rich travel planning and expense sharing platform. Powered by Google's **Gemini 1.5 Flash**, it helps travelers log expenses effortlessly via natural language or receipt scans, flags potential scams/overpricing in real-time, projects budget pacing with a witty "Splurge Advisor," and provides an interactive AI Chatbot to verify deals on the go.

---

## 🚀 Key Features

*   **👥 Smart Group Expense Sharing:** Log expenses and split costs equally or custom-tailored among trip participants.
*   **💱 Multi-currency Profile Optimization:** Configures home currency and accounts for custom credit card forex fees and flat ATM withdrawal fees to track actual travel costs.
*   **✍️ Natural Language Logging:** Input casual phrases like `"spent 1200 THB on dinner yesterday"` or `"120 USD for airport taxi"` and let Gemini extract structured metadata (amount, currency, category, description) automatically.
*   **📸 Multimodal Receipt Scanning (OCR):** Upload receipt images directly; the built-in vision model automatically reads the bill, extracts totals, detects the currency, and categorizes the transaction.
*   **🚨 Real-Time Scam & Typo Guard:** The system monitors logged items and flags suspicious charges, extreme overpricing, or potential typos (e.g. paying 10,000 JPY instead of 1,000 JPY for lunch) relative to standard destination rates.
*   **📅 AI "Splurge Advisor" Pacing:** Evaluates the budget daily burn rate, projects a precise budget exhaustion date, and serves funny, engaging, or alarming pacing guidance.
*   **💬 Interactive AI Scam Consultant:** An on-trip AI chatbot to discuss prices and verify deals (e.g. *"Is 500 Baht a fair price for a Tuk Tuk from Wat Pho to Khao San Road?"*) before you pay.
*   **📈 Rich Analytics Dashboard:** Visual analytics using interactive charts tracking spending across categories (Stay, Food, Activities, Transport, Shopping, Misc), pacing over time, and individual member shares.

---

## 🛠️ Tech Stack & Dependencies

### Backend
*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+)
*   **Database:** MongoDB via [Beanie ODM](https://beanie-odm.dev/) (object-document mapper) & Motor (async driver)
*   **AI SDK:** Google Generative AI (Gemini 1.5 Flash API)
*   **Auth:** JWT Tokens, PyJWT, Passlib (bcrypt)
*   **Environment:** python-dotenv, Pydantic v2

### Frontend
*   **Framework:** [React 19](https://react.dev/) + [Vite](https://vite.dev/) + TypeScript/JavaScript
*   **Styling:** Tailwind CSS 3
*   **Charts:** Recharts
*   **Routing:** React Router v7
*   **Icons:** Lucide React
*   **HTTP Client:** Axios

---

## 📁 Repository Structure

```text
TravelTrack/
├── backend/                       # FastAPI Python Backend
│   ├── app/
│   │   ├── app/config.py          # App settings & secrets schema
│   │   ├── app/main.py            # FastAPI initialization & error handlers
│   │   ├── app/models.py          # Beanie MongoDB documents (User, Journey, Expense)
│   │   ├── app/schemas.py         # Pydantic request/response validation schemas
│   │   ├── app/routers/           # API Endpoint controllers
│   │   │   ├── auth.py            # Signup, login, profile endpoints
│   │   │   ├── journeys.py        # Journey management, budget pacing, chatbot
│   │   │   └── expenses.py        # Expense creation, NLP parsing, OCR receipt scan, splits
│   │   └── app/utils/             # Helpers (auth, exchange rate pair fetching, Gemini API)
│   │       ├── auth.py
│   │       ├── auth_deps.py
│   │       ├── exchange.py        # Live Forex fetcher with local offline fallback
│   │       └── llm.py             # Gemini functions (NLP parse, vision OCR, scam flag, Splurge)
│   ├── .env                       # Backend local configuration
│   ├── requirements.txt           # Python backend dependencies
│   └── venv/                      # Local python virtual environment
│
├── frontend/                      # React 19 + Vite Frontend
│   ├── src/
│   │   ├── context/               # Authentication global providers
│   │   ├── pages/                 # UI Views (Login, Signup, Journeys, Details, Analytics)
│   │   ├── utils/                 # Frontend helpers (Axios instances, configuration)
│   │   ├── App.jsx                # Router config & protected route wrapper
│   │   ├── index.css              # Custom Tailwind styles & themes
│   │   └── main.jsx               # React entry point
│   ├── index.html
│   ├── tailwind.config.js
│   ├── package.json
│   └── tsconfig.json
│
├── shared_conventions.md          # Scaffolding instructions, API shapes & guidelines
└── README.md                      # Project documentation
```

---

## ⚙️ Configuration & Environment

To run the application locally, you must configure a `.env` file inside the `backend/` directory.

Create `backend/.env` containing:

```env
# MongoDB Connection URL (local instance or cloud database)
MONGODB_URL="mongodb://localhost:27017/traveltrack"

# Google Gemini API Key (Required for AI Parsing, Scam Check, Splurge Advisor, Chatbot)
GEMINI_API_KEY="your-gemini-api-key-here"

# ExchangeRate-API Key (Optional: Live exchange rate pairs. If empty, local static fallbacks are used)
EXCHANGE_RATE_API_KEY="your-exchangerate-api-key"

# JWT Token Secret (Optional: Fallback is provided in config)
JWT_SECRET="super-secret-key-change-in-production"
```

---

## 🏃 Local Setup & Run Guide

### Prerequisites
*   [Node.js](https://nodejs.org/) (v18+)
*   [Python](https://www.python.org/) (v3.10+)
*   [MongoDB](https://www.mongodb.com/) (Running locally on port `27017` or configured in backend `.env`)

### 1. Launch the Backend

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Set up a virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    *   **Windows (PowerShell):**
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    *   **macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```
4.  Install backend dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Start the FastAPI development server:
    ```bash
    python -m uvicorn app.main:app --reload --port 8000
    ```
6.  The backend server will run at `http://localhost:8000`. You can inspect and test the interactive API docs via Swagger at `http://localhost:8000/docs`.

### 2. Launch the Frontend

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install frontend dependencies:
    ```bash
    npm install
    ```
3.  Start the Vite development server:
    ```bash
    npm run dev
    ```
4.  Open your browser and navigate to `http://localhost:5173/`.

---

## 📜 Development Guidelines & Conventions

All contributions and edits must follow the development conventions outlined in [shared_conventions.md](file:///c:/Users/thanu/OneDrive/Documents/TravelTrack/shared_conventions.md):
*   **Naming Styles:** Python uses `snake_case` classes are `PascalCase`, APIs are prefixed with `/api` using `kebab-case`. React uses `camelCase` for variables and `PascalCase` for component files. Database collections and fields are strictly `snake_case`.
*   **JSON Response Shape:** Standard success and error JSON envelopes must wrap all API responses. Reference [shared_conventions.md](file:///c:/Users/thanu/OneDrive/Documents/TravelTrack/shared_conventions.md) for structure schemas.
*   **Git Constraint:** Do not commit or push files directly to git. All commits and branch merges must be left for the project owner to coordinate.
