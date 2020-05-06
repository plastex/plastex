### Makefile rules for Python virtual environments

### ==================================================================
### Variables
### ==================================================================

PROJECT = plastex
PYTHON_VERSION = 3.8.2
PYTHON_VIRTUAL_ENVIRONMENT = ${PROJECT}_${PYTHON_VERSION}

### ==================================================================
### Targets for the Python virtual environment for the project
### ==================================================================

.PHONY: python-create-virtual-environment

python-create-virtual-environment:
	@if pyenv virtualenvs | \
	grep -q ${PYTHON_VIRTUAL_ENVIRONMENT} ; \
		then \
			echo "Python virtual environment \
${PYTHON_VIRTUAL_ENVIRONMENT} already exists" ; \
		else \
			pyenv virtualenv ${PYTHON_VERSION} \
				${PYTHON_VIRTUAL_ENVIRONMENT} ; \
			pyenv local ${PYTHON_VIRTUAL_ENVIRONMENT} ; \
	fi

.PHONY: python-delete-virtual-environment

python-delete-virtual-environment:
	@if pyenv virtualenvs | \
	grep -q ${PYTHON_VIRTUAL_ENVIRONMENT} ; \
		then \
			pyenv uninstall \
				${PYTHON_VIRTUAL_ENVIRONMENT} ; \
			${RM} .python-version ; \
		else \
			echo "Python virtual environment \
${PYTHON_VIRTUAL_ENVIRONMENT} does not exist" ; \
	fi

### ==================================================================
### Target for installing the project dependencies
### ==================================================================

.PHONY: python-install-dependencies

python-install-dependencies: python-create-virtual-environment
	pip install mypy pycodestyle pytest pytest-cache

### ==================================================================
### Target for installing the project
### ==================================================================

.PHONY: python-install-${PROJECT}

python-install-${PROJECT}: python-create-virtual-environment
	pip install --requirement requirements.txt
	pip install --editable .

### End of file
