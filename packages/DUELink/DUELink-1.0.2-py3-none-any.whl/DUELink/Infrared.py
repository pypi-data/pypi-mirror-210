class InfraredController:
    def __init__(self, serialPort):
        self.serialPort = serialPort

    def Read(self):
        cmd = "print(irread())"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        if res.success:
            try:
                return int(res.respone)
            except:
                pass
        return -1

    def Enable(self, enable: bool):
        en = 0

        if enable == True:
            en = 1

        cmd = "irenable({})".format(int(en))
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()

        if res.success:
            return True

        return False
