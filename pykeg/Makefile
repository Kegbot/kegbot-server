PYTHON_TOP = $(shell dirname $(shell pwd))
PYTHON_ENV = PYTHONPATH=$(PYTHON_TOP)

PROD_SETTINGS = pykeg.settings
TEST_SETTINGS = pykeg.unittest_settings

PROD_DJANGO_ENV = $(PYTHON_ENV) DJANGO_SETTINGS_MODULE=$(PROD_SETTINGS)
TEST_DJANGO_ENV = $(PYTHON_ENV) DJANGO_SETTINGS_MODULE=$(TEST_SETTINGS)

PROD_ADMIN_COMMAND = $(PYTHON_TOP)/pykeg/bin/kegbot_admin.py
TEST_ADMIN_COMMAND = $(TEST_DJANGO_ENV) django-admin.py

PROD_ADMIN_ARGS = --settings=$(PROD_SETTINGS)
TEST_ADMIN_ARGS = --settings=$(TEST_SETTINGS)

setup: install_db admin

install_db:
	@echo "--- Installing database"
	@$(PROD_ADMIN_COMMAND) syncdb $(PROD_ADMIN_ARGS) --noinput
	@$(PROD_ADMIN_COMMAND) kb_set_defaults $(PROD_ADMIN_ARGS)

admin:
	@echo "--- Creating super user"
	@$(PROD_ADMIN_COMMAND) createsuperuser $(PROD_ADMIN_ARGS)

clean:
	rm -f kegbot.log
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
testdata: distclean setup
	$(PROD_DJANGO_ENV) scripts/gentestdata.py

fixtures: distclean test
	$(PROD_ADMIN_COMMAND) dumpdata $(PROD_ADMIN_ARGS) --format=json > core/fixtures/initial_data.json

fixtures_clean:
	rm -f core/fixtures/initial_data.json

.PHONY: setup install_db admin clean distclean test test_clean
.PHONY: testdata fixtures fixtures_clean

# vim: noet
