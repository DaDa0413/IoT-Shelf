import paho.mqtt.client as mqtt
import sys
import time
import smbus2
from RPLCD.i2c import CharLCD

sys.modules['smbus'] = smbus2

user = 'iot2020'
password = '123456'

host = "35.233.225.236"
id_dict = {'orange' : 'Xlwra2HLExjGArkgxtcl', 'apple' : 'ioTrUrnFNWR6pO0pJtIq'}

class mqtt_class(object):

    lock = True
    price = 0
    client = mqtt.Client()
    lcd = CharLCD('PCF8574', address=0x27, port=1, backlight_enabled=True)

    def __init__(self, name):

        self.name = name
        self.ID = id_dict[self.name]
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(user, password)
        self.client.connect(host, 1883, 120)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print("Client connected with result code: {}".format(str(rc)))
        self.client.subscribe([(self.ID + '/open', 2), (self.ID + '/price', 2)])

    def on_message(self, client, userdata, msg):
        # Enable lid or Set price
        if int(msg.payload) == 1:
            self.lock = False
        else:
            self.price = int(msg.payload)
            print('[ACT] Price is :' + str(self.price))
            self.lcd.clear()
            self.lcd.cursor_pos = (0, 0)
            self.lcd.write_string('Item: ' + self.name)
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string('Price: ' + str(self.price))

    def take_goods(self):
        self.client.publish(self.ID + "/take", "fuck", qos=2, retain=False)
        print('[ACT] Goods taken')

    def close_lid(self):
        self.client.publish(self.ID + "/close", "1", qos=2, retain=False)
        print('[Act] Close lid')
    
    def shut_down(self):    
        self.lcd.clear()
        self.client.disconnect()

