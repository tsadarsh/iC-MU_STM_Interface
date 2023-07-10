import serial
from time import sleep

class Communication:
    def __init__(self) -> None:
        self.device = None
    
    def write(self, data):
        try:
            return self.device.write(data)
        except serial.serialutil.SerialException:
            data = {
                'msg': "Write failed! Device disconnected.",
                'retry': True
            }
            self._ErrorHandler(data)
    
    def read_until(self):
        try:
            return self.device.read_until()
        except serial.serialutil.SerialException:
            data = {
                'msg': "Read failed! Device disconnected.",
                'retry': True
            }
            self._ErrorHandler(data)
    
    def connect(self, port, baudrate=115200):
        try:
            self.device = serial.Serial(port=port, baudrate=baudrate)
            return self.device
        except:
            return 0 # error code
    
    def close(self):
        try:
            self.device.close()
            return 1 # successful close
        except:
            return 0
    
    def _ErrorHandler(self, data):
        print(data['msg'])
        if data['retry']:
            #TODO
            ...