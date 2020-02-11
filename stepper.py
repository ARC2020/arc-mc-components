from math import floor


class StepperError(Exception):
    pass

class Stepper():
    sMicrostep = (None, 1, 2, 2, 4, 8, 16, 32) # this might be wrong, confusing from uCtrl label
    sPulsePerRev = (None, 200, 400, 800, 1600, 3200, 6400)
    sCurrent = (0.5, 1.0, 1.5, 2.0, 2.5, 2.8, 3.0, 3.5)
    sPkCurrent = (0.7, 1.2, 1.7, 2.2, 2.7, 2.9, 3.2, 4.0)
    numSwitches = 6

    def __init__(self):
        self.rgSwitches = [0] * Stepper.numSwitches
        self.bEna = 0
        self.bDir = 0
        self.bPul = 0 
        self.pulsePerRev = Stepper.sPulsePerRev[0]

    def setEna(self, state):
        self.bEna = state

    def setDir(self, state):
        self.bDir = state

    def setPul(self, state):
        self.bPul = state

    def setPort(self, port):
        '''
        some way to set ENA,DIR,PUL pins?
        '''
        pass

    def setPulsePerRev(self, ppr):
        if ppr not in Stepper.sPulsePerRev:
            raise(StepperError("{} not a valid pulse per revolution".format(ppr)))
        else:
            self.pulsePerRev = ppr

    def calcPulses(self, degree):
        pulses = degree*self.pulsePerRev/360
        return abs(floor(pulses))
    
    def rotateDegrees(self, degree):

        # check direction
        # need to double check direction mapping 
        if degree > 0:
            self.bDir = 1
        else:
            self.bDir = 0

        # get number of pulses to drive 
        pulses = self.calcPulses(degree)

        # ok now set direction and pulse somehow 

        print("pulses: ", pulses, " direction: ", self.bDir)
        


if __name__ == "__main__":
    # testing 
    stepper = Stepper()
    stepper.setPulsePerRev(400)
    stepper.rotateDegrees(36)
    stepper.rotateDegrees(-36)
    stepper.setPulsePerRev(300)