import urequests as requests
import network
import machine
import json
import time
import ssd1306

i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))#i2c for oled
oled = ssd1306.SSD1306_I2C(128, 32, i2c)
url1 = "https://www.googleapis.com/geolocation/v1/geolocate?key=AIzaSyCyLBmfp5Ghrplz5RH9JN9NR296fN-Nl9c" #getting location from google

api = "270d378bc18a8dc3439d69c2795944fc" #api for openweather

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
