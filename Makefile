.PHONY: test lint tests clean build install
MODULES=dcp tests

test: lint tests

lint:
	flake8 $(MODULES) *.py

tests:
	PYTHONWARNINGS=ignore:ResourceWarning coverage run --source=dcp_diag \
		-m unittest discover --start-directory tests --top-level-directory . --verbose

version: dcp_diag/version.py

dcp_diag/version.py: setup.py
	echo "__version__ = '$$(python setup.py --version)'" > $@

clean:
	-rm -rf build dist
	-rm -rf *.egg-info

build: version clean
	-rm -rf dist
	python setup.py bdist_wheel

install: build
	pip install --upgrade dist/*.whl

include common.mk
