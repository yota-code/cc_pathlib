#!/usr/bin/env zsh

rm ./dist/*.whl
rm ./dist/*.tar.gz

python3 setup.py sdist bdist_wheel

if [[ $1 == '--release' ]]
then
	python3 -m twine upload dist/*
else
	python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
	if [[ $? == 0 ]]
	then
		echo "you can now upload officially with the flag --release"
	fi
fi