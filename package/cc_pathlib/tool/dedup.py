#!/usr/bin/env python3

from cc_pathlib import Path

import collections
import mmap

import xxhash

"""
this code was not extensively tested, use with care
"""

class DedupDir() :

	_debug = True

	dry_run = True

	max_nlink = 16
	max_fsize = 2**24 # 16 Mo

	def __init__(self, base_dir) :
		self.base_dir = Path(base_dir).resolve()
		self.saved = 0

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

		print("SCAN", suffix_set, end=" ")
		for pth in self.base_dir.iter_on_files(* suffix_set) :
			q = pth.stat()
			if q.st_nlink < self.max_nlink :
				# if the file is already linked at least max_nlink times, just pass
				self.r_map[pth.relative_to(self.base_dir)] = q
		
		print(len(self.r_map))

		if cache :
			print("SAVE")
			print(self.r_map)
			cache_pth.save(self.r_map)

	# def hash(self, pth) :
	# 	import blake3

	# 	fsh = blake3.blake3(max_threads=blake3.AUTO)
	# 	fsh.update_mmap(self.base_dir / pth)
	# 	return fsh.digest()

	def hash(self, pth) :
		hsh = xxhash.xxh3_64()
		with (self.base_dir / pth).open("rb") as fid :
			with mmap.mmap(fid.fileno(), 0, prot=mmap.PROT_READ) as mem :
				hsh.update(mem)
		return hsh.digest()
		# return binascii.crc32((self.base_dir / pth).read_bytes())

	def dedup_name(self, pth_set=None) :
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
			# sort in size based buckets
			size_map[self.r_map[pth].st_size].add(pth)

		for k in size_map :
			size_set = size_map[k]
			if 1 < len(size_set) :
				self.dedup_inode(size_set)

	def dedup_inode(self, pth_set) :
		"""
		the input is a set of pth with the same size we keep only one per inode
		(because all files linked to the same inode are already hardlinked)
		"""
		print(f"=     dedup_inode(... {len(pth_set)})")

		inode_map = collections.defaultdict(list)
		for pth in pth_set :
			inode_map[self.r_map[pth].st_ino].append(pth)

		inode_set = set(inode_map[k][0] for k in inode_map)
		if 1 < len(inode_set) :
			self.dedup_checksum(inode_set)

	def dedup_checksum(self, pth_set:set[Path]) :
		"""
		files in pth_set have the same size but different inodes
		we sort them in buckets based on a checksum
		"""

		print(f"=       dedup_checksum({len(pth_set)} :: {pth_set})")

		hash_map = collections.defaultdict(set)
		for pth in pth_set :
			hash_map[self.hash(pth)].add(pth)

		for k in hash_map :
			file_set = hash_map[k]
			if 1 < len(file_set) :
				print(f"=         dedup_file :: {k} x{len(file_set)} :: {' '.join(str(i) for i in sorted(file_set))})")
				self.dedup_file(file_set)

	def dedup_file(self, pth_set) :
		"""
		files in pth_set have the same checksum, should have different inodes
		"""

		file_map = collections.defaultdict(set)

		pth_lst = sorted(pth_set)

		TODO: write a better algorithm which extract a list of files KNOWN with certainty to be identical

		for pth in pth_set :
			pour les petits fichiers, on peur jouer avec un dico... pour les gros, on fait comment ?
			file_map[(self.base_dir / pth).read_bytes()].add(pth)

		for k in file_map :
			file_set = file_map[k]
			if 1 < len(file_set) :
				self.fuse(file_set)
		
	def fuse(self, pth_set) :
		"""
		files in pth_set are confirmed idendical, ready to be fused
		"""
		# fuse is destructive, be careful to pass to this stage only strictly identical files

		pth_lst = sorted(pth_set)

		src = pth_lst.pop()
		src_inode = self.r_map[src].st_ino
		print(f"\t{src}")

		while pth_lst :
			if self.max_nlink <= (self.base_dir / src).stat().st_nlink :
				src = pth_lst.pop()
				src_inode = self.r_map[src].st_ino
				print(f"\t{src}")
				continue

			dst = pth_lst.pop()
			dst_inode = self.r_map[dst].st_ino

			if dst_inode != src_inode :
				if not self.dry_run :
					(self.base_dir / dst).unlink()
					(self.base_dir / dst).hardlink_to(self.base_dir / src)
				self.saved += self.r_map[dst].st_size
				print(f"\t\t<- {dst}")

	def dedup(self) :
		if self.only_same_name :
			self.dedup_name(pth_set)
		else :
			self.dedup_size(pth_set)

	def print_graph(self) :
		pass