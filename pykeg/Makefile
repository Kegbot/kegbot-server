PYTHON_TOP = $(shell dirname $(shell pwd))
PYTHON_ENV = PYTHONPATH=$(PYTHON_TOP)

PROD_SETTINGS = pykeg.settings
TEST_SETTINGS = pykeg.unittest_settings

PROD_DJANGO_ENV = $(PYTHON_ENV) DJANGO_SETTINGS_MODULE=$(PROD_SETTINGS)
TEST_DJANGO_ENV = $(PYTHON_ENV) DJANGO_SETTINGS_MODULE=$(TEST_SETTINGS)

PROD_ADMIN_COMMAND = $(PYTHON_TOP)/pykeg/bin/kegbot_admin.py
TEST_ADMIN_COMMAND = $(TEST_DJANGO_ENV) django-admin

SETUP_LOGFILE = $(PYTHON_TOP)/pykeg/setup.log

TEST_ADMIN_ARGS = --settings=$(TEST_SETTINGS)

setup: install_db admin

install_db:
	@echo "--- Logging to: $(SETUP_LOGFILE)"
	@echo "--- Installing database ..."
	@$(PROD_ADMIN_COMMAND) syncdb --all --noinput >> $(SETUP_LOGFILE)
	@$(PROD_ADMIN_COMMAND) migrate --all --fake >> $(SETUP_LOGFILE)
	@$(PROD_ADMIN_COMMAND) kb_set_defaults >> $(SETUP_LOGFILE)

admin:
	@echo "--- Creating super user ..."
	@$(PROD_ADMIN_COMMAND) createsuperuser

clean:
	rm -f kegbot.log $(SETUP_LOGFILE)
	rm -rf build
	find . -name "*.pyc" | xargs rm -f

distclean: clean test_clean fixtures_clean
	rm -f pykeg.sqlite.bin
	rm -f pykeg.sqlite.bin-journal

test: test_clean
	$(TEST_ADMIN_COMMAND) test $(TEST_ADMIN_ARGS)

test_clean:
	rm -f unittest_db.sqlite.bin
	rm -f unittest_db.sqlite.bin-journal


### These targets are obsolete or rarely used

fixtures: distclean test
	$(PROD_ADMIN_COMMAND) dumpdata $(PROD_ADMIN_ARGS) --format=json > core/fixtures/initial_data.json

fixtures_clean:
	rm -f core/fixtures/initial_data.json

.PHONY: setup install_db admin clean distclean test test_clean
.PHONY: testdata fixtures fixtures_clean

# vim: noet
