'''
Name: Aditya Wikara
UNI: aw3306
Name: Meet Desai
UNI: mpd2155
Name: Rifqi Luthfan
UNI: rl3154

Date: 2021-03-11
'''

import network
import urequests as requests
import ujson as json
import ustruct as struct
import machine
from machine import Pin, PWM
import ssd1306
import time

try:
    import usocket as socket
except:
    import socket

# set the default RTC time
#(year, month, day, weekday, hour, minute, second, millisecond).
# hour is 4 index, minute is 5 index
# hour max value is 12
i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
rtc = machine.RTC()
rtc.datetime((2021, 3, 8, 0, 10, 01, 0, 0))
accel = machine.SPI(1, baudrate=1500000, polarity=1, phase=1)
cs_pin = machine.Pin(15, machine.Pin.OUT)

# Setup for button press, matching it with the letter for training/predict
pos_check = 0
word = "COLUMBIA"
mode_button = 1
mode_label = ["training", "predict"]
record = 0
record_label = ["no", "yes"]

response_payload = {
    "Device": {
        "Feather": "Huzzah",
        "ESP": 8266
    }
}

alarm = [0,1,5]

# piezo sensor
piezo = PWM(Pin(12), freq=1000)

# initial the states
mode = 0
current_state = 0
state = [0,1]
''''''
# Setup for button press, matching it with the letter for training/predict
pos_check = 0
word = "COLUMBIA"
mode_button = 1
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

    return(x_axis, y_axis, z_axis)

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


# Main function
def gesture(get_ip_address,btn1,btn2,btn3):
    global record, pos_check, mode_button, cs_pin, accel

    button_c = machine.Pin(14, machine.Pin.IN, machine.Pin.PULL_UP)
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

    #networks = connect_to_router(get_ip_address)
    #print("Raw MAC Addresses = \n", networks.scan())
    
    #print("IP Address = \n", networks.ifconfig())

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
    
    pred = ""

    while True:
        # Freeing Memory
        gc.collect()
        gc.mem_free()

        # exit the loop
        if btn1.value()-1 or btn2.value()-1 or btn3.value()-1:
            break

        # Show retrieved data on OLED
        # Show initial text position
        oled.fill(0)
        oled.text("pred letter = "+ pred, 0, 11)
        oled.text("recording = "+ record_label[record], 0, 21)
        oled.show()
            

        # Record position data using data from accelerometer
        if record:
            accel_payload["character"] = ""

            # Take 20 sample with frequency of 1 sample per 100 ms = 10 Hz
            for _ in range(20):
                pos_x, pos_y, pos_z = get_accel_data(cs_pin, accel)
                accel_payload["x_pos"].append(pos_x)
                accel_payload["y_pos"].append(pos_y)
                accel_payload["z_pos"].append(pos_z)
                time.sleep_ms(100)

            accel_payload["x_pos"] = [accel_payload["x_pos"]]
            accel_payload["y_pos"] = [accel_payload["y_pos"]]
            accel_payload["z_pos"] = [accel_payload["z_pos"]]

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
            pred = submit_aws_json["prediction"][0]
        
        time.sleep_ms(100)

'''functions for gesture is above'''

# display time on the oled
def display_time():
    global oled, alarm
    oled.fill(0)
    current_time = format_time(rtc.datetime()[4]) + ':' + format_time(rtc.datetime()[5]) + ':' + format_time(rtc.datetime()[6])
    oled.text(("time: " + current_time), 0, 0)
    oled.show()

# functions for formatting and getting the time
def format_time(x):
    if x < 10:
        y = "0" + str(x)
        return y
    else:
        return str(x)
def alarm(btn1,btn2,btn3):
	global oled
	a,b,c,d,e,f,g,h = rtc.datetime()
	k = f
	j = e
	l = g
	while True:
		oled.fill(0)
		oled.text('Set alarm',0,0)
		oled.text('%s:%s:%s' %(j,k,l),0,10)
		oled.show()
		time.sleep(0.2)
		if btn1.value() -1:
			k +=1
			if k==60:
				j +=1
				k = 0
			time.sleep(0.5)#prevent multiple reading
		elif btn3.value() -1:
			k -= 1
			if k<0:
				j -=1
				k = 59
			time.sleep(0.5)	
		if btn2.value() -1:
			time.sleep(0.1)
			break
	time.sleep(0.5)
	return j,k,l	



# piezo alarm for 5 seconds
def alarm_sound(piezo_sensor,btn1,btn2,btn3,adc):
    piezo_sensor.duty(adc)
    oled.fill(0)
    oled.text("ALARM! Wake Up!", 0,0)
    oled.show()
    while True:
        if btn1.value()-1 or btn2.value()-1 or btn3.value()-1:
            break
    piezo_sensor.duty(0)


# adjust the contrast of the led screen
def change_brightness(adc_value):
    global oled
    # max adc value is 1024
    # max contrast value is 255
    value = (1-(adc_value/1024))*255
    oled.contrast(int(value))
    oled.show()

'''functions above this is for time and alarm'''

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

    return time_str

def display_weather():
    # Freeing Memory
    gc.collect()
    gc.mem_free()

    # API request body, need to change cellId, locationAreacode, MCC, MNC, mac address
    url1 = "https://www.googleapis.com/geolocation/v1/geolocate?key=<insert api here>" #getting location from google

    api = "<insert api here>" #api for openweather

    r = requests.post(url1,data=json.dumps({})) #getting lat and long for current location
    res = r.json()
    lat = res['location']['lat']
    lon = res['location']['lng']

    #print("%s : %s"%(lat,lon))
    url = "https://api.openweathermap.org/data/2.5/weather?lat=%s&lon=%s&appid=%s&units=metric" % (lat, lon, api) #feeding lat and long to get weather

    response = requests.get(url)
    r2=response.json()
    des = r2['weather'][0]['main'] #description of current weather
    tem = r2['main']['temp'] # current temperature

    oled.fill(0)
    oled.text('temp:%s C' %(tem),0,0) #display temp and weather
    oled.text('des: %s'%(des),0,10)
    oled.show()
    return (str(temp), str(des))

def send_tweet(tweet_msg):
    url = 'https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=<insert api here>&status='+tweet_msg
    tweet_req = requests.post(url)
    oled.fill(0)
    oled.text("Tweet Sent: ", 0, 0)
    oled.text(tweet_msg, 0, 10)
    oled.show()
    return "Tweet Sent: " + tweet_msg

def print_android_msg(json_data, msg):
    
    json_data["ResponseMessage"]= msg

    return(json_data)

# Main function
def main():
    # led screen buttons
    btn_a = Pin(13, Pin.IN)
    btn_b = Pin(0, Pin.IN)
    btn_c = Pin(2, Pin.IN)
    a = 0
    b = 0
    c = 0
    # light sensor
    adc = machine.ADC(0)
    
    # Get IP Address to bind
    get_ip_address = connect_to_router('', '')
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

        change_brightness(adc.read())
        # compare hour, minute, second
        if rtc.datetime()[4] == a and rtc.datetime()[5] == b and rtc.datetime()[6] == c:
        	alarm_sound(piezo,btn_a,btn_b,btn_c,adc.read())

        if command == "display time" and display == 1:#display time when display is on
            if btn_b.value()-1:
            	print("Alarm")
            	a,b,c = alarm(btn_a,btn_b,btn_c)
            display_time()
            msg_android = display_datetime()
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
                msg_android = "Smartwatch is OFF" #response to app
            if command == "display on":
                oled_display_handler(command)#displaying display off command for 1 second
                display = 1#turning display on again
                msg_android = "Smartwatch is ON" #response to app
            if display == 1:#only output if display is 1
                #oled_display_handler(command)
                #msg_android = command+"\n showed on feather" #response to app
                if command == "display weather":
                    print("display weather")
                    temperature, weather_desc = display_weather()
                    msg_android = "temp: " + temperature + ", weather: " + weather_desc
                    command = ""
                elif command[0:10] == "send tweet":
                    msg_android = send_tweet(command[11:])
                    command = ""
                elif command == "display time":
                    msg_android = "Display Time"
                elif command == "display on":
                    msg_android = "Smartwatch is ON"
                elif command == "gesture mode":
                    gesture(get_ip_address,btn_a,btn_b,btn_c)
                    msg_android = "Make COLUMBIA Gestures!"
                elif command == "":
                    pass
                else:
                    msg_android = "Unknown Command, Please Try Again!"
            
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
