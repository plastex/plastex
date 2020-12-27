#!/usr/bin/env bash

# This script uses sass, and postcss with cssnano and autoprefixer
# Those can be installed using npm with
# sudo npm install -g sass postcss-cli autoprefixer cssnano-cli
sass --no-source-map --update sass:build
cd build
postcss --use autoprefixer -o theme-blue-pre.css  theme-blue.css
postcss --use autoprefixer -o theme-green-pre.css  theme-green.css
postcss --use autoprefixer -o theme-white-pre.css  theme-white.css
cssnano theme-blue-pre.css > theme-blue.css
cssnano theme-green-pre.css > theme-green.css
cssnano theme-white-pre.css > theme-white.css
mv theme-blue.css theme-green.css theme-white.css ../../Themes/default/styles/
cd ..
rm -rf build
