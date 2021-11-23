#!/usr/bin/env python3

import collections

class DedupDir() :
	def __init__(self, base_dir) :
		self.base_dir = base_dir

	def build_name_map(self, path_set) :
		name_map = collections.defaultdict(set)
		for pth in path_set :
			name_map[pth.name].add(pth)

	def build_size_map(self, path_set) :
		size_map = collections.defaultdict(set)
		for pth in path_set :
			size_map[pth.stat().st_size].add(pth)

	def dedup_hash(self, path_set) :
		hash_map = collections.defaultdict(set)
		for pth in path_set :
			hash_map[hash(pth.read_bytes())].add(pth)

		for k in hash_map :
			path_subset = hash_map[k]
			if len(path_subset) :
				self.dedup_file(path_subset)


	def dedup_file(self, path_set) :
		file_map = collections.defaultdict(set)
		for pth in path_set :
			file_map[pth.read_bytes()].add(pth)

		for k in file_map :
			path_subset = file_map[k]
			if len(path_subset) :
				self.fuse(path_subset)
		
	def fuse(self, path_set) :
		# fuse is destructive, be careful to pass only strictly identical files
		path_lst = sorted(path_set)
		path_orig = path_lst.pop()
		for pth in path_lst :
			pth.unlink()
			pth.hardlink_to(path_orig)
			print(f"{pth} -> {pth_prev}")

	def dedup(self, pattern='*') :
		self.path_set = set()
		for pth in self.base_dir.rglob(self.pattern) :
			self.path_set.add(pth)



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

def dedup(base_dir, pattern='*.*') :
	if base_dir.is_dir() :
		_dedup_size_pass(base_dir, pattern)
	else :
		raise ValueError("Path() must be a directory")
