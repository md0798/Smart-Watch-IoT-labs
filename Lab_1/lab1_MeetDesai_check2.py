import machine
import time

adc = machine.ADC(0)# define adc pin
pin = machine.PWM(machine.Pin(13)) #output pins
pin2 = machine.PWM(machine.Pin(15))
while True:
	va = adc.read() #read ADC value 
	pin.duty(va) # give ADC value to LED and piezo
	pin2.duty(va)

