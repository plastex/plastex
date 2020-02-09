#!/bin/sh

set -o errexit

command_path="$(realpath "$0")"
command_directory="$(dirname "${command_path}")"

install_npm_package() {
    npm_package="$1"
    printf "Checking if %s is installed..." "${npm_package}"

    if npm list -g "${package}" > /dev/null ; then
        echo "done"
    else
        printf "\nInstalling missing package %s\n" "${npm_package}"
        npm install -g "${package}"
        echo "Installing missing package ${npm_package}...done"
        echo "Checking if ${npm_package} is installed...done"
    fi

    return 0
}

install_css() {
    echo "Installing CSS stylesheets..."
    make -C "${command_directory}" install
    echo "Installing CSS stylesheets...done"
    return 0
}

install_style_files() {
    echo "Installing style files..."
    npm_prerequisites="autoprefixer css-validator cssnano-cli \
postcss-cli sass sass-migrator"

    for package in ${npm_prerequisites} ; do
        install_npm_package "${package}"
    done

    install_css
    echo "Installing style files...done"
    return 0
}

install_style_files

exit 0
