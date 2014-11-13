from .exceptions import BackupError


def engine_name():
    return 'unknown'


def is_installed(*args, **kwargs):
    raise BackupError('Engine unsupported.')


def dump(*args, **kwargs):
    raise BackupError('Engine unsupported.')


def restore(*args, **kwargs):
    raise BackupError('Engine unsupported.')


def erase(*args, **kwargs):
    raise BackupError('Engine unsupported.')
