import urequests
import network
import machine
import json
import time
import ssd1306

i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))#i2c for oled
oled = ssd1306.SSD1306_I2C(128, 32, i2c)

url = "http://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=WVK79C36BGPPP686&status=" #url for sending tweet with api
tweet = "Lab3 checkpoint 3 sent from esp8266" # tweet to be sent
url = url+tweet
res = urequests.get(url) #requesting tweet to be sent

oled.fill(0)
oled.text('tweet:',0,0)
oled.text('%s' %(tweet),0,10)
oled.show()
