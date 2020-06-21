#-*-coding: utf-8-*-
#!/bin/sh

'''
# @file		the easymake-yaml script written by python3
# @date 	2020-06
# @author	Stephen-Zhang(github.com/stark-zhang)
# @lic		MIT and all right reserved
'''

import yaml as yml
from pathlib import Path as path

'''
# @brief	Exceptions while processing easymake configuration
'''
class TemporaryDirException(Exception):
	def __init__(self, exception_no: int, details: str):
		self.details = details
		self.exception_no = exception_no
		return

class utility:
	# the general utility class for path processing
	def __init__(self, dir: str):
		# initialize the utility to 
		pass

	def __is_dir(self, target_dir: path):
		# 
		return target_dir.is_dir() and target_dir != path('.svn') \
			and target_dir != path('.git') and target_dir != path(".vscode")

	def copy_path_structure(self, target_dir: str):
		# check the directory spcified by 'int' property, make it if the dir does not exist, and
		# copy the folder structure except 'int' value where the easymake configuration is
		target_dir = path(target_dir)

		if target_dir.exists():
			if not self.__is_dir():
				raise TemporaryDirException()

class makefile_generator:
	# the makefile generator class
	def __init__():
		# makefile generator initialized
		self.mkf_path = path('./Makefile')	# the path to Makefile
		with self.mkf_path.open(mode='w', encoding='UTF-8') as self.mkf:
			pass

