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
- SQLite3
- Pydantic
