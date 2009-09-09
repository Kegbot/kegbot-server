
import unittest
from django.conf import settings
from south.hacks import hacks

# Note: the individual test files are imported below this.

class Monkeypatcher(unittest.TestCase):

    """
    Base test class for tests that play with the INSTALLED_APPS setting at runtime.
    """

    def create_fake_app(self, name):
        
        class Fake:
            pass
        
        fake = Fake()
        fake.__name__ = name
        return fake


    def create_test_app(self):
        
        class Fake:
            pass
        
        fake = Fake()
        fake.__name__ = "fakeapp.migrations"
        fake.__file__ = os.path.join(test_root, "fakeapp", "migrations", "__init__.py")
        return fake
    
    
    def setUp(self):
        """
        Changes the Django environment so we can run tests against our test apps.
        """
        hacks.set_installed_apps(["fakeapp", "otherfakeapp"])
    
    
    def tearDown(self):
        """
        Undoes what setUp did.
        """
        hacks.reset_installed_apps()


# Try importing all tests if asked for (then we can run 'em)
try:
    skiptest = settings.SKIP_SOUTH_TESTS
except:
    skiptest = False

if not skiptest:
    from south.tests.db import *
    from south.tests.logic import *
    from south.tests.autodetection import *