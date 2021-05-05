import urequests
import network
import machine
import json
import time
import ssd1306

i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))#i2c for oled
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

url = "https://www.googleapis.com/geolocation/v1/geolocate?key=<insert api key here>" #setting up url with api


r = urequests.post(url,data=json.dumps({})) # requesting location data from google api
res = r.json() # converting data to json
lat = res['location']['lat'] # getting latitude and longitude
lon = res['location']['lng']
	
oled.fill(0)
oled.text('lat:%s' %(lat),0,0) #display lat and long on oled
oled.text('long:%s'%(lon),0,10)
oled.show()
