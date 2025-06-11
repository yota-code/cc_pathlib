#!/usr/bin/env python3

import collections
import datetime
import gzip
import lzma
import os
import pathlib
import subprocess
import socket
import sys
	
try :
	import bz2
except :
	pass

import cc_pathlib.filter.cc_json
import cc_pathlib.filter.cc_pickle
import cc_pathlib.filter.cc_numpy
import cc_pathlib.filter.cc_array
import cc_pathlib.filter.tsv

class Path(type(pathlib.Path())) :

	_available_archive = ['.gz', '.xz', '.br', '.lz', '.bz2']
	_available_filter = ['.tsv', '.json', '.txt', '.bin', '.pickle', '.npy', '.arr']
	_binary_format = ['.pickle', '.npy', '.bin', '.arr']

	_umask_dir_map = {
		'private' : 0o0700,
		'shared' : 0o2770,
		'public' : 0o2777,
	}

	def config(self) :
		if self.fsuffix in [".json", ".json.br"] :
			return cc_pathlib.filter.cc_json._JSON_config_CONTEXT(self)
		elif self.fsuffix in [".pickle",] :
			return cc_pathlib.filter.cc_pickle._PICKLE_config_CONTEXT(self)
		else :
			raise NotImplementedError

	def safe_config(self, lock) :
		if self.suffix == ".json" :
			with lock :
				return cc_pathlib.filter.cc_json._JSON_config_CONTEXT(self)
		else :
			raise NotImplementedError
			
	__iter__ = pathlib.Path.iterdir

	def iter_dirs(self) :
		return (x for x in self if x.is_dir())

	def iter_files(self) :
		return (x for x in self if x.is_file())

	@property
	def or_archive(self) :
		# if an archived version of the file exists, switch to it
		if not self.is_file() :
			for suffixe in self._available_archive :
				pth = self.parent / (self.name + suffixe)
				if pth.is_file() :
					return pth
		return self

	def archive(self, dst_dir=None, timestamp=False, delete_original=False) :
		dst_name = self.name

		if timestamp is True :
			dst_name += '.{0:%Y%m%d_%H%M%S}'.format(datetime.datetime.now())
		elif isinstance(timestamp, str) :
			dst_name += '.' + timestamp

		if dst_dir is None :
			dst_dir = self.parent

		if self.is_dir() :
			tar_pth = dst_dir / (dst_name + '.tar')
			cmd = ['tar', '--create', '--file', tar_pth, self.name]
			subprocess.run([str(i) for i in cmd], cwd=self.parent)
			cmd = ['lzip', '--best', tar_pth]
			subprocess.run([str(i) for i in cmd], cwd=self.parent)
			if delete_original :
				self.delete()
		elif self.is_file() :
			cmd = ['lzip', '--best', self]
			subprocess.run([str(i) for i in cmd])
			self.rename(dst_dir / dst_name)
			if delete_original :
				self.unlink()
		else :
			raise ValueError("can not be archived: {0}".format(self))

	def unarchive(self) :
		cmd = ['tar', '--extract', '--file', self.name]
		subprocess.run([str(i) for i in cmd], cwd=self.parent)

	def delete(self) :
		if self.is_dir() :
			self._delete_recursive()
			self.rmdir()
		elif self.is_file() :
			self.unlink()
		else :
			return

	def delete_content(self) :
		if self.is_dir() :
			self._delete_recursive()

	def _delete_recursive(self) :
		for sub in self :
			if sub.is_dir() :
				sub._delete_recursive()
				#print(f"_delete_dir({self})")
				sub.rmdir()
			else :
				#print(f"_delete_file({self})")
				sub.unlink()

	def delete_empty_dirs(self) :
		r_lst = [root for root, dirs, files in self.walk()]
		for pth in reversed(r_lst) :
			try :
				pth.rmdir()
			except OSError :
				pass
			
	def make_dirs(self, umask='shared') :
		""" create all dirs, equivalent to mkdir(parents=True) but also set permissions """
		if not self.is_dir() :
			self.make_parents(umask)

			self.mkdir()
			self.chmod(self._umask_dir_map[umask])
		return self

	def make_parents(self, umask='shared') :
		""" create all parent dirs of a given file to be """
		for p in reversed(self.parents) :
			if not p.is_dir() :
				p.mkdir()
				p.chmod(self._umask_dir_map[umask])
		return self

	def _load_archive(self, fmt=None, encoding=None) :
		""" open the compressed file, return the content """
		if fmt == '.gz' :
			z_content = self.read_bytes()
			b_content = gzip.decompress(z_content)
		elif fmt == '.xz' :
			z_content = self.read_bytes()
			b_content = lzma.decompress(z_content)
		elif fmt == '.br' :
			import brotli
			z_content = self.read_bytes()
			b_content = brotli.decompress(z_content)
		elif fmt == '.lz' :
			cmd = ['lzip', '--decompress', '--stdout', self]
			ret = subprocess.run([str(i) for i in cmd], stdout=subprocess.PIPE)
			b_content = ret.stdout
		else :
			# if fmt is None, load the file content as this
			b_content = self.read_bytes()

		return b_content if encoding is None else b_content.decode(encoding)

	def read_file(self, encoding) :
		""" load the content of a file without applying a filter, but decompress if needed """
		if self.suffix in self._available_archive :
			return self._load_archive(self.suffix, encoding)
		else :
			return self.read_text(encoding) if encoding is not None else self.read_bytes()

	def _load_filter(self, data, fmt, opt=None) :
		if fmt == '.tsv' :
			return cc_pathlib.filter.tsv.tsv_from_str(data)
		elif fmt == '.json' :
			return cc_pathlib.filter.cc_json.json_from_str(data)
		elif fmt == '.pickle' :
			return cc_pathlib.filter.cc_pickle.pickle_from_str(data)
		elif fmt == '.npy' :
			return cc_pathlib.filter.cc_numpy.numpy_from_bytes(data)
		elif fmt == '.arr' :
			s_lst = self.suffixes
			for k in cc_pathlib.filter.cc_array.array_type_to_code_map :
				if f'.{k}' in s_lst :
					return cc_pathlib.filter.cc_array.array_from_bytes(data, k)
			raise ValueError("Format not found for array encoding")
		else :
			return data

	def load(self, encoding='utf-8') :
		s_lst = self.suffixes
		fmt = None
		if s_lst and s_lst[-1] in self._available_archive :
			fmt = s_lst.pop()
		if s_lst[-1] in self._binary_format :
			encoding = None
		data = self._load_archive(fmt, encoding)
		if s_lst and s_lst[-1] in self._available_filter :
			data = self._load_filter(data, s_lst[-1])
		return data

	def save(self, data, encoding='utf-8', make_dirs='shared', ** extra_opt) :
		s_lst = self.suffixes

		self.make_parents(make_dirs)

		fmt = None
		if s_lst and s_lst[-1] in self._available_archive :
			fmt = s_lst.pop()
		if s_lst and s_lst[-1] in self._available_filter :
			data = self._save_filter(data, s_lst.pop(), extra_opt)
		self._save_archive(data, fmt, encoding, extra_opt)

	def _save_archive(self, data, fmt, encoding='utf-8', opt=None) :
		# print("Path._save_archive({0})".format(fmt))

		if isinstance(data, bytes) :
			b_data = data
			is_text = False
		else :
			b_data = data.encode(encoding)
			is_text = True

		if fmt == '.gz' :
			z_data = gzip.compress(b_data, compresslevel=9)
			self.write_bytes(z_data)
		elif fmt == '.xz' :
			z_data = lzma.compress(b_data, preset=9 | lzma.PRESET_EXTREME)
			self.write_bytes(z_data)
		elif fmt == '.br' :
			import brotli
			z_data = brotli.compress(b_data, mode=(brotli.MODE_TEXT if is_text else brotli.MODE_GENERIC))
			self.write_bytes(z_data)
		elif fmt == '.lz' :
			cmd = ['lzip', '--best', '--force', '--output', self.with_suffix('')]
			ret = subprocess.run([str(i) for i in cmd], input=b_data)
		else :
			self.write_bytes(b_data)

	def _save_filter(self, data, fmt, opt=None) :
		# print("Path._save_filter({0}, {1}, {2})".format(type(data), fmt, opt))
		if opt is None :
			opt = dict()

		if fmt == '.tsv' :
			return cc_pathlib.filter.tsv.tsv_to_str(data, ** opt)
		elif fmt == '.json' :
			return cc_pathlib.filter.cc_json.json_to_str(data, ** opt)
		elif fmt == '.pickle' :
			return cc_pathlib.filter.cc_pickle.pickle_to_str(data, ** opt)
		elif fmt == '.npy' :
			return cc_pathlib.filter.cc_numpy.numpy_to_bytes(data, ** opt)
		elif fmt == '.arr' :
			s_lst = self.suffixes
			for k in cc_pathlib.filter.cc_array.array_type_to_code_map :
				if f'.{k}' in s_lst :
					if cc_pathlib.filter.cc_array.array_type_to_code_map[k] == data.typecode :
						return cc_pathlib.filter.cc_array.array_to_bytes(data)
			raise ValueError("Error with typecode")
		else :
			return data

	# def hardlink_to(self, target) : implemented in the base class from 3.10
	# 	""" self is the source we link FROM, target is the name TO (ie. self is created) """
	# 	if target.is_file() :
	# 		os.link(target, self)
	# 	else :
	# 		raise ValueError("hardlink target must be a file")

	@property
	def fname(self) :
		# return the name of the file without all the extensions if many
		return self.name.split('.')[0]

	@property
	def fsuffix(self) :
		# return all the extensions if many
		return ''.join(self.suffixes)

	def dedup(self, * pattern_lst) :
		if self.is_dir() :
			for pattern in pattern_lst :
				cc_pathlib.tool.dedup._dedup_size_pass(self, pattern)
		else :
			raise ValueError("Path() must be a directory")

	def _run_setup(self, cmd_args, other_args, ** default_args) :
		cwd = self.resolve()

		cmd_header = '\x1b[44m{0} {1}{2} $\x1b[0m '.format(
			socket.gethostname(),
			"{0} ".format(Path(* cwd.parts[-3:])),
			datetime.datetime.now().strftime('%H:%M:%S')
		)

		cmd_line = list()
		for cmd in cmd_args :
			if isinstance(cmd, dict) :
				for k, v in cmd.items() :
					cmd_line.append('--' + str(k))
					cmd_line.append(str(v))
			else :
				cmd_line.append(str(cmd))

		print(cmd_header + ' '.join(cmd_line))

		return cmd_header, cmd_line, {'cwd': cwd,} | default_args | other_args

	def run(self, * cmd_args, ** other_args) :
		cmd_header, cmd_line, call_args = self._run_setup(cmd_args, other_args, capture_output=True, text=True)
		return subprocess.run(cmd_line, ** call_args)

	def run_verbose(self, * cmd_args, ** other_args) :
		cmd_header, cmd_line, call_args = self._run_setup(cmd_args, other_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
		with subprocess.Popen(cmd_line, ** call_args) as proc :
			if proc.stdout:
				for line in proc.stdout:
					sys.stdout.write(line)
					sys.stdout.flush()
		return proc.returncode

	def run_background(self, * cmd_args, ** other_args) :
		cmd_header, cmd_line, call_args = self._run_setup(cmd_args, other_args)
		subprocess.Popen(cmd_line, ** call_args)
			
	def __hash__(self) :
		import hashlib
		import base64
		hsh = hashlib.blake2b(str(self.resolve()).encode('utf8'), digest_size=24, salt=b"cc_pathlib")
		return base64.urlsafe_b64encode(hsh.digest()).decode('ascii')

		# file_hasher = blake3(max_threads=blake3.AUTO)
		# file_hasher.update_mmap("/big/file.txt")
		# file_hash = file_hasher.digest()
		
	def iter_on_suffix(self, * suffix_lst, skip_hidden_dir=True, follow_symlink_dir=False, yield_symlink_file=False, case_insensitive=True) :
		"""
			advanced reccursive iterator on files contained in a directory
			implemented without recursion
		"""

		if case_insensitive :
			suffix_set = {suffix.lower() for suffix in suffix_lst}
		else:
			suffix_set = set(suffix_lst)

		root_pth = self.resolve()
		assert root_pth.is_dir(), f"{root_pth} is not an existing dir"
		root_que = collections.deque()
		root_que.append(root_pth)

		while root_que :
			root_dir = root_que.popleft()
			for sub in root_dir :
				if sub.is_file() :
					if not yield_symlink_file and sub.is_symlink() :
						continue
					if suffix_set :
						for suffix in suffix_set :
							if sub.name.endswith(suffix) or ( case_insensitive and sub.name.lower().endswith(suffix) ) :
								yield sub
					else :
						yield sub
				elif sub.is_dir() :
					if sub.name.startswith('.') and skip_hidden_dir :
						continue
					if not follow_symlink_dir and sub.is_symlink() :
						continue
					root_que.append(sub)

	def is_same(self, other) :
		""" return true if both files have the same st_ino and st_dev
		which is true for hardlinked files
		"""
		s_stat, o_stat = self.stat(), other.stat()
		return (s_stat.st_ino, s_stat.st_dev) == (o_stat.st_ino, o_stat.st_dev)

	def is_identical(self, other) :
		# Check if the file sizes are the same
		s_stat, o_stat = self.stat(), other.stat()

		if (s_stat.st_ino, s_stat.st_dev) == (o_stat.st_ino, o_stat.st_dev) :
			raise ValueError("they are not identical, they are the same file")

		if s_stat.st_size != o_stat.st_size :
			return False

		# Open the files in binary mode
		with self.open('rb') as sfid, other.open('rb') as ofid :
			with (
				mmap.mmap(sfid.fileno(), 0, access=mmap.ACCESS_READ) as smap, 
				mmap.mmap(ofid.fileno(), 0, access=mmap.ACCESS_READ) as omap
			) :

			return smap == omap
