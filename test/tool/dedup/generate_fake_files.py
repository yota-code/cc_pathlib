#!/usr/bin/env python3

import random
import sys

random.seed(0)

from cc_pathlib import Path

tmp_dir = Path('tmp')
tmp_dir.make_dirs()
tmp_dir.delete_content()

letter = list('ABCDEHJKMPRSTXY')

h_lst = list()

for i in range(4096) :
	random.shuffle(letter)
	p = [letter[i] for i in range(0,random.randrange(2,4))]
	p[-1] += ''.join(letter[5:9]) + '.txt'
	q = ''.join(letter[-random.randrange(1,3):])

	if i % 8 == 0 :
		h_lst.append(tmp_dir / Path(* p))

	(tmp_dir / Path(* p)).make_parents()
	(tmp_dir / Path(* p)).write_text(q)

for h in h_lst :
	random.shuffle(letter)
	p = [letter[i] for i in range(0,random.randrange(2,4))]
	p[-1] += ''.join(letter[5:9]) + '.txt'

	if (tmp_dir / Path(* p)) == h :
		continue

	if (tmp_dir / Path(* p)).is_file() :
		(tmp_dir / Path(* p)).unlink()
	(tmp_dir / Path(* p)).make_parents()
	(tmp_dir / Path(* p)).hardlink_to(h)