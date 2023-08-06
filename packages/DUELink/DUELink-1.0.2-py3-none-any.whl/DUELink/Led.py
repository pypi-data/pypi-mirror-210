class LedController:
    def __init__(self, serialPort):
        self.serialPort = serialPort

    def Set(self, highPeriod: int, lowPeriod: int, count: int) -> bool:
        cmd = f"led({highPeriod},{lowPeriod},{count})"
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()
        return res.success
