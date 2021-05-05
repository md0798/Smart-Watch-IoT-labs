import machine
import ssd1306
import time

i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4)) #i2c for oled 
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
adc = machine.ADC(0) # light sensor reading
while True:
	va = adc.read()# read adc value for light sensor
	va2 = va*256/1024 #convert value to 256 scale as contrast range from 0 to 256
	va = 256-va2 # as we have to dim when more light
	oled.contrast(int(va)) #set oled contrast
	oled.fill(0)
	oled.text('light: %s' %(va2),0,0) #show light sensor reading
	oled.show()
