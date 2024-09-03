#!/usr/bin/env zsh

rm ./dist/*.whl
rm ./dist/*.tar.gz

python3 setup.py sdist bdist_wheel

if [[ $1 == '--release' ]]
then
	python3 -m twine upload --verbose --repository cc-pathlib_REL dist/*
else
	python3 -m twine upload --verbose --repository cc-pathlib_TST dist/*
	if [[ $? == 0 ]]
	then
		echo "you can now upload officially with the flag --release"
	fi
fi
