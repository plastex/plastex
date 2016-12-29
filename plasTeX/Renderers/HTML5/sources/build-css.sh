#!/usr/bin/env bash
sass --sourcemap=none --update sass:build
cd build
postcss --use autoprefixer -o theme-blue-pre.css  theme-blue.css
postcss --use autoprefixer -o theme-green-pre.css  theme-green.css
cssnano theme-blue-pre.css > theme-blue.css
cssnano theme-green-pre.css > theme-green.css
mv theme-blue.css theme-green.css ../../Themes/default/styles/
cd ..
rm -rf build
