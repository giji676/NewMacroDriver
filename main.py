from tkinter import *
from pystray import MenuItem as item
import pystray
from PIL import Image

import serial.tools.list_ports
import pandas as pd
import webbrowser
import promptlib
import threading
import keyboard
import serial
import time
import os

# Initial window setup, non-resizable
win = Tk()
win.title("Macro Pad Driver")
win.geometry("400x640")
win.resizable(False, False)


class Btn:
    def __init__(self, root, x, y, btnId, btnImg):
        self.x, self.y = x, y
        self.id = btnId
        self.btn = Button(root, image=btnImg, command=lambda: changeFrame(bindFrame, mainFrame, self.id))
        self.btn.place(x=self.x * 100, y=self.y * 120 + 160, width=100, height=120)

        self.funcType = None  # 0 = Run Program, 1 = Keystroke, 2 = Text, 3 = Link
        self.path = None
        self.text = None
        self.macro = None
        self.url = None


""" ---Create Frames--- """


def createMainFrame(backgroundImg):
    # Main Frame/The first frame shown, with 4x4 buttons
    frame = Frame(win)
    lbl = Label(frame, image=backgroundImg)
    lbl.image = backgroundImg
    lbl.place(x=0, y=0, width=400, height=640)
    return frame


def createBindFrame():
    # Frame displayed after a button is pressed from the main frame
    frame = Frame(win)
    runProgramBtn = Button(frame, text="Run Program", command=lambda: changeFrame(runProgramFrame, bindFrame, None))
    runProgramBtn.place(x=0, y=0, width=400, height=50)

    keystrokeBtn = Button(frame, text="Key stroke", command=lambda: changeFrame(macroRecordFrame, bindFrame, None))
    keystrokeBtn.place(x=0, y=50, width=400, height=50)

    textBtn = Button(frame, text="Text", command=lambda: changeFrame(textEnterFrame, bindFrame, None))
    textBtn.place(x=0, y=100, width=400, height=50)

    linkBtn = Button(frame, text="Link", command=lambda: changeFrame(linkEnterFrame, bindFrame, None))
    linkBtn.place(x=0, y=150, width=400, height=50)

    closeBtn = Button(frame, text="close", command=lambda: changeFrame(mainFrame, bindFrame, None))
    closeBtn.place(x=0, y=200, width=400, height=50)
    return frame


def createRunProgramFrame():
    # Frame displayed after Run Program button is pressed from the bind menu frame
    frame = Frame(win)
    runProgramBtn = Button(frame, text="Select Program", command=lambda: getProgramPath())
    runProgramBtn.place(x=0, y=0, width=400, height=50)

    enterPathLbl = Label(frame, text="Or enter program path:")
    enterPathLbl.place(x=0, y=50, width=400, height=50)

    enterPathEnt = Entry(frame, textvariable=pathEntVar)
    enterPathEnt.place(x=0, y=100, width=400, height=30)

    saveBtn = Button(frame, text="Save", command=lambda: saveProgramPath())
    saveBtn.place(x=0, y=130, width=400, height=50)

    cancelBtn = Button(frame, text="Cancel", command=lambda: changeFrame(mainFrame, runProgramFrame, None))
    cancelBtn.place(x=0, y=180, width=400, height=50)

    return frame


def createMacroRecordFrame():
    # Frame displayed after Key stroke button is pressed from the bind menu frame
    frame = Frame(win)

    startBtn = Button(frame, text="Start", command=lambda: getKeyStrokes())
    startBtn.place(x=0, y=0, width=400, height=50)

    infoLbl = Label(frame, text="Click Start button, press any key stokes you want except Enter.\nPress Enter when you want to stop recording the key strokes.")
    infoLbl.place(x=0, y=50, width=400, height=50)

    saveBtn = Button(frame, text="Save", command=lambda: saveKeyStrokes())
    saveBtn.place(x=0, y=100, width=400, height=50)

    cancelBtn = Button(frame, text="Cancel", command=lambda: changeFrame(mainFrame, macroRecordFrame, None))
    cancelBtn.place(x=0, y=150, width=400, height=50)

    return frame


def createTextEnterFrame():
    # Frame displayed after Text button is pressed from the bind menu frame
    frame = Frame(win)
    textLbl = Label(frame, text="Enter text you want to type")
    textLbl.place(x=0, y=0, width=400, height=50)

    enterTextEnt = Entry(frame, textvariable=textEntVar)
    enterTextEnt.place(x=0, y=50, width=400, height=30)

    saveBtn = Button(frame, text="Save", command=lambda: saveText())
    saveBtn.place(x=0, y=80, width=400, height=50)

    cancelBtn = Button(frame, text="Cancel", command=lambda: changeFrame(mainFrame, textEnterFrame, None))
    cancelBtn.place(x=0, y=130, width=400, height=50)

    return frame


def createLinkEnterFrame():
    # Frame displayed after Link button is pressed from the bind menu frame
    frame = Frame(win)
    textLbl = Label(frame, text="Enter the url to open")
    textLbl.place(x=0, y=0, width=400, height=50)

    enterLinkEnt = Entry(frame, textvariable=linkEntVar)
    enterLinkEnt.place(x=0, y=50, width=400, height=30)

    saveBtn = Button(frame, text="Save", command=lambda: saveLink())
    saveBtn.place(x=0, y=80, width=400, height=50)

    cancelBtn = Button(frame, text="Cancel", command=lambda: changeFrame(mainFrame, linkEnterFrame, None))
    cancelBtn.place(x=0, y=130, width=400, height=50)

    return frame


""" ---Keybind Functions--- """


def getProgramPath():
    path = (promptlib.Files()).file()
    pathEntVar.set(path)


def saveProgramPath():
    # Get the path entered
    path = getStringVariables(pathEntVar)

    # Load keybinds.csv
    csvFile = pd.read_csv("keybinds.csv")
    data = csvFile.to_records()

    # Set the correct function type and function in keybinds.csv
    data[activeBtn][1] = 0
    data[activeBtn][2] = path

    # Write to the csv file
    csvFile = pd.DataFrame(data, columns=header)
    csvFile.to_csv("keybinds.csv", index=False)

    # Update the button list
    makeBtns()

    # Return to the main menu
    changeFrame(mainFrame, runProgramFrame, None)


def getKeyStrokes():
    global keyStrokes
    keyStrokes = []

    # Keyboard module records key presses until Enter is pressed
    recorded = keyboard.record(until="enter")
    if len(recorded) != 0:
        offset = 0
        for x in range(len(recorded)):
            newX = x - offset
            # Remove a key stroke if it was repeated, as it will have no effect - e.g. "a down", "a down" has no effect
            if recorded[newX].name == recorded[newX-1].name and recorded[newX].event_type == recorded[newX-1].event_type:
                recorded.pop(newX)
                offset += 1
    recorded.pop() # Pops the Enter keystroke from the end of the list

    for key in recorded:
        keyStrokes.append((key.name, key.event_type))

    saveKeyStrokes()


def saveKeyStrokes():
    global keyStrokes
    macroHeader = ['key', 'action']

    # Create keylog.csv file with the keystrokes
    keylogCsv = pd.DataFrame(keyStrokes, columns=macroHeader)
    fName = str(activeBtn) + "_keylog.csv"
    keylogCsv.to_csv(fName, index=False)

    # Change the function type in the keybinds.csv, change the function to the file name of the keylog.csv file
    data = (pd.read_csv("keybinds.csv")).to_records()
    data[activeBtn][1] = 1
    data[activeBtn][2] = fName

    # Write to the keybinds.csv file
    keybindsCsv = pd.DataFrame(data, columns=header)
    keybindsCsv.to_csv("keybinds.csv", index=False)

    makeBtns()


def replayMacro(btnId):
    # Load the key strokes file
    fName = str(btnId) + "_keylog.csv"
    data = (pd.read_csv(fName)).to_records()

    # For each key stroke/row press/release the key
    for row in data:
        if row[2] == "down":
            keyboard.press(row[1])
            time.sleep(0.03)
        if row[2] == "up":
            keyboard.release(row[1])
            time.sleep(0.03)


def saveText():
    # Get the text entered
    text = getStringVariables(textEntVar)

    # Load keybinds.csv
    csvFile = pd.read_csv("keybinds.csv")
    data = csvFile.to_records()

    # Set the correct function type and function in keybinds.csv
    data[activeBtn][1] = 2
    data[activeBtn][2] = text

    # Write to the csv file
    csvFile = pd.DataFrame(data, columns=header)
    csvFile.to_csv("keybinds.csv", index=False)

    # Update the button list
    makeBtns()

    # Return to the main menu
    changeFrame(mainFrame, textEnterFrame, None)


def saveLink():
    # Get the link entered
    link = getStringVariables(linkEntVar)

    # Load keybinds.csv
    csvFile = pd.read_csv("keybinds.csv")
    data = csvFile.to_records()

    # Set the correct function type and function in keybinds.csv
    data[activeBtn][1] = 3
    data[activeBtn][2] = link

    # Write to the csv file
    csvFile = pd.DataFrame(data, columns=header)
    csvFile.to_csv("keybinds.csv", index=False)

    # Update the button list
    makeBtns()

    # Return to the main menu
    changeFrame(mainFrame, linkEnterFrame, None)


""" ---Misc Functions--- """


def changeFrame(frame1, frame2, btnId):
    # Disables frame2, enables frame1
    # If btnId is not None, sets global active btnId
    global activeBtn

    if frame1 == bindFrame:
        activeBtn = btnId
    else:
        btnId = None
    frame1.pack(fill="both", expand=1)
    frame2.pack_forget()


def getStringVariables(var):
    return var.get()


def createVariables():
    # Creates initial StringVars
    global activeBtn, keyStrokes, pathEntVar, textEntVar, linkEntVar

    activeBtn = None
    keyStrokes = None
    pathEntVar = StringVar()
    textEntVar = StringVar()
    linkEntVar = StringVar()


def defaultFileSetup():
    global header

    header = ['funcType', 'function']

    # Load the keybinds if the file exists, create a default file if it doesn't
    if os.path.isfile("keybinds.csv"):
        makeBtns()
    else:
        writeData = []
        # Create the default structure of the keybinds.csv file
        for x in range(16):
            writeData.append(("X", " "))


        data = pd.DataFrame(writeData, columns=header)
        data.to_csv("keybinds.csv", index=False)

        makeBtns()


def makeBtns():
    # Populates btn class in grid with function and function types from the keybinds.csv file
    global grid
    data = (pd.read_csv("keybinds.csv")).to_records()
    # 0 = Run Program, 1 = Key stroke, 2 = Text, 3 = Link
    for row in data:
        if row[1] == "0":
            grid[row[0]].funcType = 0
            grid[row[0]].path = row[2]
        elif row[1] == "1":
            grid[row[0]].funcType = 1
            grid[row[0]].path = row[2]
        elif row[1] == "2":
            grid[row[0]].funcType = 2
            grid[row[0]].text = row[2]
        elif row[1] == "3":
            grid[row[0]].funcType = 3
            grid[row[0]].url = row[2]


def hardwareCheck(port):
    # Return True if the hardware is found
    if type(port).__name__ == 'Device':
        if 'ID_BUS' not in port or port['ID_BUS'] != 'usb' or 'SUBSYSTEM' not in port or port['SUBSYSTEM'] != 'tty':
            return False
        usbId = 'usb vid:pid={}:{}'.format(port['ID_VENDOR_ID'], port['ID_MODEL_ID'])
    else:
        usbId = port[2].lower()

    if usbId.startswith('usb vid:pid=2e8a:000a'):
        return True
    return False


def btnListen():
    while True:
        if serialPort.in_waiting > 0:
            serialString = serialPort.readline()
            msg = int(serialString.decode("Ascii")) - 1
            if msg > 8:  # Offset the msg numbers after 8 because of a hardware side issue
                msg -= 1
            try:
                if grid[msg].funcType == 0:  # Run program
                    try:
                        os.startfile(grid[msg].path)
                        time.sleep(0.5)
                    except:
                        pass

                elif grid[msg].funcType == 1:  # Play macro
                    try:
                        replayMacro(msg)
                        time.sleep(0.2)
                    except:
                        pass

                elif grid[msg].funcType == 2:  # Type text
                    try:
                        keyboard.write(grid[msg].text)
                    except:
                        pass

                elif grid[msg].funcType == 3:  # Open link
                    try:
                        webbrowser.open(grid[msg].url, new=0, autoraise=True)
                        time.sleep(0.2)
                    except:
                        pass
            except:
                pass


def main():
    # Main function
    # List the serial ports connected
    ports = list(serial.tools.list_ports.comports())

    # Check if a raspberry pi device is connected to the computer
    # Only move on if the device is found
    global serialPort

    deviceFound = False
    while not deviceFound:
        for port in ports:
            if hardwareCheck(port):
                serialPort = serial.Serial(port=port.name, baudrate=9600, bytesize=8, timeout=2,
                                           stopbits=serial.STOPBITS_ONE)
                deviceFound = True

    global mainFrame, bindFrame, runProgramFrame, macroRecordFrame, textEnterFrame, linkEnterFrame
    global grid

    backgroundImg = PhotoImage(file="assets/background.png")  # Background image of the MainFrame
    btnImg = PhotoImage(file="assets/btnBackground.png")  # Background image of the 4x4 buttons on the MainFrame

    # Create initial StringVars
    createVariables()

    # Create initial frames
    mainFrame = createMainFrame(backgroundImg)
    bindFrame = createBindFrame()
    runProgramFrame = createRunProgramFrame()
    macroRecordFrame = createMacroRecordFrame()
    textEnterFrame = createTextEnterFrame()
    linkEnterFrame = createLinkEnterFrame()

    # Create 4x4 grid buttons from Btn class
    btnId = 0
    grid = []
    for y in range(4):
        for x in range(4):
            grid.append(Btn(mainFrame, x, y, btnId, btnImg))
            btnId += 1

    # Check if keybinds.csv exists, if it doesn't, create a default file
    defaultFileSetup()

    # Display the initial frame (MainFrame)
    changeFrame(mainFrame, runProgramFrame, None)

    # Start a separate thread to listen to macro pad button presses
    btnPressListen = threading.Thread(target=btnListen)
    btnPressListen.start()

    win.protocol('WM_DELETE_WINDOW', hideWindow)
    win.mainloop()


def quitWindow(icon, item):
    icon.stop()
    win.destroy()
    quit()


def showWindow(icon, item):
    icon.stop()
    win.after(0, win.deiconify())


def hideWindow():
    win.withdraw()
    image = Image.open("assets/icon.ico")
    menu = (item('Quit', quitWindow), item('Show', showWindow))
    icon = pystray.Icon("name", image, "Macro Pad Driver", menu)
    icon.run()


""" ---Program Entry--- """

if __name__ == "__main__":
    main()
