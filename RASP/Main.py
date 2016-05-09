#!/usr/bin/env python

import Tkinter
from Tkinter import Button, Tk, Canvas, Label# import OSC support ( PyOSC )
from PIL import ImageTk, Image
import ttk
from OSC import OSCServer, OSCClient, OSCMessage
import subprocess               # To start subprocesses (e.g. mpg123)
import tkFont                   # GUI implementation
import socket                   # For IP determination
import time                     # Time
import logging                  # Log messages
import gauges


logging.basicConfig(level=logging.WARNING)        #DEBUG, INFO, WARNING, ERROR, CRITICAL

testMode = False                                # Set to true to run it on not PiCas Computers (without I2C devices)
invertedScreenColor = False                     # Due to driver problems the screen color is inverted so we're unsing reverse colors

OSCServerIP = "0.0.0.0"
OSCServerPort = 7000
OSCServerIP = "192.168.178.48"
OSCServerPort = 9000

# -----Peripheral initialization-----#
if (not testMode):
    invertedScreenColor = True     # automatically switching with test mode :)

    #Text to speech initialization
    import pyttsx  # Text to speech support
    engine = pyttsx.init()


    # I2C Addresses
    ISL29023_ADDR = 0x44
    AnalogBoard_ADDR = 0x22

    #analog Board
    import analogBoard
    analogBoard = analogBoard.init(AnalogBoard_ADDR)    # Initialization
    logging.info("Analog Board called" + analogBoard.getDeviceName() + "initialized")
    print analogBoard.getDeviceName()

    #ISL29023
    import ISL29023
    brightness = ISL29023.isl(ISL29023_ADDR)
    logging.info("ISLS29023 brightness sensor initialized")

    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)        #use Board mapping as Pin names
    dataPin = 29                    #Serial Input 74HC165
    clockEnablePin = 31             #Clock enable  74HC165
    clockPin = 33                   #CLK Output 74HC165
    loadPin = 36                    #data Load pin 74HC165
    GPIO.setup(dataPin, GPIO.IN)
    GPIO.setup(clockEnablePin, GPIO.OUT)
    GPIO.setup(clockPin, GPIO.OUT)
    GPIO.setup(loadPin, GPIO.OUT)
    logging.info("GPIO Pins initialized")
    # IMU

    import RTIMU
    import os.path
    import math

    SETTINGS_FILE = "RTIMULib"
    logging.info("Using settings file " + SETTINGS_FILE + ".ini")
    if not os.path.exists(SETTINGS_FILE + ".ini"):
        logging.warning("Settings file does not exist, will be created")
    s = RTIMU.Settings(SETTINGS_FILE)
    imu = RTIMU.RTIMU(s)
    logging.info("IMU recognized: " + imu.IMUName())
    if not imu.IMUInit():
        logging.error("IMU Init Failed")
        sys.exit(1)
    else:
        logging.info("IMU Init Succeeded")
    #set any fusion parameters
    imu.setSlerpPower(0.02)
    imu.setGyroEnable(True)
    imu.setAccelEnable(True)
    imu.setCompassEnable(True)

    logging.info("Recommended Poll Interval: %dmS\n" % imu.IMUGetPollInterval())
else:
    logging.warning("Starting in Testmode!")

#-----OSC initialization-----#
server = OSCServer(("0.0.0.0", 7000))
OSCC = OSCClient()
OSCC.connect(("192.168.178.48", 9000))  # connect to tablet

#-----GUI initialization-----#

#--COLOR Sheme definitions
if invertedScreenColor:
    grey = "light slate grey"
    green = "purple"
    yellow = "blue"
    red     = "cyan"
    white   = "black"
    black   = "white"
else:
    grey = "light slate grey"
    green = "green"
    yellow = "yellow"
    red     = "red"
    white   = "white"
    black   = "black"

c_height = 476 #the border lines are approx 2px
c_width = 316 #316

root = Tk()
root.config(width=(c_width - 45), height=c_height, bg=black)
if not testMode:
    root.config(cursor="none")
    root.attributes("-fullscreen", True)    #if not in test mode switch to fullscreen


textFont = tkFont.Font(family="Helvetica", size=36, weight="bold")

# Declare Variables
measuredItems = ["RPM", "Water TMP", "Oil Temp", "Oil Press", "EGT", "Fuel Flow", "Fuel(left)", "Voltage"]
errorBoxItems = ["TEMP", "PRESS", "FUEL", "POWER", "ERROR"]
errorBoxItemsColor = ["red", "green", "green", "yellow", "green"]
measuredItemsColor = [red, green, yellow, green, green, green, green]
measuredItemsValue = [1, 65, 89, 10, 768, 7.8, 65, 12.6]
buttonPressed = ([0, 0, 0, 0, 0, 0, 0, 0])

#Flight Data#
roll = 0;
pitch = 0;
yaw = 0;


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 0))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def setupGrid(parent):

    parent.rowconfigure(0, minsize=120)
    parent.rowconfigure(1, minsize=120)
    parent.rowconfigure(2, minsize=120)
    parent.rowconfigure(3, minsize=120)

    parent.columnconfigure(0, minsize=20)
    parent.columnconfigure(1, minsize=125)
    parent.columnconfigure(2, minsize=125)
    parent.columnconfigure(3, minsize=20)

class background:
    def __init__(self,parent):
        C = Canvas(parent, bg=black, height=c_height, width=(c_width - 40))
        C.grid(row=0, column=1, rowspan=8, columnspan=2)
        self.screen = C
    def get_Name(self):
        return self.screen

class bootWindow:
    def __init__(self, parent):
        logging.info("Host IP: " +get_ip())
        self.screen = Canvas(parent, bg=black, height=480, width=320)
        self.screen.place(x=0,y=0)
        Testline = self.screen.create_line(160, 0, 160, 480, fill=red)
        Testline2 = self.screen.create_line(0, 240, 320, 240, fill=red)
        self.img = ImageTk.PhotoImage(Image.open("images/logo.PNG"))
        self.imglabel = Label(self.screen, image=self.img).place(x=160, y=150, anchor="center")

        self.text = self.screen.create_text(160,270 , text="Loading, Please wait...", fill=white, font=(textFont, 13))

        self.p = ttk.Progressbar(self.screen, orient="horizontal", length=200, mode='determinate')
        self.p.place(x=160, y=300, anchor="center")
        # LOAD ALL THE STUFF!!
        parent.update()
        self.p.step(10)
        parent.update()
        #time.sleep(1)
        self.p.step(10)
        parent.update()
        #time.sleep(1)
        self.p.step(30)
        parent.update()
        time.sleep(1)
        self.screen.destroy()
        self.p.destroy()
    def hide(self):
        pass
    def show(self):
        pass
    def update(self):
        pass
    def __del__(self):
        pass

class mainWindow:
    def __init__(self,parent):
        # left side
        # create Gauges (canvas,color, value, maxVal, name, Scale Factor)
        self.gauge1 = gauges.hybridGauge(parent, measuredItemsColor[0], 1, 500, measuredItems[0], 0.9, white, black, textFont)
        self.gauge2 = gauges.hybridGauge(parent, measuredItemsColor[1], 1, 100, measuredItems[1], 0.9, white, black, textFont)
        self.gauge3 = gauges.hybridGauge(parent, measuredItemsColor[2], 1, 120, measuredItems[2], 0.9, white, black, textFont)
        self.gauge4 = gauges.hybridGauge(parent, measuredItemsColor[1], 1, 020, measuredItems[3], 0.9, white, black, textFont)

        # right side
        self.gauge5 = gauges.hybridGauge(parent, measuredItemsColor[1], 1, 1500,measuredItems[4], 0.9, white, black, textFont)
        self.gauge6 = gauges.hybridGauge(parent, measuredItemsColor[1], 1, 25, measuredItems[5], 0.9, white, black, textFont)
        self.gauge7 = gauges.hybridGauge(parent, measuredItemsColor[1], 1, 120,measuredItems[6], 0.9, white, black, textFont)
        self.gauge8 = gauges.hybridGauge(parent, measuredItemsColor[1], 1, 18,measuredItems[7], 0.9, white, black, textFont)
    def update(self):
        self.gauge1.updateval(measuredItemsValue[0])
        self.gauge2.updateval(measuredItemsValue[1])
        self.gauge3.updateval(measuredItemsValue[2])
        self.gauge4.updateval(measuredItemsValue[3])
        self.gauge5.updateval(measuredItemsValue[4])
        self.gauge6.updateval(measuredItemsValue[5])
        self.gauge7.updateval(measuredItemsValue[6])
        self.gauge8.updateval(measuredItemsValue[7])
    def hide(self):
        self.gauge1.grid_remove()
        self.gauge2.grid_remove()
        self.gauge3.grid_remove()
        self.gauge4.grid_remove()
        self.gauge5.grid_remove()
        self.gauge6.grid_remove()
        self.gauge7.grid_remove()
        self.gauge8.grid_remove()
    def show(self):
        # left
        self.gauge1.grid(column=1, row=0, sticky="WENS")
        self.gauge2.grid(column=1, row=1, sticky="WENS")
        self.gauge3.grid(column=1, row=2, sticky="WENS")
        self.gauge4.grid(column=1, row=3, sticky="WENS")

        # right
        self.gauge5.grid(column=2, row=0, sticky="WENS")
        self.gauge6.grid(column=2, row=1, sticky="WENS")
        self.gauge7.grid(column=2, row=2, sticky="WENS")
        self.gauge8.grid(column=2, row=3, sticky="WENS")

class engWindow:
    def __init__(self, parent):
        self.value2 = Canvas(parent, bg=black, height=50, width=50)
        self.text = self.value2.create_text(160, 270, text="Loading", fill=white, font=(textFont, 10))
    def update(self):
        pass
    def hide(self):
        pass
    def show(self):
        pass

class navWindow:
    def __init__(self, parent):
        self.gauge1 = gauges.digitalGauge(parent, measuredItemsColor[4], 100,measuredItems[0], white, black, textFont)
        #self.text = self.screen.create_text(120,270 , text="Nav Window here", fill=white, font=(textFont, 13))

    def update(self):
        self.gauge1.updateval(measuredItemsValue[4])
    def hide(self):
        self.gauge1.grid_remove()
    def show(self):
        self.gauge1.grid(column=1, row=0, sticky="WENS")

class setupWindow:
    def __init__(self, parent):
        pass
    def update(self):
        pass
    def hide(self):
        pass
    def show(self):
        pass


class buttonSet:
    def __init__(self, window):
        # left
        mainButton = Label( window,  text="MAIN", wraplength=1 ).grid(column=0, row=0, sticky="WENS")
        engButton = Label( window,  text="ENG", wraplength=1 ).grid(column=0, row=1, sticky="WENS")
        navButton = Label( window,  text="NAV", wraplength=1 ).grid(column=0, row=2, sticky="WENS")
        setupButton = Label( window,  text="SETUP", wraplength=1 ).grid(column=0, row=3, sticky="WENS")

        # right
        plusButton = Label( window,  text="+", wraplength=1 ).grid(column=3, row=0, sticky="WENS")
        minusButton = Label( window,  text="-", wraplength=1 ).grid(column=3, row=1, sticky="WENS")
        cancelButton = Label( window,  text="CANCEL", wraplength=1 ).grid(column=3, row=2, sticky="WENS")
        enterButton = Label( window,  text="ENTER", wraplength=1 ).grid(column=3, row=3, sticky="WENS")


def readIMU():
    if imu.IMURead():
        # x, y, z = imu.getFusionData()
        # print("%f %f %f" % (x,y,z))
        data = imu.getIMUData()
        fusionPose = data["fusionPose"]
        print "r: %f p: %f y: %f" % (math.degrees(fusionPose[0]),
        math.degrees(fusionPose[1]), math.degrees(fusionPose[2]))
    else:
        print "Sorry no data!"



# initializing Classes
canvas = background(root)   # Create Canvas Background
setupGrid(root)
bootScreen = bootWindow(root)
mainScreen = mainWindow(root)
engScreen = engWindow(root)
navScreen = navWindow(root)
setupScreen = setupWindow(root)
Buttons = buttonSet(root)  # drawing a Set of buttons


class ActiveWindow:
    def __init__(self):
        self.activeWindow = 'NONE'

    def load(self,  selection):
        if selection == 'MAIN':
            if selection == self.activeWindow:
                mainScreen.update()
            if selection != self.activeWindow:
                mainScreen.show()
                engScreen.hide()
                setupScreen.hide()
                navScreen.hide()
                self.activeWindow = selection

        if selection == 'ENG':
            if selection == self.activeWindow:
                engScreen.update()
            if selection != self.activeWindow:
                mainScreen.hide()
                engScreen.show()
                setupScreen.hide()
                navScreen.hide()
                self.activeWindow = selection
        if selection == 'NAV':
            if selection == self.activeWindow:
                navScreen.update()
            if selection != self.activeWindow:
                mainScreen.hide()
                engScreen.hide()
                setupScreen.hide()
                navScreen.show()
                self.activeWindow = selection

        if selection == 'SETUP':
            if selection == self.activeWindow:
                setupScreen.update()
            if selection != self.activeWindow:
                mainScreen.hide()
                engScreen.hide()
                setupScreen.show()
                navScreen.hide()
                self.activeWindow = selection
    def get(self):
        return self.activeWindow
loadActiveWindow = ActiveWindow()

def read_shift_regs():
    bitVal = 0
    bytesVal = 0
    GPIO.output(clockEnablePin, GPIO.HIGH)  # clock disable
    GPIO.output(loadPin, GPIO.LOW)

    time.sleep(0.005)
    GPIO.output(loadPin, GPIO.HIGH)
    GPIO.output(clockEnablePin, GPIO.LOW)  # clock enable
    for x in range(0, 8):
        GPIO.output(clockPin, GPIO.LOW)
        if GPIO.input(dataPin) == GPIO.LOW:
            bitVal = 0
            buttonPressed[x]= 0
        elif GPIO.input(dataPin) == GPIO.HIGH:
            bitVal = 1
            buttonPressed[x]= 1
        #print "Pin " + str(x) + ":" + str(bitVal)
        bytesVal |= (bitVal << ((8-1) - x))
        time.sleep(0.005)
        GPIO.output(clockPin, GPIO.HIGH)
    return bytesVal


def updateScreen():

    if (measuredItemsValue[0] < 255): #For testing

        measuredItemsValue[0] += 1
    else:
        pass
    measuredItemsValue[1] = root.winfo_width()  # for debugging Purpose
    measuredItemsValue[2] = root.winfo_height()  # for debugging Purpose

    loadActiveWindow.load(loadActiveWindow.get())
    root.after(50, updateScreen) #update Screen every 50ms
    if not testMode:
        root.after(30, workButtons)

        #root.after(100, measuredItemsValue[4] == brightness.read)
        #root.after(100, readIMU)


def oscSend():
    oscrot1 = OSCMessage()
    oscrot1.setAddress("/engine/RPM")
    oscrot1.append(measuredItemsValue[0])
    OSCC.send(oscrot1)

    oscrot2 = OSCMessage()
    oscrot2.setAddress("/engine/OilPress")
    oscrot2.append(measuredItemsValue[1])
    OSCC.send(oscrot2)

    oscrot3 = OSCMessage()
    oscrot3.setAddress("/engine/OilTemp")
    oscrot3.append(measuredItemsValue[2])
    OSCC.send(oscrot3)

    oscrot4 = OSCMessage()
    oscrot4.setAddress("/engine/EGT")
    oscrot4.append(measuredItemsValue[3])
    OSCC.send(oscrot4)

def workButtons():
    read_shift_regs()
    if buttonPressed[0]==1:             #left side
        loadActiveWindow.load("SETUP")
    elif buttonPressed[1]==1:
        loadActiveWindow.load("NAV")
        #subprocess.Popen(['mpg123', "pullup.mp3"])
    elif buttonPressed[2]==1:
        loadActiveWindow.load("ENG")
    elif buttonPressed[3]==1:
        loadActiveWindow.load("MAIN")
    elif buttonPressed[4]==1:           #right side (+)
        engine.say("300")
        engine.runAndWait()
    elif buttonPressed[5]==1:           # (-)
        pass
    elif buttonPressed[6]==1:           # (cancel)
        pass
    elif buttonPressed[7]==1:           # (enter)
        rate = engine.getProperty('rate')
        engine.setProperty('rate', rate-40)
        engine.say("Pull up! Pull up!")
        engine.runAndWait()





loadActiveWindow.load("MAIN")
updateScreen()
try:
    oscSend()
except:
    logging.warning('Watch out!')
root.mainloop()
