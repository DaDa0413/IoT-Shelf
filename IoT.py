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
switch1_pin = 17
switch2_pin = 22
switch3_pin = 27
buzzer_pin = 24
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

def btn_callback(channel):
    #TODO
    global switch_enable
    if switch_enable:
        print('[INFO] Goods taken')

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
    switch_enable = False
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(photoresistor_pin, GPIO.IN)
    GPIO.setup(switch1_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
    GPIO.setup(switch2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
    GPIO.setup(switch3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
    GPIO.add_event_detect(switch1_pin, GPIO.FALLING, callback=btn_callback, bouncetime=300)  
    GPIO.add_event_detect(switch2_pin, GPIO.FALLING, callback=btn_callback, bouncetime=300)  
    GPIO.add_event_detect(switch3_pin, GPIO.FALLING, callback=btn_callback, bouncetime=300)  
    GPIO.setup(buzzer_pin, GPIO.OUT)  

    shelf = shelf_module(client)
    while(True):
        if shelf.state == 'wait_for_mqtt':
            if mqtt_sub_enable == False:
                mqtt_sub_enable = True
        elif shelf.state == 'wait_for_open':
            print('wait for open~~~')
            print('[INFO] Start photoresistor Module (Low Enable)')
            while True:
                if not GPIO.input(photoresistor_pin):
                    shelf.open_lid()
                    break
                time.sleep(0.2)
        elif shelf.state == 'wait_for_close':
            # TODO Enable switch & timer
            print('wait for close~~')
            print('[INFO] Start photoresistor Module (High Enable)')
            prev_time = time.time()
            switch_enable = True
            while True:
                if GPIO.input(photoresistor_pin):
                    shelf.close_lid()
                    break
                if time.time() - prev_time > 5:
                    print('[Warn] Time out')
                    shelf.open_too_long()
                    break
                time.sleep(0.2)
            switch_enable = False
        elif shelf.state == 'forget_to_close':
            print('forget to close~~')
            while True:
                GPIO.output(buzzer_pin, GPIO.HIGH)
                time.sleep(0.001)
                GPIO.output(buzzer_pin, GPIO.LOW)
                time.sleep(0.001)
                if GPIO.input(photoresistor_pin):
                    shelf.close_lid()
                    break
        else:
            print("[ERROR] Unknown state")
            
        
