# 🧠 Advisor FastAPI — AI-Powered Life Insurance Recommendation API

Advisor FastAPI is a modular **FastAPI backend** that uses **Google Gemini**, **E2B Sandbox**, and **Firecrawl** to simulate an intelligent financial advisor that recommends optimal **life insurance coverage** and **term plan comparisons** based on user profiles.

It’s designed for scalability — modular architecture, clean controllers, and future-ready routes like `/advisor/history` and `/advisor/compare`.

---

## 🚀 Features

- ⚡ **FastAPI-based backend** — lightweight, asynchronous, and production-ready.
- 🤖 **Gemini AI integration** — generates reasoning and coverage recommendations.
- 🧮 **E2B Sandbox (simulated)** — deterministic calculation of coverage formula.
- 🔍 **Firecrawl Integration (simulated)** — mimics fetching latest insurance plans.
- 🧱 **Modular architecture** — clean folder separation: core, services, models, controllers, routers.
- 🧠 **Scalable routes**:
  - `POST /advisor/advise` → Get coverage recommendation
  - `GET /advisor/history` → Retrieve past advice (in-memory)
  - `POST /advisor/compare` → Compare multiple user profiles
  - `GET /advisor/health` → Quick system status check
- 🧩 **Easily extendable** for DB persistence, caching, or ML model integration.

---

## 🗂️ Project Structure

```
AI_LifeInsuranceAdvisor_v2/
│
├── app/
│   ├── main.py                 ← FastAPI entry point
│   ├── core/                   ← config, utilities
│   ├── services/               ← Gemini integration
│   ├── models/                 ← Pydantic schemas
│   ├── controllers/            ← business logic
│   └── routers/                ← route definitions
│
├── .env                        ← environment variables
├── requirements.txt            ← dependencies
├── pyproject.toml              ← project metadata
├── README.md                   ← documentation
└── uv.lock                     ← dependency lock (optional)
```

---

## 🧰 Tech Stack

| Component | Description |
|------------|--------------|
| **FastAPI** | Core API framework |
| **Google Generative AI (Gemini)** | Model for reasoning & recommendation |
| **E2B Sandbox** | Secure Python computation environment |
| **Firecrawl** | Simulated product search integration |
| **Pydantic** | Request validation |
| **Uvicorn** | ASGI server for FastAPI |
| **Streamlit (optional)** | Companion UI for visual testing |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/advisor-fastapi.git
cd advisor-fastapi
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate      # (Mac/Linux)
.venv\Scripts\activate         # (Windows)
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment
Create a `.env` file in the project root:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

(Optional) Add others:
```bash
FIRECRAWL_API_KEY=your_firecrawl_key_here
E2B_API_KEY=your_e2b_key_here
```

---

## 🚀 Run the API

Run locally with **Uvicorn**:

```bash
uvicorn app.main:app --reload
```

Open the Swagger UI:
👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🧪 Example Requests

### ✅ POST `/advisor/advise`
```json
{
  "age": 35,
  "annual_income": 85000,
  "dependents": 2,
  "location": "United States",
  "total_debt": 200000,
  "available_savings": 50000,
  "existing_life_insurance": 100000,
  "income_replacement_years": 10,
  "currency": "USD"
}
```

**Response:**
```json
{
  "coverage_amount": 750000,
  "coverage_currency": "USD",
  "recommendations": [
    {"name": "XYZ Term Plan", "summary": "...", "link": "..."}
  ],
  "research_notes": "Simulated Firecrawl search.",
  "timestamp": "2025-11-06T15:05:12Z"
}
```

### 🕒 GET `/advisor/history`
Returns previously generated advice sessions (in-memory).

### ⚖️ POST `/advisor/compare`
Takes multiple profiles and compares coverage recommendations.

---

## 🧩 Future Enhancements

- 💾 SQLite / SQLModel persistence for `/advisor/history`
- 🧠 Real Firecrawl API integration
- 🧮 Replace simulated E2B with live code execution
- 🐳 Docker + Kubernetes deployment
- 🔐 OAuth2-based authentication for user tracking

---

## 🧑‍💻 Development

### Run with auto-reload
```bash
uvicorn app.main:app --reload
```

### Run tests (if added)
```bash
pytest -v
```

---

## 📜 License
This project is distributed under the MIT License.

---

## 👨‍💻 Author
**Suyash Utekar**  
🚀 FastAPI + AI Engineer | Building scalable AI-driven backend systems  
📧 Contact: [minecraftzannds@gmail.com](mailto:minecraftzannds@gmail.com)
