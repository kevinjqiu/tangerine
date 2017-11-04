flake8:
	flake8 --max-line-length=120 tangerine tests

test:
	py.test --cov tests/ --cov tangerine tests

release:
	python setup.py sdist bdist_wheel upload
