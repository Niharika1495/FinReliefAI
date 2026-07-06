# FinRelief AI - Backend Architecture

The backend of FinRelief AI is built with **FastAPI** (Python 3.10+), incorporating SQLAlchemy as the ORM, Pydantic for request/response serialization/validation, and SQLite as the relational storage layer.

---

## Folder Architecture

The backend code is localized in `app/`. It follows Clean Architecture principles:

```
app/
├── core/             # Base configurations (settings.py, security.py)
├── database/         # Session handlers and DB declarations
├── models/           # Declarative database models (entities)
├── schemas/          # Pydantic schemas (data transfer objects)
├── routers/          # Endpoint controllers grouped by topic
├── dependencies/     # Dependency injection (DB session, current user)
├── services/         # Orchestrates business logic flow
├── financial_engine/ # Calculations (DTI, Loan analytics)
├── settlement_engine/# AI/Rule predictions on loan settlements
├── ai/               # AI generation wrappers (Gemini API integrations)
├── auth/             # Cryptography and hashing helpers
├── middleware/       # CORS, Logging, and Rate limiting middlewares
├── utils/            # Shared utilities and helpers
└── static/           # Temp storage for generated PDFs & documents
```

---

## Local Development Setup

### 1. Environment Activation
Create a Python virtual environment and activate it:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Dependency Installation
Install backend packages listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env` and fill out your keys:
```bash
cp .env.example .env
```

### 4. Running the Dev Server
Launch Uvicorn with auto-reload enabled:
```bash
uvicorn app.main:app --reload --port 8000
```
The interactive API documentation will be available at:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Coding Conventions
1. **Pydantic Schemas vs. ORM Models**: Never return database models directly from endpoint functions. Always map them using Pydantic serialization models (defined in `app/schemas/`) to enforce security boundaries.
2. **Modular Engines**: The `financial_engine` and `settlement_engine` modules must remain purely algorithmic and testable in isolation. Avoid writing database queries inside these engines. Pass native types, dataclasses, or lists.
3. **Database Sessions**: Inject database sessions using the dependency resolver `app.dependencies.get_db`. Ensure transaction context is managed via context managers or FastAPI endpoint cycle hooks.
