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
class EasyMakeBaseException(Exception):
	# the baisc exception class for easymake-yaml
	def __init__(self, excep_no: int, details: str):
		self.details = details
		self.excep_no = excep_no

class TemporaryDirException(EasyMakeBaseException):
	# the error about temporary folder
	def __repr__(self):
		self.excep_id = 'TemporaryDirException'
		return  self.excep_id + ':'+ str(self.excep_no) + ', ' + self.details

class DefaultConfigNotExistException(EasyMakeBaseException):
	# will be raised when cannot find default configuration files
	def __repr__(self):
		self.excep_id = 'DefaultConfigNotExistException'
		return self.excep_id + ':' + str(self.excep_no) + ', ' + self.details

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
			pass

class makefile_generator:
	# the makefile generator class
	def __init__(self):
		# makefile generator initialized
		self.mkf_path = path('./Makefile')	# the path to Makefile
		with self.mkf_path.open(mode='w', encoding='UTF-8') as self.mkf:
			pass

'''
# @brief	some functions
'''
def find_default_configuration() -> str:
	# search the default configuration file named <easymake.yml> or <emake.yml>
	default_config = path('./easymake.yml')

	if default_config.exists() and default_config.is_file():
		return str(default_config)

	default_config = path('./emake.yml')

	if default_config.exists() and default_config.is_file():
		return str(default_config)

	raise DefaultConfigNotExistException(0, "Error: Cannot find the default configuration")


if __name__ == '__main__':
	try:
		print(find_default_configuration())

	except EasyMakeBaseException as e:
		print(repr(e))
