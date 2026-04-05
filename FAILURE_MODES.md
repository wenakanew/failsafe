# ⚠️ Failure Modes Documentation – Failsafe Social API

This document outlines how the system behaves under failure conditions and how it maintains reliability.

---

## 1. Invalid Input (Client Errors)

### Scenario
User sends malformed or incomplete JSON:
- Missing fields (e.g., no email)
- Invalid email format
- Age below allowed limit
- Empty or oversized post content

### Behavior
- API responds with `400 Bad Request`
- Returns structured JSON:
```json
{
  "error": "Bad Request",
  "message": "Specific validation error"
}
```

### Reliability Strategy
Strict validation before processing. Early rejection prevents DB corruption.

---

## 2. Duplicate User Creation (Idempotency)

### Scenario
User attempts to create an account with an existing email

### Behavior
API returns 200 OK. Returns existing user data, includes message: "User already exists".

### Reliability Strategy
Enforced via Database uniqueness constraint and Application-level check (get_or_none).

---

## 3. Non-existent Resource Access

### Scenario
Creating a post with an invalid user_id

### Behavior
API responds with 404 Not Found:
```json
{
  "error": "Not Found",
  "message": "User ID not found"
}
```

### Reliability Strategy
Referential integrity validation before DB write.

---

## 4. Database Failure / Transient Errors

### Scenario
Temporary DB connection failure or interruption

### Behavior
Operation retried up to 3 times. If still failing → 500 Internal Server Error.

### Reliability Strategy
Retry wrapper (retry_db_operation) prevents failure from brief interruptions.

---

## 5. Internal Server Errors

### Scenario
Unexpected exceptions (bugs, edge cases)

### Behavior
API responds with:
```json
{
  "error": "Internal Server Error",
  "message": "System encountered an unexpected failure"
}
```

### Reliability Strategy
Global error handler prevents stack trace leaks. Ensures consistent API response format.

---

## 6. Service Health Monitoring

### Scenario
Load balancer or external system checks service health

### Behavior
/health endpoint returns 200 OK if DB is reachable, returns 500 if DB is down. Includes latency measurement.

### Reliability Strategy
Enables traffic routing decisions. Detects degraded system early.

---

## 7. Container Crash (Chaos Engineering)

### Scenario
Application process is killed manually.

### Behavior
Docker automatically restarts container.

### Reliability Strategy
`restart: always` policy in docker-compose. Ensures service self-recovers without human intervention.
