
from DUELink.SerialInterface import SerialInterface

class DigitalController:    

    def __init__(self, serialPort:SerialInterface):
        self.serialPort = serialPort

    def Read(self, pin, inputType: 0) -> bool:
        if pin == 'a' or pin == 'A':
            pin = 97

        if pin == 'b' or pin == 'B':
            pin = 98

        if pin < 0 or (pin >= self.serialPort.DeviceConfig.MaxPinIO and pin != 97 and pin != 98 and pin != 108): #A, B, Led
            raise ValueError("Invalid pin")

        pull = "0"
        if inputType == 1:
            pull = "1"
        elif inputType == 2:
            pull = "2"

        cmd = f"print(dread({pin},{pull}))"
        self.serialPort.WriteCommand(cmd)

        respone = self.serialPort.ReadRespone()

        if respone.success:            
            try:
                value = int(respone.respone)
                return value == 1
            except:
                pass

        return False

    def Write(self, pin, value: bool) -> bool:
        if pin == 'l' or pin == 'L':
            pin = 108

        if pin < 0 or (pin >= self.serialPort.DeviceConfig.MaxPinIO and pin != 108): # Led
            raise ValueError("Invalid pin")

        cmd = f"dwrite({pin},{1 if value else 0})"
        self.serialPort.WriteCommand(cmd)

        respone = self.serialPort.ReadRespone()

        return respone.success
