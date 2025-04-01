#!/usr/bin/env python3

from cc_pathlib import Path

import collections
import mmap
import random

import xxhash

"""
this code was not extensively tested, use with care
"""

class DedupDir() :

	"""
	TODO:
		d'abord scanner par (st_dev, st_ino) ! ça sert à rien d'avoir deux fois des fichiers de même inode !!!!
		ensuite trier par taille (la selection par nom est con comme tout, ou alors à la selection initiale)
		puis par hash
	"""

	_debug = True

	dry_run = True

	max_nlink = 8
	max_fsize = 2**26 # 64 Mo

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

		self.s_map = dict()
		self.i_map = collections.defaultdict(list)

		for pth in self.base_dir.iter_on_files(* suffix_set) :
			q = pth.stat()
			if q.st_nlink < self.max_nlink :
				# if the file is already linked at least max_nlink times, skip it
				p = pth.relative_to(self.base_dir)
				self.s_map[q.st_ino] = q.st_size
				self.i_map[q.st_ino].append(p)

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

	# def dedup_name(self, pth_set=None) :
	# 	raise NotImplementedError
	# 	"""
	# 	the input is the full list of files
	# 	we sort them by name and call dedup_size() with each bucket 
	# 	"""
	# 	print(f"= dedup_name(... {len(pth_set) if pth_set is not None else pth_set})")

	# 	if pth_set is None :
	# 		pth_set = set(self.r_map)

	# 	name_map = collections.defaultdict(set)
	# 	for pth in pth_set :
	# 		name_map[pth.name].add(pth)

	# 	for k in name_map :
	# 		name_set = name_map[k]
	# 		if 1 < len(name_set) :
	# 			self.dedup_size(name_set)

	def dedup_size(self) :
		"""
		we sort inodes in buckets of files of the same size
		"""
		# print(f"=   dedup_size(... {len(pth_set) if pth_set is not None else pth_set})")
		
		size_map = collections.defaultdict(set)
		for k in self.i_map :
			# size -> inode_set
			size_map[self.s_map[k]].add(k)

		for k in size_map :
			bucket_set = size_map[k]
			if 1 < len(bucket_set) :
				self.dedup_hash(bucket_set)

	# def dedup_inode(self, pth_set, size) :
	# 	"""
	# 	the input is a set of pth with the same size
	# 	we keep only one per inode
	# 	(because all files linked to the same inode are already hardlinked)
	# 	"""
	# 	print(f"=     dedup_inode(... {len(pth_set)})")

	# 	inode_map = collections.defaultdict(list)
	# 	for pth in pth_set :
	# 		inode_map[self.r_map[pth].st_ino].append(pth)

	# 	self.dedup_hash(inode_map, size)

	def dedup_hash(self, inode_set) :
		"""
		inodes in inode_set have the same size
		we sort them in buckets based on a checksum
		"""

		# print(f"=       dedup_hash({len(pth_set)} :: {pth_set})")

		hash_map = collections.defaultdict(set)
		for k in inode_set :
			# hash -> inode_set
			hash_map[self.hash(self.i_map[k][0])].add(k)

		for k in hash_map :
			bucket_set = hash_map[k]
			if 1 < len(bucket_set) :
				# print(f"=         dedup_file :: {k} x{len(file_set)} :: {' '.join(str(i) for i in sorted(file_set))})")
				self.dedup_file(bucket_set)

	def dedup_file(self, inode_set) :
		"""
		inodes in inode_set have the same size and same checksum
		we call fuse as soon as two of them are equal
		"""

		if self.s_map[next(iter(inode_set))] < self.max_fsize :
			file_map = collections.defaultdict(set)
			for k in inode_set :
				file_map[(self.base_dir / self.i_map[k][0]).read_bytes()].add(k)

			for k in file_map :
				bucket_set = file_map[k]
				if 1 < len(bucket_set) :
					self.fuse(bucket_set)
		
	def fuse(self, inode_set) :
		"""
		inodes in inode_set have are confirmed to point idendical files !
		"""
		# fuse is destructive, be careful to pass to this stage only strictly identical files

		# on commence par classer les inodes par nombre de fichiers qui y sont liés
		inode_lst = sorted((len(self.i_map[k]), k) for k in inode_set)

		def pick_src() :
			src_ino, src_pth = None, None
			while True :
				if src_pth is None or self.max_nlink <= (self.base_dir / src_pth).stat().st_nlink :
					if inode_lst :
						src_len, src_ino = inode_lst.pop(-1)
						src_pth = self.i_map[src_ino][0]
						yield src_pth
					else :
						return
				else :
					yield src_pth

		src_picker = pick_src()

		while inode_lst :
			dst_len, dst_ino = inode_lst.pop()
			try :
				for dst_pth in self.i_map[dst_ino] :
					src_pth = next(src_picker)
					(self.base_dir / dst_pth).unlink()
					(self.base_dir / dst_pth).hardlink_to(self.base_dir / src_pth)

					# print(f"{src_pth} <- {dst_pth}")
					self.saved += self.s_map[dst_ino]
			except StopIteration :
				break
				
	def dedup(self) :
		if self.only_same_name :
			self.dedup_name(pth_set)
		else :
			self.dedup_size(pth_set)

	def print_graph(self) :
		pass