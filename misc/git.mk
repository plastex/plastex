### Makefile rules for Git

### ==================================================================
### Variables
### ==================================================================

PROJECT = plastex
GIT_REMOTES = origin upstream
GIT_REMOTE_ORIGIN_URL = git@github.com:nyraghu/plastex.git
GIT_REMOTE_UPSTREAM_URL = https://github.com/plastex/plastex.git
GIT_BRANCHES = dockerisation html-notes master nixisation
GIT_CURRENT_BRANCH = $(shell git rev-parse --abbrev-ref HEAD)

### ==================================================================
### Targets for git remote
### ==================================================================

define upcase =
$(shell echo $1 | tr a-z A-Z)
endef

define GIT_REMOTE_template =
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

$(foreach remote,${GIT_REMOTES},$(eval $(call \
			GIT_REMOTE_template,${remote})))

### ==================================================================
### Targets for git branch
### ==================================================================

define GIT_BRANCH_template =
.PHONY: git-branch-$1

git-branch-$1:
	@if git show-ref --verify --quiet refs/heads/$1 ; \
		then \
			echo "Git branch $1 already exists" ; \
		else \
			git branch $1 ; \
	fi
endef

$(foreach branch,${GIT_BRANCHES},$(eval $(call \
			GIT_BRANCH_template,${branch})))

.PHONY: git-branch-show-current

git-branch-show-current:
	@echo "${GIT_CURRENT_BRANCH}"

### ==================================================================
### Targets for git checkout
### ==================================================================

define GIT_CHECKOUT_template =
.PHONY: git-checkout-$1

git-checkout-$1: git-branch-$1
	git checkout $1
endef

$(foreach branch,$(filter-out \
	${GIT_CURRENT_BRANCH},${GIT_BRANCHES}),$(eval \
	$(call GIT_CHECKOUT_template,${branch})))

### ==================================================================
### Targets for git push
### ==================================================================

define GIT_PUSH_template =
.PHONY: git-push-$1

git-push-$1: git-branch-$1
	git push --set-upstream origin $1

endef

$(foreach branch,${GIT_BRANCHES},$(eval $(call \
			GIT_PUSH_template,${branch})))

.PHONY: git-push-current-branch

git-push-current-branch:
	git push --set-upstream origin ${GIT_CURRENT_BRANCH}

### ==================================================================
### Targets for git pull
### ==================================================================

define GIT_PULL_template =
.PHONY: git-pull-$1

git-pull-$1: git-checkout-$1
	git branch --set-upstream-to=origin/$1
	git pull
	git checkout ${GIT_CURRENT_BRANCH}
endef

$(foreach branch,${GIT_BRANCHES},$(eval $(call \
			GIT_PULL_template,${branch})))

.PHONY: git-pull-current-branch

git-pull-current-branch:
	git branch --set-upstream-to=origin/${GIT_CURRENT_BRANCH}
	git pull

### ==================================================================
### Targets for git merge
### ==================================================================

define GIT_MERGE_template =
.PHONY: git-merge-$1-into-$2

git-merge-$1-into-$2: git-branch-$1 git-branch-$2
	git checkout $2
	git merge $1
	git checkout ${GIT_CURRENT_BRANCH}
endef

$(foreach source,${GIT_BRANCHES},$(foreach \
	target,$(filter-out ${source},${GIT_BRANCHES}),$(eval \
	$(call GIT_MERGE_template,${source},${target}))))

ifneq (${GIT_CURRENT_BRANCH},master)
.PHONY: git-merge-current-branch-into-master

git-merge-current-branch-into-master:
	git checkout master
	git merge ${GIT_CURRENT_BRANCH}
	git checkout ${GIT_CURRENT_BRANCH}
endif

### ==================================================================
### Target for checking Git ignored files
### ==================================================================

.PHONY: git-check-ignore

git-check-ignore:
	git check-ignore -v $$(find * -type f)

### End of file
