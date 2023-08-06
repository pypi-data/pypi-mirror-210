env: venv
	venv/bin/pip install --upgrade pip
	venv/bin/pip install -r requirements-dev.txt --use-pep517
	venv/bin/pip install -e .

venv:
	python3.9 -m venv venv

publish: venv
	rm -fr dist/*
	venv/bin/hatch build
	venv/bin/hatch publish

flake8:
	venv/bin/flake8 dead_code_finder

mypy:
	venv/bin/mypy dead_code_finder

test:
	venv/bin/pytest $(PYTEST_ME_PLEASE)

check: test flake8 mypy
