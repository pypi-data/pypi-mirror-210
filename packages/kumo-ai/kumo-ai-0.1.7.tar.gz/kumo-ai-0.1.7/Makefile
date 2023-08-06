
# Build package of SDK
package:
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	python setup.py sdist bdist_wheel

publish: package
	pip install twine
	twine upload --repository testpypi dist/*
