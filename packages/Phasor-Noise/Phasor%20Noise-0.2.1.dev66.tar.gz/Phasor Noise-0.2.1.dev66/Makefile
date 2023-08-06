upload:
	twine upload --repository pypi dist/*
build:
	pip install -r requirements.txt
	python -m pip install --upgrade build
	python -m build
install:
	pip install -e .