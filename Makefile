PROJECT = plastex
GIT_REMOTE_ORIGIN_URL = git@github.com:nyraghu/plastex.git
GIT_REMOTE_UPSTREAM_URL = https://github.com/plastex/plastex.git
GIT_BRANCH = html-notes
PYTHON_VERSION = 3.8.1
PYTHON_VIRTUAL_ENVIRONMENT = \
	${PROJECT}_${GIT_BRANCH}_${PYTHON_VERSION}

.DEFAULT_GOAL = all

define PHONIES =
all \
git-checkout-master \
python-create-virtual-environment \
python-delete-virtual-environment \
python-install-project
endef

.PHONY: ${PHONIES}

all:
	@echo "This is a dummy default target; use one of the \
specific targets."

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

git-checkout-master:
	git checkout master

define GIT_BRANCH_template =
.PHONY: git-branch-create-$1 git-branch-checkout-$1 git-branch-push-$1

git-branch-create-$1:
	@if git show-ref --verify --quiet refs/heads/$1 ; \
		then \
			echo "Git branch ${GIT_BRANCH} \
already exists" ; \
		else \
			git branch $1 ; \
	fi

git-branch-checkout-$1:
	git checkout $1

git-branch-push-$1:
	 git push --set-upstream origin $1
endef

$(eval $(call GIT_BRANCH_template,${GIT_BRANCH}))

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

python-install-project: python-create-virtual-environment
	pip install --requirement requirements.txt
	pip install --editable .
