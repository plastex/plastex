### Build a Docker image, and run Bash in a container of that image.

## This shell script is for building and running Docker images for
## developing and running the plastex package.
##
## Usage: This script should be invoked from the main directory of the
## package as `sh docker/docker.sh ACTION', where ACTION is either
## `build-development', `build-application', `run-development', or
## `run-application'.

action="$(echo "$1" | sed 's@-@_@g')"
docker_id="nyraghu"
image_version="0.1.0"
python_version="3.8.2"
python_image_type="slim-buster"
python_image_tag="${python_version}-${python_image_type}"
tag="${image_version}-python-${python_version}"
project_name="plastex"

build_development() {
    local image repository_name

    repository_name="${project_name}-development"
    image="${docker_id}/${repository_name}:${tag}"

    docker build \
           --build-arg="PYTHON_IMAGE_TAG=${python_image_tag}" \
           --build-arg="NODE_JS_MAJOR_VERSION=13" \
           --tag=${image} --target=development .

    return 0
}

build_application() {
    local image repository_name

    repository_name="${project_name}-application"
    image="${docker_id}/${repository_name}:${tag}"

    docker build \
           --build-arg="PYTHON_IMAGE_TAG=${python_image_tag}" \
           --build-arg="NODE_JS_MAJOR_VERSION=13" \
           --tag=${image} --target=application .

    return 0
}

run_development() {
    local image repository_name sourcedir targetdir uid

    repository_name="${project_name}-development"
    image="${docker_id}/${repository_name}:${tag}"
    sourcedir=$(pwd)
    targetdir=/home/docker/plastex
    uid=$(id -u ${USER})

    docker run --env="DOCKERUID=${uid}" --interactive=true --rm=true \
           --tty=true \
           --mount type=bind,source=${sourcedir},target=${targetdir} \
           ${image}

    return 0
}

run_application() {
    local image repository_name sourcedir targetdir uid

    repository_name="${project_name}-application"
    image="${docker_id}/${repository_name}:${tag}"
    sourcedir=$(pwd)
    targetdir=/home/docker/plastex
    uid=$(id -u ${USER})

    docker run --interactive=true --rm=true --tty=true ${image}

    return 0
}

${action}

exit 0

### End of file
