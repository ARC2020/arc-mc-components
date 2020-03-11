from .dac import DAC

class ThrottleError(Exception):
    pass


class Throttle():
    vref = 5
    def __init__(self, io, pin, pwm):
        '''exit
        pwm = 0 for DAC output
        pwm = 1 for PWM output 
        '''
        self.io = io
        self.pin = pin 
        self.pwm = pwm
        self.maxV = 3.7
        self.minV = 0.7

    def setup(self):
        if self.pwm:
            self.io.setMode(self.pin)
            self.io.write(self.pin, 0)

        else:
            self.dac = DAC(self.io)
            self.dac.setup()

    def setVolt(self, volt):
        if volt < self.minV or volt > self.maxV:
            raise ThrottleError('Volt out of bound: ', volt, ' V')

        if self.pwm:
            duty = self.calcDuty(volt)
            self.pwmWrite(duty)

        else:
            self.dacWrite(volt)

    def calcDuty(self, volt):
        return int(volt/Throttle.vref * (2**8-1))

    def off(self):
        if self.pwm:
            self.pwmWrite(0)
        else:
            self.dac.off()

    def pwmWrite(self, duty, freq = 1000):
        if duty == 0: 
            self.io.pwmStop(self.pin)
        else:
            self.io.pwmStart(self.pin, duty, freq)

    def dacWrite(self, volt):
        self.dac.setVolt(volt)
    

if __name__ == "__main__":
    try:
        from .rpi_interface import IO
    except Exception:
        from rpi_interface import IO
    
    print('Connecting to pi')
    gpio = IO()
    
    # pwm setup 
    PWM = 2
    gpio = IO()
    throttle = Throttle(gpio, PWM, 1)
    print("throttle setup")
    throttle.setup()
    print("set 2V")
    throttle.setVolt(2)
    wait = input()
    print("set 3.7V")
    throttle.setVolt(3.7)
    wait = input()
    throttle.off()