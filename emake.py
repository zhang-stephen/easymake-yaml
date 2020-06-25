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
import sys, os

'''
# @brief	some variables
'''
options = [
		'f:o:cb:e:nh?v',
		['file=', 'output=', 'check-complier', 'build=', 'exec=', 'just-print', 'help', 'version'],
]	

'''
# @brief	Exceptions while processing easymake configuration
'''
class EasyMakeBaseException(Exception):
	# the baisc exception class for easymake-yaml
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
	# will be raised when cannot find default configuration files
	def __repr__(self):
		return self.format('DefaultConfigNotExistException')

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

def check_command_exists(os_name: str, command: str):
	# check spcified command exists or not in the PATH
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
