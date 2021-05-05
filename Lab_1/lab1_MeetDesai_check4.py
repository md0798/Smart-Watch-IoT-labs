import machine
import time

global adc, pin_pi, pin_led,pin2
adc = machine.ADC(0)
pin_pi = machine.PWM(machine.Pin(13))
pin_led = machine.PWM(machine.Pin(15))
pin2 = machine.Pin(14,machine.Pin.IN)
		
def inte(pin1):

	cur_value = pin2.value() #debounce 
    	active = 0
    	while active < 20:
        	if pin2.value() != cur_value:
        	    active += 1
        	else:
        	    active = 0
        	time.sleep(0.001)

	while pin2.value(): # when button is pressed adc value is given to led and piezo
		va = adc.read()
		pin_pi.duty(va)
		pin_led.duty(va)
	
	pin_pi.duty(0) #when button is not pressed turn off peizo and led
	pin_led.duty(0)

while True:
	pin2.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=inte) #interrupt is generated when button is pressed or released
