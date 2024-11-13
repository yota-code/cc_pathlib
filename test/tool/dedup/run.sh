#!/usr/bin/env zsh

rm -rf tmp ref
./generate_fake_files.py
cp -r tmp ref

pathlib_dedup tmp

diff -r tmp ref
du -s tmp
du -s ref