import serial

class Communication:
    def __init__(self) -> None:
        self.device = None
    
    def write(self, data):
        return self.device.write(data)
    
    def read_until(self):
        return self.device.read_until()
    
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