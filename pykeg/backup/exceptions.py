class BackupError(IOError):
    """Base backup exception."""


class AlreadyInstalledError(BackupError):
    """Attempt to restore against a non-pristine system."""


class InvalidBackup(BackupError):
    """Backup corrupt or not valid."""
