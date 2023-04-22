#!/usr/bin/env python3

import collections

"""
this code was not extensively tested, use with care
"""

class DedupDir() :
	def __init__(self, base_dir) :
		self.base_dir = base_dir

	def dedup_name(self, pth_set) :
		name_map = collections.defaultdict(set)
		for pth in pth_set :
			name_map[pth.name].add(pth)

		for k in name_map :
			path_subset = name_map[k]
			if len(path_subset) :
				self.dedup_size(path_subset)

	def dedup_size(self, pth_set) :
		size_map = collections.defaultdict(set)
		for pth in pth_set :
			size_map[pth.stat().st_size].add(pth)

		for k in size_map :
			path_subset = size_map[k]
			if len(path_subset) :
				self.dedup_hash(path_subset)

	def dedup_hash(self, pth_set) :
		hash_map = collections.defaultdict(set)
		for pth in pth_set :
			hash_map[hash(pth.read_bytes())].add(pth)

		for k in hash_map :
			path_subset = hash_map[k]
			if len(path_subset) :
				self.dedup_file(path_subset)

	def dedup_file(self, pth_set) :
		file_map = collections.defaultdict(set)
		for pth in pth_set :
			file_map[pth.read_bytes()].add(pth)

		for k in file_map :
			path_subset = file_map[k]
			if len(path_subset) :
				self.fuse(path_subset)
		
	def fuse(self, pth_set) :
		# fuse is destructive, be careful to pass to this stage only strictly identical files
		pth_lst = sorted(pth_set)

		pth_orig = pth_lst.pop()
		inode_orig = pth_orig.stat().st_ino

		for pth_test in pth_lst :
			inode_test = pth_test.stat().st_ino
			if inode_test != inode_orig :
				pth_test.unlink()
				pth_test.hardlink_to(pth_orig)
				print(f"{pth_test} -> {pth_orig}")

	def dedup(self, pattern='*', same_name=False) :
		pth_set = set()
		for pth in self.base_dir.rglob(self.pattern) :
			pth_set.add(pth)

		if same_name :
			self.dedup_name(pth_set)
		else :
			self.dedup_size(pth_set)


