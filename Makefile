flake8:
	flake8 --max-line-length=120 tangerine tests

test:
	py.test --cov tests/ --cov tangerine tests

incpatch:
	python -c 'v=open("tangerine/VERSION").read(); v=list(map(int, v.split("."))); v[-1]+=1; v=".".join(map(str, v)); open("tangerine/VERSION", "w").write(v)'

incminor:
	python -c 'v=open("tangerine/VERSION").read(); v=list(map(int, v.split("."))); v[1]+=1; v=".".join(map(str, v)); open("tangerine/VERSION", "w").write(v)'

incmajor:
	python -c 'v=open("tangerine/VERSION").read(); v=list(map(int, v.split("."))); v[0]+=1; v=".".join(map(str, v)); open("tangerine/VERSION", "w").write(v)'

release:
	python setup.py sdist bdist_wheel upload
