from transitions import Machine
class shelf_module(object):

    states = ['wait_for_mqtt', 'wait_for_open', 'wait_for_close', 'forget_to_close']

    def __init__(self, client):
        self.client = client
        self.machine = Machine(model=self, states=shelf_module.states, initial='wait_for_mqtt')
        self.machine.add_transition(trigger='get_mqtt', source='wait_for_mqtt', dest='wait_for_open')
        self.machine.add_transition(trigger='open_lid', source='wait_for_open', dest='wait_for_close')
        self.machine.add_transition(trigger='close_lid', source='wait_for_close', dest='wait_for_mqtt')
        self.machine.add_transition(trigger='open_too_long', source='wait_for_close', dest='forget_to_close')
        self.machine.add_transition(trigger='close_lid', source='forget_to_close', dest='wait_for_mqtt')

    def get_mqtt_handler(self):
        # self.client.loop_stop()
        self.get_mqtt()
        print('[INFO] State:' + self.state)
    
    def open_lid_handler(self):
        pass
    
    def close_lid_handler(self):
        pass
    
    def open_too_long_handler(self):
        pass