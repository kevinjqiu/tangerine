flake8:
	flake8 --max-line-length=120 tangerine tests

test:
	py.test --cov tests/ --cov tangerine tests
