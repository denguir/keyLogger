# from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# browser = webdriver.Firefox()
# print (browser.current_url)
import win32gui
import time

def get_active_window_hwnd():
    return win32gui.GetForegroundWindow()


if __name__ == '__main__':
	time.sleep(2)
	hwnd = get_active_window_hwnd()
	b = win32gui.GetWindowText(hwnd)
	print(b)