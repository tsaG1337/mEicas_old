# mEicas
This is the basic demonstration Software for the mEICAS Flight computer

The code for the ADC-Board (MCU) is using the Arduino framework and is (mostly) written in C.

The Code for the Raspberry is written in basic Python 2 and uses the Tkinter Framework.

For further Updates visit https://github.com/tsaG1337/mEicas




## Setup Values

The demonstrator Software has the following flags to control the initialization or runtime of the program:

```python
testmode = False
```
If testmode is set to true the I2C, GPIO Support and fullscreen mode is disabled and the mouse pointer is activated.
Thereby it is possible to run the software on workstations such as Mac or Windows PCs.

```python
invertedScreenColor = True
```
Due to a error in the electric circuit or a driver issue (still not resolved) the color of the display is reversed.
By setting this flag to True (default) the software will use reverse colors to keep the color sheme as desired.


## Starting the demo software

If you are running the mEICAS headless:
To start this python script from a SSH Terminal first bind your terminal to the Display by using

```
export &DISPLAY=:1.0
```

This could also be "0.0", depending on how many sessions you opened.

to start the script just type

```
sudo DISPLAY=:1.0 python Main.py
```
mEicas
2015-2016
by Patrick Bihn 
