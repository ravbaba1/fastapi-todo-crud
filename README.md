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
7. # Secure Backend Identity & Access Control API

This milestone updates our containerized FastAPI stack with enterprise-grade User Authentication, cryptographic token validation, and hardened tenant database isolation.

## 🛡️ Applied Security Implementations

1. **Cryptographic Identity Control**: Complete integration with the Supabase GoTrue Auth layer using FastAPI's `HTTPBearer` pattern [ravbaba1]. The backend intercepts incoming requests, strips the Bearer token, and cryptographically validates the JWT signature, integrity, and lifespan [ravbaba1].
2. **Anti-IDOR (Insecure Direct Object Reference) Defense**: Neutralized data leak vulnerabilities by re-architecting the database schema to include a mandatory `user_id` column. Every SQL query is parameterized (`WHERE user_id = ?`) to enforce strict ownership boundaries [ravbaba1]. 
3. **SQL Injection Countermeasures**: Zero raw string interpolation inside query paths. Input sanitization is handled natively via query parameters.

---

## 🚀 Environment Configuration

Create a `.env` file in the root directory to store your project secrets (this file is masked from Git via `.gitignore`):

```env
SUPABASE_URL="https://supabase.co"
SUPABASE_ANON_KEY="eyJhbGciOiJIUzI1N......."
```

---

## 🛠️ Deployment & Manual Security Audit Flow

To launch the secure container stack and perform an exploit verification run:

### 1. Rebuild and Run the Stack
```bash
# Clear old stale volumes and build caches
docker compose down --volumes --remove-orphans
docker rmi backendenginnering-web

# Build fresh from manifests and boot
docker compose build --no-cache
docker compose up
```

### 2. Manual Penetration Testing (Swagger UI)
Once Uvicorn starts, open your host browser to `http://localhost:8000/docs`.

* **Step 1 (Sign Up & Log In)**: Use `POST /auth/signup` to register a test user. Authenticate via `POST /auth/login` to obtain your long `access_token` string [ravbaba1].
* **Step 2 (Unlock Route Guardians)**: Click the green **Authorize 🔓** button at the top right of Swagger UI [ravbaba1]. Paste the raw token payload into the value box and click authorize [ravbaba1]. All endpoints will lock securely (**🔒**).
* **Step 3 (Verify Route Protection)**: Execute a `GET /tasks` request without an authorization token to verify the server instantly drops the connection with a `401 Unauthorized` block.

### 3. Multi-Tenant Isolation Simulation (IDOR Audit)
1. Authenticate as **User A**, create an object using `POST /tasks`, and copy the assigned task index `id` (e.g., `1`).
2. Clear your browser auth state, login under a separate context as **User B**, and apply User B's token to the authorization field.
3. Attempt to fetch or execute a malicious `DELETE /tasks/1` targeting User A's row.
4. Verify the database context boundary captures the mismatch, blocks the execution vector, and returns a secure error: `"Item not found or unauthorized deletion attempt."`

