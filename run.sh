#!/bin/sh
cd ./app
pip3 install -r requirements/dev.txt

echo "#####################################################"
echo "#############       E2R CONVERTER       #############"
echo "#####################################################"

python3 manage.py runserver