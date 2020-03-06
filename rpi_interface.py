import pigpio # library to contriol rpi pins
from time import sleep


class IO():
    ''''
    pin: 0 to 53 based off of pi broadcom number
    KC: other funtionality to add? watchdog for pin
    '''
    def __init__(self, host = None, port = None):
        if host is None:
            self.pi = pigpio.pi()
        else:
            self.pi = pigpio.pi(host, port)

    def setMode(self, pin, output = 1):
        if output:
            self.pi.set_mode(pin, pigpio.OUTPUT)
        else:
            self.pi.set_mode(pin, pigpio.INPUT) 

    def getMode(self, pin):
        '''
        0 = INPUT
        1 = OUTPUT
        Any other number is an ALT pin
        '''
        return self.pi.get_mode(pin)
        
    def setInputMode(self, pin, pullup = 1):
        '''
        0 = pulldown
        1 = pullup
        else off
        KC: check if pin set to be input?
        '''
        if pullup == 0:
            self.pi.set_pull_up_down(pin, pigpio.PUD_DOWN)

        elif pullup == 1:
            self.pi.set_pull_up_down(pin, pigpio.PUD_UP)
        else:
            self.pi.set_pull_up_down(pin, pigpio.PUD_OFF)

    def read(self, pin):
        return self.pi.read(pin)

    def write(self, pin, level):
        self.pi.write(pin, level)

    def toggle(self, pin):
        '''
        pin must be set as output for this to work
        '''
        state = self.read(pin)
        state ^= 1 # performs xor operation with 1
        self.write(pin, state)


    def disconnect(self):
        self.pi.stop()

    def clkStart(self, pin, freq):
        '''
        sets pin to output low if not already set
        uses the PWM functionality w 50% duty cycle
        at the corresponding frequency
        '''

        # output zero 
        if self.getMode(pin) != 1:
            self.setMode(pin)
        
        self.write(pin, 0)

        # set duty cycle to 50% out of 8 bit number
        self.pi.set_PWM_dutycycle(pin, 128)

        # the frequency is hardcoded so it pick the closest freq
        self.pi.set_PWM_frequency(pin, freq)

    def clkStop(self, pin):
        self.pi.set_PWM_dutycycle(pin, 0)

    def triggerCallback(self, pin, func, state = 1):
        '''
            Calls a user supplied function(callback) whenever state detected on pin
            states:
                0 = falling edge 
                1 = rising edge 
                2 = either 0 or 1 
            Callback function recieves: gpio, level, tick
            gpio: 0 to 31
            level:
                0 = falling edge 
                1 = rising edge
                2 = watchdog timeout 
            tick: 32 bit number of microseconds since boot, count restarts every 72 minutes
        '''
        states = [pigpio.FALLING_EDGE, pigpio.RISING_EDGE, pigpio.EITHER_EDGE]
        self.pi.callback(pin, states[state], func)
        
    def sendPulses(self, pin, numPulse, freq):

        self.write(pin, 0)
        delay = (2*freq)**-1
        for i in range(numPulse):
            sleep(delay)
            self.write(pin, 1)
            sleep(delay)
            self.write(pin, 0)

    def getFreq(self, pin):
        return self.pi.get_PWM_frequency(pin)

    def calcRamp(self, steps):
        startFreq = 500
        endFreq = 4300
        increments = 10
        incFreq = (endFreq - startFreq)//increments
        ramp = [0]*(increments+1)
        numSteps = steps//(2*increments)
        countSteps = steps
        countFreq = startFreq
        for i in range(increments):
            pair = [countFreq, numSteps] 
            ramp[i] = pair
            countSteps -= numSteps
            countFreq  += incFreq
        # populate remainder in last step
        ramp[-1] = [endFreq, countSteps]
        return ramp

    def generateRamp(self, pin, ramp):
        '''
        Generate ramp wave forms.
        ramp:  List of [Frequency, Steps], max length 20 
        Steps: 0 to 65535
        '''
        self.pi.wave_clear()     # clear existing waves
        length = len(ramp)  # number of ramp levels
        wid = [-1] * length

        # Generate a wave per ramp level
        for i in range(length):
            frequency = ramp[i][0]
            micros = int(500000 / frequency)
            wf = []
            wf.append(pigpio.pulse(1 << pin, 0, micros))  # pulse on
            wf.append(pigpio.pulse(0, 1 << pin, micros))  # pulse off
            self.pi.wave_add_generic(wf)
            wid[i] = self.pi.wave_create()

        # Generate a chain of waves
        chain = []
        for i in range(length):
            steps = ramp[i][1]
            x = steps & 255
            y = steps >> 8
            chain += [255, 0, wid[i], 255, 1, x, y]

        self.pi.wave_chain(chain)  # Transmit chain.

if __name__ == "__main__":

    # Set GPIO17/PIN11 for DIR control 
    DIR = 17
    
    # Set GPIO27/PIN13 for PUL control 
    PUL = 27

    dut = IO()
    #  Configure pins 
    dut.setMode(DIR)
    dut.setMode(PUL)

    # set both low 
    dut.write(DIR, 0)
    dut.write(PUL, 0)

    # test toggle
    dut.toggle(DIR)
    sleep(1)
    dut.toggle(DIR)

    # test clk function
    dut.clkStart(PUL, 10)
    dut.sendPulses(DIR, 100, 10)
    # sleep(10)
    dut.clkStop(PUL)

    # test ramp function
    dut.generate_ramp(PUL, [
        [320, 200],
	    [500, 400],
	    [800, 500]])
    
    dut.disconnect()
