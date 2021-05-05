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
rtc.datetime((2021, 3, 8, 0, 0, 01, 0, 0))

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

    # update SSD1306 OLED display
    '''
    # commented out
    oled.fill(0)
    oled.text("ESP8266 Clock", 0, 1)
    oled.text(date_str, 0, 11)
    oled.text(time_str, 0, 21)
    oled.show()
    '''
    return time_str

def display_weather():
    # API request body, need to change cellId, locationAreacode, MCC, MNC, mac address
    api_data = {
        "homeMobileCountryCode": 310,
        "homeMobileNetworkCode": 410,
        "radioType": "gsm",
        "carrier": "TMobile",
        "considerIp": "true",
        "cellTowers": [
            {
                "cellId": 15232770,
                "locationAreaCode": 857,
                "mobileCountryCode": 310,
                "mobileNetworkCode": 260,
                "age": 0,
                "signalStrength": -60,
                "timingAdvance": 15
            }
        ],
        "wifiAccessPoints": [
            {
                "macAddress": "f4:5c:89:99:c9:11",
                "signalStrength": -43,
                "age": 0,
                "channel": 11,
                "signalToNoiseRatio": 0
            }
        ]
    }

    # API endpoint url for Google Geolocation
    url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=<insert api here>'
    # API request
    geoloc_req = requests.post(url, data=json.dumps(api_data))
    # API response
    geoloc_response= json.loads(geoloc_req.text)
    print(geoloc_response)
    # get the data from the response 
    lat = geoloc_response['location']['lat']
    lng = geoloc_response['location']['lng']
    acc = geoloc_response['accuracy']

    # API endpoint url for OpenWeather
    url = 'http://api.openweathermap.org/data/2.5/weather?lat='+str(lat)+'&lon='+str(lng)+'&APPID=<insert api here>'
    # API request
    weather_req = requests.post(url)
    # API response
    weather_response = json.loads(weather_req.text)
    print(weather_response)
    # get the data from the response, temp in celsius
    temp = weather_response['main']['temp'] - 273.15
    weather = weather_response['weather'][0]['main']

    # display the data in the oled screen
    oled.fill(0)
    temperature = 'temp: ' + str(temp) + ' C'
    weather_desc = 'desc: ' + str(weather)
    oled.text(temperature, 0, 0)
    oled.text(weather_desc, 0, 10)
    oled.show()
    return (str(temp), str(weather))

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
