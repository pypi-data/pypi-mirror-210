class TemperatureController:
    def __init__(self, serialPort):
        self.serialPort = serialPort

    def Read(self, pin: int, sensortype: int) -> float:
        cmd = f"print(temp({pin},{sensortype}))"
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()
        return res.success
    
    def __get_dht11(self):
        return 11

    def __get_dht12(self):
        return 12
    
    def __get_dht21(self):
        return 21
    
    def __get_dht22(self):
        return 22
    
    def __set_dht(self):
        return
    
    Dht11 = property(__get_dht11, __set_dht)
    Dht12 = property(__get_dht12, __set_dht)
    Dht21 = property(__get_dht21, __set_dht)
    Dht22 = property(__get_dht22, __set_dht)
