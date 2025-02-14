install-unix:
	@echo "Installing..."
	@if [ "$(shell which poetry)" = "" ]; then \
		$(MAKE) install-poetry-unix; \
	fi
	@$(MAKE) setup-poetry
	poetry install


install-poetry-unix:
	@echo "Installing poetry..."
	@curl -sSL https://install.python-poetry.org | python3 -
	@$(eval include ${HOME}/.poetry/env)


setup-poetry:
	@echo "Installing project plugin..."
	@poetry self add poetry-multiproject-plugin

	@echo "Creating virtual environment..."
	@poetry config virtualenvs.in-project true
	@poetry env use python

	@echo "Installing dependencies..."
	@poetry install --without dev


format:
	@poetry run yapf ./app -i --recursive
	@poetry run isort ./app
	@poetry run ruff check ./app --fix
