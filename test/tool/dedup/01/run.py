#!/usr/bin/env python3

import random
import sys

random.seed(0)

from cc_pathlib import Path

tmp_dir = Path('./tmp')
tmp_dir.make_dirs()
tmp_dir.delete(content_only=True)

letter = 'abcdefghijklmnopqrstuvwxyz0123456789'

content_map = dict()

for i in range(256) :
	l = random.randrange(8, 16)
	c = random.randrange(len(letter))
	m = letter[c] * l

	(tmp_dir / f"{i:04d}.txt").write_text( m )
	content_map[i] = m

tmp_dir.dedup('*.txt')

exit_value = 0
for i in content_map :
	m_ref = content_map[i]
	m_tst = (tmp_dir / f"{i:04d}.txt").read_text()
	if m_ref != m_tst :
		exit_value = i + 1
		break

tmp_dir.delete()

sys.exit(exit_value)