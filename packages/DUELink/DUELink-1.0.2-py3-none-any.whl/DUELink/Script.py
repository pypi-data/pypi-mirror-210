import time
from DUELink.SerialInterface import SerialInterface

class ScriptController:
    def __init__(self, serialPort : SerialInterface):
        self.serialPort = serialPort

    def Run(self):
        cmd = "run"
        self.serialPort.WriteCommand(cmd)
        time.sleep(0.001)

    def New(self) -> bool:
        cmd = "new"
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()

        return res.success
    
    def Load(self, script : str) -> bool:
        cmd = "pgmstream()"

        raw = script.encode('ASCII')

        data = bytearray(len(raw) + 1)

        data[len(raw)] = 0

        data[0:len(raw)] = raw        

        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()

        if (res.success == False) :
            return False
        
        self.serialPort.WriteRawData(data, 0, len(data))

        res = self.serialPort.ReadRespone()
        return res.success
            
    
    def __Load2(self, script : str) -> bool:
        ret = True
        cmd = "$"
        self.serialPort.WriteCommand(cmd)
        time.sleep(0.001)
        script = script.replace("\r", "")

        startIdx = 0

        for i in range(0, len(script)):
            subscript = ""

            if (script[i] == '\n'):
                subscript = script[startIdx:i-startIdx]
                startIdx = i + 1
            elif i == len(script) - 1:
                 subscript = script[startIdx:i-startIdx + 1]

            self.serialPort.WriteCommand(subscript)

            res = self.serialPort.ReadRespone()

            if (res.success == False):
                ret = False
                break
        
        cmd = ">"
        self.serialPort.WriteCommand(cmd)
    
        res = self.serialPort.ReadRespone()
        
        return ret and res.success
    
    def Read(self) -> str:
        cmd = "list"

        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone2()

        return res.respone
    
    def Execute(self, script : str) -> bool:
        cmd = script
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()

        return res.respone
    
    def IsRunning(self) -> bool:
        self.serialPort.DiscardInBuffer()

        dataWrite = bytearray(1)
        dataRead = bytearray(1)

        dataWrite[0] = 0xFF
        dataRead[0] = 0x00

        self.serialPort.WriteRawData(dataWrite, 0, 1)
        time.sleep(0.001)
      
        count = self.serialPort.ReadRawData(dataRead, 0, 1)

        if count == 0:
            # if running, should received 0xff
            # it not, need to send '\n' to clear 0xff that was sent.
            dataWrite[0] = 10
            self.serialPort.WriteRawData(dataWrite, 0, 1)

            self.serialPort.ReadRespone()

        return dataRead[0] == 0xFF

       