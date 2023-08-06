from typing import Optional

class I2cController:
    def __init__(self, serialPort) -> None:
        self.serialPort = serialPort

    def Write(self, address: int, data: bytes, offset: int, length: int) -> bool:
        return self.WriteRead(address, data, offset, length, None, 0, 0)

    def Read(self, address: int, data: bytearray, offset: int, length: int) -> bool:
        return self.WriteRead(address, None, 0, 0, data, offset, length)

    def WriteRead(self, address: int, dataWrite: Optional[bytes], offsetWrite: int, countWrite: int, dataRead: Optional[bytearray], offsetRead: int, countRead: int) -> bool:
        if (dataWrite is None and dataRead is None) or (countWrite == 0 and countRead == 0):
            raise ValueError("At least one of dataWrite or dataRead must be specified")
        
        if dataWrite is None and countWrite != 0:
            raise Exception("dataWrite null but countWrite not zero")

        if dataRead is None and countRead != 0:
            raise Exception("dataRead null but countRead not zero")

        if dataWrite is not None and offsetWrite + countWrite > len(dataWrite):
            raise ValueError("Invalid range for dataWrite")

        if dataRead is not None and offsetRead + countRead > len(dataRead):
            raise ValueError("Invalid range for dataRead")

        cmd = f"i2cstream({address},{countWrite},{countRead})"
        self.serialPort.WriteCommand(cmd)        

        if countWrite > 0:
            res = self.serialPort.ReadRespone()

            if not res.success:
                raise ValueError("I2c error:" + res.respone)
            
            self.serialPort.WriteRawData(dataWrite, offsetWrite, countWrite)

        if countRead > 0:
 
            if self.serialPort.ReadRawData(dataRead, offsetRead, countRead) != countRead:
                raise ValueError("I2C read raw data error.")

        res = self.serialPort.ReadRespone()
        return res.success