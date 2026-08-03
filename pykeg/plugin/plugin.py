"""Plugin interface for extending the Kegbot frontend."""

import logging

from pykeg.plugin.datastore import ModelDatastore


class Plugin:
    """Interface class for plugins."""

    NAME = None
    SHORT_NAME = None
    DESCRIPTION = None
    VERSION = None
    URL = None

    def __init__(self, datastore=None, plugin_registry=None):
        self.datastore = datastore if datastore else ModelDatastore(self.get_short_name())
        self.logger = logging.getLogger(self.get_short_name())
        self.plugin_registry = plugin_registry or {}

    @classmethod
    def get_version(cls):
        """Return the curent plugin version.

        Subclasses should set the class attribute VERSION, which is
        returned by the default implementation.

        Returns:
            The version, as a tuple of (major, minor, micro[, tag]).
            Major, minor, and micro must be integers; tag, if present,
            must be an arbitrary string.
        """
        if not cls.VERSION:
            raise NotImplementedError
        return cls.VERSION

    @classmethod
    def get_name(cls):
        """Return a human-readable (one or two word) name for this plugin.

        Subclasses should set the class attribute NAME, which is
        returned by the default implementation.
        """
        if not cls.NAME:
            raise NotImplementedError
        return cls.NAME

    @classmethod
    def get_short_name(cls):
        """Return a short for this plugin.

        Subclasses should set the class attribute NAME, which is
        returned by the default implementation.
        """
        if not cls.SHORT_NAME:
            raise NotImplementedError
        return cls.SHORT_NAME

    @classmethod
    def get_description(cls):
        """Return a concise human-readable description for this plugin.

        Subclasses should set the class attribute DESCRIPTION, which is
        returned by the default implementation.
        """
        if not cls.DESCRIPTION:
            raise NotImplementedError
        return cls.DESCRIPTION

    @classmethod
    def get_url(cls):
        """Returns the information URL (homepage) for the plugin.

        Subclassses should set the class attribute URL, which is returned
        by the default implementation.
        """
        if not cls.URL:
            raise NotImplementedError
        return cls.URL

    # Plugin methods

    def handle_new_events(self, event):
        """Called synchronously when new events are posted.

        Plugins should *quickly* perform any work. Long-running work can be
        performed by scheduling a background task in this method.
        """
        pass

    # Helpers

    def save_form(self, form, prefix):
        return self.datastore.save_form(form, prefix)

    def load_form(self, form_cls, prefix, **form_kwargs):
        return self.datastore.load_form(form_cls, prefix, **form_kwargs)
