import machine
import ssd1306
import time
pinA = machine.Pin(0,machine.Pin.IN)#same method used in c4.py
pinB = machine.Pin(16,machine.Pin.IN)
pinC = machine.Pin(2,machine.Pin.IN)
pin = machine.PWM(machine.Pin(12)) #output pins
pin2 = machine.PWM(machine.Pin(13))
i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
rtc = machine.RTC()
rtc.datetime((2021, 2, 3, 1, 10, 0, 0, 0))

k=0
j=0
l=0

def alarm():
	pin.duty(1023)
	pin2.duty(1023)
	time.sleep(10)
	pin.duty(0)	
	pin2.duty(0)

while True:
	a,b,c,d,e,f,g,h = rtc.datetime()
	if pinB.value():
		oled.fill(0)
		oled.text('%s:%s:%s' %(e,f,g),0,0)
		oled.show()
		if f==k and e==j and g==l:
			alarm()
	else:
		k = f
		j = e
		l = g
		while True:
			oled.fill(0)
			oled.text('Set alarm',0,0)
			oled.text('%s:%s:%s' %(j,k,l),0,10)
			oled.show()
			time.sleep(0.2)
			if pinA.value() -1:
				k +=1
				if k==60:
					j +=1
					k = 0
				time.sleep(0.5)#prevent multiple reading
			elif pinC.value() -1:
				k -= 1
				if k<0:
					j -=1
					k = 59
				time.sleep(0.5)	
			if pinB.value() -1:
				time.sleep(0.1)
				break
		
		time.sleep(0.5)	
