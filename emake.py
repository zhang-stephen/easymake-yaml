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
from getopt import gnu_getopt
import sys, os, re

'''
# @brief	some variables
'''
options = [
		'f:o:cb:e:nh?v',
		['file=', 'output=', 'check-complier', 'build=', 'exec=', 'just-print', 'help', 'version'],
]

version = '0.0.1-alpha'

'''
# @brief	Exceptions while processing easymake configuration
'''
class EasyMakeBaseException(Exception):
	'''
	The basic exception class for easymake-yaml
	'''
	def __init__(self, excep_no: int, details: str):
		self.details = details
		self.excep_no = excep_no

	def format(self, excep_name: str) -> str:
		return  excep_name + ': '+ str(self.excep_no) + ', ' + self.details

class TemporaryDirException(EasyMakeBaseException):
	# the error about temporary folder
	def __repr__(self):
		return self.format('TemporaryDirException')

class DefaultConfigNotExistException(EasyMakeBaseException):
	'''
	will be raised when cannot find default configuration files
	'''
	def __repr__(self):
		return self.format('DefaultConfigNotExistException')

class CommandStringIllegalException(EasyMakeBaseException):
	'''
	will be raised when compiler deduced failed
	'''
	def __repr__(self):
		return self.format('CommandStringIllegalException')

class default_complier:
	'''
	A class to store information of property "compiler"
	'''
	class command:
		'''
		A sub-class to store sub-property 'command'
		'''
		def __init__(self):
			'''
			default value from GNU Compiler Collections(gcc.gnu.org)
			'''
			self.cc = 'gcc'
			self.cxx = 'g++'
			self.ar = 'ar'

		def cc_praser(self, property: str, value: str):
			'''
			use one of sub-property(cc, cxx, ar) to deduce others command, via regex
			do not deduce other commands from ar
			'''
			# the real filename of command may be started with '/' and must be ended without '/'.
			# so we can use this rule to find where the real command is and deduce other commands

			# deduce from property 'cc'
			if property == 'cc':
				self.cc = value
				if 'gcc' in self.cc:
					pattern = self._cc_re_compile('gcc')
					matches = re.search(pattern, self.cc)
					if matches is not None:
						# get the correct sub-string which may be start with '/'
						cc_to_match = matches.group(0).replace('gcc', 'g++')
						ar_to_match = matches.group(0).replace('gcc', 'ar')

						# replace them, and as same as following processes
						self.cxx = re.sub(pattern, cc_to_match, self.cc)
						self.ar = re.sub(pattern, ar_to_match, self.cc)

				if 'clang' in self.cc:
					pattern = self._cc_re_compile('clang')
					matches = re.search(pattern, self.cc)
					if matches is not None:
						cc_to_match = matches.group(0).replace('clang', 'clang++')
						ar_to_match = matches.group(0).replace('clang', 'llvm-ar')
						self.cxx = re.sub(pattern, cc_to_match, self.cc)
						self.ar = re.sub(pattern, ar_to_match, self.cc)

				if matches is None:
					raise CommandStringIllegalException(11, "Cannot find value of property \'%s\'" % property)
				
			# deduce from property 'cxx'
			if property == 'cxx':
				self.cc = value
				if 'g++' in self.cc:
					pattern = self._cc_re_compile('g++')
					matches = re.search(pattern, self.cc)
					if matches is not None:
						cc_to_match = matches.group(0).replace('g++', 'gcc')
						ar_to_match = matches.group(0).replace('g++', 'ar')
						self.cxx = re.sub(pattern, cc_to_match, self.cc)
						self.ar = re.sub(pattern, ar_to_match, self.cc)

				if 'clang++' in self.cc:
					pattern = self._cc_re_compile('clang++')
					matches = re.search(pattern, self.cc)
					if matches is not None:
						cc_to_match = matches.group(0).replace('clang++', 'clang')
						ar_to_match = matches.group(0).replace('clang++', 'llvm-ar')
						self.cxx = re.sub(pattern, cc_to_match, self.cc)
						self.ar = re.sub(pattern, ar_to_match, self.cc)

				if matches is None:
					raise CommandStringIllegalException(11, "Cannot find value of property \'%s\'" % property)

		def _cc_re_compile(self, command_to_match: str) -> str:
			'''
			a private function to get a regex string
			'''
			return r'\/?' + command_to_match + r'((?!\/).)*$'

	def __init__(self):
		self.command = self.command()			# sub-property: command
		self.flags = None						# sub-property: flags(for C/C++ Compiler)
		self.cflags = None						# sub-property: flags for c compiler
		self.ccflags = None						# sub-property: flags for c++ compiler
		self.arflags = None						# sub-property: flags archive tool
		self.ldflags = None						# sub-property: flags ld
		self.libpath = None						# sub-property: the path to search libraries(-L)
		self.hpath = None						# sub-property: the path to search headers(-i)
		self.links = None						# property in global: the libraries will be linked(-l)
		self.headers = None						# property in global: the headers will be included(-I)


class extra_compiler:
	'''
	A class to store information of property "extraCompiler"
	'''
	def __init__(self):
		pass

class custom_target:
	'''
	A class to store information of property "customTarget"
	'''
	# TODO: this class will be defined in the future
	pass

class Makefile:
	'''
	to receive infomation of yaml praser, and generate Makefile
	'''
	def __init__(self):
		pass

'''
# @brief	some functions
'''
def find_default_configuration() -> str:
	'''	
	search the default configuration file named <easymake.yml> or <emake.yml>
	'''
	default_config = path('./easymake.yml')

	if default_config.exists() and default_config.is_file():
		return str(default_config)

	default_config = path('./emake.yml')

	if default_config.exists() and default_config.is_file():
		return str(default_config)

	raise DefaultConfigNotExistException(0, "Error: Cannot find the default configuration")

def check_command_exists(os_name: str, command: str) -> bool:
	'''
	check spcified command exists or not in the PATH
	'''
	if '/' in command or '\\' in command:
		# if '/' or '\' is in command, it may be in absolute path
		return path(command).exists()

	else:
		# in MS Windows, the spliter of PATH is ';', in Unix-like, it's ':'
		path_spliter = ';' if os_name == 'nt' else ':'

		# and, `.exe` is neccessery suffix of complete command in MS Windows
		command += '.exe' if os_name == 'nt' else ''

		# search command in the PATH
		for p in os.environ['PATH'].split(path_spliter):
			if (path(p) / command).exists():
				return True

def copy_root_structure(output_dir: str):
	'''
	copy structure of project root to output directory(the value of property 'int')
	'''
	pass

def usage():
	print("Usage: %s [OPTIONS]..." % sys.argv[0])

# Execute this script in shell
if __name__ == '__main__':
	try:
		# prase the CLI Options
		opts, args = gnu_getopt(sys.argv[1:], options[0], options[1])

	except EasyMakeBaseException as e:
		print(repr(e))
	
	except Exception as e:
		print(repr(e))

# EOF
