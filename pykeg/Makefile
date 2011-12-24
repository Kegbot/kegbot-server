PYTHON_TOP = $(shell dirname $(shell pwd))
PYTHON_ENV = PYTHONPATH=$(PYTHON_TOP)

ADMIN_COMMAND = kegbot-admin.py

SETUP_LOGFILE = $(PYTHON_TOP)/pykeg/setup.log

setup: install_db admin

install_db:
	@echo "--- Logging to: $(SETUP_LOGFILE)"
	@echo "--- Installing database ..."
	@$(ADMIN_COMMAND) kb_setup >> $(SETUP_LOGFILE)

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

distclean: clean fixtures_clean
	rm -f pykeg.sqlite.bin
	rm -f pykeg.sqlite.bin-journal
	for f in $(hg status -ni .); do rm -i $f; done

test:
	@echo "--- Running all tests"
	$(ADMIN_COMMAND) test pykeg
# Extra args for coverage:
# --with-coverage --cover-package=pykeg --cover-html \
# --cover-html-dir=buid/coverage

### These targets are obsolete or rarely used

fixtures: distclean test
	$(ADMIN_COMMAND) dumpdata $(PROD_ADMIN_ARGS) --format=json > core/fixtures/initial_data.json

fixtures_clean:
	rm -f core/fixtures/initial_data.json

.PHONY: setup install_db admin clean distclean test sync_and_migrate
.PHONY: testdata fixtures fixtures_clean

# vim: noet
