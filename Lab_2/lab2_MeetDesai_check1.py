import machine
import ssd1306
import time
pinA = machine.Pin(0,machine.Pin.IN)
pinB = machine.Pin(16,machine.Pin.IN)#input for buttons
pinC = machine.Pin(2,machine.Pin.IN)
i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))#i2c for oled
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
rtc = machine.RTC()#rtc to set time
rtc.datetime((2021, 2, 3, 1, 10, 0, 0, 0))

while True:
	a,b,c,d,e,f,g,h = rtc.datetime()#getting variables from rtc tuple
	if (pinA.value() and pinB.value() and pinC.value()):#checking if any button is pressed
		oled.fill(0)
		oled.text('%s:%s:%s' %(e,f,g),0,0)# display time
		oled.show()
	else:
		if pinA.value()-1: # if button A is pressed
			e +=1 # increase hour by 1
			rtc.datetime((2021, 2, 3, 1, e, f, g, h))
			time.sleep(1)
		elif pinB.value() -1:#if button B is pressed
			f +=1 #increase minute by 1
			if f>=60:#if minute is greater than 60
				e += 1 #increase hour by 1
				f = 0 # set minute to 0
			rtc.datetime((2021, 2, 3, 1, e, f, g, h))
			time.sleep(1)
		elif pinC.value()-1:#if button C is pressed
			e -= 1 #decrease hour by 1
			rtc.datetime((2021, 2, 3, 1, e, f, g, h))
			time.sleep(1)
