import datetime
import os
import tkinter as tk
import pyttsx3 

engine = pyttsx3.init() 

err='\n\U0000274C ERROR \U0001F605 OCCURED \U0000274C\n'

def openapp(appname):
	if isinstance(appname,str):
		from AppOpener import open
		open(appname)
	else:
		print(err)	

def randict(d):
	import random as r
	nd,l={},[]
	for i in d:
	    l+=[i]
	while True:
		ran=r.randint(0,len(l)-1)
		if len(l)==len(nd):
			break
		if l[ran] not in nd:
			nd[l[ran]]=d[l[ran]]
	return nd	

def FIGlet(string):
	if isinstance(string,str):
		import pyfiglet

		FIGlet = pyfiglet.figlet_format(string)

		return FIGlet
	else:
		print(err)	

def pytoexe(filename,windowed=False,noconsole=True):
	if isinstance(filename,str) and isinstance(windowed,bool) and isinstance(noconsole,bool):
		if filename.endswith('.py'):
			import os

			files,cmd=os.listdir(),''

			if noconsole==True:
				cmd+=f'cmd /k pyinstaller {filename} --onefile --noconsole'
			else:
				cmd+=f'cmd /k pyinstaller {filename} --onefile'

			if windowed==True:
				cmd+=f' --windowed'		

			if filename in files:
				os.system(cmd)	
			else:
				print(err)
		else:
			print(err)				
	else:
		print(err)		

class AI:
	def ChatGPT(prompt,api_key,engine="text-davinci-003",max_tokens=1024,temperature=0.7):
		if isinstance(prompt,str) and isinstance(api_key,str):	
			import openai

			openai.api_key = api_key

			completions = openai.Completion.create(engine=engine,prompt=prompt,max_tokens=max_tokens,n=1,stop=None,temperature=temperature)

			return completions.choices[0].text.strip()
		else:
			print(err)

def aboutbattery(string):
	if isinstance(string,str):
		if string=='percentage':
			import psutil

			battery = psutil.sensors_battery()

			percent = str(battery.percent)+'%'

			return percent

		elif string=='charging?':
			import psutil

			battery = psutil.sensors_battery()

			plugged = battery.power_plugged

			return plugged

		else:
			print(err)   
	else:
		print(err)		   

def percent(string):
	if isinstance(string,str):
		percent,number='',''

		for i in string:
			if i=='%':
				break
			else:
				percent+=i	

		string=string[::-1]

		for i in string:
			if i==' ':
				break
			else:
				number+=i

		number=number[::-1]

		return (eval(number) * eval(percent))/100
	else:
		print(err)	

def resizeimg(size,path):
	if isinstance(size,tuple) and isinstance(path,str):
		from PIL import Image

		img = Image.open(path)

		img_resized = img.resize(size)

		fname="Pydule Resize Image -" + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".png"

		img_resized.save(fname)
	else:
		print(err)	

def GetWebHTML(url):
	if isinstance(url,str):
		import requests

		page = requests.get(url)

		return page.text
	else:
		print(err)	

def screenshot(sec=0):
	if isinstance(sec,int) or isinstance(sec,float):
		import pyautogui
		import time as t
		import datetime

		t.sleep(sec)

		myScreenshot = pyautogui.screenshot()

		fname="Pydule Screen Shot -" + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".png"

		myScreenshot.save(fname)
	else:
		print(err)	

def SpeechtoText(string=''):
	if isinstance(string,str):
		import speech_recognition as sr

		r = sr.Recognizer()

		mic = sr.Microphone()

		with mic as source:
			print(string,end='')
			audio = r.listen(source)

		try:
			return r.recognize_google(audio)
		except:
			print(err)
	else:
		print(err)	    

def recintaudio(sec):
	if isinstance(sec,int):
		if sec>0:
			import soundcard as sc
			import soundfile as sf
			import datetime

			out = "Pydule Recorded Internel Audio -" + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".wav"
			rate=48000

			with sc.get_microphone(id=str(sc.default_speaker().name),include_loopback=True).recorder(samplerate=rate) as mic:
				data=mic.record(numframes=rate*sec)
				sf.write(file=out,data=data[:,0],samplerate=rate)
		else:
			print(err)
	else:
		print(err)		

def recscreen():
	import pyautogui
	import cv2
	import numpy as np
	import datetime

	screen_size = pyautogui.size()

	filename = "Pydule Recorded Screen -" + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".avi"

	fourcc = cv2.VideoWriter_fourcc(*"XVID")

	out = cv2.VideoWriter(filename, fourcc, 20.0, screen_size)

	cv2.namedWindow("Recording", cv2.WINDOW_NORMAL)

	cv2.resizeWindow("Recording", 480, 270)

	while True:
		img = pyautogui.screenshot()

		frame = np.array(img)

		frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

		out.write(frame)

		cv2.imshow('Live', frame)

		if cv2.waitKey(1) == ord('q'):
			break

	out.release()
	cv2.destroyAllWindows()

def recmic(sec):
	if isinstance(sec,int):
		import pyaudio
		import wave
		audio=pyaudio.PyAudio()
		stream=audio.open(format=pyaudio.paInt16,channels=1,rate=44100,input=True,frames_per_buffer=1024)
		frames=[]

		fn = "Pydule Recorded Microphone-" + str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".wav"
		for i in range(0,int(44100/1024*(sec+1))):
			data=stream.read(1024)
			frames.append(data)

		stream.stop_stream()
		stream.close()
		audio.terminate()

		sound_file=wave.open(fn,'wb')
		sound_file.setnchannels(1)
		sound_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
		sound_file.setframerate(44100) 
		sound_file.writeframes(b''.join(frames))
		sound_file.close()
	else:
		print(err)	   

def mulmatrix(x,y):
	import numpy as np

	return np.dot(np.array(x), np.array(y))

def swapdict(d):
	if isinstance(d,dict):
		new={}

		for i in d:
			new[d.get(i)]=i

		return new
	else:
		print(err)

def sepstr(st,n):
	if isinstance(st,str) and isinstance(n,int):
		l,s=[],''

		for i in st:
			if len(s)!=n:
				s+=i
			else:
				l+=[s]
				s=''
				s+=i
		if len(s)>0:
			l+=[s]    

		return l 
	else:
		print(err)

def DecryptStr(st,k):
	s,nd='',{}
	keys={'A': '+!=^-&!@', 'B': '&_-@@#^&', 'C': '@+!&@_^+', 'D': '^$%%!$+$', 'E': '-_-&!*_!', 'F': '^^+!=+%=', 'G': '==%&+_#&', 'H': '$%+==_@^', 'I': '=*$$^*#@', 'J': '=#=+$*_=', 'K': '#&##&^+&', 'L': '*+_$#_$%', 'M': '_!&!-^-+', 'N': '%-_^!!@@', 'O': '-+_=#^=!', 'P': '&!^^^#&=', 'Q': '*-&$%%*@', 'R': '!=!*=^^%', 'S': '##!+^$--', 'T': '%-@#%&$+', 'U': '^+&_$_%_', 'V': '!__^!#-!', 'W': '@$-_##--', 'X': '--^!=&@@', 'Y': '=#=@=!=%', 'Z': '_^-@-_=^', 'a': '*&=+&-=^', 'b': '^@+%!!*^', 'c': '$@@_&-@^', 'd': '!&=#--=+', 'e': '!%&%_+!#', 'f': '+_$_$@*^', 'g': '^**%!@!&', 'h': '*&&!=-^-', 'i': '*-^+@=%&', 'j': '+!$#_%**', 'k': '=*$&-_+=', 'l': '_=#_%=#_', 'm': '&+$%$#+*', 'n': '&^^%_+^_', 'o': '&&!$%&@@', 'p': '$-&==^&@', 'q': '_&$_*#_#', 'r': '#!*-!+*@', 's': '#&@&%+!+', 't': '!=_*=+%_', 'u': '#$*=&=!_', 'v': '=^-##+$*', 'w': '^$!_&$$&', 'x': '!==&$$=-', 'y': '@=&!*=$$', 'z': '^_=@_=+-', '1': '-_-@+=^@', '2': '$#=!$_%@', '3': '#-=+$%@$', '4': '=#__%&##', '5': '--&$@^#=', '6': '#@!+_##*', '7': '_%$%#@!$', '8': '*=-*@_^+', '9': '$_^^^+%=', '0': '+@=*$*+-', '!': '-^%@&-@-', '@': '+##=@%_-', '#': '=-$=-_&+', '$': '*%&@%@%*', '%': '=^^%*&&=', '^': '+@#-^!_&', '&': '&--&@!#!', '*': '=@=#*+$@', '_': '^$--@@-&', '=': '@%_*-&=#', '-': '@@-@+@+_', '+': '#-!@!+=@', '(': '#+$^@%%$', ')': '!&^$&-$+', '[': '%_%-#-==', ']': '#^%#_!%%', '`': '#@%+&&*_', '~': '_+@-_&@%', '{': '=%-#+-&!', '}': '_@!!_@+-', '?': '+@%^&&!@', '\\': '!_-$!&-@', "'": '&==++^-^', '/': '_%=*&__&', ';': '+-!=#=#@', ':': '_+*=!$_$', '"': '%_#_%$&=', '<': '%#&+_!!$', '>': '*#+=&*%#', '.': '=&-$#_-$', ',': '%&%-%#_&', ' ': '^=%@=#=!'}
	if isinstance(st,str) and isinstance(k,dict):
		for i in keys:
			if keys[i] in k:
				nd[i]=k[keys[i]]

		nd=swapdict(nd)
		sr=sepstr(st,7)

		for i in range(len(sr)):
			s+=nd[sr[i]]

		return s
	else:
		print(err)    

def EncryptStr(string):
	if isinstance(string,str):
		import random as r
		ex=['!','@','#','$','%','^','&','*','_','=','-','+']
		s,Ans,d,e='',[],{'A': None, 'B': None, 'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'H': None, 'I': None, 'J': None, 'K': None, 'L': None, 'M': None, 'N': None, 'O': None, 'P': None, 'Q': None, 'R': None, 'S': None, 'T': None, 'U': None, 'V': None, 'W': None, 'X': None, 'Y': None, 'Z': None, 'a': None, 'b': None, 'c': None, 'd': None, 'e': None, 'f': None, 'g': None, 'h': None, 'i': None, 'j': None, 'k': None, 'l': None, 'm': None, 'n': None, 'o': None, 'p': None, 'q': None, 'r': None, 's': None, 't': None, 'u': None, 'v': None, 'w': None, 'x': None, 'y': None, 'z': None,'1':None,'2':None,'3':None,'4':None,'5':None,'6':None,'7':None,'8':None,'9':None,'0':None,'!':None,'@':None,'#':None,'$':None,'%':None,'^':None,'&':None,'*':None,'_':None,'=':None,'-':None,'+':None,'(':None,')':None,'[':None,']':None,'`':None,'~':None,'{':None,'}':None,'?':None,'\\':None,'\'':None,'/':None,';':None,':':None,'\"':None,'<':None,'>':None,'.':None,',':None,' ':None},{}
		keys,new={'A': '+!=^-&!@', 'B': '&_-@@#^&', 'C': '@+!&@_^+', 'D': '^$%%!$+$', 'E': '-_-&!*_!', 'F': '^^+!=+%=', 'G': '==%&+_#&', 'H': '$%+==_@^', 'I': '=*$$^*#@', 'J': '=#=+$*_=', 'K': '#&##&^+&', 'L': '*+_$#_$%', 'M': '_!&!-^-+', 'N': '%-_^!!@@', 'O': '-+_=#^=!', 'P': '&!^^^#&=', 'Q': '*-&$%%*@', 'R': '!=!*=^^%', 'S': '##!+^$--', 'T': '%-@#%&$+', 'U': '^+&_$_%_', 'V': '!__^!#-!', 'W': '@$-_##--', 'X': '--^!=&@@', 'Y': '=#=@=!=%', 'Z': '_^-@-_=^', 'a': '*&=+&-=^', 'b': '^@+%!!*^', 'c': '$@@_&-@^', 'd': '!&=#--=+', 'e': '!%&%_+!#', 'f': '+_$_$@*^', 'g': '^**%!@!&', 'h': '*&&!=-^-', 'i': '*-^+@=%&', 'j': '+!$#_%**', 'k': '=*$&-_+=', 'l': '_=#_%=#_', 'm': '&+$%$#+*', 'n': '&^^%_+^_', 'o': '&&!$%&@@', 'p': '$-&==^&@', 'q': '_&$_*#_#', 'r': '#!*-!+*@', 's': '#&@&%+!+', 't': '!=_*=+%_', 'u': '#$*=&=!_', 'v': '=^-##+$*', 'w': '^$!_&$$&', 'x': '!==&$$=-', 'y': '@=&!*=$$', 'z': '^_=@_=+-', '1': '-_-@+=^@', '2': '$#=!$_%@', '3': '#-=+$%@$', '4': '=#__%&##', '5': '--&$@^#=', '6': '#@!+_##*', '7': '_%$%#@!$', '8': '*=-*@_^+', '9': '$_^^^+%=', '0': '+@=*$*+-', '!': '-^%@&-@-', '@': '+##=@%_-', '#': '=-$=-_&+', '$': '*%&@%@%*', '%': '=^^%*&&=', '^': '+@#-^!_&', '&': '&--&@!#!', '*': '=@=#*+$@', '_': '^$--@@-&', '=': '@%_*-&=#', '-': '@@-@+@+_', '+': '#-!@!+=@', '(': '#+$^@%%$', ')': '!&^$&-$+', '[': '%_%-#-==', ']': '#^%#_!%%', '`': '#@%+&&*_', '~': '_+@-_&@%', '{': '=%-#+-&!', '}': '_@!!_@+-', '?': '+@%^&&!@', '\\': '!_-$!&-@', "'": '&==++^-^', '/': '_%=*&__&', ';': '+-!=#=#@', ':': '_+*=!$_$', '"': '%_#_%$&=', '<': '%#&+_!!$', '>': '*#+=&*%#', '.': '=&-$#_-$', ',': '%&%-%#_&', ' ': '^=%@=#=!'},{}
		while True:
			if len(Ans)!=95:
				n=''
				for i in range(7):
					n+=ex[r.randint(0,11)]
				if n not in Ans:
					Ans+=[n]
			else:
				break
		for i,j in zip(d,Ans):
			d[i]=j

		for i in string:
			s+=d[i]

		for i in d:
			n=ord(i)
			e[n]=d[i]

		for i,j in zip(keys,e):
			new[keys[i]]=e[j]

		new=randict(new)

		return s,new
	else:
		print(err)	

def wjson(data,path):
	if isinstance(data,dict) and isinstance(path,str):
		import json

		with open(path,'w') as json_file:
			json.dump(data,json_file)
	else:
		print(err)		

def askfile():
	from tkinter.filedialog import askopenfilename

	filepath = askopenfilename()

	return filepath

def delfile(filename):
	if isinstance(filename,str):
		if filename=='askfile':
			import os
			from tkinter.filedialog import askopenfilename
			
			filename = askopenfilename()
			os.remove(filename)

		else:	
			import os

			os.remove(filename)
	else:
		print(err)

def deljsonele(path):
	if isinstance(path,str):
		import json

		jsonfile=json.load(open(path))
		copy=jsonfile.copy()

		k=eval(input('Enter the Key : '))

		del copy[k]

		with open(path,'w') as json_file:
			json.dump(copy,json_file)	
	else:
		print(err)	

def upjson(path):
	if isinstance(path,str):
		import json
		jsonfile=json.load(open(path))
		copy=jsonfile.copy()

		k=eval(input('Enter the Key : '))
		v=eval(input('Enter the Value : '))
		copy[k]=v

		with open(path,'w') as json_file:
			json.dump(copy,json_file)
	else:
		print(err)		

def num(n):
	if isinstance(n,int):
		if str(n).endswith('1') and not(str(n).endswith('11')):
			s=str(n)+'st'
		elif str(n).endswith('2') and not(str(n).endswith('12')):
			s=str(n)+'nd'
		elif str(n).endswith('3') and not(str(n).endswith('13')):
			s=str(n)+'rd'        
		else:
			s=str(n)+'th'

		return s 
	else:
		print(err)	
def intuple(x,index,element):
	if isinstance(x,tuple):
		new=()
		if len(x)<=index:
			new+=x+(element,)
		else:	
			for i,j in zip(range(len(x)),x):
				if i==index:
					new+=(element,)+(j,)
				else:
					new+=(j,)
		return new	
	else:
		print(err)

def instr(x,index,element):
	if isinstance(x,str):
		new=''
		if len(x)<=index:
			new+=x+element
		else:	
			for i,j in zip(range(len(x)),x):
				if i==index:
					new+=element+j
				else:
					new+=j
		return new
	else:
		print(err)			

def askfolder():
	from tkinter import filedialog

	folder = filedialog.askdirectory()

	return folder

def msgbox(type,title='Pydule',text='YOUR TEXT HERE'):
	if isinstance(type,str) and isinstance(title,str) and isinstance(text,str):
		from tkinter import messagebox
		if type=='info':
			return messagebox.showinfo(title,text)
		elif type=='error':
			return messagebox.showerror(title,text)
		elif type=='warning':
			return messagebox.showwarning(title,text)
		elif type=='question':
			return messagebox.askquestion(title,text)
		elif type=='okcancel':
			return messagebox.askokcancel(title,text)
		elif type=='retrycancel':
			return messagebox.askretrycancel(title,text)
		elif type=='yesno':
			return messagebox.askyesno(title,text)
		elif type=='yesnocancel':
			return messagebox.askyesnocancel(title,text)							
		else:
			print(err)
	else:
		print(err)			

def functions():
	def lower(s):
		return s.lower()
	l=['randict()','FIGlet()','pytoexe()','aboutbattery()','GPTGAME1()','percent()','msgbox()','askfolder()','askfile()','delfile()','resizeimg()','GetWebHTML()','TrackLocation()','num()','screenshot()','SpeechtoText()','ChatGPT() Use from Pydule import AI','recintaudio()','recmic()','recscreen()','mulmatrix()','EncryptStr()','DecryptStr()','swapdict()','sepstr()','wjson()','deljsonele()','upjson()','copy()','translate()','cqrcode()','summatrix()','submatrix()','intuple()','instr()','reSet()','reStr()','reDict()','reTuple()','pickcolor()','search()','playmusic()','restart_system()','shutdown_system()','todaysdate()','timenow()','say()','openfile()','weathernow()','setvoice()','voicerate()']
	l1=list(map(lower,l))
	l2,final=l1.copy(),[]
	l1.sort()

	for i in range(len(l)):
		for j in range(len(l)):
			if l1[i]==l2[j]:
				final.append(l[j])

	print('Available Functions : \n')
	import time as t
	for i in range(len(l)):
		print(f'\t{i+1}.{final[i]}')
		t.sleep(0.1)

def summatrix(x,y):
	import numpy as np

	result = np.array(x) + np.array(y)
	
	return result

def submatrix(x,y):
	import numpy as np
	result = np.array(x) - np.array(y)

	return result

def reDict(x,oele,nele):
	if isinstance(x,dict):
		new={}
		for i in x:
			if i==oele:
				new[nele]=x.get(i)
			else:
				new[i]=x.get(i)

		return new		
	else:
		print(err)

def translate(content,language):
	if isinstance(content,str) and isinstance(language,str):
		from deep_translator import GoogleTranslator

		translated = GoogleTranslator(source='auto', target=language.lower()).translate(content)

		return translated
	else:
		print(err)	
	
def cqrcode(data,filename):
	if isinstance(data,str) and filename.endswith('.png') or filename.endswith('.jpg'):
		import qrcode

		img = qrcode.make(data)

		img.save(filename)

		print('\nQrcode Saved Successfully \U00002714\n')
	else:
		print(err)	
	
def Author():
	print('\nThis Pydule is Created by D.Tamil Mutharasan \U0001F608\n')

def reStr(oldstr,index,newstr):
	if isinstance(oldstr,str):
		new=''
		for i in range(len(oldstr)):
			if i==index:
				new+=newstr
			else:
				new+=oldstr[i]

		return new
	else:
		print(err)	

def reSet(oldset,element,newelement):
	if isinstance(oldset,set):
		new=set()
		for i in oldset:
			if i==element:
				new.add(newelement)
			else:
				new.add(i)

		return new				
	else:
		print(err)		

def reTuple(oldtup,index,newtup):
	if isinstance(oldtup,tuple):
		new=tuple()
		for i in range(len(oldtup)):
			if i==index:
				new+=(newtup,)
			else:
				new+=(oldtup[i],)

		return new
	else:
		print(err)	

def copy(string):
	if isinstance(string,str):	
		import pyperclip
		pyperclip.copy(string)
	else:
		print(err)

def pickcolor():
	from tkinter import colorchooser
	c=colorchooser.askcolor(title='Pydule Color Picker \U00002714')
	copy('\''+str(c[-1])+'\'')
	print(f'Choosen Color ({c[-1]}) is Copied \U00002714')

def GPTGAME1():
	import pygame
	import random

	pygame.init()

	window_width = 800
	window_height = 600

	points=0

	black = (0,0,0)
	white = (255,255,255)

	game_window = pygame.display.set_mode((window_width, window_height))
	pygame.display.set_caption('Catch the Circle')

	class Star:
		def __init__(self):
			self.x = random.randint(0, window_width)
			self.y = random.randint(0, window_height)
			self.size = random.randint(15, 30)
			self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))

		def draw(self):
			pygame.draw.circle(game_window, self.color, (self.x, self.y), self.size)

	class Player:
		def __init__(self):
			self.x = window_width // 2
			self.y = window_height // 2
			self.size = 20
			self.color = (255,0,0)
			self.speed = 5

		def draw(self):
			pygame.draw.circle(game_window, self.color, (self.x, self.y), self.size)

		def move(self):
			keys = pygame.key.get_pressed()
			if keys[pygame.K_LEFT]:
				self.x -= self.speed
			if keys[pygame.K_RIGHT]:
				self.x += self.speed
			if keys[pygame.K_UP]:
				self.y -= self.speed
			if keys[pygame.K_DOWN]:
				self.y += self.speed

	star = Star()

	player = Player()

	game_running = True
	while game_running:
		game_window.fill(black)

		star.draw()

		player.draw()
		player.move()

		if abs(star.x - player.x) < (star.size + player.size) // 2 and abs(star.y - player.y) < (star.size + player.size) // 2:
			points+=1
			star = Star()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				print(f'You Scored {points} Points !!')
				game_running = False

		pygame.display.update()

	pygame.quit()
	
def search(content):
	if isinstance(content,str):
		import pywhatkit as kt
		kt.search(content)	
		print('\nSearching \U0001F50E...\n')		
	else:
		print(err)	
	
def playmusic(path):
	if isinstance(path,str):
		if path=='askfile':
			import os
			from tkinter.filedialog import askopenfilename
			import time
			import pyglet

			filename = askopenfilename()

			media_player = pyglet.media.Player()

			song = pyglet.media.load(filename)

			media_player.queue(song)

			media_player.play()

			time.sleep(song.duration)

			media_player.pause()
		else:
			import os
			from tkinter.filedialog import askopenfilename
			import time
			import pyglet

			media_player = pyglet.media.Player()

			song = pyglet.media.load(path)

			media_player.queue(song)

			media_player.play()

			time.sleep(song.duration)

			media_player.pause()
	else:
		print(err)

def restart_system():
	print('\nRestarting the System \U0001F4BB...\n')		
	os.system("shutdown /r /t 1")
	
def shutdown_system():
	print('\nShutting Down Your System \U0001F4BB...\n')
	os.system("shutdown /s /t 1")
	
def todaysdate():
	from datetime import date
	d=date.today()

	return d
	
def timenow():
	from datetime import datetime
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S %p")

	return current_time
	
def say(content,save=False):
	if isinstance(content,str):	
		engine.say(content)
		if save==True:
			engine.save_to_file(text=content,filename=content+'.mp3')
		engine.runAndWait()  
	else:
		print(err)

def openfile(path):
	if isinstance(path,str):	
		if path=='askfile':
			from tkinter import filedialog
			filename = filedialog.askopenfilename()
			os.startfile(filename)
		else:	
			os.startfile(path)
	else:
		print(err)		

def weathernow(place):
	if isinstance(place,str):
		import requests
		from bs4 import BeautifulSoup
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

		def weather(city,place):
			city = city.replace(" ", "+")
			res = requests.get(
				f'https://www.google.com/search?q={city}&oq={city}&aqs=chrome.0.35i39l2j0l4j46j69i60.6128j1j7&sourceid=chrome&ie=UTF-8', headers=headers)
			soup = BeautifulSoup(res.text, 'html.parser')
			time = soup.select('#wob_dts')[0].getText().strip()
			info = soup.select('#wob_dc')[0].getText().strip()
			weather = soup.select('#wob_tm')[0].getText().strip()
			details=['City Name : '+place,info,weather+'°C']

			return details
		city = place+" weather"

		return weather(city,place)
	else:
		print(err)	

def TrackLocation(string):
	if isinstance(string,str) and len(string)==13:
		import phonenumbers

		from phonenumbers import geocoder

		number = phonenumbers.parse(string)

		location = geocoder.description_for_number(number, "en")

		return location
	else:
		print(err)	

def setvoice(num):
	if isinstance(num,int):
		voices=engine.getProperty('voices')
		engine.setProperty('voice',voices[num].id)	
	else:
		print(err)	

def voicerate(num):
	if isinstance(num,int):
		engine.setProperty('rate',num)
	else:
		print(err)	