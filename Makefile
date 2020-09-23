POETRY_RUN=poetry run
HONCHO_RUN=honcho -e .env run python manage.py

install:
	  poetry install

format:
	  $(POETRY_RUN) black.

lint:
	  $(POETRY_RUN) flake8 .

test: format lint
	  $(POETRY_RUN) honcho -e .env-test run coverage run manage.py test
		$(POETRY_RUN) coverage report -m --fail-under=88
		$(POETRY_RUN) coverage html

start:
	  $(POETRY_RUN) honcho -e .env start

migrate:
	  $(POETRY_RUN) $(HONCHO_RUN) migrate

makemigrations:
	  $(POETRY_RUN) $(HONCHO_RUN) makemigrations $(ARGS)

shell:
	  $(POETRY_RUN) $(HONCHO_RUN) shell

manage:
	  $(POETRY_RUN) $(HONCHO_RUN) $(ARGS)

db-reset:
	  dropdb ezpunishments2 --if-exists
		createdb -U postgres ezpunishments2

db: db-reset migrate

.PHONY: install test format lint start migrate makemigrations shell manage db-reset db
