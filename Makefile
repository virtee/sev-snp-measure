all: test

test:
	python3 -m unittest discover --verbose tests/

lint:
	flake8 . --count --max-complexity=10 --max-line-length=127 --statistics

typecheck:
	mypy .

coverage:
	python3 -m coverage run -m unittest discover tests/
	python3 -m coverage report
	python3 -m coverage html

build_packages:
	rm -rf dist
	python3 -m build

publish_packages:
	python3 -m twine upload dist/*
