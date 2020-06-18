# import paho.mqtt.client as mqtt
import json
import time
import sys
import RPi.GPIO as GPIO

from utils.shelf import shelf_module
from utils.mqtt_lib import mqtt_class
# import mqtt_lib as mqtt_lib

# user = 'iot2020'
# password = '123456'

# host = "35.233.225.236"
# shelfID = 'Xlwra2HLExjGArkgxtcl'

photoresistor_pin = 23
switch1_pin = 17
switch2_pin = 22
switch3_pin = 27
buzzer_pin = 24
motor_pin = 12

PWM_FREQ = 50

# def on_connect(client, userdata, flags, rc):
#     print("Connected with result code: {}".format(str(rc)))
#     client.subscribe(shelfID + '/open', 2)

# def on_message(client, userdata, msg):
#     global lock

#     # Enable lid
#     if int(msg.payload) == 1:
#         lock = False

def btn_callback(channel):
    #TODO
    global switch_enable
    if switch_enable:
        print('[INFO] Goods taken')

def angle_to_duty_cycle(angle=0):
    duty_cycle = (0.05 * PWM_FREQ) + (0.19 * PWM_FREQ * angle / 180)
    return duty_cycle

if __name__ == '__main__':

    # Set mqtt
    # lock = True
    # client = mqtt.Client()
    # client.on_connect = on_connect
    # client.on_message = on_message
    # client.username_pw_set(user, password)
    # client.connect(host, 1883, 120)
    # client.loop_start()
    mqtt = mqtt_class()

    # Set RPi
    switch_enable = False
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(photoresistor_pin, GPIO.IN)
    GPIO.setup(switch1_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
    GPIO.setup(switch2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
    GPIO.setup(switch3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
    GPIO.setup(buzzer_pin, GPIO.OUT)  
    GPIO.setup(motor_pin, GPIO.OUT)
    GPIO.add_event_detect(switch1_pin, GPIO.FALLING, callback=btn_callback, bouncetime=300)  
    GPIO.add_event_detect(switch2_pin, GPIO.FALLING, callback=btn_callback, bouncetime=300)  
    GPIO.add_event_detect(switch3_pin, GPIO.FALLING, callback=btn_callback, bouncetime=300)  
    pwm = GPIO.PWM(motor_pin, PWM_FREQ)
    pwm.start(0)

    shelf = shelf_module()
    try:
        while(True):
            if shelf.state == 'wait_for_mqtt':
                print('[INFO] State: wait_for_mqtt')
                while True:
                    if mqtt.lock == False:
                        pwm.ChangeDutyCycle(angle_to_duty_cycle(90))
                        shelf.get_mqtt()
                        break
            elif shelf.state == 'wait_for_open':
                print('[INFO] State: wait_for_open')
                print('[INFO] Start photoresistor Module (Low Enable)')
                while True:
                    if not GPIO.input(photoresistor_pin):
                        shelf.open_lid()
                        break
                    time.sleep(0.2)
            elif shelf.state == 'wait_for_close':
                # TODO Enable switch & timer
                print('[INFO] State: wait_for_close')
                print('[INFO] Start photoresistor Module (High Enable)')
                prev_time = time.time()
                switch_enable = True
                while True:
                    if GPIO.input(photoresistor_pin):
                        shelf.close_lid()
                        pwm.ChangeDutyCycle(angle_to_duty_cycle(180))
                        mqtt.lock = True

                        break
                    if time.time() - prev_time > 5:
                        shelf.open_too_long()
                        break
                    time.sleep(0.2)
                switch_enable = False
            elif shelf.state == 'forget_to_close':
                print('[INFO] State: forget_to_close')
                while True:
                    GPIO.output(buzzer_pin, GPIO.HIGH)
                    time.sleep(0.001)
                    GPIO.output(buzzer_pin, GPIO.LOW)
                    time.sleep(0.0009)
                    if GPIO.input(photoresistor_pin):
                        shelf.close_lid()
                        pwm.ChangeDutyCycle(angle_to_duty_cycle(180))
                        mqtt.lock = True
                        break
            else:
                print("[ERROR] Unknown state")
    except KeyboardInterrupt:
        print('[INFO] Bye~')
        GPIO.cleanup()
            
