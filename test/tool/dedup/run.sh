#!/usr/bin/env zsh

rm -rf tmp

for i in {1..3}
do
	rm -rf ref
	./generate_fake_files.py
	cp -r tmp ref

	pathlib_dedup tmp

	diff -r tmp ref
	du -s tmp
	du -s ref
done