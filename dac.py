class DACError(Exception):
    pass


class DAC():
    ADDR = 0x62
    WRITEFAST   = 0b00
    WRITE       = 0b010
    WRITEEEPROM = 0b011
    OPMODE      = ( 0b00,   # normal mode
                    0b01,   # power down 1kOhm to gnd
                    0b10,   # power down 100kOhm to gnd
                    0b11)   # power down 500kOhm to gnd
    DACZERO     = 0b000000000000
    readBytes   = 5
    lsb5V       = 1.22 # milivolt
    lsb3V       = 0.73 

    def __init__(self , io, i2cMode = 1):
        # i2c is either 0 or 1 corresponding to i2c pins on rpi
        self.io = io
        self.i2cMode = i2cMode


    def setup(self):
        self.i2cHandle = self.io.pi.i2c_open(self.i2cMode, DAC.ADDR)

    def read(self):
        (numByte, readData) = self.io.pi.i2c_read_device(self.i2cHandle, DAC.readBytes)
        if numByte != DAC.readBytes:
            raise DACError('Did not read back correctly, instead read {} bytes and data: {}'.format(numByte, readData))
        return readData

    def readEeprom(self, data = None):
        if data is None:
            data = self.read()

        eepromRdy   = data[0][0]
        pwrMode     = data[DAC.readBytes-2][1:2]
        dacVal      = data[DAC.readBytes-2][4:]
        dacVal.append(data[DAC.readBytes-1])
        return eepromRdy, pwrMode, dacVal

    def readDac(self, data = None):
        if data is None:
            data = self.read()
        pwrOnReset  = data[0][1]
        pwrMode     = data[0][5:6]
        dacVal      = data[1]
        dacVal.append(data[2][0:3])
        return pwrOnReset, pwrMode, dacVal

    def writeFast(self, dacVal = None, pwrMode=None):
        if dacVal is None:
            dacVal = DAC.DACZERO
        if pwrMode is None:
            pwrMode = DAC.OPMODE[0]
        #data = DAC.WRITEFAST << 2
        #data = data | pwrMode
        #data = (data << 12) | dacVal
        # repeat data again in message 
        data = bin(dacVal)
        data = data[2:]
        size = len(data)
        if size < 12:
            data = '0'*(12-size)+data
        msg = '0000'+data
        #msg = (data << 16) | data
        msg = msg + msg
        print(msg)
        print(len(msg))
        #msgBin = bin(msg)
        #msgBin = msgBin[2:]
        #print(msgBin)
        self.io.pi.i2c_write_device(self.i2cHandle, msg)

    def setVolt(self, volt):
        if volt < 0 or volt > 5:
            raise DACError(volt, " not a valid DAC voltage")
        dacValue = int((volt*1000) / DAC.lsb5V)
        print(dacValue)
        print(bin(dacValue))
        self.writeFast(dacValue)

    def off(self):
        self.writeFast(pwrMode=DAC.OPMODE[-1])

if __name__ == "__main__":
    try:
        from .rpi_interface import IO
    except Exception:
        from rpi_interface import IO
    print('Connecting to pi')
    gpio = IO()
    print('DAC init')
    dac = DAC(gpio)
    print('DAC setup')
    dac.setup()
    #print('Read DAC')
    #print(dac.readDac())
    #print('Read EEProm')
    #print(dac.readEeprom())
    #wait = input()
    print('Setting 1.0V')
    dac.setVolt(1.0)
    #print(dac.readDac())
