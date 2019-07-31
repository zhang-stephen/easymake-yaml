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
class makefile_yaml:
	# Data Members
	content = None,		# the yaml object to parse
	cMode = None,		# compilation mode
	cOutName = None,	# filename of binary file
	cSources = [],		# source files
	cIncludes = [],		# include paths
	cLibPath = [],		# extra library paths
	cLibLink = [],		# libraries to directly link
	cISA = [],			# compiler flag to specify ISA
	cFlags = [],		# other flags to compiler
	cSubpath = [],		# Full path of Sub-Makefile
	cTempPath = None,	# path to store temporary files
	cWorkPath = None,	# the work path(pwd/cwd)
	cExcmd = None		# extra command would be executed before compiling
	

	# Methods of compiler yaml class
	@err_handler()
	def __init__(self, fpath):
		cont = open(fpath, 'r', encoding = "utf-8")

		self.content = yaml.safe_load(cont.read())
		self.cWorkPath = os.getcwd()

		cont.close()

	@err_handler()
	def parse_mode(self):
		if 'mode' in self.content['proj']:
			self.cMode = self.content['proj']['mode']
		else:
			raise Exception("Error: No Compilation Mode Spcified!")

	def parse_output(self):
		if 'out' in self.content['proj']:
			self.cOutName = self.content['proj']['out']

	@err_handler()
	def parse_sources(self):
		if 'src' in self.content['proj']:
			self.cSources = self.content['proj']['src']
		else:
			raise(Exception("Error: No Source Files"))

	def parse_includes(self):
		if 'inc' in self.content['proj']:
			self.cIncludes = self.content['proj']['inc']
	
	def parse_libpath(self):
		if 'lib' in self.content['proj']:
			self.cLibPath = self.content['proj']['lib']

	def parse_liblink(self):
		if 'link' in self.content['proj']:
			self.cLibLink = self.content['proj']['link']
	
	def parse_isa(self):
		if 'isa' in self.content['proj']:
			self.cISA = self.content['proj']['isa']
	
	def parse_flags(self):
		if 'flags' in self.content['proj']:
			self.cFlags = self.content['proj']['flags']
	
	def parse_subpath(self):
		if 'subpath' in self.content['proj']:
			self.cSubpath = self.content['proj']['subpath']

	def parse_excmd(self):
		if 'excmd' in self.content['proj']:
			self.cExcmd = self.content['proj']['excmd']

	def parser(self):
		# parse all key in yaml
		self.parse_mode()
		self.parse_output()
		self.parse_sources()
		self.parse_includes()
		self.parse_liblink()
		self.parse_libpath()
		self.parse_isa()
		self.parse_flags()
		self.parse_subpath()
		self.parse_excmd()

# The class to parse the extra configuration yaml
# this yaml can override the default settings in emake
class configuration_yaml:

	@err_handler()
	def __init__(self, fpath):
		cont = open(fpath, 'r', encoding = "utf-8")

		self.content = yaml.safe_load(cont.read())
		self.cWorkPath = os.getcwd()

		cont.close()

config = makefile_yaml(sys.argv[1])
config.parser()

# EOF
