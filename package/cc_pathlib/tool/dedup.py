#!/usr/bin/env python3

import collections

def _dedup_size_pass(base_dir, pattern) :
	size_map = collections.defaultdict(set)
	for pth in base_dir.rglob(pattern) :
		size_map[pth.stat().st_size].add(pth)

	_dedup_checksum_pass(size_map)

def _dedup_checksum_pass(size_map) :
	for k in reversed( sorted(size_map) ) :

		pth_set = size_map[k]
		if len(pth_set) <= 1 :
			continue

		checksum_map = collections.defaultdict(set)
		for pth in pth_set :
			checksum_map[ hash(pth.read_bytes()) ].add(pth)

		_dedup_content_pass(checksum_map)

def _dedup_content_pass(checksum_map) :
	for k in checksum_map :

		pth_set = checksum_map[k]
		if len(pth_set) <= 1 :
			continue

		content_map = collections.defaultdict(set)
		for pth in pth_set :
			content_map[pth.read_bytes()].add(pth)

		_dedup_inode_pass(content_map)

def _dedup_inode_pass(content_map) :
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

def dedup(base_dir, pattern) :
	if base_dir.is_dir() :
		_dedup_size_pass(base_dir, pattern)
	else :
		raise ValueError("Path() must be a directory")
