
import gc
import network
import urequests as requests
import ujson as json
import ustruct as struct
import machine
import ssd1306
import time

try:
	import usocket as socket
except:
	import socket

# Settings for WiFi
settings = {
	"wifi_name": '',
	"wifi_pass": ''
}

# Port Initializations
i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
accel = machine.SPI(1, baudrate=1500000, polarity=1, phase=1)
cs_pin = machine.Pin(15, machine.Pin.OUT)

# Setup for button press, matching it with the letter for training/predict
pos_check = 0
word = "COLUMBIA"
mode_button = 0
mode_label = ["training", "predict"]
record = 0
record_label = ["no", "yes"]


def twos_complement(val, nbits):
	'''
	Compute the 2's complement of int value val
	'''
	if val < 0:
		val = (1 << nbits) + val
	else:
		if (val & (1 << (nbits - 1))) != 0:
			# If sign bit is set.
			# compute negative value.
			val = val - (1 << nbits)
	return (val)

def get_accel_data(cs_pin, accel):
	'''
	Function to get x, y data from accelerometer
	'''

	# Get x_axis reading
	accel.write(b'\xb2') # read register for first byte of X_axis readings
	x_1 = accel.read(1) # read 1 byte from the previously mentioned register
	accel.write(b'\xb3') # read register for second byte of X_axis readings
	x_2 = accel.read(1) # read 1 byte from the previously mentioned register
	x_axis = (int.from_bytes(x_1, 'big') | int.from_bytes(x_2, 'big') << 8) # need to get 16 bit data

	# Get y_axis reading
	accel.write(b'\xb4') # read register for first byte of Y_axis readings
	y_1 = accel.read(1) # read 1 byte from the previously mentioned register
	accel.write(b'\xb5') # read register for second byte of Y_axis readings
	y_2 = accel.read(1) # read 1 byte from the previously mentioned register
	y_axis = (int.from_bytes(y_1, 'big') | int.from_bytes(y_2, 'big') << 8) # need to get 16 bit data

	# Get z_axis reading
	accel.write(b'\xb6') # read register for first byte of Z_axis readings
	z_1 = accel.read(1) # read 1 byte from the previously mentioned register
	accel.write(b'\xb7') # read register for second byte of Z_axis readings
	z_2 = accel.read(1) # read 1 byte from the previously mentioned register
	z_axis = (int.from_bytes(z_1, 'big') | int.from_bytes(z_2, 'big') << 8) # need to get 16 bit data

	x_axis = twos_complement(x_axis, 16)
	y_axis = twos_complement(y_axis, 16)
	z_axis = twos_complement(z_axis, 16)

	print(x_axis, y_axis, z_axis)

	#x_out = x_axis/2048.0
	#y_out = y_axis/2048.0
	#z_out = z_axis/2048.0

	#print(x_out, y_out, z_out)
	#return(x_out, y_out, z_out)

	return(x_axis, y_axis, z_axis)


def connect_to_router(ssid, pw):
	'''
	Function to connect to a router and then return WiFi MAC addresses from the vicity
	'''
	wifi = network.WLAN(network.STA_IF) # Create WiFi object
	if not wifi.isconnected():
		print("connecting to network...")
		wifi.active(True)
		wifi.connect(ssid, pw) # Connect to WiFi with the input SSID and Password
		while not wifi.isconnected():
			pass
	print("connected")
	# return wifi object
	return(wifi)

def debouncing(button):
	'''
	Function to check debouncing by reading signal consecutively for certain milliseconds
	'''
	# Initialize value for loop
	val = None
	for _ in range(25): # number of sample to check consistency
		if val != None and val != button.value(): # check button value and compare it to the saved value
			return None # if not the same, return none
		val = button.value() # update saved value with the button value
		time.sleep_ms(1) # sleep 1 ms for each iteration so in total it will be 30ms sampling
	return(val) # after consistent button sample is met, return the saved value

def record_changer(button):
	global record
	'''
	Function to change to start record data after pressing button
	'''
	if debouncing(button) == None: # if it's on the debouncing state, return nothing
		return
	elif not debouncing(button): # button pressed condition
		# increment the mode in each button press
		record = 1 - record

def letter_changer(button):
	global pos_check
	'''
	Function to change to select the current letter to be recorded
	'''
	if debouncing(button) == None: # if it's on the debouncing state, return nothing
		return
	elif not debouncing(button): # button pressed condition
		# increment the mode in each button press
		pos_check = (pos_check + 1) % 8

# Main function
def main():
	global record, pos_check

	# Freeing Memory
	gc.collect()
	gc.mem_free()

	# Initialize buttons and its interrupt
	button_b = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)
	button_b.irq(trigger=machine.Pin.IRQ_FALLING, handler=letter_changer)
	button_c = machine.Pin(2, machine.Pin.IN, machine.Pin.PULL_UP)
	button_c.irq(trigger=machine.Pin.IRQ_FALLING, handler=record_changer)

	# Initialize SPI registers for accelerometer
	pwr_ctrl = b'\x2d\x28'
	dt_format = b'\x31\x0f'
	bw_rate = b'\x2c\x08'
	int_enable = b'\x2e\x00'
	fifo_ctrl = b'\x38\x9f'
	cs_pin.value(0)
	accel.write(pwr_ctrl)
	accel.write(dt_format)
	accel.write(bw_rate)
	accel.write(int_enable)
	accel.write(fifo_ctrl)
	cs_pin.value(1)
	time.sleep_ms(100)

	networks = connect_to_router(ssid = settings["wifi_name"], pw=settings["wifi_pass"])
	#print("Raw MAC Addresses = \n", networks.scan())
	
	print("IP Address = \n", networks.ifconfig())

	# Use JSON format for all API
	headers = {"Content-Type": "application/json"}

	# accelerometer data payload initialization
	accel_payload = {
		"character" : "Z", 
		"x_pos" : [], 
		"y_pos" : [],
		"z_pos" : []
	}

	cs_pin.value(0)
	while True:
		# Show retrieved data on OLED
		# Show initial text position
		oled.fill(0)
		oled.text("mode = "+ mode_label[mode_button], 0, 1)
		oled.text("letter = "+ word[pos_check], 0, 11)
		oled.text("recording = "+ record_label[record], 0, 21)
		oled.show()

		# Record position data using data from accelerometer
		if record:
			accel_payload["character"] = word[pos_check]

			# Take 20 sample with frequency of 1 sample per 100 ms = 10 Hz
			for _ in range(20):
				pos_x, pos_y, pos_z = get_accel_data(cs_pin, accel)
				accel_payload["x_pos"].append(pos_x)
				accel_payload["y_pos"].append(pos_y)
				accel_payload["z_pos"].append(pos_z)
				time.sleep_ms(100)

			# Send Accelerometer API data to AWS using POST method
			submit_aws_url = ""
			submit_aws_response = requests.post(submit_aws_url, headers=headers, data=json.dumps(accel_payload))
			submit_aws_json = json.loads(submit_aws_response.content)
			print("payload response = \n", submit_aws_json)

			record = 0
			accel_payload = {
				"character" : "Z", 
				"x_pos" : [], 
				"y_pos" : [],
				"z_pos" : []
			}
		
		time.sleep_ms(100)

if __name__ == "__main__":
	main()
