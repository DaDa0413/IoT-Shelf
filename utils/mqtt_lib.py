import paho.mqtt.client as mqtt
user = 'iot2020'
password = '123456'

host = "35.233.225.236"
shelfID = 'Xlwra2HLExjGArkgxtcl'

class mqtt_class(object):

    lock = True
    open_sub = mqtt.Client()
    # price_sub = 
    # close_pub = 
    # take_pub =

    def __init__(self):

        self.open_sub.on_connect = self.open_on_connect
        self.open_sub.on_message = self.open_on_message
        self.open_sub.username_pw_set(user, password)
        self.open_sub.connect(host, 1883, 120)
        self.open_sub.loop_start()

    def open_on_connect(self, client, userdata, flags, rc):
        print("Open_sub connected with result code: {}".format(str(rc)))
        self.open_sub.subscribe(shelfID + '/open', 2)

    def open_on_message(self, client, userdata, msg):
        # Enable lid
        if int(msg.payload) == 1:
            self.lock = False
