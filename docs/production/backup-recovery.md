# ULTRON BACKUP & DISASTER RECOVERY PROCEDURES

---

## 1. Automated Backup Execution

Run backup script to create timestamped database and credential snapshot:

```bash
python scripts/backup_restore.py
```

Backups are saved to `./backups/ultron_backup_YYYYMMDD_HHMMSS/`.

---

## 2. Automated Restore Verification Test

To verify backup validity and test disaster recovery:

```bash
python scripts/backup_restore.py --test-restore
```

An unverified backup is not considered valid.
