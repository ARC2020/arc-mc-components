import time
class Ebrake():
    ebrakeOn = 0
    ebrakeOff = 1
    def __init__(self, io, pinMbrake, pinEbrake):
        self.io = io
        self.pinMbrake = pinMbrake
        self.pinEbrake = pinEbrake
        self.stateMbrake = 0 
        self.stateEbrake = 0
        self.flagBrake = 0  

    def setup(self, func = None):
        self.setOutputPin(self.pinEbrake, 1)
        self.setInputPin(self.pinMbrake, func)

    def setInputPin(self, pin, func = None):
        if func is None:
            func = self.mbrakeCallback
        self.pinMbrake = pin
        self.stateMbrake = self.io.read(pin)
        # do not set pin to input, experimentally worse
        self.io.triggerCallback(pin, func, state = 2)

    def setOutputPin(self, pin, level):
        '''
        relay is active-low
        0 = normally-open switch closes 
        1 = normally-open switch open
        '''
        self.pinEbrake = pin
        self.io.setMode(pin, output = 1)
        self.io.write(pin, Ebrake.ebrakeOff)
        self.stateEbrake = self.io.read(pin)

    def readMbrake(self):
        return self.io.read(self.pinMbrake)

    def setEbrake(self, state = 0):
        '''
        relay is active-low
        0 = normally-open switch closes 
        1 = normally-open switch open
        '''
        self.io.write(self.pinEbrake, state)
        self.stateEbrake = state
        self.flagBrake = state

    def mbrakeCallback(self, pin, level, tick):
        # print('triggered callback, time: ',time.time())
        if pin != self.pinMbrake:
            return 
        # ebrake will trigger pin 
        # check if ebrake on
        if self.stateEbrake == Ebrake.ebrakeOn:
            return
        # trigger is bouncy read pin to see if state changed
        state = self.readMbrake() 
        if state != self.stateMbrake:
            self.flagBrake = state
            self.stateMbrake = state
            print("Manual brake engaged")
            print("Manual brake", "on" if state==0 else "off")
            print(f'State: {state}')
            print(f'tick : {tick}')
        
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
