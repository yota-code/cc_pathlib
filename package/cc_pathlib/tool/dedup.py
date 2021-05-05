#!/usr/bin/env python3

import collections

from cc_pathlib import Path

def dedup_size_pass(base_dir, pattern) :
	print(f"dedup_size_pass({base_dir}, {pattern})")

	size_map = collections.defaultdict(set)
	for pth in base_dir.rglob(pattern) :
		size_map[pth.stat().st_size].add(pth)

	dedup_checksum_pass(size_map)

def dedup_checksum_pass(size_map) :
	for k in reversed( sorted(size_map) ) :

		pth_set = size_map[k]
		if len(pth_set) <= 1 :
			continue

		checksum_map = collections.defaultdict(set)
		for pth in pth_set :
			checksum_map[ hash(pth.read_bytes()) ].add(pth)

		dedup_content_pass(checksum_map)

def dedup_content_pass(checksum_map) :
	for k in checksum_map :

		pth_set = checksum_map[k]
		if len(pth_set) <= 1 :
			continue

		content_map = collections.defaultdict(set)
		for pth in pth_set :
			content_map[pth.read_bytes()].add(pth)

		dedup_inode_pass(content_map)

def dedup_inode_pass(content_map) :
	for k in content_map :
		
		pth_set = content_map[k]
		if len(pth_set) <= 1 :
			continue

		inode_prev = None
		pth_prev = None
		for pth in pth_set :
			inode_curr = pth.stat().st_ino
			if inode_prev is not None and pth_prev is not None :
				if inode_prev != inode_curr :
					pth.unlink()
					pth.hardlink_to(pth_prev)
					print(f"{pth} -> {pth_prev}")
			else :
				inode_prev = inode_curr
				pth_prev = pth

def dedup(base_dir, pattern_lst=['*.svg', '*.json', '*.json.br', '*.svg.br']) :

	for pattern in pattern_lst :
		dedup_size_pass(base_dir, pattern)

if __name__ == '__main__' :

	import sys

	try :
		base_dir = Path( sys.argv[1] )
	except :
		base_dir = Path()

	if base_dir.is_dir() :
		dedup(base_dir)