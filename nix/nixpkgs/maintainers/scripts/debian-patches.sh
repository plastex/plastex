#!/bin/sh

# Download patches from debian project
# Usage $0 debian-patches.txt debian-patches.nix
# An example input and output files can be found in applications/graphics/xara/

DEB_URL=https://sources.debian.org/data/main
declare -a deb_patches
mapfile -t deb_patches < $1

# First letter
deb_prefix="${deb_patches[0]:0:1}"
prefix="${DEB_URL}/${deb_prefix}/${deb_patches[0]}/debian/patches"

if [[ -n "$2" ]]; then
    exec 1> $2
fi

cat <<EOF
# Generated by $(basename $0) from $(basename $1)
let
  prefix = "${prefix}";
in
[
EOF
for ((i=1;i < ${#deb_patches[@]}; ++i)); do
    url="${prefix}/${deb_patches[$i]}"
    sha256=$(nix-prefetch-url $url)
    echo "  {"
    echo "    url = \"\${prefix}/${deb_patches[$i]}\";"
    echo "    sha256 = \"$sha256\";"
    echo "  }"
done
echo "]"