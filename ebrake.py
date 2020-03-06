class Ebrake():
    def __init__(self, io, pinMBrake, pinEBrake):
        self.io = io
        self.pinMBrake = pinMBrake
        self.pinEBrake = pinEBrake 

    def setup(self, func = None):
        self.setInputPin(self.pinMBrake, func)
        self.setOutputPin(self.pinEBrake)

    def setInputPin(self, pin, func = None):
        if func is None:
            func = self.mBrakeCallback
        self.pinMBrake = pin
        self.io.triggerCallback(pin, func, state = 2)

    def setOutputPin(self, pin):
        self.pinEbrake = pin
        self.io.getMode(pin, output = 1)

    def readMBrake(self):
        return self.io.read(self.pinMBrake)

    def setEbrake(self, on = 1):
        self.io.write(self.pinEBrake, on)

    def mBrakeCallback(self, pin, level, tick):
        if pin != self.pinMBrake:
            return 
        if level == 1:
            # rising edge occured, notify pi 
            # raise flag?
            pass
        if level == 0:
            # falling edge
            # notify pi 
            pass
        return level 
