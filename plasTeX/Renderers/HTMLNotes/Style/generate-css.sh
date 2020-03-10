#!/bin/sh

### Generate CSS files for the HTMLNotes renderer of plasTeX.

## Generate CSS files for the HTMLNotes renderer of plasTeX from Sass
## sources in a Docker container of an official Node.js image.  This
## script is meant to be used in a Dockerfile in the top directory of
## the plasTeX project, like this:
##
##   COPY plasTeX/Renderers/HTMLNotes/Style .
##   RUN sh generate-css.sh

PATH=/bin:/usr/bin:/usr/local/bin

set -o errexit

## Space separated list.
themes="green"

source_directory="sass"

build_directory="build"

for theme in ${themes}; do
    input_file="${source_directory}/theme-${theme}/main.scss"
    output_file="${build_directory}/theme-${theme}.css"
    sass --no-source-map "${input_file}":"${output_file}"
done

exit 0

### End of file
