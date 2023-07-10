import serial

class Communication:
    def __init__(self) -> None:
        self.ser = None
    
    def write(self, data):
        return self.ser.write(data)
    
    def read_until(self):
        return self.ser.read_until()
    
    def connect(self, port, baudrate=115200):
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate)
            return self.ser
        except:
            return 0 # error code
    
    def close(self):
        try:
            self.ser.close()
            return 1 # successful close
        except:
            return 0