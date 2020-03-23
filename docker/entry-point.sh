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
check_uid_is_natural_number ()
{
    case "${uid}" in
        *[!0-9]* | '')
            printf "Error: value of DOCKERUID is not a natural number
===> DOCKERUID = ${uid}
"
            exit 1
            ;;
        * )
            true
            ;;
    esac

    return 0
}

## Create the working directory.
do_working_directory ()
{
    local working_directory

    working_directory=${HOME}/plastex

    mkdir -p "${working_directory}"
    cd "${working_directory}"
    make -C plasTeX/Renderers/HTMLNotes/Style install
    pip install --editable .

    return 0
}

## Perfom this action if the specified UID is that of root.
do_root ()
{
    do_working_directory
    exec ${command}

    return 0
}

## Perform this action if a non-root user with the specified UID
## exists in the image.
do_user_exists ()
{
    local passwd_entry

    passwd_entry=$1

    printf "Error: UID ${uid} is already assigned to a non-root user \
in the Docker image
===> DOCKERUID = ${uid} conflicts with the following entry in \
/etc/passwd:
===> ${passwd_entry}
"
    exit 2
}

## Perform this action if the specified UID is not that of root, and
## does not belong to any non-root used in the image.
do_user ()
{
    local comment home name shell

    comment="Docker User"
    name=docker
    shell=/bin/bash
    home=/home/${name}

    useradd -U -c "${comment}" -s "${shell}" -u "${uid}" "${name}"
    export HOME="${home}"
    export PS1="[\u:\w]\$ "
    do_working_directory
    gosu "${name}" ${command}

    return 0
}

## Combine all the above actions into one action.
do_execute ()
{
    local passwd_entry

    check_uid_is_natural_number

    if [ "${uid}" -eq 0 ] ; then
        do_root
    elif passwd_entry=$(getent passwd "${uid}") ; then
        do_user_exists "${passwd_entry}"
    else
        do_user
    fi

    return 0
}

## Perform the combined action.
do_execute

exit 0

### End of file
