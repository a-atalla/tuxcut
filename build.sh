#!/bin/bash

# Clean old packages
rm -rf *.deb
rm -rf *.rpm

## Build server bin
pyinstaller -s -F  server/tuxcutd.py 

## BUild client bin
pyinstaller -s -F  client/tuxcut.py

## copy the 2 bin to the pkg folder
rm -rf pkg/opt/tuxcut/*
mv dist/tuxcut pkg/opt/tuxcut
mv dist/tuxcutd pkg/opt/tuxcut

## build rpm
# fpm -s dir -t rpm  -n tuxcut -v 6.xxx -d "libpcap" -d "arptables" -d "bind-utils" -d "net-tools" -C pkg

## build deb
# fpm -s dir -t deb  -n tuxcut -v 6.xxx -d "libpcap0.8" -d "arptables" -d "dnsutils" -d "net-tools" -C pkg
