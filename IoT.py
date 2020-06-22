import json
import time
import sys
import RPi.GPIO as GPIO

from utils.shelf import shelf_module
from utils.mqtt_lib import mqtt_class

photoresistor_pin = 23
switch1_pin = 17
switch2_pin = 22
switch3_pin = 27
buzzer_pin = 24
motor_pin = 12

PWM_FREQ = 50

def btn_callback17(channel):
    #TODO
    global switch_enable
    global good_17
    if switch_enable and good_17:
        mqtt.take_goods()
        good_17 = False

def btn_callback22(channel):
    #TODO
    global switch_enable
    global good_22
    if switch_enable and good_22:
        mqtt.take_goods()
        good_22 = False

def btn_callback27(channel):
    #TODO
    global switch_enable
    global good_27
    if switch_enable and good_27:
        mqtt.take_goods()
        good_27 = False

def angle_to_duty_cycle(angle=0):
    duty_cycle = (0.05 * PWM_FREQ) + (0.19 * PWM_FREQ * angle / 180)
    return duty_cycle

if __name__ == '__main__':
    
    good_17 = False
    good_22 = False
    good_27 = False

    # Set mqtt
    mqtt = mqtt_class(sys.argv[1])

    # Set RPi
    switch_enable = False
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(photoresistor_pin, GPIO.IN)
    GPIO.setup(switch1_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
    GPIO.setup(switch2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
    GPIO.setup(switch3_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
    GPIO.setup(buzzer_pin, GPIO.OUT)  
    GPIO.setup(motor_pin, GPIO.OUT)
    pwm = GPIO.PWM(motor_pin, PWM_FREQ)
    pwm.start(0)
    pwm.ChangeDutyCycle(angle_to_duty_cycle(180))

    if  GPIO.input(switch1_pin):
        good_17 = True
        print('[INIT] Good 1 exist')
        GPIO.add_event_detect(switch1_pin, GPIO.FALLING, callback=btn_callback17, bouncetime=1000)  
    if  GPIO.input(switch2_pin):
        good_22 = True
        print('[INIT] Good 2 exist')
        GPIO.add_event_detect(switch2_pin, GPIO.FALLING, callback=btn_callback22, bouncetime=1000)  
    if  GPIO.input(switch3_pin):
        good_27 = True
        print('[INIT] Good 3 exist')
        GPIO.add_event_detect(switch3_pin, GPIO.FALLING, callback=btn_callback27, bouncetime=1000)  

    shelf = shelf_module()
    try:
        while(True):
            if shelf.state == 'wait_for_mqtt':
                print('[INFO] State: wait_for_mqtt')
                while True:
                    # print(GPIO.input(switch1_pin))
                    # print(GPIO.input(switch2_pin))
                    # print(GPIO.input(switch3_pin))
                    # time.sleep(1)
                    if mqtt.lock == False:
                        pwm.ChangeDutyCycle(angle_to_duty_cycle(90))
                        shelf.get_mqtt()
                        break
            elif shelf.state == 'wait_for_open':
                print('[INFO] State: wait_for_open')
                print('[ACT] Start photoresistor Module (Low Enable)')
                while True:
                    if not GPIO.input(photoresistor_pin):
                        shelf.open_lid()
                        break
                    time.sleep(0.2)
            elif shelf.state == 'wait_for_close':
                print('[INFO] State: wait_for_close')
                print('[ACT] Start photoresistor Module (High Enable)')
                prev_time = time.time()
                switch_enable = True
                while True:
                    if GPIO.input(photoresistor_pin):
                        shelf.close_lid()
                        mqtt.close_lid()
                        time.sleep(5)
                        pwm.ChangeDutyCycle(angle_to_duty_cycle(180))
                        mqtt.lock = True
                        break
                    if time.time() - prev_time > 30:
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
                        mqtt.close_lid()
                        time.sleep(5)
                        pwm.ChangeDutyCycle(angle_to_duty_cycle(180))
                        mqtt.lock = True
                        break
            else:
                print("[ERROR] Unknown state")
    except KeyboardInterrupt:
        print('[INFO] Bye~')
        pwm.ChangeDutyCycle(angle_to_duty_cycle(90))
        time.sleep(2)
        GPIO.cleanup()
        mqtt.shut_down()
            
