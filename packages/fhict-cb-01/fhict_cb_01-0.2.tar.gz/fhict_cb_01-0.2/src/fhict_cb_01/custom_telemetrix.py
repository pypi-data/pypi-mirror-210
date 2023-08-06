from telemetrix import telemetrix

import time

class CustomTelemetrix(telemetrix.Telemetrix):

    def __init__(self, com_port=None, 
                 arduino_instance_id=1, arduino_wait=5,
                 sleep_tune=0.001,
                 shutdown_on_exception=True):
        super().__init__(com_port, arduino_instance_id=1, 
                            arduino_wait=arduino_wait, sleep_tune=sleep_tune, 
                            shutdown_on_exception=shutdown_on_exception)
   
            
           
    def displayOff(self) :
        self._send_command([self._DISPLAY_OFF])
    
    def displayOn(self) :
        self._send_command([self._DISPLAY_ON])
    
    def displayClear(self) :
        self._send_command([self._DISPLAY_CLEAR])
        
    def displaySetBrightness(self, brightness) :
        self._send_command([self._DISPLAY_SET_BRIGHTNESS, brightness])
        
    def displayCharAt(self, pos, char, showDot=False):
        """
        Configure dht sensor prior to operation.
        @param pos n number on arduino
        @param char
        """
        data = [self._DISPLAY_SHOW_CHAR, pos, char, showDot]
        self._send_command(data)

    def displayShow(self, value) :
        string = str(value)
        self.displayClear()
        pos = 0
        prev = '.'
        for letter in string:
            if letter == '.' and prev != '.':
                self.displayCharAt(pos - 1, ord(prev), showDot = True)
            else :
                self.displayCharAt(pos, ord(letter), showDot = False)
                pos += 1
            prev = letter
      
    def set_pin_mode_digital_input_pullup(self, PIN, callback = None) :
        if callback == None :
            callback = self._store_digital_pin_state
        super().set_pin_mode_digital_input_pullup(PIN, callback)
        time.sleep(0.01)

    def set_pin_mode_digital_input(self, PIN, callback = None) :
        if callback == None :
            callback = self._store_digital_pin_state
        super().set_pin_mode_digital_input(PIN, callback=callback)
        # small delay to get at least one callback in
        time.sleep(0.01)
    
    # we override the parent class definition with a default callback
    def set_pin_mode_dht(self, PIN, callback = None, dht_type=11, wait=2) :
        if callback == None:
            callback = self._store_dht
        super().set_pin_mode_dht(PIN, callback=callback, dht_type=dht_type)
        self.dht_pin = PIN
        self.dht_last_data = None

        #Optional,  wait for some period for data to arrive
        if wait > 0 :
            time.sleep(wait)

    def dht_read(self, PIN): 

        if PIN != self.dht_pin:
            self.set_pin_mode_dht(PIN)
        return self.dht_last_data
    
    def _store_dht(self, data) :
        self.dht_last_data = data[4:]

    # read from the digital pin. If it received any data for this pin it returns 
    # a tuple with the level and the timestamp of that measurement, otherwise returns
    # None
    def digital_read(self, pin) : 
        if pin in self._digital_pin_states :
            return self._digital_pin_states[pin]
        else: 
            return None
    
    def _store_digital_pin_state(self, data):
        """
        Default callback to store data
        data is a list with pin_type, pin_number, pin_value, raw_time_stamp
        The pin type is not interesting it is always 2
        """
        self._digital_pin_states[data[1]] = data[2:]
    """
    Private Sysex commands, these need to match those in the sketch 
    """
    _DISPLAY_OFF            = 57
    _DISPLAY_ON             = 58
    _DISPLAY_CLEAR          = 59
    _DISPLAY_SET_BRIGHTNESS = 60
    _DISPLAY_SHOW_CHAR      = 61
    _digital_pin_states = {}
    


