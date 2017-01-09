#!/bin/bash
version=$(sed -ne 's/version=\([0-9]*\.[0-9]*\)/\1/p' metadata.txt)
major=$(echo $version | cut -f1 -d.)
minor=$(echo $version | cut -f2 -d.)
next=$major.$(( $minor + 1 ))
echo bumping $version to $next
sed -i "s/version=$version/version=$next/" metadata.txt
sed -i "s/version = '$version'/version = '$next'/" help/source/conf.py
sed -i "s/release = '$version'/release = '$next'/" help/source/conf.py
