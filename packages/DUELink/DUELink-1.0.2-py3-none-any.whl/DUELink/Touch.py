class TouchController:
    def __init__(self, serialPort):
        self.serialPort = serialPort

    def Read(self, pin):
        cmd = "print(touchread({0}))".format(pin)
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()
        val = False
        if res.success:
            try:
                val = int(res.respone) == 1
                return val
            except:
                pass
        return val
