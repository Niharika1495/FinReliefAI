# FinRelief AI - AI Powered Debt Relief & Financial Recovery Platform

FinRelief AI is a production-grade, scalable platform designed to empower individuals with financial analysis, settlement prediction, and AI-negotiation strategies. The platform helps users analyze their Debt-to-Income (DTI) ratio, predict loan settlement options, and generate professional negotiation letters utilizing the Google Gemini API.

This document outlines the **Phase 1 Architecture & Folder Structure Setup**.

---

## Table of Contents
1. [Recommended Architecture](#recommended-architecture)
2. [Clean Architecture Explanation](#clean-architecture-explanation)
3. [Complete Folder Tree](#complete-folder-tree)
4. [Folder and File Directory (Purpose)](#folder-and-file-directory-purpose)
5. [Text Data Flow Diagram](#text-data-flow-diagram)
6. [Future Scalability & Modular Evolution](#future-scalability--modular-evolution)

---

## Recommended Architecture

FinRelief AI is built using a **Decoupled Architecture** consisting of a **FastAPI backend** and a **React + Vite frontend**. The system follows **Clean Architecture (Onion Architecture)** principles to separate the presentation layer, the business logic, and the data access layers.

```
       +-------------------------------------------------+
       |                  Presentation                   |
       |             React + Tailwind Web App            |
       +-----------------------+-------------------------+
                               |  HTTP (JSON)
                               v  
       +-----------------------+-------------------------+
       |                   API / Routes                  |
       |              FastAPI Router Endpoints           |
       +-----------------------+-------------------------+
                               |  DTOs (Pydantic Schemas)
                               v
       +-----------------------+-------------------------+
       |                  Business Logic                 |
       |    Services / Engines (Financial, Settlement, AI)  |
       +-----------------------+-------------------------+
                               |  ORM (SQLAlchemy Models)
                               v
       +-----------------------+-------------------------+
       |                 Data Access Layer               |
       |              SQLAlchemy + SQLite Database       |
       +-------------------------------------------------+
```

### Key Architectural Guidelines
- **Strict Separation of Concerns**: The business logic (Engines, Services) is unaware of how data is fetched or rendered. The UI (React) communicates only via standardized JSON payloads over HTTP.
- **Dependency Inversion**: High-level modules (e.g. financial engine) define interface/schema contracts. Low-level modules (e.g. database sessions) conform to these contracts.
- **Stateless API**: The backend stores no session state locally. Authentication is handled using JSON Web Tokens (JWT) signed by a secret key.

---

## Clean Architecture Explanation

Clean Architecture divides the application into concentric layers:

1. **Entities / Models (Core)**: Represents the business concepts (Users, Debts, Predictions). These are independent of external frameworks or databases.
2. **Use Cases / Services (Core Logic)**: Contains application-specific business rules. This layer decides how data moves between models and engines (e.g., calculating aggregate debt status, preparing prompt variables for Gemini).
3. **Interface Adapters (Controllers & Repositories)**: Converts data between the format expected by the services and the external frameworks (FastAPI routing layer, SQLAlchemy queries, Pydantic serialization).
4. **Frameworks & Drivers (External)**: Includes databases, web servers, third-party APIs (Gemini). These are kept at the outermost edge of the system to make them easy to swap.

This results in a system that is:
- **Testable**: Business logic can be tested without databases or servers.
- **Independent of UI**: The frontend framework can be upgraded or swapped without affecting the backend logic.
- **Independent of Database**: SQLite can be easily swapped for PostgreSQL by updating the `DATABASE_URL` in the environment configuration, without altering core logic.

---

## Complete Folder Tree

```
FinReliefAI/
├── .gitignore
├── README.md
├── backend/
│   ├── .env.example
│   ├── README.md
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── ai/
│       │   └── __init__.py
│       ├── api/
│       │   └── __init__.py
│       ├── auth/
│       │   └── __init__.py
│       ├── config/
│       │   └── __init__.py
│       ├── core/
│       │   └── __init__.py
│       ├── database/
│       │   └── __init__.py
│       ├── dependencies/
│       │   └── __init__.py
│       ├── financial_engine/
│       │   └── __init__.py
│       ├── middleware/
│       │   └── __init__.py
│       ├── models/
│       │   └── __init__.py
│       ├── routers/
│       │   └── __init__.py
│       ├── schemas/
│       │   └── __init__.py
│       ├── services/
│       │   └── __init__.py
│       ├── settlement_engine/
│       │   └── __init__.py
│       ├── static/
│       │   └── .gitkeep
│       ├── tests/
│       │   └── __init__.py
│       └── utils/
│           └── __init__.py
└── frontend/
    ├── index.html
    ├── package.json
    ├── postcss.config.js
    ├── README.md
    ├── tailwind.config.js
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── assets/
        │   └── .gitkeep
        ├── components/
        │   └── .gitkeep
        ├── context/
        │   └── .gitkeep
        ├── hooks/
        │   └── .gitkeep
        ├── layouts/
        │   └── .gitkeep
        ├── pages/
        │   └── .gitkeep
        ├── routes/
        │   └── .gitkeep
        ├── services/
        │   └── .gitkeep
        ├── styles/
        │   └── index.css
        └── utils/
            └── .gitkeep
```

---

## Folder and File Directory (Purpose)

### Backend Layout (`backend/`)

| Path / Folder | Type | Purpose |
| :--- | :--- | :--- |
| **`app/`** | Folder | The core container for the FastAPI application code. |
| **`app/api/`** | Folder | Handles API global properties, namespaces, and version configurations (e.g., `v1`). |
| **`app/core/`** | Folder | Contains application-wide core configurations, security helpers, and JWT encoding/decryption rules. |
| **`app/config/`** | Folder | Configuration constants and schema configuration loaders. |
| **`app/database/`** | Folder | Setup for database connectors, declarative base metadata, and SQLAlchemy connection sessions. |
| **`app/models/`** | Folder | Declares database schemas (SQLAlchemy tables representing User, Debt, Settlement, etc.). |
| **`app/schemas/`** | Folder | Declares Pydantic data schemas representing incoming requests, responses, and validation constraints. |
| **`app/services/`** | Folder | Contains standard business logic layers coordinating DB data and API results. |
| **`app/financial_engine/`** | Folder | Isolated computation module focusing on financial calculations (DTI ratios, monthly payments). |
| **`app/settlement_engine/`** | Folder | Isolated module handling negotiation algorithms, risk scoring, and settlement success prediction. |
| **`app/ai/`** | Folder | Integration layer with the Google Gemini API (prompt templates, response parsers). |
| **`app/auth/`** | Folder | Helper logic focusing on hashing, verification, password check rules, and permission checks. |
| **`app/middleware/`** | Folder | Custom middlewares (Request logging, custom headers, CORS enforcement, Rate Limiting). |
| **`app/utils/`** | Folder | Reusable system-wide helpers (date parsers, currency converters, string formatters). |
| **`app/dependencies/`** | Folder | Injectable dependencies for FastAPI endpoints (e.g. database session access, token extraction). |
| **`app/routers/`** | Folder | Endpoint routes split logically (auth routes, analytics routes, loan routes, AI routes). |
| **`app/static/`** | Folder | Serves static assets, including generated PDF copies of settlement negotiation letters. |
| **`app/tests/`** | Folder | Automated unit, integration, and performance tests using `pytest`. |
| **`app/main.py`** | File | Entry point. Sets up Uvicorn binding parameters, configures middleware, and maps routers. |
| **`requirements.txt`** | File | Lists production and test dependencies for the Python virtual environment. |
| **`.env.example`** | File | Defines expected environment keys (API keys, ports, database configurations) without value secrets. |
| **`README.md`** | File | Details developer workspace instructions, running, testing, and formatting guidelines. |

---

### Frontend Layout (`frontend/`)

| Path / Folder | Type | Purpose |
| :--- | :--- | :--- |
| **`src/`** | Folder | The core source directory for the React application. |
| **`src/assets/`** | Folder | Holds assets like SVGs, static system imagery, brand icons, and custom logos. |
| **`src/components/`** | Folder | Modular UI elements (buttons, inputs, cards, data grids, modal dialogues). |
| **`src/layouts/`** | Folder | Layout containers (Sidebar wrappers, Guest views, Dashboard shell). |
| **`src/pages/`** | Folder | Full page layouts bound to router states (Dashboard, Prediction, Letters, Profile). |
| **`src/hooks/`** | Folder | Contains reusable React hooks (e.g. `useAuth`, `useLocalStorage`, `useDebounce`). |
| **`src/context/`** | Folder | Context API files representing application state (Auth Session, Global Theme, Calculations state). |
| **`src/services/`** | Folder | API request layer utilizing Axios to query backend FastAPI endpoints. |
| **`src/utils/`** | Folder | Client-side helper scripts (date manipulation, string converters, graph data parsing). |
| **`src/routes/`** | Folder | Declares the route tree configuration mapping URLs to Pages, and defines Guards (e.g., protected routes). |
| **`src/styles/`** | Folder | Entrypoint for tailwind layers, typography overrides, and custom gradients/glassmorphism utilities. |
| **`src/App.jsx`** | File | Application root. Integrates router, style layers, context providers, and boundary shells. |
| **`src/main.jsx`** | File | Mounts the React virtual DOM tree into the index.html target node. |
| **`package.json`** | File | Node package manager scripts, build configurations, and project dependencies. |
| **`vite.config.js`** | File | Configures Vite, including plugins (React), server ports, proxy rules, and path aliases. |
| **`tailwind.config.js`** | File | Tailwind CSS layout configuration, styling variables, and target file mapping. |
| **`postcss.config.js`** | File | Auto-prefixing and Tailwind plugin injection wrapper configurations. |
| **`index.html`** | File | HTML shell containing mount hooks, favicon settings, and Google Fonts links. |
| **`README.md`** | File | Client instructions on building, running dev servers, testing, and structuring modules. |

---

## Text Data Flow Diagram

```
[User Action on UI]
        |
        v
[React Component (Page)]  --->  Calls  ---> [Custom Hook (e.g. useLoans)]
                                                   |
                                                   v
[Axios API Request (Service)]  <-------------------+
        |
        |  HTTP POST /api/v1/settlements (JSON Payload)
        v
[FastAPI Middleware]  (Verifies CORS / CORS / Logs)
        |
        v
[FastAPI Router Endpoint (app/routers/)]
        |
        |  Validates using Pydantic Schemas (app/schemas/)
        v
[FastAPI Dependencies]  (Injects DB Session app/database/ & User Context app/auth/)
        |
        v
[Service Orchestration Layer (app/services/)]
        |
        +---> Calculates Aggregates using [Financial Engine (app/financial_engine/)]
        |
        +---> Predicts Thresholds using [Settlement Engine (app/settlement_engine/)]
        |
        +---> Drafts Letter via [AI Interface (app/ai/)]  <---> [Google Gemini API]
        |
        v
[ORM Data Layer (app/models/)]  ---> Persists ---> [SQLite Database]
        |
        v
[Standard Pydantic Response]  ---> Serialized JSON ---> [Response back to React client]
```

---

## Future Scalability & Modular Evolution

As FinRelief AI grows, this architecture supports scalability in three dimensions:

### 1. Business Logic Partitioning (Engines & Services)
- Calculations (`financial_engine`) and negotiations (`settlement_engine`) are entirely isolated from CRUD operations.
- As the AI negotiation algorithms evolve or we switch models (e.g., from Gemini to Claude or custom models), we only change the `app/ai/` interface. The routes and database structures remain unaffected.

### 2. Multi-Database Scaling
- By separating core operations in `app/database` and using SQLAlchemy models (`app/models`), swapping SQLite for PostgreSQL, MySQL, or Amazon RDS requires zero code changes to queries. You only update the connection string in `.env`.

### 3. Frontend Component & Route Organization
- The folder `frontend/src/services/` acts as an SDK wrapper. Under the hood, we can migrate from simple Axios requests to React Query or Redux Toolkit, and only the service folder needs modification.
- Routing paths are centralized under `src/routes/`, enabling the easy configuration of authorization boundaries, lazy loading, and code splitting of pages.
