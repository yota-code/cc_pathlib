#!/usr/bin/env python3

import base64
import hashlib

import xxhash

from cc_pathlib import Path
	
class Attentive() :

	_debug = True

	_config = {
		# if the cache_pth is None and tmp_cache is True, create a cache file in /tmp
		'tmp_cache' : False,
	}

	def __init__(self, base_dir:Path=None, cache_pth:Path=None) :
		self.base_dir = (Path(base_dir) if base_dir is not None else Path()).resolve()

		assert self.base_dir.is_dir()
		
		if cache_pth is not None :
			if self._config['tmp_cache'] and cache_pth is None :
				txt = str(self.base_dir).encode('utf8')
				hsh = hashlib.blake2b(txt, digest_size=24, salt=b"cc")
				key = base64.urlsafe_b64encode(hsh.digest()).decode('ascii')
				tmp = Path('/tmp/cc').make_dirs('private')
				self.cache_pth = tmp / f"{key}.pickle"
			else :
				self.cache_pth = cache_pth.with_suffix('.pickle')

			if self.cache_pth.is_file() :
				self.m = self.cache_pth.load()
			else :
				self.m = dict()
		else :
			self.cache_pth = None
			self.m = dict()
		self.z = dict() # list of tasks in progress
		for local_pth in self.m :
			pth = self.base_dir / local_pth
			if not pth.is_file() :
				print("DEL", local_pth)
				self.m.pop(local_pth, None)

	def flush(self) :
		if self._debug :
			self.cache_pth.with_suffix('.tsv').save(
				[[f"{self.m[k]:024X}", k] for k in sorted(self.z)] +
				[['-'*8,],] + 
				[[f"{self.m[k]:024X}", k] for k in sorted(self.m)]
			)
		self.cache_pth.save(self.m)

	def hash(self, local_pth) :
		pth = self.base_dir / local_pth
		if pth.is_file() :
			siz = pth.stat().st_size & 0xFFFF_FFFF
			bin = pth.read_bytes()
			hsh = xxhash.xxh3_64(bin, seed=siz).intdigest()
			key = (siz << 64) + hsh
			return key, bin
		else :
			return None, b''

	def todo(self, local_pth) :
		"""
		1. open the file located at self.base_dir / local_pth
		2. compute the hash and compare it with the cached one
		3. if different return the content of the file else return None
		"""
		key, bin = self.hash(local_pth)
		if key is None :
			self.m.pop(local_pth, None)
			return None
		if local_pth in self.m and self.m[local_pth] == key :
			return None
		self.z[local_pth] = key
		return bin
	
	def done(self, local_pth) :
		key = self.z.pop(local_pth, None)
		if key is not None :
			self.m[local_pth] = key
