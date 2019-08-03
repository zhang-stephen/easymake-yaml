#!/usr/bin/python
# -*- coding: UTF-8 -*-

'''
# emake.py: easy-make tool based on yaml, running with Python 3.6.2 and later
# Copyright (C) 2019 Stephen-Zhang, All Right Reserved
# License: MIT(https://opensource.org/licenses/MIT)
'''
# import the neccessry libraries
import yaml
import os
import time
import argparse as ap
import sys
import subprocess as sbp
import re
import pathlib

# Decorator for ERR Handler
def err_handler(printdebug=True):

	def inner1(f):

		def inner2(*args, **kwargs):
			try:
				res = f(*args, **kwargs)

			except Exception as err:
				if printdebug:
					# import sys
					info = sys.exc_info()[2].tb_frame.f_back
					temp = "file:{}\nline:{}\tfunction:{}\terror:{}"
					print(temp.format(info.f_code.co_filename, info.f_lineno, f.__name__, repr(err)))
					res = None

					exit() # if error ocurred, exit

			return res    

		return inner2

	return inner1

# Decorator for exception handler
def excp_handler(printdebug=True):

	def inner1(f):

		def inner2(*args, **kwargs):
			try:
				res = f(*args, **kwargs)

			except Exception as err:
				if printdebug:
					# import sys
					info = sys.exc_info()[2].tb_frame.f_back
					temp = "file:{}\nline:{}\tfunction:{}\terror:{}"
					print(temp.format(info.f_code.co_filename, info.f_lineno, f.__name__, repr(err)))
					res = None

			return res    

		return inner2

	return inner1

# the class to parse makefile yaml
class emkfile:

	'''
	# @brief	default constructor
	# @param 	fpath
	#				the path of emakefile
	# @retval	none
	'''
	@err_handler()
	def __init__(self, fpath):
		# get emakefile path(folder)
		self.fpath = pathlib.Path(fpath)

		# define some tags
		self.__critical_tags = ('mode', 'src',)
		self.__header = 'proj'

		# Read the emakefile
		self.yaml_read(fpath)

		# Verification of file header
		if self.__header not in self.content:
			raise Exception('Error: Wrong File Header')
	
	'''
	# @brief	read yaml
	# @param 	fpath
	#				as same as constructor
	# @retval	none
	'''
	@err_handler()
	def yaml_read(self, fpath):
		cont = open(fpath, 'r', encoding = 'utf-8')
		self.content = yaml.safe_load(cont.read())
		cont.close()

	'''
	# @brief	parse the necessary tags
	# @param 	tag
	#				string to parse
	# @retval	none
	'''
	@err_handler()
	def tag_critical(self, tag):
		if tag in self.content[self.__header]:
			return self.content[self.__header][tag]
		else:
			raise Exception("Error: Missing critical tags: " + tag)

	'''
	# @brief	parse the unnecessary tags
	# @param 	tag
	#				string to parse
	# @retval	none
	'''
	def tag_normal(self, tag):
		if tag in self.content[self.__header]:
			return self.content[self.__header][tag]
	
	'''
	# @brief	reload of operator []
	# @param 	index
	#				index to access
	# @retval	list
	'''
	# Operator [] Reload
	def __getitem__(self, index):
		if index in self.__critical_tags:
			ret = self.tag_critical(index)
		else:
			ret =  self.tag_normal(index)

		if type(ret) is not list:
			return [ret]
		else:
			return ret
	
	'''
	# @brief	get paths of sub-emakefile
	# @param	none
	# @retval	list or None
	'''
	def get_subproj(self):
		if 'subpath' in self.content[self.__header]:
			return  self['subpath']
		else:
			return None
	
	'''
	# @brief	get list of source files
	# @param 	none
	# @retval	list
	'''
	def get_srcfiles(self):
		return self['src']

class subemkfile(emkfile):
	'''
	# @brief	default constructor of subemkfile class
	# @param 	fpath
	#				the path of subpriority emakefile
	# @retval	none
	'''
	@err_handler()
	def __init__(self, fpath):
		# get emakefile path(folder)
		self.fpath = pathlib.Path(fpath)

		# define some tags
		self.__critical_tags = ('src',)
		self.__header = 'subproj'

		# Read the emakefile
		self.yaml_read(fpath)

		# Verification of file header
		if self.__header not in self.content:
			raise Exception('Error: Wrong File Header')

def main():

	# build a most-prority project
	xProject = emkfile(sys.argv[1])

	# change the workspace
	if xProject.fpath is not os.getcwd():
		os.chdir(xProject.fpath.parent)

	# generate list of Subprority Projects
	subProjects = [subemkfile(x) for x in xProject.get_subproj()]
	print(subProjects[0].fpath)

	# pathlib test
	print(pathlib.Path(r'../emake.py').is_file())
		
# For Test Case
if __name__ == "__main__":
	main()

# EOF
