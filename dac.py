class DACError(Exception):
    pass


class DAC():
    ADDR = 0x62
    WRITEFAST   = 0b00
    WRITE       = 0b10
    WRITEEEPROM = 0b11
    OPMODE      = ( 0b00,   # normal mode
                    0b01,   # power down 1kOhm to gnd
                    0b10,   # power down 100kOhm to gnd
                    0b11)   # power down 500kOhm to gnd
    DACZERO     = 0b000000000000
    readBytes   = 5
    lsb5V       = 1.22 # milivolt
    lsb3V       = 0.73 
    verbose     = 1

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

    def getBStr(self, data, byteNum):
        byteData = data[byteNum]
        byteB = bin(byteData)[2:] # remove '0b' prefix
        return byteB


    def readEeprom(self, data = None):
        if data is None:
            data = self.read()

        eepromRdy   = self.getBStr(data, 0)[0]
        pwrMode     = self.getBStr(data, DAC.readBytes-2)[1:2]
        dacVal      = self.getBStr(data, DAC.readBytes-2)[4:]
        dacVal.append(self.getBStr(data, DAC.readBytes-1))
        return eepromRdy, pwrMode, dacVal

    def readDac(self, data = None):
        if data is None:
            data = self.read()
        pwrOnReset  = self.getBStr(data, 0)[1]
        pwrMode     = self.getBStr(data, 0)[5:6]
        dacVal      = self.getBStr(data, 1)
        dacVal.append(self.getBStr(data, 2)[0:3])
        return pwrOnReset, pwrMode, dacVal

    def writeFast(self, dacVal):
        if dacVal > 2**12:
            raise DACError("dacVal > 12-bits: ", dacVal)
        # send the msg twice
        # msg = bytes([dacVal, dacVal])
        msg = dacVal.to_bytes(2,byteorder='big')
        msg += msg
        self.sendDac(dacVal, msg)

    def writeEepromDac(self, dacVal):
        # b0 to b2: mode
        mode = DAC.WRITEEEPROM
        # all other bits in byte zero
        mode = mode << 5
        msg = bytes([mode])
        # next 2 bytes are for dacVal 
        # last 4 bits unused 
        dacBytes = (dacVal << 4).to_bytes(2,byteorder='big')
        msg += dacBytes
        # send msg twice 
        msg += msg
        self.sendDac(dacVal, msg)

    def sendDac(self, dacVal, msg):
        if DAC.verbose:
            print('Setting dac: ',dacVal )
            print('Sending: ', msg, ' bits: ', len(msg))
        self.io.pi.i2c_write_device(self.i2cHandle, msg)

    def setVolt(self, volt, eeprom = 0):
        if volt < 0 or volt > 5:
            raise DACError(volt, " not a valid DAC voltage")
        dacVal = int((volt*1000) / DAC.lsb5V)
        if DAC.verbose:
            print("Setting ", volt, " V")
        if eeprom:
            self.writeEepromDac(dacVal)
        else:
            self.writeFast(dacVal)

    def off(self, pwrMode = None):
        if pwrMode is None:
            pwrMode = DAC.OPMODE[-1]
        if DAC.verbose:
            print("Setting 0 V")
            print("PWR Mode: ", pwrMode)
        cmd = pwrMode << 4
        self.io.pi.i2c_write_device(self.i2cHandle, bytes([cmd, 0, cmd, 0]))

    @classmethod
    def binary(cls, num):
        b = bin(num)
        return b[2:]

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
    wait = input()
    dac.setVolt(2.0, eeprom = 1)
    print(dac.readEeprom())
    dac.off(DAC.OPMODE[-1])
