class UartController:
    def __init__(self, serialport):
        self.serialport = serialport

    def Enable(self, baudrate):
        cmd = "uartinit({})".format(baudrate)
        self.serialport.WriteCommand(cmd)
        res = self.serialport.ReadRespone()
        return res.success

    def Write(self, data):
        cmd = "uartwrite({})".format(data)
        self.serialport.WriteCommand(cmd)
        res = self.serialport.ReadRespone()
        return res.success

    def BytesToRead(self):
        cmd = "x=uartcount():print(x)"
        self.serialport.WriteCommand(cmd)
        res = self.serialport.ReadRespone()
        if res.success:
            try:
                ready = int(res.respone)
                return ready
            except:
                pass
        raise Exception("BytesToRead error!")

    def Read(self):
        cmd = "x=uartread():print(x)"
        self.serialport.WriteCommand(cmd)
        res = self.serialport.ReadRespone()
        if res.success:
            try:
                data = int(res.respone)
                return data
            except:
                pass
        raise Exception("Uart receving error!")
