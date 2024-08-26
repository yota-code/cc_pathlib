#!/usr/bin/env python3

if [[ ! -d tmp ]]
then
	./generate_fake_files.py
fi

pathlib_dedup tmp