POETRY_RUN=poetry run
HONCHO_RUN=honcho -e .env run python manage.py

install:
	  poetry install

format:
	  $(POETRY_RUN) black .

lint:
	  $(POETRY_RUN) flake8 .

test: format lint
	  $(POETRY_RUN) ${HONCHO_RUN} test

wait_for_db:
		$(POETRY_RUN) $(HONCHO_RUN) wait_for_db

migrate:
	  $(POETRY_RUN) $(HONCHO_RUN) migrate

makemigrations:
	  $(POETRY_RUN) $(HONCHO_RUN) makemigrations $(ARGS)

start: wait_for_db migrate
		$(POETRY_RUN) $(HONCHO_RUN) runserver

shell:
	  $(POETRY_RUN) $(HONCHO_RUN) shell

manage:
	  $(POETRY_RUN) $(HONCHO_RUN) $(ARGS)

db-reset:
	  dropdb ezpunishments2 --if-exists
		createdb -U postgres ezpunishments2

db: db-reset migrate
	  echo "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('smiileyface', 'Testpass123')" | $(POETRY_RUN) $(HONCHO_RUN) shell

.PHONY: install format lint test wait_for_db migrate makemigrations start shell manage db-reset db
