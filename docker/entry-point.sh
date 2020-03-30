### Execute a command as a specified user.

## This is an entry-point script for the Docker image for developing
## the plastex package.
##
## The script takes the value of the environment variable DOCKERUID to
## be the UID of the specified user.  If this variable is not set, or
## if its value is the empty string, then the script assumes that the
## UID 0, that of root, has been specified.
##
## The arguments given to the script form the command that will be
## executed.  In case there are no arguments to the script, a shell
## will be executed.
##
## Usage: This script should be used in an ENTRYPOINT instruction in
## the Dockerfile in the main directory of the package, as follows:
##
##   COPY docker/entry-point.sh /usr/local/src/docker/
##
##   ENTRYPOINT ["/bin/sh", "/usr/local/src/docker/entry-point.sh"]
##
## After building a Docker image `foo:bar' in the main directory with
##
##   docker build --tag=foo:bar --target=development .
##
## one can, for example, do the following:
##
##   docker run -e DOCKERUID=1729 -i -t foo:bar /bin/bash
##
##   docker run -i -t foo:bar touch /root/quux
##
## See
## https://denibertovic.com/posts/handling-permissions-with-docker-volumes/

command="${@:-/bin/bash}"
uid="${DOCKERUID:-0}"

## Check if the specified UID is a natural number.
## https://stackoverflow.com/a/18620446
case "${uid}" in
    *[!0-9]* | '')
        printf "Error: value of DOCKERUID is not a natural number
===> DOCKERUID = ${uid}
"
        exit 1
        ;;
esac

## Create the working directory.
install_plastex() {
    local project_directory

    project_directory="$1"

    cd "${project_directory}"
    make -C plasTeX/Renderers/HTMLNotes/Style install
    pip install --editable .

    return 0
}

if [ "${uid}" -eq 0 ] ; then
    install_plastex "/root/plastex"
    ${command}
elif passwd_entry="$(getent passwd "${uid}")" ; then
    printf "Error: UID ${uid} is already assigned to a non-root user \
in the Docker image
===> DOCKERUID = ${uid} conflicts with the following entry in \
/etc/passwd:
===> ${passwd_entry}
"
    exit 2
else
    comment="Docker User"
    name="docker"
    shell="/bin/bash"
    home="/home/${name}"

    install_plastex "${home}/plastex"
    useradd -U -c "${comment}" -s "${shell}" -u "${uid}" "${name}"
    mkdir -p "${home}"
    cp -r /etc/skel/.[a-z]* "${home}"
    echo 'PS1="[\u:\w]\$ "' >> ${home}/.bashrc
    chown -R "${uid}:${uid}" "${home}"
    gosu "${name}" ${command}
fi

exit 0

### End of file
