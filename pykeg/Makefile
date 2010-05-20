PYTHON_TOP = $(shell dirname $(shell pwd))
PYTHON_ENV = PYTHONPATH=$(PYTHON_TOP)

TEST_SETTINGS = pykeg.unittest_settings
ADMIN_COMMAND = $(PYTHON_TOP)/pykeg/bin/kegbot_admin.py

SETUP_LOGFILE = $(PYTHON_TOP)/pykeg/setup.log

setup: install_db admin

install_db:
	@echo "--- Logging to: $(SETUP_LOGFILE)"
	@echo "--- Installing database ..."
	@$(ADMIN_COMMAND) syncdb --all --noinput >> $(SETUP_LOGFILE)
	@$(ADMIN_COMMAND) migrate --all --fake >> $(SETUP_LOGFILE)
	@$(ADMIN_COMMAND) kb_set_defaults >> $(SETUP_LOGFILE)

admin:
	@echo "--- Creating super user ..."
	@$(ADMIN_COMMAND) createsuperuser

sync_and_migrate:
	@echo "--- Syncing and migrating"
	@$(ADMIN_COMMAND) syncdb
	@$(ADMIN_COMMAND) migrate --all

clean:
	rm -f kegbot.log $(SETUP_LOGFILE)
	rm -rf build dist src/kegbot.egg-info
	find . -name "*.pyc" | xargs rm -f

distclean: clean test_clean fixtures_clean
	rm -f pykeg.sqlite.bin
	rm -f pykeg.sqlite.bin-journal

test: test_clean
	DJANGO_SETTINGS_MODULE=$(TEST_SETTINGS) $(ADMIN_COMMAND) test core

test_clean:
	rm -f unittest_db.sqlite.bin
	rm -f unittest_db.sqlite.bin-journal


### These targets are obsolete or rarely used

fixtures: distclean test
	$(ADMIN_COMMAND) dumpdata $(PROD_ADMIN_ARGS) --format=json > core/fixtures/initial_data.json

fixtures_clean:
	rm -f core/fixtures/initial_data.json

.PHONY: setup install_db admin clean distclean test test_clean sync_and_migrate
.PHONY: testdata fixtures fixtures_clean

# vim: noet
