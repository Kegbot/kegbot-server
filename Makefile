fixtures: export DATABASE_URL = sqlite:///test-db.sqlite
fixtures: export KEGBOT_BASE_URL = http://fixture.example.com/
fixtures: export KEGBOT_ENV = test
fixtures:
	rm -f test-db.sqlite
	bin/kegbot generate_fixtures
	rm -f test-db.sqlite

.PHONY: fixtures