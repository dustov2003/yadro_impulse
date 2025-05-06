ifeq ($(shell test -e '.env' && echo -n yes),yes)
	include .env
endif


ifndef APP_PORT
override APP_PORT = 8080
endif

ifndef APP_HOST
override APP_HOST = 127.0.0.1
endif


args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

APPLICATION_NAME = dag_service
TEST = poetry run python -m pytest --verbosity=2 --showlocals --log-level=DEBUG
CODE = $(APPLICATION_NAME) tests

HELP_FUN = \
	%help; while(<>){push@{$$help{$$2//'options'}},[$$1,$$3] \
	if/^([\w-_]+)\s*:.*\#\#(?:@(\w+))?\s(.*)$$/}; \
    print"$$_:\n", map"  $$_->[0]".(" "x(20-length($$_->[0])))."$$_->[1]\n",\
    @{$$help{$$_}},"\n" for keys %help; \

env:
	@$(eval SHELL:=/bin/bash)
	@cp .env.example .env

help:
	@echo -e "Usage: make [target] ...\n"
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)


lint:
	poetry run python3 -m pylint $(CODE)

format:
	poetry run python3 -m isort $(CODE)
	poetry run python3 -m black $(CODE)

migrate:
	cd $(APPLICATION_NAME)/db && alembic upgrade $(args)

run:
	docker-compose up -d --build

revision:
	cd $(APPLICATION_NAME)/db && alembic revision --autogenerate

open_db:
	docker exec -it postgres psql -d $(POSTGRES_DB) -U $(POSTGRES_USER)

open_service:
	docker exec -it $(APPLICATION_NAME) /bin/bash

test:
	make run && docker exec -it $(APPLICATION_NAME) /bin/bash -c "poetry run pytest tests/ -v"

test-cov:
	make run && docker exec -it $(APPLICATION_NAME) /bin/bash -c "poetry run pytest tests/ -v --cov=dag_service --cov-report html --cov-fail-under=80"
clean:
	rm -fr *.egg-info dist

%::
	echo $(MESSAGE)