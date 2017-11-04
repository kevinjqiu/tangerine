flake8:
	flake8 --max-line-length=120 tangerine tests

test:
	py.test --cov tests/ --cov tangerine tests

tag:
	git tag "v$$(cat tangerine/VERSION)"
	git push --tags

incpatch:
	python -c 'v=open("tangerine/VERSION").read(); v=list(map(int, v.split("."))); v[-1]+=1; v=".".join(map(str, v)); open("tangerine/VERSION", "w").write(v)'
	git commit -a -m"Bump major version"

incminor:
	python -c 'v=open("tangerine/VERSION").read(); v=list(map(int, v.split("."))); v[1]+=1; v=".".join(map(str, v)); open("tangerine/VERSION", "w").write(v)'
	git commit -a -m"Bump minor version"

incmajor:
	python -c 'v=open("tangerine/VERSION").read(); v=list(map(int, v.split("."))); v[0]+=1; v=".".join(map(str, v)); open("tangerine/VERSION", "w").write(v)'
	git commit -a -m"Bump patch version"

release:
	make tag
	python setup.py sdist bdist_wheel upload
