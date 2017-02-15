clean:
	rm -rf build dist *.egg*
build: clean
	python setup.py sdist bdist_wheel
upload: build
	twine upload dist/*
