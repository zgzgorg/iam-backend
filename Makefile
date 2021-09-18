GITDIR := $(shell git rev-parse --show-toplevel)

FIND_GITIGNORE_FILTER = 'for path; do git check-ignore -q "$$path" || echo "$$path" ;done'

PY_SOURCE_GLOB = $(shell find * -not -path '*/\.*' -name "*.py" -exec sh -c \
						  	$(FIND_GITIGNORE_FILTER) \
					      find-sh {} +)
SH_SOURCE_GLOB = $(shell find * -not -path '*/\.*' -type f -name "*.sh" -exec sh -c \
						  	$(FIND_GITIGNORE_FILTER) \
					      find-sh {} +)

IGNORE_PEP = E203,E221,E241,E272,E501,F811,W503

MAX_LINE_LENGTH = 100

BLACK_ARGS =

ifneq ($(wildcard setup.py),)
	PACKAGE_NAME=$(shell sed -n "s/PACKAGE_NAME[ ]*=[ ]*[\",\']\(.*\)[\",\'].*/\1/p" setup.py)
endif

.PHONY: all
all : clean lint


.PHONY: test
test: shelltest pytest


.PHONY: lint
lint: check-black pylint pycodestyle flake8 mypy shellcheck


.PHONY: format
format: black


.PHONY: print_target
print_target:
	@echo "----------------------------------------------------------------------"
	@echo ":: $(target)"
	@echo "----------------------------------------------------------------------"


.PHONY: clean
clean:
	@$(MAKE) target=$@ print_target
	rm -rf dist/* .pytype .mypy_cache


.PHONY: dist
dist:
	@$(MAKE) target=$@ print_target
	@if [ -f "setup.py" ]; then \
		python3 setup.py sdist bdist_wheel; \
	else \
		echo "'setup.py' not found. Please ensure this folder is a package"; \
	fi


.PHONY: pytest
pytest:
	@$(MAKE) target=$@ print_target
	@if [ -d "tests" ]; then \
		pytest --cov=$(PACKAGE_NAME) --cov-report term-missing tests/; \
	else \
		echo "'tests' directory does not exist. Please ensure you have unit test in this package"; \
	fi


.PHONY: shelltest
shelltest:
	@$(MAKE) target=$@ print_target
ifeq ($(SH_SOURCE_GLOB),)
	@echo "No shell file found"
else
	# bash '-n': check the syntax of a script without having to execute it
	@for sh_file in $(SH_SOURCE_GLOB); do \
		bash -n "$${sh_file}" || exit 1 ; \
	done
endif


.PHONY: pylint
# E0202: https://www.technovelty.org/python/pylint-and-hiding-of-attributes.html
# W0511: (warning notes in code comments; message varies)
# R0801: Similar lines in %s files
pylint:
	@$(MAKE) target=$@ print_target
ifeq ($(PY_SOURCE_GLOB),)
	@echo "No Python file found"
else
	pylint \
		--rcfile="$(GITDIR)/.pylintrc" \
		--disable=C0330,E0202,W0511,R0801,cyclic-import \
		$(PY_SOURCE_GLOB)
endif


.PHONY: pycodestyle
pycodestyle:
	@$(MAKE) target=$@ print_target
ifeq ($(PY_SOURCE_GLOB),)
	@echo "No Python file found"
else
	pycodestyle \
		--statistics \
		--max-line-length $(MAX_LINE_LENGTH) \
		--count \
		--ignore="$(IGNORE_PEP)" \
		$(PY_SOURCE_GLOB)
endif


.PHONY: flake8
flake8:
	@$(MAKE) target=$@ print_target
ifeq ($(PY_SOURCE_GLOB),)
	@echo "No Python file found"
else
	flake8 \
		--max-line-length $(MAX_LINE_LENGTH) \
		--ignore="$(IGNORE_PEP)" \
		$(PY_SOURCE_GLOB)
endif


.PHONY: mypy
mypy:
	@$(MAKE) target=$@ print_target
ifeq ($(PY_SOURCE_GLOB),)
	@echo "No Python file found"
else
	MYPYPATH="stubs/" mypy \
		$(PY_SOURCE_GLOB)
endif

.PHONY: pytype
pytype:
	@$(MAKE) target=$@ print_target
ifeq ($(PY_SOURCE_GLOB),)
	@echo "No Python file found"
else
	rm -rf  .pytype
	pytype \
		--config=$(GITDIR)/setup.cfg \
		--disable=import-error,pyi-error \
		$(PY_SOURCE_GLOB)
endif

.PHONY: shellcheck
shellcheck:
	@$(MAKE) target=$@ print_target
ifeq ($(SH_SOURCE_GLOB),)
	@echo "No shell file found"
else
	shellcheck \
		$(SH_SOURCE_GLOB)
endif


.PHONY: check-black
# Run the black tool in check mode only (won't modify files)
check-black:
	@$(MAKE) target=$@ print_target
ifeq ($(PY_SOURCE_GLOB),)
	@echo "No Python file found"
else
	@echo "Checking black with code format"
	black \
		--check \
		--line-length $(MAX_LINE_LENGTH) \
		$(BLACK_ARGS) \
		$(PY_SOURCE_GLOB)
endif


.PHONY: black
black:
	@$(MAKE) target=$@ print_target
ifeq ($(PY_SOURCE_GLOB),)
	@echo "No Python file found"
else
	black \
		--line-length $(MAX_LINE_LENGTH) \
		$(BLACK_ARGS) \
		$(PY_SOURCE_GLOB)
endif


.PHONY: install-githook
install-githook:
	@$(MAKE) target=$@ print_target
	# cleanup existing pre-commit configuration (if any)
	pre-commit clean
	pre-commit gc
	# setup pre-commit
	# Ensures pre-commit hooks point to latest versions
	pre-commit autoupdate
	pre-commit install
	pre-commit install --hook-type pre-push
	pre-commit install --hook-type commit-msg


.PHONY: uninstall-githook
uninstall-githook:
	@$(MAKE) target=$@ print_target
	pre-commit clean
	pre-commit gc
	pre-commit uninstall
	pre-commit uninstall --hook-type pre-push
	pre-commit uninstall --hook-type commit-msg


.PHONY: develop
develop:
	@$(MAKE) target=$@ print_target
	pip3 install -r $(GITDIR)/requirements.txt
	pip3 install -r $(GITDIR)/requirements-dev.txt
	$(MAKE) install-githook
	pip3 install -r requirements.txt
	pip3 install -r requirements-dev.txt
	python3 setup.py --verbose develop


.PHONY: undevelop
undevelop:
	@$(MAKE) target=$@ print_target
	python3 setup.py --verbose develop --uninstall


.PHONY: deploy-version
deploy-version:
	@if [ ! -f "setup.py" ]; then \
		echo "'setup.py' not found. Please ensure this folder is a package"; \
		exit 1; \
	fi; \
	if [ ! -f "VERSION" ]; then \
		echo "'VERSION' file doesn't exist. Please ensure have VERSION file in this package"; \
		exit 1; \
	fi; \
	sed -i "s/VERSION = .*/VERSION = \"$$(cat VERSION)\"/" $(PACKAGE_NAME)/version.py


.PHONY: bump-version
bump-version:
	@newVersion=$$(awk -F. '{print $$1"."$$2"."$$3+1}' < VERSION) \
		&& echo $${newVersion} > VERSION \
		&& git add VERSION \
		&& git commit -m "$${newVersion}" > /dev/null \
		&& echo "Bumped version to $${newVersion}"


.PHONY: update-requirements
update-requirements:
	pip-compile -q -o requirements.txt requirements.in
	pip-compile -q -o requirements-dev.txt requirements-dev.in
