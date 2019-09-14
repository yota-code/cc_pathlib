#!/usr/bin/env python3

import datetime
import io
import json
import os
import pickle
import tempfile
import shutil
import subprocess

import sys
import lzma, bz2, gzip

try :
	import brotli
	_imported_brotli = True
except :
	_imported_brotli = False

from cc_pathlib.path import Path