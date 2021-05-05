import machine
import time

pin2 = machine.Pin(14,machine.Pin.IN) # Take input from pin 14

def debounce(pin2):
	cur_value = pin2.value() # getting current value
    	active = 0 #counter
    	while active < 20: #counter 20ms
        	if pin2.value() != cur_value:#check if the pin is same as before
        	    active += 1 #increase counter
        	else:
        	    active = 0
        	time.sleep(0.001)# sleep 1ms
	if pin2.value(): # check if button is pressed
		print("Button is pressed")
	else:
		print("Not pressed")	
	
while True:
	pin2.irq(trigger=machine.Pin.IRQ_RISING | machine.Pin.IRQ_FALLING, handler=debounce)# trigger interrupt when button is pressed
		
