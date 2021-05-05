import machine
import time
import ssd1306

hspi = machine.SPI(1, baudrate= 1500000, polarity = 1, phase =1) #spi interface for adxl345
cs = machine.Pin(15,machine.Pin.OUT)#chip select output at pin 15
i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))#i2c connection for oled
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
x_l = 45#initial x and y for string
y_l = 15
buf = bytearray(6) #buffer for accelerometer data
buf = list(buf) #list of buffer
cs.value(1) 
time.sleep_ms(50)
cs.value(0) #starting spi connection
hspi.write(b'\x21\x00') #initialising neccessary registers
hspi.write(b'\x31\x0F')
hspi.write(b'\x2d\x28')
hspi.write(b'\x2c\x0A')
hspi.write(b'\x2e\x00')
hspi.write(b'\x38\x9F')

cs.value(1)
time.sleep_ms(50)
cs.value(0) #restarting spi connection

st = 'Hello' #string to be displayed

def Xaxes(): #get Xaxes data from accelerometer
	hspi.write(b'\xB3') # writing the address of register from which data is required
	buf[0]=hspi.read(1)#reading the MSB X axes data
	buf[0] = int.from_bytes(buf[0],'big') #converting the X axes byte data to int
	hspi.write(b'\xB2')
	buf[1] = hspi.read(1)#reading LSB X axes data
	buf[1] = int.from_bytes(buf[1],'big')#converting the byte data to int
	x_a = buf[0:2]#making a list of MSB,LSB data of xaxes
	x_a = bytearray(x_a)# converting data to byte to get the value of 2 bytes together
	x_a = int.from_bytes(x_a,'Big')#converting 2 bytes of data to int 
	#print(x_a)
	return x_a # returing final int value of x axes data
	
def yaxes(): #similar to xaxes for y axes data
	hspi.write(b'\xB5')
	buf[2]=hspi.read(1)
	buf[2] = int.from_bytes(buf[2],'big')
	hspi.write(b'\xB4')
	buf[3] = hspi.read(1)
	buf[3] = int.from_bytes(buf[3],'big')
	y_a = buf[2:4]
	y_a = bytearray(y_a)
	y_a = int.from_bytes(y_a,'Big')
	#print(y_a)
	return y_a
	
def zaxes(): #similar to x axes for z axes data
	hspi.write(b'\xB7')
	buf[4]=hspi.read(1)
	buf[4] = int.from_bytes(buf[4],'big')
	hspi.write(b'\xB6')
	buf[5] = hspi.read(1)
	buf[5] = int.from_bytes(buf[5],'big')
	z_a = buf[4:6]
	z_a = bytearray(z_a)
	z_a = int.from_bytes(z_a,'Big')
	#print(z_a)
	return z_a
	

while True: #main loop
	x = Xaxes() # getting x,y,z axes data
	y = yaxes()
	z = zaxes()
	print(x,y,z)
	oled.fill(0)
	oled.text('%s'%(st),x_l,y_l) #printing string on oled display
	oled.show()
	l = len(st) #getting the length of string
	if x==0 and y==0: #initial condition text should not move
		print("start")
	elif x>32768 and y>32678: # a value >32768 implies its negative since the data is in 2s complement
		print("Down")
		y_l +=5 # increment y axis display if acclerometer goes down
		if y_l > 32: # if display goes beyond limit of screen reset to 0
			y_l = 0
	elif x<32678 and y>32678:
		print("Right")
		x_l += 10 #increment x axis display if acclerometer goes right
		if x_l >128:#if it goes out of display
			x_l = -(l*8) #8 pixels is approx lenght of 1 character, multiply by lenght of string and start text from there
	elif x<32678 and y<32678:
		print("Up")
		y_l -=5
		if y_l<0:
			y_l = 32
	elif x>32678 and y<32678:
		print("Left")
		x_l -=10
		if x_l<-(l*8):
			x_l = 128
	
	time.sleep(1.5) #time delay
	
