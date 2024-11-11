#!/usr/bin/env zsh

if [[ ! -d tmp ]]
then
	./generate_fake_files.py
fi

pathlib_dedup tmp