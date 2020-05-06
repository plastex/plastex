### Makefile rules for a Docker container

### ==================================================================
### Variables
### ==================================================================

PROJECT = plastex
DOCKER_BUILD_HOOK = hooks/build
DOCKER_RUN_SCRIPT = docker/run.sh

### ==================================================================
### Targets for building Docker images
### ==================================================================

.PHONY: docker-build-development docker-build-application

docker-build-development:
	DOCKER_REPO=index.docker.io/nyraghu/plastex-development \
		DOCKER_TAG=latest ${DOCKER_BUILD_HOOK}

docker-build-application:
	DOCKER_REPO=index.docker.io/nyraghu/plastex-application \
		DOCKER_TAG=latest ${DOCKER_BUILD_HOOK}

### ==================================================================
### Targets for running Docker images
### ==================================================================

.PHONY: docker-run-development docker-run-application

docker-run-development:
	${SHELL} ${DOCKER_RUN_SCRIPT} development

docker-run-application:
	${SHELL} ${DOCKER_RUN_SCRIPT} application

### ==================================================================
### Targets for access control lists (ACL)
### ==================================================================

.PHONY docker-build-development docker-build-application: acl

acl:
	setfacl -R -b ${CURDIR}
	setfacl -R -m u::rwX,g::r-X,o::r-X ${CURDIR}
	setfacl -R -d -m u::rwx,g::r-x,o::r-x ${CURDIR}

### End of file
