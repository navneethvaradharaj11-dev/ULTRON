import os
import shutil
import pytest
from scripts.backup_restore import perform_backup, verify_restore


def test_backup_and_restore_verification():
    test_backup_dir = "test_backups_dir"
    backup_path = perform_backup(test_backup_dir)
    assert os.path.exists(backup_path)

    verified = verify_restore(backup_path)
    assert verified is True

    # Cleanup
    if os.path.exists(test_backup_dir):
        shutil.rmtree(test_backup_dir)
