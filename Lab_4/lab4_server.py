'''
Name: Aditya Wikara
UNI: aw3306
Name: Meet Desai
UNI: mpd2155
Name: Rifqi Luthfan
UNI: rl3154


Date: 2021-03-08
'''

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


i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
rtc = machine.RTC()
rtc.datetime((2021, 3, 8, 0, 10, 01, 0, 0))

response_payload = {
	"Device": {
		"Feather": "Huzzah",
		"ESP": 8266
	}
}

def display_off():
	oled.fill(0)
	oled.show()


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
	# return IP Address
	return(wifi.ifconfig())

def oled_display_handler(text_dsp):
	'''
	Function to display text on OLED
	'''
	oled.fill(0)
	oled.text(text_dsp, 0, 0)
	oled.show()

def display_datetime():
	'''
	Function to display time and date
	'''
	# generate formated date/time strings from internal RTC
	date_str = "Date: {0:4d}-{1:02d}-{2:02d}".format(*rtc.datetime())
	time_str = "Time: {4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())

	# update SSD1306 OLED display
	oled.fill(0)
	oled.text("ESP8266 Clock", 0, 1)
	oled.text(date_str, 0, 11)
	oled.text(time_str, 0, 21)
	oled.show()


def print_android_msg(json_data, msg):
	
	json_data["ResponseMessage"]= msg

	return(json_data)

# Main function
def main():

	# Get IP Address to bind
	#sta_if.connect('Apartment 2S_EXT', 'satwik1234')
	get_ip_address = connect_to_router('username', 'password')
	print(get_ip_address)
	command = "" #command from app
	display = 1#current display state
	socket_address = socket.getaddrinfo(get_ip_address[0], 3000)[0][-1] #starting socket binding 3000 port number
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	s.settimeout(1)#setting timeout at 1 second
	s.bind(socket_address)
	s.listen(5)
	print('listening on', socket_address)

	while True:
		if command == "display time" and display == 1:#display time when display is on
			display_datetime()
			response = print_android_msg(response_payload, "Time displayed")#response to app
		
		try:
			conn, addr = s.accept()#accepting messages on port
			print('Got a connection from %s' % str(addr))
			request = conn.recv(1024)#receving data
			print('Content =\n %s' % request.decode('utf-8'))
			method, url, version  = str(request.decode('utf-8')).split('\r\n')[0].split() #splitting data
			json_input  = json.loads(str(request.decode('utf-8')).split('\r\n')[-1]) # getting json data
			command = json_input["text"] #getting the command given
			if command == "display off": 
				oled_display_handler(command)#displaying display off command for 1 second
				time.sleep(1)
				display_off()
				display = 0#turning display off
				msg_android = "Display turned off" #response to app
			if command == "display on":
				display = 1#turning display on again
				msg_android = "Display turned on" #response to app
			if display == 1:#only output if display is 1
				oled_display_handler(command)
				msg_android = command+"\n showed on feather" #response to app
			
			response = print_android_msg(response_payload, str(msg_android))
			conn.send("HTTP/1.1 200 OK\n")
			
			conn.send("Content-Type: application/json\n")
			conn.send("Connection: close\n\n")
			conn.sendall(json.dumps(response))
			time.sleep(1)
		except:#timeout does nothing
			pass


if __name__ == "__main__":
	main()
