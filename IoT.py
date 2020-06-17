import paho.mqtt.client as mqtt
import json
import time
import sys
import RPi.GPIO as GPIO

from utils.shelf import shelf_module

projectKey = 'PK7TPY1BSCAHCZ1E5H'
deviceId = '22725254260'
sensorId = 'openlid'

host = "iot.cht.com.tw"
topic = '/v1/device/' + deviceId + '/sensor/' + sensorId + '/rawdata'

photoresistor_pin = 23


def on_connect(client, userdata, flags, rc):
    print("Connected with result code: {}".format(str(rc)))
    client.subscribe(topic, 2)


def on_message(client, userdata, msg):
    global mqtt_sub_enable
    json_array = json.loads(str(msg.payload)[2:-1])
    # Enable lid
    if json_array['value'][0] == '1' and mqtt_sub_enable == True:
        shelf.get_mqtt_handler()
        mqtt_sub_enable = False


if __name__ == '__main__':

    # Set mqtt
    mqtt_sub_enable = False
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    user, password = projectKey, projectKey
    client.username_pw_set(user, password)
    client.connect(host, 1883, 60)
    client.loop_start()

    # Set RPi
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(photoresistor_pin, GPIO.IN)
    print('[INFO] Start photoresistor Module')

    shelf = shelf_module(client)
    while(True):
        if shelf.state == 'wait_for_mqtt':
            if mqtt_sub_enable == False:
                mqtt_sub_enable = True
        elif shelf.state == 'wait_for_open':
            # TODO Enable photoresistor
            print('wait for open~~~')
            while True:
                if GPIO.input(photoresistor_pin):
                    shelf.open_lid()
                    break
                time.sleep(0.2)
        elif shelf.state == 'wait_for_close':
            # TODO Enable switch & timer
            print('wait for close~~')
            strs = input()
            if strs == 'close':
                shelf.close_lid()
        elif shelf.state == 'forget_to_close':
            # TODO Enable buzzer
            pass
        else:
            print("[ERROR] Unknown state")
            
        
