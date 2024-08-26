#!/usr/bin/env python3

import random
import sys

random.seed(0)

from cc_pathlib import Path

tmp_dir = Path('tmp')
tmp_dir.make_dirs()
tmp_dir.delete_content()

letter = list('ABCDEHJKMPRSTXY')

for i in range(4096) :
	random.shuffle(letter)
	p = [letter[i] for i in range(0,random.randrange(2,4))]
	p[-1] += '.txt'
	q = letter[-1]

	(tmp_dir / Path(* p)).make_parents()
	(tmp_dir / Path(* p)).write_text(q)
