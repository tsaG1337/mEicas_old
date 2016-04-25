### ISL9023 Python Module
import smbus, array

CMD1 = 0
CMD2 = 1
DATALSB = 2
DATAMSB = 3

i2cbus = smbus.SMBus(1)
i2cdata = array.array('H',[0,0,0])

# define class
class isl:
    def __init__(self,address):
         global dev_address
         dev_address = address
         i2cdata[0] = CMD1
         i2cdata[1] = 0b10100000
         i2cbus.write_byte_data(dev_address, i2cdata[0], i2cdata[1])

         i2cdata[0] = CMD2;
         i2cdata[1] = 0b00000011
         i2cbus.write_byte_data(dev_address, i2cdata[0], i2cdata[1])

    def read(self):
        MSB = i2cbus.read_byte_data(dev_address, DATAMSB)   #Read most Significant Byte
        LSB = i2cbus.read_byte_data(dev_address, DATALSB)   #Read least Significant Byte
        light = ((MSB<<8) + LSB)
        return (64000 * light)/65536    #convert and return the value in Lux
