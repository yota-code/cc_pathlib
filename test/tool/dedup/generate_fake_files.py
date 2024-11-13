#!/usr/bin/env python3

import random
import sys

random.seed(0)

from cc_pathlib import Path

tmp_dir = Path('tmp')
tmp_dir.make_dirs()
tmp_dir.delete_content()

letters = list('ABCDEHJKMPRSTXYZ')

a_lst = random.sample(letters, 16)
b_lst = random.sample(letters, 16)
c_lst = random.sample(letters, 16)
d_lst = random.sample(letters, 16)

l_lst = list()
for i in range(16) :
	a, b, c, d = a_lst[i], b_lst[i], c_lst[i], d_lst[i]
	l_lst.append(a_lst[i])
	l_lst.append(a_lst[3*i % 16] + b_lst[5*i % 16])
	l_lst.append(a_lst[7*i % 16] + b_lst[11*i % 16] + c_lst[13*i % 16])
	l_lst.append(a_lst[17*i % 16] + b_lst[19*i % 16] + c_lst[23*i % 16] + d_lst[29*i % 16])

random.shuffle(l_lst)
print(l_lst)

h_lst = list()

for i in range(8192) :
	random.shuffle(letters)
	p = [letters[i] for i in range(0,random.randrange(2,4))]
	p[-1] += ''.join(letters[5:9]) + '.txt'
	q = random.choice(l_lst)

	if i % 16 == 0 :
		h_lst.append(tmp_dir / Path(* p))

	(tmp_dir / Path(* p)).make_parents()
	(tmp_dir / Path(* p)).write_text(q)

for h in h_lst :
	random.shuffle(letters)
	p = [letters[i] for i in range(0,random.randrange(2,4))]
	p[-1] += ''.join(letters[5:9]) + '.txt'

	if (tmp_dir / Path(* p)) == h :
		continue

	if (tmp_dir / Path(* p)).is_file() :
		(tmp_dir / Path(* p)).unlink()
	(tmp_dir / Path(* p)).make_parents()
	(tmp_dir / Path(* p)).hardlink_to(h)
