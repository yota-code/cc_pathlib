
def CacheCache
		if cache :
			if isinstance(cache, str) :
				cache = Path(cache)
			if isinstance(cache, Path) :
				self.cache_pth = cache.with_suffix('.pickle')
			else :
				txt = str(self.base_dir).encode('utf8')
				hsh = hashlib.blake2b(txt, digest_size=24, salt=b"cc")
				key = base64.urlsafe_b64encode(hsh.digest()).decode('ascii')
				cache_dir = (Path('/tmp') / f"pathlib_{key}").make_dirs('private')
				self.cache_pth = cache_dir / self._config['_cache_name']

			if self.cache_pth.is_file() :
				self.mtime_map = self.cache_pth.load()
			else :
				self.mtime_map = dict()
		else :
			# cache disabled completely
			self.cache_pth = None
