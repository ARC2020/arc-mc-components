from numpy import diff, mean
from time import sleep
verbose = 1

class Tachometer():
    def __init__(self, io, sensePin, buttonLeft, pwr, circ = 2055):
        self.io = io
        self.sensePin = sensePin
        self.buttonLeft = buttonLeft
        self.pwr = pwr
        self.circ = circ
        self.t1 = io.pi.get_current_tick()
        self.speed = 0

    def on(self):
        self.io.write(self.pwr, 1)

    def off(self):
        self.io.write(self.pwr, 0)

    def pwrSetup(self, bootWait = 3.5, sleepWait = 0.8):
        self.io.setMode(self.pwr, output = 1)
        state = self.io.read(self.pwr)
        if state == 1:
            self.off()
            sleep(sleepWait)
        self.on()
        sleep(bootWait)

    def reboot(self, bootWait = 3.5, sleepWait = 0.8):
        self.off()
        sleep(sleepWait)
        self.on()
        sleep(bootWait)
        self.buttonSetup(14)

    def wakeup(self):
        '''
        use if tach unresponsive, tach will fall asleep if no activity occurs for 300 seconds
        '''
        self.io.sendPulses(self.buttonLeft, numPulse = 1, freq = 5)

    def setup(self, func = None):
        self.pwrSetup()
        self.buttonSetup(14)
        if func is None:
            func = self.tachCallback 
        self.io.triggerCallback(self.sensePin, func, state = 1)
        self.io.pi.set_watchdog(self.sensePin, 60000) # max amount watchdog can wait: 60s

    def buttonSetup(self, pulses):
        self.io.setMode(self.buttonLeft, output = 1)
        self.io.write(self.buttonLeft, 1)
        self.io.sendPulses(self.buttonLeft, numPulse = 14, freq = 5)

    def tickToMilisecond(self, tick):
        return tick//1000 # // = integer division

    def rpmToKmh(self, rpm):
        return  rpm*3.6 #  to convert to km/hr

    def calcRPM(self, times):
        timeDelta = diff(times)
        timeAvg = mean(timeDelta)
        timeAvg = self.tickToMilisecond(timeAvg)
        return self.circ/timeAvg # m/s

    def tachCallback(self, pin, level, tick):
        if pin != self.sensePin:
            return 
        # maybe add some signal processing
        if verbose:
            print(f"t1: {self.t1} tick: {tick}")
            print(f"level: {level}")
        if level == 2: # watchdog timeout 
            print("watchdog timeout")
            self.wakeup()
            return
        self.rpm = self.calcRPM([self.t1, tick])
        kmh = self.rpmToKmh(self.rpm)
        print(f"Speed {self.rpm} m/s, {kmh} km/hr")
        self.t1 = tick

if __name__ == "__main__":
    import time
    try:
        from .rpi_interface import IO
    except Exception:
        from rpi_interface import IO

    print('Connecting to pi')
    gpio = IO()

    TACH = 21
    BUTTON = 20

    print('Setting up tach')
    tach = Tachometer(gpio, TACH, BUTTON)
    tach.setup()
    wait = 100
    print(f"waiting for {wait} seconds")
    time.sleep(wait)

