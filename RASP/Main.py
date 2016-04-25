#!/usr/bin/env python

import Tkinter
from Tkinter import Button, Tk, Canvas, Label
# import OSC support ( PyOSC )
import ttk
from OSC import OSCServer, OSCClient, OSCMessage
import tkFont #GUI implementation
import socket #for IP determination
import time

# I2C Addresses
ISL29023_ADDR = 0x44
AnalogBoard_ADDR = 0x22

Testmode = True  #Set to true to run it on not PiCas Computers (without I2C devices)


if (not Testmode):
    import analogBoard
    analogBoard = analogBoard.init(AnalogBoard_ADDR)
    print "device name:"
    print analogBoard.getDeviceName()

server = OSCServer(("0.0.0.0", 7000))
OSCC = OSCClient()
OSCC.connect(("192.168.178.48", 9000))  # connect to tablet

c_height = 476 #the border lines are approx 2px
c_width = 316

root = Tk()
root.config(width=(c_width - 45), height=c_height, bg="black",)
#root.config(width=(c_width - 40), height=c_height, bg="black", cursor="none")
#root.resizable(width=0, height=0)

textFont = tkFont.Font(family="Helvetica", size=36, weight="bold")

# Declare Variables
measuredItems = ["RPM", "Water TMP", "Oil Temp", "Oil Press", "EGT", "Fuel Flow", "Fuel Quant.", "Voltage"]
errorBoxItems = ["TEMP", "PRESS", "FUEL", "POWER", "ERROR"]
errorBoxItemsColor = ["red", "green", "green", "yellow", "green"]
measuredItemsColor = ["green", "green", "green", "green", "green", "green", "green"]
measuredItemsValue = [1, 65, 89, 10, 768, 7.8, 65, 12.6]

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
        C = Canvas(parent, bg="black", height=c_height, width=(c_width - 40))
        C.grid(row=0, column=1, rowspan=8, columnspan=2)
        self.screen = C
    def get_Name(self):
        return self.screen

class bootWindow:
    def __init__(self, parent):
        print get_ip()
        self.screen = Canvas(parent, bg="black", height=480, width=320)
        self.screen.place(x=0,y=0)
        Testline = self.screen.create_line(160, 0, 160, 480, fill="red")
        Testline2 = self.screen.create_line(0, 240, 320, 240, fill="red")

        self.text = self.screen.create_text(160,270 , text="Loading, Please wait...", fill="white", font=(textFont, 13))

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
        self.isOpen = False
        #left side
        self.gauge1 = digitalGauge(parent, measuredItemsColor[0], 1, 500, measuredItems[0], 0.9)
        self.gauge2 = digitalGauge(parent, measuredItemsColor[1], 1, 100, measuredItems[1], 0.9)
        self.gauge3 = digitalGauge(parent, measuredItemsColor[2], 1, 120, measuredItems[2], 0.9)
        self.gauge4 = digitalGauge(parent, measuredItemsColor[1], 1, 020, measuredItems[3], 0.9)

                #right side
        self.gauge5 = digitalGauge(parent, measuredItemsColor[1], 1, 1500,measuredItems[4], 0.9)
        self.gauge6 = digitalGauge(parent, measuredItemsColor[1], 1, 25, measuredItems[5], 0.9)
        self.gauge7 = digitalGauge(parent, measuredItemsColor[1], 1, 120,measuredItems[6], 0.9)
        self.gauge8 = digitalGauge(parent, measuredItemsColor[1], 1, 18,measuredItems[7], 0.9)
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
        self.isOpen = False
    def show(self):
        #left
        self.gauge1.grid(column=1, row=0, sticky="WENS")
        self.gauge2.grid(column=1, row=1, sticky="WENS")
        self.gauge3.grid(column=1, row=2, sticky="WENS")
        self.gauge4.grid(column=1, row=3, sticky="WENS")

        #right
        self.gauge5.grid(column=2, row=0, sticky="WENS")
        self.gauge6.grid(column=2, row=1, sticky="WENS")
        self.gauge7.grid(column=2, row=2, sticky="WENS")
        self.gauge8.grid(column=2, row=3, sticky="WENS")
        self.isOpen = True
    def isActive(self):
        return self.isOpen

class engWindow:
    def __init__(self, parent):
        self.value2 = Canvas(parent, bg="black", height=50, width=50)
        self.text = self.value2.create_text(160, 270, text="Loading", fill="white", font=(textFont, 10))
    def update(self):
        pass
    def hide(self):
        self.value2.grid_remove()
    def show(self):
        self.value2.grid(column=1, row=1, sticky="WENS")

class navWindow:
    def __init__(self, parent):
        pass
    def update(self):
        pass
    def hide(self):
        pass
    def show(self):
        pass

class setupWindow:
    def __init__(self, parent):
        pass
    def update(self):
        pass
    def hide(self):
        pass
    def show(self):
        pass

class digitalGauge(Canvas):
    def __init__(self, window,color, value, maxVal, name, gaugeScale):
        Canvas.__init__(self, window, bg="black", height=100, width=100)
        xval = 20
        yval = 10
        self.maxVal = maxVal
        self.value = value

        self.gaugeValue = self.maxVal / float(value)  # calculate the GaugeValue

        self.hand = self.create_arc(xval, yval, (xval + 100 * gaugeScale),
                                      (yval + 100 * gaugeScale), start=0,
                                      extent=-(220 / self.gaugeValue), fill=color)  # Draw hand

        self.outline = self.create_arc(xval - 3, yval - 3, (xval + 100 * gaugeScale + 3),
                                         (yval + 100 * gaugeScale + 3), start=0, extent=-220, style="arc",
                                         outline="white", width=2)  # draw outline

        self.valueBox = self.create_rectangle((xval + 50 * gaugeScale), yval + 20 * gaugeScale,
                                                xval + 100 * gaugeScale + 3, yval + 50 * gaugeScale,
                                                outline='white',
                                                width=2)  # draw Value Box

        self.value1 = self.create_text(xval + 54 * gaugeScale, yval + 22 * gaugeScale, anchor="nw",
                                         text=self.value,
                                         fill="white", font=(textFont, int(round(15 * gaugeScale))))

        self.value2 = self.create_text(xval, yval - 8, anchor="nw", text=name, fill="white",
                                         font=(textFont, int(round(19 * gaugeScale))))


    def updateval(self, valueUpdated):
        self.itemconfig(self.value1, text=valueUpdated)
        gaugeValue = self.maxVal / float(valueUpdated)
        self.itemconfig(self.hand, extent=-(220 / gaugeValue))

class buttonSet:
    def __init__(self, window):
        # left
        mainButton = Button(window, text="MAIN", wraplength=1, command=lambda: loadActiveWindow.load("MAIN"),font=(textFont, 6),
                 bg="light slate grey").grid(column=0, row=0, sticky="WENS")
        Button(window, text="ENG", wraplength=1, command=lambda: loadActiveWindow.load("ENG"), font=(textFont, 8),
                 bg="light slate grey").grid(column=0, row=1, sticky="WENS")
        Button(window, text="NAV", wraplength=1, command=lambda: loadActiveWindow.load("NAV"), font=(textFont, 8),
                 bg="light slate grey").grid(column=0, row=2, sticky="WENS")
        Button(window, text="SETUP", wraplength=1, command=lambda: loadActiveWindow.load("STAT"), font=(textFont, 8),
                 bg="light slate grey").grid(column=0, row=3, sticky="WENS")
        # right
        Button(window, text="+", wraplength=1, command=lambda: loadActiveWindow.load("PLUS"), font=(textFont, 8),
               bg="light slate grey").grid(column=3, row=0, sticky="WENS")
        Button(window, text="-", wraplength=1, command=lambda: loadActiveWindow.load("MINUS"), font=(textFont, 8),
               bg="light slate grey").grid(column=3, row=1, sticky="WENS")
        Button(window, text="CANCEL", wraplength=1, command=lambda: loadActiveWindow.load("CANCEL"), font=(textFont, 8),
               bg="light slate grey").grid(column=3, row=2, sticky="WENS")
        Button(window, text="ENTER", wraplength=1, command=lambda: loadActiveWindow.load("ENTER"), font=(textFont, 8),
               bg="light slate grey").grid(column=3, row=3, sticky="WENS")

#initializing Classes
canvas = background(root)   #Create Canvas Background
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

def updateScreen():

    if (measuredItemsValue[0] < 255): #For testing

        measuredItemsValue[0] += 1
    else:
        pass
    measuredItemsValue[1] = root.winfo_width()  # for debugging Purpose
    measuredItemsValue[2] = root.winfo_height()  # for debugging Purpose

    loadActiveWindow.load(loadActiveWindow.get())
    root.after(50, updateScreen) #update Screen every 50ms
    #if Testmode != True:
        #do soemthing
    #oscSend()



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



loadActiveWindow.load("MAIN")
updateScreen()
oscSend()
root.mainloop()
