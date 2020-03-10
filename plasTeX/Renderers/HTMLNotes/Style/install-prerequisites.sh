#!/bin/sh

### Install prerequisites of plasTeX in a Docker container.

## Install packages required for building and running plasTeX in a
## Docker container of an official Node.js image.  This script is
## meant to be used in a Dockerfile in the top directory of the
## plasTeX project, like this:
##
##   FROM node
##   COPY plasTeX/Renderers/HTMLNotes/Style/install-prerequisites.sh .
##   RUN sh install-prerequisites.sh

PATH=/bin:/usr/bin:/usr/local/bin

set -o errexit

## Space separated lists.
debian_prerequisites="gosu make"
npm_prerequisites="sass"

export DEBIAN_FRONTEND=noninteractive

apt-get --quiet=2 update

for package in ${debian_prerequisites} ; do
    apt-get --no-install-recommends --option="DPkg::Use-Pty=0" \
            --quiet=2 install "${package}"
done

for package in ${npm_prerequisites} ; do
    npm install -g "${package}"
done

which sass

exit 0

### End of file
