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

# Book Scraper → Secure To-Do API Pipeline

A small, polite scraper that pulls 60 books from [books.toscrape.com](https://books.toscrape.com/)
(a free, scraping-legal practice site), cleans and validates the data, then
stores it through an authenticated FastAPI + Supabase backend.

## What this project actually does

Two things are happening, and it's worth keeping them separate:

1. **Scraping and cleaning** — `scraper.py` fetches paginated HTML, parses
   messy text like `"£51.77"` and `"Three"` into real numbers, and validates
   every record against a Pydantic schema before it goes anywhere.
2. **Storage** — the backend (`main.py`) only exposes a to-do API
   (`/tasks`), so each validated book gets reshaped to fit that schema:
   price and rating are folded into the task's `title` string, and stock
   status becomes `completed`. A book isn't conceptually a task — it's
   adapted to fit the one storage container available. See
   [Known limitations](#known-limitations) below for how to fix this properly.

## Architecture

```
books.toscrape.com  →  scraper.py  →  BookSchema (validation)  →  FastAPI /tasks  →  SQLite (items table)
                                                ↑
                                      authenticated via Supabase
                                      (/auth/login, Bearer token)
```

## Files

| File | Purpose |
|---|---|
| `main.py` | FastAPI backend. Handles Supabase auth (`/auth/signup`, `/auth/login`) and a Bearer-token-protected CRUD API for `/tasks`, backed by a local SQLite `items` table. |
| `database.py` | SQLite connection + table setup (referenced by `main.py`; not covered in detail here). |
| `scraper.py` | The scraper. Logs into the API, scrapes 60 books across 3 pages, validates each with `BookSchema`, and POSTs each one to `/tasks`. |
| `.env` | Holds real credentials (Supabase keys, scraper login). **Never commit this file.** |

## Setup

### 1. Install dependencies

```bash
pip install fastapi uvicorn python-dotenv supabase requests beautifulsoup4 pydantic
```

### 2. Environment variables

Create a `.env` file in the project root (same folder as `main.py` and
`scraper.py`) with:

```
SUPABASE_URL=your-supabase-project-url
SUPABASE_ANON_KEY=your-supabase-anon-key
API_USER_EMAIL=your-real-email@example.com
API_USER_PASSWORD=your-real-password
```

Use the **real** credentials for an account you've already created and
confirmed — not placeholder text. `scraper.py` loads this file automatically
via `python-dotenv`; values already set in your shell take priority over
`.env` if both are present.

### 3. Create and confirm a user

Start the backend (`uvicorn main:app --reload`), open Swagger UI at
`http://127.0.0.1:8000/docs`, and use `/auth/signup` to create the account
matching your `.env` credentials. Supabase will send a confirmation email —
click the link (or manually confirm the user in the Supabase dashboard under
Authentication → Users) before login will work.

## Running it

```bash
# Terminal 1 — start the backend
uvicorn main:app --reload

# Terminal 2 — run the scraper
python scraper.py
```

Expected output: a robots.txt check, a successful login, then 60 "Success"
log lines as each book is validated and inserted, ending on a summary line.

## What makes the scraper "polite"

- **Checks `robots.txt` before touching anything else.** Refuses to run if
  the target page is disallowed or robots.txt can't be read at all.
- **Identifies itself honestly.** Sends a descriptive `User-Agent` rather
  than pretending to be a browser.
- **Throttles requests.** A fixed delay between page fetches (`REQUEST_DELAY`).
- **Retries with backoff, not forever.** Network hiccups get a few retries
  with increasing wait time rather than an infinite loop or an instant crash.
- **Never trusts scraped data.** Every record is checked against
  `BookSchema` (title required, price > 0, rating 1–5) before it's sent to
  the API. Anything that fails validation is logged and dropped — it never
  reaches the database.

## Known limitations

- **Price and rating aren't stored as real fields.** `TaskBlueprint` only
  has `title` and `completed`, so the scraper crams price/rating into the
  title as text (`"Book Title (£51.77, 3★)"`). To fix properly: add
  `price` and `rating` columns to the `items` table and matching fields to
  `TaskBlueprint`, then update both `main.py`'s `create_task` and
  `scraper.py`'s `api_payload` to use them directly.
- **Re-running the scraper duplicates data.** Nothing currently checks
  "has this book already been stored?" — running it twice produces 120
  rows, not 60. A unique key (e.g. the book's detail-page URL) would be
  needed to make re-runs safe.
- **SQLite `id` gaps after deletes are normal.** IDs don't reset or reuse
  after a row is deleted (e.g. test tasks made via Swagger) — an id range
  like 3–62 instead of 1–60 just reflects earlier rows that were deleted,
  not a scraping error.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `Missing API_USER_EMAIL / API_USER_PASSWORD environment variables` | Vars not set in this shell session, or `.env` isn't being loaded/found | Set them with `$env:API_USER_EMAIL = '...'` (PowerShell) for this session, or confirm `.env` is in the same folder and `python-dotenv` is installed |
| `401 Client Error: Unauthorized` on login | Credentials don't match a real, confirmed Supabase account | Log the response body (`Login rejected (401): {...}`) to see the real Supabase message — usually "Invalid login credentials" (wrong email/password) or "Email not confirmed" |
| Env var prints as literal placeholder text (`you@example.com`) | Example command copied verbatim without substituting real values | Re-set with your actual credentials, in single quotes in PowerShell to avoid `$`-expansion issues |
| Scraper gets 0 books, page has no `article.product_pod` | Wrong start URL (e.g. `toscrape.com` instead of `books.toscrape.com`) | Confirm `BOOK_SITE_START = "https://books.toscrape.com/index.html"` |
| Task IDs don't start at 1 | Earlier test rows were created and deleted; SQLite doesn't reuse ids | Expected behavior, not a bug — row *count* is what matters |

## Result

60 books scraped across 3 pages, each validated for a non-empty title, a
positive numeric price, and a rating between 1 and 5, then stored through an
authenticated API call — with the whole run surviving malformed cards,
network hiccups, and page failures without crashing.

