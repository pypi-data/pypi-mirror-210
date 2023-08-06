# python_travelmanager
python lib for travelmanager (https://travelmanager.de/)

## install dev
python -m venv venv
. venv/Scripts/activate
pip install -r requirements_dev.txt
pre-commit install --hook-type pre-push

## build
python -m build
