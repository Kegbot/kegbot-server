DJANGO_ENV = DJANGO_SETTINGS_MODULE=pykeg.settings

setup:
	$(DJANGO_ENV) python manage.py syncdb --noinput
	$(DJANGO_ENV) python scripts/setdefaults.py

install:
	python setup.py install

distclean: clean
	rm -f pykeg.sqllite.bin

clean:
	rm -f keg.log
	rm -rf build
	find . -name "*.pyc" | xargs rm -f

test: distclean setup
	$(DJANGO_ENV) python scripts/gentestdata.py

unittests:
	$(DJANGO_ENV) python manage.py test
