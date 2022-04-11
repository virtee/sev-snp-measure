all: test

test:
	python3 -m unittest discover tests/

lint:
	flake8 . --count --max-complexity=10 --max-line-length=127 --statistics

typecheck:
	mypy .

build_packages:
	rm -rf dist
	python3 -m build

publish_packages:
	python3 -m twine upload dist/*
