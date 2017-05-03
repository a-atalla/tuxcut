#!/usr/bin/env bash

# clean the old icons.py
rm -rf ../icons.py
arr=($(ls *.png))

# create new icons.py with all ocons in the directory

for icon in ${arr[@]}
do
    if [ $icon = ${arr[0]} ]; then
        img2py $icon ../icons.py
    else
        img2py -a $icon ../icons.py
    fi
done
