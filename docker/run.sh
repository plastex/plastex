### Build a Docker image, and run Bash in a container of that image.

## This is a shell script for running Docker images for developing and
## using the plastex package.
##
## Usage: This script should be invoked from the main directory of the
## package as `sh docker/run.sh STAGE', where STAGE is either
## `development' or `application'.

stage="$1"
docker_id="nyraghu"
tag="latest"
project_name="plastex"
repository_name="${project_name}-${stage}"
image="${docker_id}/${repository_name}:${tag}"

development() {
    local sourcedir targetdir uid

    sourcedir=$(pwd)
    targetdir=/home/docker/plastex
    uid=$(id -u ${USER})

    docker run --env="DOCKERUID=${uid}" --interactive=true --rm=true \
           --tty=true \
           --mount type=bind,source="${sourcedir}",target="${targetdir}" \
           "${image}"

    return 0
}

application() {
    docker run --interactive=true --rm=true --tty=true "${image}"

    return 0
}

${stage}

exit 0

### End of file
