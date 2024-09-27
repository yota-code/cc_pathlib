#!/usr/bin/env python3

import base64
import enum
import hashlib

import xxhash

from cc_pathlib import Path


class FileStatus(enum.Enum) :
	UNCHANGED = 0
	MODIFIED = 1
	DELETED = -1



"""
Il faut faire une liste de tous les fichiers surveillés
dans cette liste il faut marquer les fichiers qui méritent d'être traité à nouveau
ce système se base uniquement sur la date de modification et le fait qu'elle ait changée depuis la dernière fois

name -> inode
inode -> mtime

"""
	
class Attentive() :

	_debug = True

	_config = {
		# if the cache_pth is None and tmp_cache is True, create an automatic cache file in /tmp
		'tmp_cache' : False,
	}

	def __init__(self, base_dir, cache_arg=True) :
		self.base_dir = Path(base_dir).resolve()

		assert self.base_dir.is_dir()
		
		if cache_arg :
			if isinstance(cache_arg, str) or isinstance(cache_arg, Path) :
				cache_dir = Path(cache_arg).resolve().make_dirs()
			else :
				txt = str(self.base_dir).encode('utf8')
				hsh = hashlib.blake2b(txt, digest_size=24, salt=b"cc")
				key = base64.urlsafe_b64encode(hsh.digest()).decode('ascii')
				cache_dir = (Path('/tmp') / f"pathlib_{key}").make_dirs('private')
			self.cache_pth = cache_dir / 'attentive.pickle'

			if self.cache_pth.is_file() :
				self.m = self.cache_pth.load()
			else :
				self.m = dict()
		else :
			# cache disabled completely
			self.cache_pth = None

		self.z = dict() # list of tasks in progress
		self.d = dict() # set of deleted files

		# for local_pth in self.m :
		# 	pth = self.base_dir / local_pth
		# 	if not pth.is_file() :
		# 		print(f"{__class__.__name__} DEL {local_pth}")
		# 		self.m.pop(local_pth, None)
		# 		self.d.add(local_pth)

	def save(self) :
		if self._debug :
			self.cache_pth.with_suffix('.tsv').save(
				[[f"{self.z[k]:024X}", k] for k in sorted(self.z)] +
				[['-'*8,],] + 
				[[f"{self.m[k]:024X}", k] for k in sorted(self.m)]
			)
		self.cache_pth.save(self.m)

	def todo(self, local_pth) :
		"""
		1. open the file located at self.base_dir / local_pth
		2. compute the hash and compare it with the cached one
		3. if different return the content of the file else return None
		4. if a file is returned, local_pth is stored in the "in progress" map
		"""
		pth = self.base_dir / local_pth

		if not pth.is_file() :
			# le fichier a été supprimé
			self.d[local_pth] = None
			return FileStatus.DELETED, b''

		siz = pth.stat().st_size & 0xFFFF
		bin = pth.read_bytes()
		hsh = xxhash.xxh3_64(bin, seed=siz).intdigest()
		key = (siz << 64) + hsh

		if local_pth in self.m and self.m[local_pth] == key :
			return FileStatus.UNCHANGED, b''

		self.z[local_pth] = key
		return FileStatus.MODIFIED, bin
	
	def done(self, local_pth) :
		if local_pth in self.d :
			del self.d[local_pth]
			self.m.pop(local_pth, None)
		elif local_pth in self.z :
			key = self.z.pop(local_pth, None)
			self.m[local_pth] = key
		else :
			assert local_pth in self.m

# class Attentive() :

# 	_debug = True

# 	_config = {
# 		# if the cache_pth is None and tmp_cache is True, create an automatic cache file in /tmp
# 		'tmp_cache' : False,
# 		'_cache_name' : "attentive.pickle"
# 	}

# 	def __init__(self, base_dir:Path=None, cache=True) :
# 		self.base_dir = (Path(base_dir) if base_dir is not None else Path()).resolve()

# 		assert self.base_dir.is_dir()

# 		if cache :
# 			if isinstance(cache, str) :
# 				cache = Path(cache)
# 			if isinstance(cache, Path) :
# 				self.cache_pth = cache.with_suffix('.pickle')
# 			else :
# 				txt = str(self.base_dir).encode('utf8')
# 				hsh = hashlib.blake2b(txt, digest_size=24, salt=b"cc")
# 				key = base64.urlsafe_b64encode(hsh.digest()).decode('ascii')
# 				cache_dir = (Path('/tmp') / f"pathlib_{key}").make_dirs('private')
# 				self.cache_pth = cache_dir / self._config['_cache_name']

# 			if self.cache_pth.is_file() :
# 				self.z = self.cache_pth.load()
# 			else :
# 				self.z = dict()
# 		else :
# 			# cache disabled completely
# 			self.cache_pth = None

# 		self.todo_map = dict()

# 		for local_pth in self.z :
# 			pth = self.base_dir / local_pth
# 			if not pth.is_file() :
# 				print("DEL", local_pth)
# 				self.z.pop(local_pth, None)

# 	def flush(self) :
# 		if self._debug :
# 			self.cache_pth.with_suffix('.tsv').save(
# 				[[f"{self.m[k]:024X}", k] for k in sorted(self.z)] +
# 				[['-'*8,],] + 
# 				[[f"{self.m[k]:024X}", k] for k in sorted(self.m)]
# 			)
# 		self.cache_pth.save(self.m)

# 	def get_key(self, local_pth) :
# 		pth = self.base_dir / local_pth
# 		if pth.is_file() :
# 			siz = pth.stat().st_size & 0xFFFF_FFFF
# 			bin = pth.read_bytes()
# 			hsh = xxhash.xxh3_64(bin, seed=siz).intdigest()
# 			key = (siz << 64) + hsh
# 			return key, bin
# 		else :
# 			return None, b''

# 	def get_key_file(self, local_pth) :
# 		""" return the key, and the file content itself, if it was 

# 	def todo(self, local_pth) :
# 		"""
# 		1. open the file located at self.base_dir / local_pth
# 		2. compute the hash and compare it with the cached one
# 		3. if different return the content of the file else return None
# 		"""
# 		key, bin = self.hash(local_pth)
# 		if key is None :
# 			self.m.pop(local_pth, None)
# 			return None
# 		if local_pth in self.m and self.m[local_pth] == key :
# 			return None
# 		self.z[local_pth] = key
# 		return bin
	
# 	def done(self, local_pth) :
# 		key = self.z.pop(local_pth, None)
# 		if key is not None :
# 			self.m[local_pth] = key
