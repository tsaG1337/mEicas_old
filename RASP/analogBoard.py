### ISL9023 Python Module
import smbus, array

#Register Pointer Bytes


i2cbus = smbus.SMBus(1)

# define class
class init:
    def __init__(self,address):
         global dev_address
         dev_address = address

    def getDeviceName(self):   
        #10 byte
        i2cdataString = ["0","0","0","0","0","0","0","0","0","0"]
        i2cdata = [0,0,0,0,0,0,0,0,0,0]
        for i in range(0,10):
            i2cdata[i] = i2cbus.read_byte_data(dev_address, 0x01)
            i2cdataString[i] = chr(i2cdata[i])
        returnString = ""
        returnString = ''.join(i2cdataString)
        return returnString

    def getID(self):
        ID = i2cbus.read_byte_data(dev_address, 0x02)
        return ID

    def getHardwareID(self):
        hardVersion = i2cbus.read_byte_data(dev_address, 0x03)
        return hardVersion

    def getSoftwareID(self):
        softVersion = i2cbus.read_byte_data(dev_address, 0x04)
        return softVersion

    def getInputVoltage(self):
        voltage = i2cbus.read_word_data(dev_address, 0x05)
        return voltage

    def readNTC(self, number):
        NTCVal = i2cbus.read_word_data(dev_address, (number+0x05))
        return NTCVal

    def PressNTC(self, number):
        PressVal = i2cbus.read_word_data(dev_address, (number + 0x12))
        return PressVal

    def readTacho(self, number):
        TachoVal = i2cbus.read_word_data(dev_address, (number + 0x14))
        return TachoVal

    def getChargeStat(self):
        ChargeStat = i2cbus.read_byte_data(dev_address, 0x16)
        return ChargeStat

    def getBatteryStat(self):
        BatteryStat = i2cbus.read_byte_data(dev_address, 0x17)
        return BatteryStat

    def getMstCtn(self):
        MstCtnVal = i2cbus.read_byte_data(dev_address, 0x18)
        return MstCtnVal

    def setMstCtn(self, val):
        i2cbus.write_byte_data(dev_address, 0x18, val)

