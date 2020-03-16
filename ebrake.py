import time
class Ebrake():
    def __init__(self, io, pinMBrake, pinEBrake):
        self.io = io
        self.pinMBrake = pinMBrake
        self.pinEBrake = pinEBrake
        self.stateMBrake = 0 # open
        self.stateEBrake = 0
        self.flagBrake = 0  

    def setup(self, func = None):
        self.setOutputPin(self.pinEBrake)
        self.setInputPin(self.pinMBrake, func)

    def setInputPin(self, pin, func = None):
        if func is None:
            func = self.mBrakeCallback
        self.pinMBrake = pin
        # do not set pin to input, experimentally worse
        self.io.triggerCallback(pin, func, state = 2)

    def setOutputPin(self, pin):
        self.pinEbrake = pin
        self.io.setMode(pin, output = 1)
        self.io.write(pin, 1)

    def readMBrake(self):
        return self.io.read(self.pinMBrake)

    def setEbrake(self, state = 0):
        self.io.write(self.pinEBrake, state)
        self.stateEBrake = state
        self.flagBrake = state

    def mBrakeCallback(self, pin, level, tick):
        if pin != self.pinMBrake:
            return 
        # trigger is bouncy read pin to see if state changed
        state = self.readMBrake()
        if state != self.stateMBrake:
            self.flagBrake = state
            self.stateMBrake = state
            print(f'Level: {state}')
            print(f'tick : {tick}')
        # print('triggered callback, time: ',time.time())
        return level 

if __name__ == "__main__":
    
    try:
        from .rpi_interface import IO
    except Exception:
        from rpi_interface import IO
    
    print('Connecting to pi')
    gpio = IO()

    RELAY = 20 
    SENSE = 21

    ebrake = Ebrake(gpio, SENSE, RELAY)
    ebrake.setup()
    print("Ebrake: 1, OPEN")
    ebrake.setEbrake(1)
    wait = input("Hit enter to set Ebrake: 0 CLOSE")
    ebrake.setEbrake(0)
    print("waiting for 5 seconds")
    time.sleep(5)
    print("setting back to OPEN")
    ebrake.setEbrake(1)
    time.sleep(5)
