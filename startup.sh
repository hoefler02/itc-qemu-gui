#!/bin/bash

green='\033[0;32m'
yellow='\033[0;33m'
red='\033[0;31m'
off='\033[0m'

if [ ! -d "./venv" ]; then
    echo -e "${yellow}[+]${off} Creating virtual enviornment"
    python3 -m venv venv
fi

if [ -z $VIRTUAL_ENV ]; then
    echo -e "${yellow}[+]${off} Running virtual enviornment"
    source ./venv/bin/activate 
fi

installed=$(pip3 list 2>/dev/null)

for package in $(awk -F "==" '{print $1}' ./requirements.txt); do
    echo $installed | grep $package >/dev/null
    if [ $? -eq 1 ]; then
        echo -e "${yellow}[+]${off} Installing required package $package"
        pip3 install $(grep $package ./requirements.txt)
    fi
done

echo -e "${green}[+]${off} Running GUI"
python3 ./main.py
