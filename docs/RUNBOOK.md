# 🚨 Incident Runbooks

**"The Runbook does not sleep. Write instructions for your nonfunctional 3 AM self."**

---

## 🔴 Alert: `Service_Down`

**Trigger:** /health endpoint fails continuously for >2 minutes or PagerDuty receives a `502 Bad Gateway` repeatedly.

### Step-by-Step Response:
1. **Acknowledge the Alert:** Mark the alert "In Progress" so the rest of the team knows you are investigating.
2. **Check Container Status:**
   SSH into the host instance.
   ```bash
   docker ps
   ```
   *Are the API containers running? Is Docker attempting to restart them in a loop?*
3. **Scan the Logs:**
   If the container is restarting repeatedly, capture the exit logs immediately:
   ```bash
   docker logs failsafe-api --tail 100
   ```
4. **Identify the Core Fault:**
   - If the log reads: `peewee.OperationalError: FATAL: password authentication failed` → DB Credentials have been rotated or lost. *Action: Validate `.env`.*
   - If the log reads: `ModuleNotFoundError` or invalid Python code → A bad deploy bypassed CI. *Action: Execute emergency GIT Rollback (See [DEPLOY.md](DEPLOY.md)).*
   - If the logs are frozen but container is up → The process is deadlocked (Waitress/Gunicorn thread starvation). *Action: Manually force `docker restart failsafe-api`.*

---

## 🟡 Alert: `High_Database_Latency`

**Trigger:** `/health` endpoint reports `latency_ms > 1000` for 3 consecutive intervals.

### Step-by-Step Response:
1. **Validate It:** Open the monitoring dashboard or manually hit `/health` to confirm the numbers.
2. **Probe Database CPU/Connections:**
   Access the PostgreSQL instance to see if connections are saturated.
   ```sql
   SELECT count(*) FROM pg_stat_activity;
   ```
3. **Determine the Bottleneck:**
   - Is it high traffic? If we are facing a user tsunami, the DB may be locking up scaling the Peewee connection limit pooling. *Action*: We may need to manually dial up container numbers in `docker-compose` if load balancing is available.
   - Is it a rogue query? Ensure the `User.get_or_none()` calls aren't scanning non-indexed fields. Email is unique and indexed, so it shouldn't be the issue.
4. **Alleviation (Short-Term):** Restart the container to clear the queue connection pools:
   ```bash
   docker restart failsafe-api
   ```
