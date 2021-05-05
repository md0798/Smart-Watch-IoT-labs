import machine
import time


pin = machine.Pin(0,machine.Pin.PULL_UP) #red led initialised
pin2 = machine.Pin(2,machine.Pin.PULL_UP) # blue led initialised
	


while True:
	
	for i in range(2): #for loop to blink led
		pin.value(0) # turn on both leds together
		pin2.value(0)
		time.sleep(1)# sleep for 1 second
		pin.value(1) # turn off red led
		time.sleep(1)
		
	for j in range(2):#for loop to blink led
		pin.value(0)
		pin2.value(1)
		time.sleep(1)# sleep for 1 second
		pin.value(1)
		time.sleep(1)
	

