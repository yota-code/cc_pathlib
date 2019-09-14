#!/usr/bin/env zsh

rm ./dist/*.whl
rm ./dist/*.tar.gz

python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
