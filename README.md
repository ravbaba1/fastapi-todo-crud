# FastAPI To-Do CRUD API with SQLite Persistent Database 🛠️🗄️🔒

A production-style learning backend project completed for my **Flyrank** internship track. This project demonstrates building full CRUD routes integrated directly with a localized relational database.

## 🚀 Key Milestone Stages Completed
- **Stage 0-3 (CRUD Routing)**: Programmed clean endpoints using FastAPI to handle full data life cycles.
- **Stage 4 (Raw SQL Mastery)**: Configured schema directly using native SQLite statements and verified row indexes inside the engine room interface.
- **Stage 5 (Data Persistence & Schema Rules)**: Migrated local runtime memory storage into an isolated hard drive database (`todo.db`) using relational tables.

## 🛡️ Offensive Security Principles Applied
- **SQL Injection (SQLi) Defense**: Replaced all string concatenation queries with strictly bounded **parameterized parameters** (`?` placeholders). This isolates incoming user fields so malicious commands are never executed by the SQL engine.
- **Data Poisoning Mitigation**: Mandated type safety checking via **Pydantic models**, dropping structural payloads that fail schema verification rules (`422 Unprocessable Content`).

## 💻 Technical Stack
- Python 3.13
- FastAPI
- PostgreSQL 16 (via Docker)
- Pydantic

## 🐳 Containerization Milestone: Postgres Migration Report

### 1. Architecture Proof
- The underlying application storage engine was completely swapped from an ephemeral setup to PostgreSQL. 
- Because of clean separation of layers, only `database.py` required modifications. Zero routes or core service files (`main.py`) were changed or broken during this database migration.

### 2. Multi-Container Orchestration
- The entire stack is fully orchestrated via `docker-compose.yml`. 
- Running a single command (`docker compose up`) successfully spins up both the PostgreSQL relational database container (`flyrank_postgres`) and the FastAPI backend service engine (`flyrank_api`) on a shared local network wrapper.

### 3. Data Persistence Verification Proof
To verify that data survives independent container lifecycles, the following testing protocol was executed:
1. Navigated to the Swagger documentation interface (`http://localhost:8000/docs`).
2. Executed a `POST` request to insert rows of mock testing data.
3. Executed a `GET` request to verify the rows were written successfully.
4. Stopped the active execution stack using `Ctrl + C` and cleanly dismantled the environment via `docker compose down`.
5. Restarted the system using `docker compose up`.
6. Executed a subsequent `GET` request. The previously saved items persisted intact, proving that the `postgres_data` volume is bound and storing state information correctly.
