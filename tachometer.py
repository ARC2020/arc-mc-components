from numpy import diff, mean

verbose = 0

class Tachometer():
    def __init__(self, io, pin, circ = 2055):
        self.io = io
        self.pin = pin
        self.circ = circ
        self.t1 = 0
        self.speed = 0

    def setup(self, func = None):
        if func is None:
            func = self.tachCallback 
        self.io.triggerCallback(self.pin, func, state = 1)

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
        if pin != self.pin:
            return 
        # maybe add some signal processing
        if verbose:
            print(f"t1: {self.t1} tick: {tick}")
            print(f"level: {level}")
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

    print('Setting up tach')
    tach = Tachometer(gpio, TACH)
    tach.setup()
    wait = 100
    print(f"waiting for {wait} seconds")
    time.sleep(wait)

