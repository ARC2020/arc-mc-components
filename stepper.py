from math import floor

class StepperError(Exception):
    pass

class Stepper():
    sMicrostep = (None, 1, 2, 2, 4, 8, 16, 32) # this might be wrong, confusing from uCtrl label
    sPulsePerRev = (None, 200, 400, 800, 1600, 3200, 6400)
    sCurrent = (0.5, 1.0, 1.5, 2.0, 2.5, 2.8, 3.0, 3.5)
    sPkCurrent = (0.7, 1.2, 1.7, 2.2, 2.7, 2.9, 3.2, 4.0)
    gearboxRatio = 77    
    numSwitches = 6

    def __init__(self, io, pinDir, pinPul, pinEna = None):
        self.io = io
        self.pinDir = pinDir
        self.pinPul = pinPul
        self.pinEna = pinEna
        self.pulsePerRev = Stepper.sPulsePerRev[0]

    def setupPin(self, pin):
        '''
        uses rpi IO to set pin to output
        '''
        self.io.setMode(pin)

    def setup(self):
        '''
        intializes pul and dir pins and sets them low
        '''
        self.setupPin(self.pinDir)
        self.setPin(self.pinDir, 0)
        self.setupPin(self.pinPul)
        self.setPin(self.pinPul, 0)


    def setPin(self, pin, state):
        '''
        general way to set pin
        '''
        self.io.write(pin, state)

    def getPin(self, pin):
        return self.io.read(pin)

    def toggleDir(self):
        self.io.toggle(self.pinDir)

    def setPulsePerRev(self, ppr):
        if ppr not in Stepper.sPulsePerRev:
            raise(StepperError("{} not a valid pulse per revolution".format(ppr)))
        else:
            self.pulsePerRev = ppr

    def calcPulses(self, degree):
        stepAngle = 360/(self.pulsePerRev*Stepper.gearboxRatio)
        pulses = degree/stepAngle
        return abs(floor(pulses))
    
    def rotate(self, degree):

        # check direction
        # need to double check direction mapping 
        if degree > 0:
            bDir = 1
        else:
            bDir = 0

        # get number of pulses to drive 
        pulses = self.calcPulses(degree)

        # ok now set direction and pulse somehow 
        print("pulses: ", pulses, " direction: ", bDir)
        self.setPin(self.pinDir, bDir)
        if pulses > 8000:
            ramp = self.io.calcRamp(pulses)
            print(ramp)
            self.io.generateRamp(self.pinPul, ramp)
        else: 
            self.io.sendPulses(self.pinPul, pulses, 800)


if __name__ == "__main__" and __package__ is None:
    # testing 
    #from os import sys, path
    #sys.path.append(path.dirname(path.abspath(__file__)))
    import time
    try:
        from .rpi_interface import IO
    except Exception:
        from rpi_interface import IO
    # Set GPIO17/PIN11 for DIR control 
    DIR = 17
    
    # Set GPIO27/PIN13 for PUL control 
    PUL = 27

    gpio = IO()
    stepper = Stepper(gpio, pinDir=DIR, pinPul=PUL)
    stepper.setup()
    #stepper.gearboxRatio = 1
    stepper.setPulsePerRev(200)
    wait = input()
    start = time.time()
    stepper.rotate(360)
    print("elapsed time: ",time.time()-start)
    wait = input()
    stepper.rotate(-36)
    wait = input()
    stepper.rotate(36)
      
    
