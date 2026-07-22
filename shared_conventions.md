# TravelTrack Pro - Shared Conventions & Local Run Instructions

This document outlines the API standards, naming conventions, and setup instructions agreed upon during the Day 1 scaffolding.

---

## 1. API Response Shape Conventions

To keep frontend integrations clean and predictable, all backend JSON responses must adhere to the following standard shapes:

### Success Response Shape
```json
{
  "data": {
    "id": "64b0f342f1d9a24c88514101",
    "title": "Southeast Asia Adventure",
    "total_budget": 150000.0
  },
  "error": null
}
```

### Error Response Shape
```json
{
  "data": null,
  "error": {
    "code": "JOURNEY_NOT_FOUND",
    "message": "The journey with ID 64b0f342f1d9a24c88514101 does not exist in the database."
  }
}
```

---

## 2. Naming Conventions

* **Backend (Python / FastAPI):**
  * Variables, functions, and file names: `snake_case` (e.g., `get_journey_details`, `models.py`).
  * Class names: `PascalCase` (e.g., `ExpenseSplit`, `Journey`).
  * Endpoints: `kebab-case` prefixed with `/api` (e.g., `/api/expenses/parse-text`).
* **Frontend (JavaScript / React):**
  * Variables and functions: `camelCase` (e.g., `activeJourney`, `fetchJourneys`).
  * Component and page file names: `PascalCase` (e.g., `JourneyDetail.jsx`, `Login.jsx`).
* **Database (MongoDB / Beanie):**
  * Collection names: plural `snake_case` (e.g., `users`, `journeys`, `expenses`).
  * Fields: `snake_case` (e.g., `amount_local`, `exchange_rate_used`).

---

## 3. How to Run Locally

### Running the Backend
1. Open a terminal in the `backend/` directory.
2. Activate the virtual environment:
   * **Windows (PowerShell):** `.\venv\Scripts\Activate.ps1`
   * **macOS/Linux:** `source venv/bin/activate`
3. Run the development server:
   * `python -m uvicorn app.main:app --reload --port 8000`
4. Access the API documentation at: `http://localhost:8000/docs`

### Running the Frontend
1. Open a terminal in the `frontend/` directory.
2. Start the Vite development server:
   * `npm run dev`
3. Access the web app at: `http://localhost:5173/`
