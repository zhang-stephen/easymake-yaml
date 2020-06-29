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
from getopt import getopt
from enum import Enum
import sys, os, re

'''
# @brief	Exceptions while processing easymake configuration
'''

class SingleInstanceMetaClass(type):
	'''
	the metaclass to implement single-instance mode(without thread lock)
	'''
	def __call__(cls, *args, **kwargs):
		if not hasattr(cls, "_instance"):
			cls._instance = super(SingleInstanceMetaClass, cls).__call__(*args, **kwargs)
		return cls._instance

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

class CLIOptionOrArgumentException(EasyMakeBaseException):
	'''
	will be raised when CLI option is illegal
	'''
	def __repr__(self):
		return self.format("CLIOptionOrArgumentException")

class OptionState:
	'''
	A class to receive CLI Options Value(using static member variables)
	'''
	flag_check_compiler = False
	flag_just_print = False
	flag_log = False
	flag_update_self = False
	flag_call_make = False 				# call make in the console after makefile generating or not
	config_path = ''
	mkfile_path = './Makefile'
	mk_exec = 'make'					# the command of GNU make(default)/LLVM make
	mk_jobs = 1							# the -j options used by make
	
class Command:
	'''
	A private class to store sub-property 'command' for 'compiler'
	'''
	def __init__(self):
		'''
		default value from GNU Compiler Collections(gcc.gnu.org)
		'''
		self.cc = 'gcc'
		self.cxx = 'g++'
		self.ar = 'ar'

	def cc_deduce(self, property: str):
		'''
		use one of sub-property(cc, cxx, ar) to deduce others command, via regex
		do not deduce other commands from ar
		'''
		# the real filename of command may be started with '/' and must be ended without '/'.
		# so we can use this rule to find where the real command is and to deduce other commands

		# deduce from property 'cc'
		if property == 'cc':
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

class DefaultCompiler(metaclass = SingleInstanceMetaClass):
	'''
	A class to store information of property "compiler"
	'''
	def __init__(self):
		# the followings are property definitions, they will be declerated as such [primary, prased, bool],
		# and the 'primary' is the primary data from .yml, 'prased' is the data after processing(will be written into Makefile), 
		# and 'bool' is to indicate if this attribute exists or not(the g_ means this property is in root scope)
		self.command = [None, None, False]					# sub-property: command
		self.flags = [None, None, False]					# sub-property: flags(for C/C++ Compiler)
		self.cflags = [None, None, False]					# sub-property: flags for c compiler
		self.ccflags = [None, None, False]					# sub-property: flags for c++ compiler
		self.arflags = [None, None, False]					# sub-property: flags archive tool
		self.ldflags = [None, None, False]					# sub-property: flags ld
		self.libpath = [None, None, False]					# sub-property: the path to search libraries(-L)
		self.hpath = [None, None, False]					# sub-property: the path to search headers(-I)
		self.links = [None, None, False]					# property in global: the libraries will be linked(-l)
		self.headers = [None, None, False]					# property in global: the headers will be included(-i)

class ExtraCompiler:
	'''
	A class to store information of property "extraCompiler"
	this class will be wirtten into Makefile as explicit rules
	'''
	def __init__(self,):
		pass

class CustomTarget:
	'''
	A class to store information of property "customTarget"
	'''
	# TODO: this class will be defined in the future
	pass

class Makefile:
	'''
	to receive infomation of yaml praser, and generate Makefile
	if property 'subpath' exists, we need serveral of this class to store and prase
	'''
	def __init__(self, config_data: dict):
		self.config = config_data						# primary data from *.yml file
		self.mkfile_cache = []							# the mkfile generator cache, will be written into Makefile after prasing complete
		# the followings are property definitions, they will be declerated as such [primary, prased, bool],
		# and the 'primary' is the primary data from .yml, 'prased' is the data after processing(will be written into Makefile), 
		# and 'bool' is to indicate if this attribute exists or not(the g_ means this property is in root scope)
		self.r_sources = [None, None, False] 
		self.r_default_compiler = [None, None, False]
		self.r_int_dir = [None, './', False]			# compiler output dir, the ./(the project root dir) is in the default
		self.r_subpath = [None, None, False]			# in the default, the 'subpath' does not exist and not need to be prased
		self.r_extra_compile = [[], [], False]			# property 'extraCompiler' will be put in a list
		self.r_platform = [None, None, False]			# property 'platform' to assitant some operations
		self.r_output = [None, 'main', True]			# property 'output' to sepcify output filename, default is 'main'
		self.r_mode = ['exec', None, False]				# property 'output' to sepcify compiling mode

	def compile_target_praser(self):
		'''
		to get compiling mode and target
		'''
		# read primary data 
		if 'platform' in self.config:
			self.r_platform[0] = self.config['platform']
			self.r_platform[2] = True

		if 'mode' in self.config:
			self.r_mode[0] = self.config['mode']
			self.r_mode[2] = True

		if 'output' in self.config:
			self.r_output[0] = self.config['output']
			self.r_output[2] = True

		if 'int' in self.config:
			self.r_int_dir[0] = self.config['int']
			self.r_int_dir[2] = True

		# prasing the target filename
		if self.r_mode[0] == 'exec' and self.r_platform == 'win32':
			self.r_output[1] = self.r_output[0] + '.exe'

		if self.r_mode[0] == 'lib':
			self.r_output[1] = 'lib' + self.r_output[0] + '.a'

		if self.r_mode[0] == 'dll':
			if self.r_platform[0] == 'win32':
				self.r_output[1] = 'lib' + self.r_output[0] + '.a.dll'
			else:
				self.r_output[1] = 'lib' + self.r_output[0] + '.so'

		# copy project root path structure
		if path(self.r_int_dir[0]) not in (path('./'), path('.vscode'), path('.git'), path('.svn')):
			utility.copy_root_structure(self.r_int_dir[0])

	def default_compiler_praser(self):
		'''
		take out info about default compiler from primary data
		'''
		# confirm whether r_default_compiler shoule be initialized
		_requests = [_key in self.config.keys() for _key in ['links', 'headers' 'compiler']]
		if True in _requests:
			self.r_default_compiler[2] = True
			self.r_default_compiler[0] = DefaultCompiler()

			# take out effective data
			if 'links' in self.config.keys():
				self.r_default_compiler[0].links[0] = self.config['links']
				self.r_default_compiler[0].links[1] = True

			if 'headers' in self.config.keys():
				self.r_default_compiler[0].headers[0] = self.config['headers']
				self.r_default_compiler[0].headers[1] = True

			if 'compiler' in self.config.keys():
				# prase sub-property of 'compiler'
				if 'libs' in self.config['compiler']:
					self.r_default_compiler[0].libs[0] = self.config['compiler']['libs']
					self.r_default_compiler[0].libs[1] = True

				if 'inc' in self.config['compiler']:
					self.r_default_compiler[0].hpath[0] = self.config['compiler']['inc']
					self.r_default_compiler[0].hpath[1] = True

				if 'command' in self.config['compiler']:			# special 
					self.r_default_compiler[0].command[0] = Command()
					self.r_default_compiler[0].command[1] = True

					_requests = {_key: (_key in self.config['compiler']['command'].keys()) for _key in ('cc', 'cxx', 'ar')}
					if _requests['cc']:
						self.r_default_compiler[0].command[0].cc = self.config['compiler']['command']['cc']

					if _requests['cxx']:
						self.r_default_compiler[0].command[0].cxx = self.config['compiler']['command']['cxx']

					if _requests['ar']:
						self.r_default_compiler[0].command[0].ar = self.config['compiler']['command']['ar']

					# if there is only 'cc' or 'cxx, then deduce other command
					if _requests['cc'] and not _requests['cxx'] and not _requests['ar']:
						self.r_default_compiler[0].command[0].cc_deduce('cc')

					if _requests['cxx'] and not _requests['cc'] and not _requests['ar']:
						self.r_default_compiler[0].command[0].cc_deduce('cxx')

			utility.log('cc: %s, cxx: %s, ar: %s' % (self.r_default_compiler[0].command[0].cc, self.r_default_compiler[0].command[0].cxx, self.r_default_compiler[0].command[0].ar))

		else:
			return

'''
# @brief	some functions
'''
class utility:
	'''
	a class including all utility(tool) functions, 
	'''

	options = [
		'lf:o:cb:e:nh?v',
		['log', 'file=', 'output=', 'check-complier', 'build=', 'exec=', 'just-print', 'help', 'version'],
	]

	_version = '0.0.1-alpha'

	@staticmethod
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

	@staticmethod
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
	
	@staticmethod
	def copy_root_structure(output_dir: str):
		'''
		copy structure of project root to output directory(the value of property 'int')
		'''
		# scan all sub-directories in the root path of project
		sub_dirs = [str(x) for x in list(path('./').glob('**'))]

		# delete the .git/.svn/.vscode and the out_dir itself
		sub_dirs = filter(lambda x : not (x.startswith('git') or x.startswith('.svn') or x.startswith('.vscode')) and x not in ('.', output_dir), sub_dirs)
		
		# build TRIE and do DFS traversing
		# use the TRIE to find out longest prefixes, and use mkdir command to build them in output_dir
		
	
	@staticmethod
	def usage():
		print("Usage: %s [OPTIONS]..." % sys.argv[0])

	@staticmethod
	def version():
		print(utility._version)

	@staticmethod
	def log(*values):
		'''
		a function to print content of param detail and other information
		'''
		if OptionState.flag_log:
			print(values)

# Execute this script in shell
if __name__ == '__main__':
	try:
		# try to prase the CLI Options

		# if there's no cli option, print help info and exit
		if len(sys.argv) <= 1:
			utility.usage(), sys.exit(0)
		
		# prase cli options
		opts, args = getopt(sys.argv[1:], utility.options[0], utility.options[1])

		for opt, value in opts:
			# print version info on the console
			if opt in ('v', '-v', '--version'):
				utility.version(), sys.exit(0)

			# print usage info on the console
			if opt in ('h', '-h', '--help'):
				utility.usage(), sys.exit(0)

			# prase CLI Options and store them to class
			if opt in ('f', '-f', '--file'):
				OptionState.config_path = value

			if opt in ('o', '-o', '--output'):
				OptionState.mkfile_path = value

			if opt in ('e', '-e', '--exec'):
				OptionState.mk_exec = value

			if opt in ('b', '-b', '--build'):
				OptionState.flag_call_make = True
				OptionState.mk_jobs = int(value)
			
			if opt in ('l', '-l', '--log'):
				OptionState.flag_log = True

			if opt in ('n', '-n', '--just-print'):
				OptionState.flag_just_print = True

			if opt in ('c', '-c', '--check-compiler'):
				OptionState.flag_check_compiler = True
	
		# CLI Options prasing is complete, then configuration file prasing will be started

		# read the .yml and transform it to python structure
		# if '-f' or '--file' was read in CLI, the default configuration path will be re-written by user input
		# the default encoding of .yml is UTF-8
		true_config_path = utility.find_default_configuration() if OptionState.config_path == '' else OptionState.config_path
		with open(true_config_path, encoding='UTF-8', mode='r') as f:
			primary_config_data = yml.safe_load(f)

		# change cwd/pwd accroding to true_config_path
		os.chdir(path(true_config_path).parent)
		utility.log("Info: Current Working Folder is ", os.getcwd())

		# instantiate class Makefile to receive and prase configuration
		rx_mkfile_generator = Makefile(primary_config_data) 

		# prase the primary configuration data
		rx_mkfile_generator.default_compiler_praser()

	except EasyMakeBaseException as e:
		print(repr(e))
	
	except Exception as e:
		print(repr(e))

# EOF
