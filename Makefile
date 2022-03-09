all: test

test:
	python3 -m unittest discover tests/

lint:
	flake8 . --count --max-complexity=10 --max-line-length=127 --statistics
