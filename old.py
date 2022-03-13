from tkinter import *
from pystray import MenuItem as item
import pystray
from PIL import Image

from tkinter.messagebox import showinfo
import pandas as pd
import webbrowser
import promptlib
import threading
import keyboard
import serial
import serial.tools.list_ports
import time
import os


ports = list(serial.tools.list_ports.comports())

def is_macro_pad(port):
	if type(port).__name__ == 'Device':
		if ('ID_BUS' not in port or port['ID_BUS'] != 'usb' or 'SUBSYSTEM' not in port or port['SUBSYSTEM'] != 'tty'):
			return False
		usb_id = 'usb vid:pid={}:{}'.format(port['ID_VENDOR_ID'], port['ID_MODEL_ID'])
	else:
		usb_id = port[2].lower()

	if usb_id.startswith('usb vid:pid=2e8a:000a'):
		return True
	return False

deviceFound = False
while not deviceFound:
	for port in ports:
		if is_macro_pad(port):
			serialPort = serial.Serial(port=port.name, baudrate=9600, bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
			deviceFound = True

serialString = ""

win = Tk()
win.title("Macro Pad Driver")


def get_program_path(id):
	try:
		showinfo(title=".url warning",
				 message="If you are trying to open a .url file (such as steam game) try getting the url from the file properties and using 'Open Link' function.")
		path = (promptlib.Files()).file()
		
		btnList[id].funcType = 0
		btnList[id].path=path
		
		csv_file = pd.read_csv("keybinds.csv")
		data = csv_file.to_records()
		
		data[id][1] = 0
		data[id][2] = path
		
		csv_file = pd.DataFrame(data, columns=header)
		csv_file.to_csv("keybinds.csv", index=False)
		
		make_btns()
	except:
		showinfo(title="Warning", message="If you are trying to open a .url file (such as steam game) try getting the url from the file properties and using 'Open Link' function.")


def get_link(id):
	url = link_var_list[id].get()
	
	btnList[id].funcType = 2
	btnList[id].url = url
	
	csv_file = pd.read_csv("keybinds.csv")
	data = csv_file.to_records()
	
	data[id][1] = 2
	data[id][2] = url
	
	csv_file = pd.DataFrame(data, columns=header)
	csv_file.to_csv("keybinds.csv", index=False)
	
	make_btns()


def get_key_combo(id):
	key_strokes = []
	recorded = keyboard.record(until="enter")
	if len(recorded) != 0:
		offset = 0
		for x in range(len(recorded)):
			new_x = x - offset
			if recorded[new_x].name == recorded[new_x-1].name and recorded[new_x].event_type == recorded[new_x-1].event_type:
				recorded.pop(new_x)
				offset += 1
	recorded.pop()
	
	for key in recorded:
		key_strokes.append((key.name, key.event_type))
	macro_header = ['key', 'action']
	
	keylog_csv = pd.DataFrame(key_strokes, columns=macro_header)
	f_name = str(id) +"_keylog.csv"
	keylog_csv.to_csv(f_name, index=False)
	
	data = (pd.read_csv("keybinds.csv")).to_records()
	data[id][1] = 1
	data[id][2] = f_name
	
	keybinds_csv = pd.DataFrame(data, columns=header)
	keybinds_csv.to_csv("keybinds.csv", index=False)
	
	make_btns()


def make_btns():
	global btnList
	data = (pd.read_csv("keybinds.csv")).to_records()
	for row in data:
		if row[1] == "0":
			btnList[row[0]].funcType = 0
			btnList[row[0]].path = row[2]
		elif row[1] == "1":
			btnList[row[0]].funcType = 1
			btnList[row[0]].path = row[2]
		elif row[1] == "2":
			btnList[row[0]].funcType = 2
			btnList[row[0]].url = row[2]

		
def default_setup():
	global btnList, header, link_var_list
	btnList = []
	link_var_list = []
	
	for x in range(16):
		link_var_list.append(StringVar())
	
	for x in range(16):
		row = rowClass(x)
		btnList.append(row)
	
	header = ['funcType', 'function']
	write_data = [
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " "),
		("X", " ")
	]
	
	if os.path.isfile("keybinds.csv"):
		make_btns()
	
	else:
		data = pd.DataFrame(write_data, columns=header)
		data.to_csv("keybinds.csv", index=False)
		make_btns()


class rowClass:
	def __init__(self, id):
		self.id = id
		self.lblText = "BTN " + str(self.id + 1) + " function"
		self.label = Label(win, text=self.lblText)
		self.label.grid(row=self.id, column=0)
		
		self.programBtn = Button(win, text="Open program", command=lambda id=self.id : get_program_path(id))
		self.programBtn.grid(row=self.id, column=1)
		
		self.macroBtn = Button(win, text="Key combination", command=lambda id=self.id : get_key_combo(id))
		self.macroBtn.grid(row=self.id, column=2)
		
		self.linkLbl = Label(win, text="Open Link")
		self.linkLbl.grid(row=self.id, column=3)
		
		self.linkEnt = Entry(win, textvariable=link_var_list[id])
		self.linkEnt.grid(row=self.id, column=4)
		
		self.saveBtn = Button(win, text="Save Link", command=lambda id=self.id : get_link(id))
		self.saveBtn.grid(row=self.id, column=5)
		
		self.funcType = None # 0 = launcher, 1 = macro, 2 = link
		self.path = None
		self.macro = None
		self.url = None

def replay_macro(id):
	f_name = str(id) + "_keylog.csv"
	data = (pd.read_csv(f_name)).to_records()
	
	for row in data:
		if row[2] == "down":
			keyboard.press(row[1])
			time.sleep(0.03)
		if row[2] == "up":
			keyboard.release(row[1])
			time.sleep(0.03)

def btn_listen():
	global btnList
	
	while True:
		if serialPort.in_waiting > 0:
			serialString = serialPort.readline()
			msg = int(serialString.decode("Ascii"))-1
			if msg > 8:
				msg -= 1
			try:
				if btnList[msg].funcType == 0:
					try:
						os.startfile(btnList[msg].path)
						time.sleep(0.2)
					except:
						pass

				elif btnList[msg].funcType == 1:
					replay_macro(msg)
					time.sleep(0.5)

				elif btnList[msg].funcType == 2:
					webbrowser.open(btnList[msg].url, new=0, autoraise=True)
					time.sleep(0.2)
			except:
				pass


def quit_window(icon, item):
	icon.stop()
	win.destroy()


def show_window(icon, item):
	icon.stop()
	win.after(0, win.deiconify())


def hide_window():
	win.withdraw()
	image=Image.open("assets/icon.ico")
	menu=(item('Quit', quit_window), item('Show', show_window))
	icon=pystray.Icon("name", image, "Macro Pad Driver", menu)
	icon.run()


""" --- Program Entry --- """

default_setup()

btn_thread = threading.Thread(target=btn_listen)
btn_thread.start()

win.protocol('WM_DELETE_WINDOW', hide_window)
win.mainloop()