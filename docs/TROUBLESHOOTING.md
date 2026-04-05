# 🐛 Troubleshooting & Configuration Guide

## ⚙️ Environment Variables (Config)

To run the FailSafe API, the following variables must be configured. During local runtime, `.env.example` provides safe fallbacks.

| Variable | Description | Default (Local) | Required in Prod? |
|----------|-------------|-----------------|-------------------|
| `FLASK_ENV` | Application environment mode (development or production). | `development` | Yes |
| `DATABASE_NAME` | Target database name. | `hackathon_db` | Yes |
| `DATABASE_HOST` | Host address for connection. | `localhost` | Yes |
| `DATABASE_PORT` | Port for DB connection. | `5432` | Yes |
| `DATABASE_USER` | DB Auth User. | `postgres` | Yes |
| `DATABASE_PASSWORD` | DB Auth Password. | `postgres` | Yes |

---

## 🛠️ Known Bugs and Fixes

### 1. Issue: "uv" command not found during CI/Local Test Execution
- **Symptom:** Running `uv sync` returns a PowerShell CommandNotFound or bash error.
- **Why it happened:** The user's system does not have Astral `uv` globally installed, but our template testing commands rely on it.
- **The Fix:** We implemented a `Dockerfile` that internally installs `uv` and runs the codebase seamlessly. For GitHub Actions, we used the `astral-sh/setup-uv@v4` action to ensure it auto-installs on the runner.

### 2. Issue: Database Integrity Crash on Duplicate Records
- **Symptom:** Creating a user with an email already in the DB caused the Flask app to throw a 500 error due to Peewee `IntegrityError`.
- **Why it happened:** We strictly enforced `unique=True` on the email field, causing Peewee to reject the transaction violently.
- **The Fix:** We added Idempotency checks to `POST /users` that query the DB first (`User.get_or_none`). If a user exists, we intercept it gracefully and reply `200 OK` with the existing user data, preventing the internal crash entirely.

### 3. Issue: Test Database Polluting the Production Database
- **Symptom:** Running `pytest` locally dropped or wiped out tables from `hackathon_db`!
- **Why it happened:** The app was directly bound to the Postgres `db` proxy across the application state.
- **The Fix:** We modified `init_db()` in `app/database.py` to identify if the `TESTING=1` environment variable was active. If it is active, the app automatically swaps `PostgresqlDatabase` out for an in-memory `SqliteDatabase(':memory:')`, isolating all mock assertions seamlessly.
