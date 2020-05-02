"""Base notification module."""


from builtins import object


class BaseNotificationBackend(object):
    """Base class for notification backend implementations."""

    def name(self):
        raise NotImplementedError

    def notify(self, event, user):
        """Sends a single notification.

        Args:
            event: the SystemEvent triggering a notification.
            user: the user who should receive the notification.

        Returns:
            True on success, False otherwise.
        """
        raise NotImplementedError("Subclasses must override notify() method")
