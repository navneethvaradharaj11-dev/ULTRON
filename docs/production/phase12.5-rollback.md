# PROJECT ULTRON — EMERGENCY ROLLBACK PROCEDURES

---

## 1. Rollback Trigger Criteria

Automatic rollback is triggered when:
1. Health checks (`/health/live` or `/health/ready`) fail post-deployment.
2. Database migration execution exits with non-zero code.
3. Container crash-loop occurs.

---

## 2. Manual Emergency Rollback Execution

```bash
# Execute emergency rollback script
bash ./scripts/deploy/rollback.sh
```
