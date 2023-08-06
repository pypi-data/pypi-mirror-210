import time

class NeoController:
    MAX_LED_NUM = 256

    def __init__(self, serialPort):
        self.serialPort = serialPort
        self.SupportLedNumMax = self.MAX_LED_NUM

    def Show(self, pin: int, count: int):
        cmd = "neoshow({0}, {1})".format(pin, count)
        self.serialPort.WriteCommand(cmd)

        # each led need 1.25us delay blocking mode
        delay = (self.MAX_LED_NUM * 3 * 8 * 1.25) / 1000000
        time.sleep(delay)

        res = self.serialPort.ReadRespone()

        return res.success

    def Clear(self):
        cmd = "neoclear()"
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()

        return res.success

    def SetColor(self, id: int, color: int):
        red = (color >> 16) & 0xFF
        green = (color >> 8) & 0xFF
        blue = (color >> 0) & 0xFF

        if id < 0 or id > self.MAX_LED_NUM:
            return False

        cmd = "neoset({0},{1},{2},{3})".format(id, red, green, blue)
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()

        return res.success

    def SetMultiple(self, pin: int, color):
        if len(color) > self.MAX_LED_NUM:
            return False
        
        length = len(color) 
        offset = 0
        
        data = bytearray(length*3)

        for i in range(offset, length + offset):
            data[(i - offset) * 3 + 0] = (color[i] >> 16) & 0xff
            data[(i - offset) * 3 + 1] = (color[i] >> 8) & 0xff
            data[(i - offset) * 3 + 2] = (color[i] >> 0) & 0xff

        cmd = "neostream({0}, {1})".format(pin, len(data))
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()

        if res.success:
            self.serialPort.WriteRawData(data, 0, len(data))
            res = self.serialPort.ReadRespone()

        return res.success
