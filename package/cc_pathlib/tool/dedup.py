#!/usr/bin/env python3

from cc_pathlib import Path

import collections

import binascii

"""
this code was not extensively tested, use with care
"""

class DedupDir() :

	dry_run = True

	def __init__(self, base_dir) :
		self.base_dir = Path(base_dir).resolve()

	def scan(self, * suffix_lst, cache=True) :
		suffix_set = set(suffix_lst)

		if cache :
			import urllib
			cache_pth = Path("/tmp/cc_pathlib") / (urllib.parse.quote(str(self.base_dir), safe='') + '.pickle')
			print("cache_pth =", cache_pth)
			if cache_pth.is_file() :
				print("LOAD")
				self.r_map = cache_pth.load()
				return

		self.r_map = dict()
		# self.r_map[None] = suffix_set

		print("SCAN", suffix_set, end=" ")
		for pth in self.base_dir.iter_recursive(* suffix_set) :
			self.r_map[pth.relative_to(self.base_dir)] = pth.stat()
		print(len(self.r_map))

		if cache :
			print("SAVE")
			print(self.r_map)
			cache_pth.save(self.r_map)

	def hash(self, pth) :
		return binascii.crc32((self.base_dir / pth).read_bytes())

	def dedup_name(self, pth_set) :
		print(f"= dedup_name(... {len(pth_set) if pth_set is not None else pth_set})")

		if pth_set is None :
			pth_set = set(self.r_map)

		name_map = collections.defaultdict(set)
		for pth in pth_set :
			name_map[pth.name].add(pth)

		for k in name_map :
			path_subset = name_map[k]
			if 1 < len(path_subset) :
				self.dedup_size(path_subset)

	def dedup_size(self, pth_set=None) :
		print(f"=   dedup_size(... {len(pth_set) if pth_set is not None else pth_set})")
		if pth_set is None :
			pth_set = set(self.r_map)
		size_map = collections.defaultdict(set)
		for pth in pth_set :
			size_map[self.r_map[pth].st_size].add(pth)

		for k in size_map :
			size_set = size_map[k]
			if 1 < len(size_set) :
				self.dedup_inode(size_set)

	def dedup_inode(self, pth_set) :
		""" the input is a set of pth with the same size
		we keep only one per inode
		(because all files linked to the same inode are already hardlinked)
		"""
		print(f"=     dedup_inode(... {len(pth_set)})")
		inode_map = collections.defaultdict(list)
		for pth in pth_set :
			inode_map[self.r_map[pth].st_ino].append(pth)

		inode_set = set(inode_map[k][0] for k in inode_map)
		if 1 < len(inode_set) :
			self.dedup_hash(inode_set)

	def dedup_hash(self, pth_set) :
		print(f"=       dedup_hash(... {len(pth_set)})")
		hash_map = collections.defaultdict(set)
		for pth in pth_set :
			hash_map[self.hash(pth)].add(pth)

		for k in hash_map :
			path_subset = hash_map[k]
			if len(path_subset) :
				self.dedup_file(path_subset)

	def dedup_file(self, pth_set) :
		print(f"=         dedup_file(... {len(pth_set)})")
		file_map = collections.defaultdict(set)
		for pth in pth_set :
			file_map[(self.base_dir / pth).read_bytes()].add(pth)

		for k in file_map :
			file_set = file_map[k]
			if 1 < len(file_set) :
				self.fuse(file_set)
		
	def fuse(self, pth_set) :
		# fuse is destructive, be careful to pass to this stage only strictly identical files
		pth_lst = sorted(pth_set)

		pth_orig = pth_lst.pop()
		inode_orig = self.r_map[pth_orig].st_ino

		print(f"\t{pth_orig}")
		for pth_test in pth_lst :
			inode_test = self.r_map[pth_test].st_ino
			if inode_test != inode_orig :
				if self.dry_run :
					pass
					# pth_test.unlink()
					# pth_test.hardlink_to(pth_orig)
				print(f"\t  <- {pth_test}")

	def dedup(self) :
		if self.only_same_name :
			self.dedup_name(pth_set)
		else :
			self.dedup_size(pth_set)


