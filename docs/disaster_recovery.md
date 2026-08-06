# ContextOS - Disaster Recovery & Backup Operating Procedure

**Owner:** Principal DevOps Engineer  
**Target RTO:** < 5 Minutes  
**Target RPO:** < 1 Minute  

---

## 1. Backup & Restore Operating Procedures

### PostgreSQL Database Snapshots
- **Automated Schedule**: Continuous WAL archiving + daily full `pg_dump` snapshot.
- **Verification Script**: `python scripts/backup_restore_drill.py`
- **Manual Backup Trigger**:
  ```bash
  docker exec -t contextos_postgres pg_dump -U contextos contextos_db > backup_snapshot.sql
  ```
- **Manual Restore Command**:
  ```bash
  docker exec -i contextos_postgres psql -U contextos contextos_db < backup_snapshot.sql
  ```

---

## 2. Container Restart & Rollback Resilience

1. **Self-Healing Probes**: Docker `healthcheck` probes restart failed API containers automatically within 15 seconds.
2. **Graceful Failover**: In the event of primary database failover, `asyncpg` connection pool automatically reconnects on next API request.
