#!/usr/bin/en python3

import json
import datetime
import pathlib

class JSONCustomEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, set) :
			try :
				return sorted(obj)
			except TypeError :
				return list(obj)
		elif isinstance(obj, datetime.datetime) :
			return obj.isoformat()
		elif isinstance(obj, pathlib.Path) :
			return str(obj)
		else:
			return json.JSONEncoder.default(self, obj)

class _JSON_config_CONTEXT(dict) :
	def __init__(self, pth) :
		self.pth = pth

	def __enter__(self) :
		if not self.pth.is_file() :
			dict.__init__(self)
		else :
			dict.__init__(self, self.pth.load())
		return self
	
	def sync(self) :
		self.pth.save(self, filter_opt={"verbose":True})

	def __exit__(self, exc_type, exc_value, traceback) :
		self.pth.save(self, filter_opt={"verbose":True})


def json_from_str(txt) :
	return json.loads(txt)

def json_to_str(obj, verbose=False) :
	p = {
		'ensure_ascii' : False,
		'sort_keys' : True,
		'cls' : JSONCustomEncoder
	}
	if verbose :
		p['indent'] = '\t'
	else :
		p['separators'] = (',', ':')
	return json.dumps(obj, ** p)
