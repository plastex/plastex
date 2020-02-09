### Makefile for fork of plasTeX project

### ==================================================================
### Variables
### ==================================================================

PROJECT = plastex
GIT_REMOTES = origin upstream
GIT_REMOTE_ORIGIN_URL = git@github.com:nyraghu/plastex.git
GIT_REMOTE_UPSTREAM_URL = https://github.com/plastex/plastex.git
GIT_BRANCHES = html-notes master
GIT_CURRENT_BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
PYTHON_VERSION = 3.8.1
PYTHON_VIRTUAL_ENVIRONMENT = ${PROJECT}_${PYTHON_VERSION}

### ==================================================================
### Default target
### ==================================================================

.DEFAULT_GOAL = all

.PHONY: all

all:
	@echo "This is a dummy default target; use one of the \
specific targets."

### ==================================================================
### Targets for adding Git remotes
### ==================================================================

define upcase =
$(shell echo $1 | tr a-z A-Z)
endef

define GIT_REMOTE_ADD_template =
.PHONY: git-remote-add-$1

git-remote-add-$1:
	@if git config remote.$1.url > /dev/null 2>&1 ; \
		then \
			echo "Git remote $1 already exists" ; \
		else \
			git remote add $1 \
			${GIT_REMOTE_$(call upcase,$1)_URL} ; \
	fi
endef

$(foreach remote,origin upstream,$(eval $(call \
			GIT_REMOTE_ADD_template,${remote})))

### ==================================================================
### Targets for creating and checking out Git branches
### ==================================================================

define GIT_BRANCH_template =
.PHONY: git-branch-create-$1

git-branch-create-$1:
	@if git show-ref --verify --quiet refs/heads/$1 ; \
		then \
			echo "Git branch $1 already exists" ; \
		else \
			git branch $1 ; \
	fi

.PHONY: git-branch-checkout-$1

git-branch-checkout-$1: git-branch-create-$1
	git checkout $1

.PHONY: git-branch-merge-$1

git-branch-merge-$1: git-branch-create-$1
	git checkout master
	git merge $1
endef

$(foreach branch,${GIT_BRANCHES},$(eval $(call \
			GIT_BRANCH_template,${branch})))

### ==================================================================
### Target for pushing the current branch
### ==================================================================

.PHONY: git-branch-push-${GIT_CURRENT_BRANCH}

git-branch-push-${GIT_CURRENT_BRANCH}:
	 git push --set-upstream origin $1

### ==================================================================
### Target for checking Git ignored files
### ==================================================================

.PHONY: git-check-ignore

git-check-ignore:
	git check-ignore -v $$(find * -type f)

### ==================================================================
### Targets for Python virtual environments
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
### Target for installing the project
### ==================================================================

.PHONY: python-install-${PROJECT}

python-install-${PROJECT}: python-create-virtual-environment
	pip install --requirement requirements.txt
	pip install --editable .

### End of file
