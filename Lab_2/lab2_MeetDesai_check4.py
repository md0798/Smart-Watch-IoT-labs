import machine
import ssd1306
import time
pinA = machine.Pin(0,machine.Pin.IN) # Pins for buttons A,B and C
pinB = machine.Pin(16,machine.Pin.IN)
pinC = machine.Pin(2,machine.Pin.IN)
pin = machine.PWM(machine.Pin(12)) #output pins for led and piezo
pin2 = machine.PWM(machine.Pin(13))
i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4)) #i2c for oled
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
rtc = machine.RTC() #rtc time set
rtc.datetime((2021, 2, 3, 1, 10, 0, 0, 0)) #time set to 10:0:0 date - 3/2/2021
adc = machine.ADC(0) # adc input for light sensor

k=0
j=0
l=0

def alarm():
	pin.duty(1023) #when alarm is raised led and piezo is on
	pin2.duty(1023)
	time.sleep(10) # wait 10 seconds before turning alarm off
	pin.duty(0)	
	pin2.duty(0)

while True:
	va = adc.read() #read light sensor value
	va2 = va*256/1024 #convert value to 256 scale as contrast range from 0 to 256
	va = 256-va2 # as we have to dim when more light
	oled.contrast(int(va)) #set oled contrast
	a,b,c,d,e,f,g,h = rtc.datetime() #extract all individual values from tuple
	if (pinA.value() and pinB.value() and pinC.value()): # keep checking if any button is pressed
		oled.fill(0) 
		oled.text('%s:%s:%s' %(e,f,g),0,0) #display time
		oled.text('light: %s' %(va2),0,10) # display light sensor reading
		oled.show()
		if f==k and e==j and g==l: # start alarm if set alarm value matches current time
			alarm()
	elif pinA.value()-1: # if button A is pressed
			f +=1 #increase hour time
			if f>=60:
				e+=1
				f=0
			rtc.datetime((2021, 2, 3, 1, e, f, g, h))
			time.sleep(1)
		
	elif pinC.value()-1:#if button C is pressed
			f -= 1 #decrease hour time
			if f<0:
				e-=1
				f=59
			rtc.datetime((2021, 2, 3, 1, e, f, g, h))
			time.sleep(1)
		
	elif pinB.value()-1: #if button B is pressed enter alarm set mode
		k = f # get value of time when B is pressed
		j = e
		l = g
		while True:
			oled.fill(0)
			oled.text('Set alarm',0,0)
			oled.text('%s:%s:%s' %(j,k,l),0,10)#show alarm time to be set
			oled.show()
			time.sleep(0.2)
			if pinA.value() -1:#if A is pressed increase minute by 1
				k +=1
				if k==60:#if minute goes over 60 then increase hour
					j +=1
					k = 0
				time.sleep(0.5)#prevent multiple reading
			elif pinC.value() -1: #if C is pressed decrease minute by 1
				k -= 1
				if k<0:#if minute goes below 0
					j -=1 #decrease hour by 1
					k = 59 # set minute to 59
				time.sleep(0.5)	
			if pinB.value() -1: # if B is pressed then set the current alarm time
				time.sleep(0.1)
				break
		
		time.sleep(0.5) 
