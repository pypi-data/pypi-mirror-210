
# Build package of SDK
package:
	rm -rf dist
	rm -rf build
	python setup.py sdist bdist_wheel

publish: package
	pip install twine
	twine upload --repository testpypi dist/*
