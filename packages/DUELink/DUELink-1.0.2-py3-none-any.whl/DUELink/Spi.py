from typing import Optional

import time
from DUELink.SerialInterface import SerialInterface

class SpiController:
    def __init__(self, serialPort:SerialInterface):
        self.serialPort = serialPort

    def Write(self, dataWrite: bytes, offset: int, length: int, chipselect: int = -1) -> bool:
        return self.WriteRead(dataWrite, offset, length, None, 0, 0, chipselect)

    def Read(self, dataRead: bytearray, offset: int, length: int, chipselect: int = -1) -> bool:
        return self.WriteRead(None, 0, 0, dataRead, offset, length, chipselect)

    def WriteRead(self, dataWrite: Optional[bytes], offsetWrite: int, countWrite: int,
                  dataRead: Optional[bytearray], offsetRead: int, countRead: int,
                  chipselect: int = -1) -> bool:
        if chipselect >= self.serialPort.DeviceConfig.MaxPinIO:
            raise ValueError("InvalidPin")

        if (dataWrite is None and dataRead is None) or (countWrite == 0 and countRead == 0):
            raise ValueError("Invalid arguments")

        if dataWrite is not None and offsetWrite + countWrite > len(dataWrite):
            raise ValueError("Invalid arguments")

        if dataRead is not None and offsetRead + countRead > len(dataRead):
            raise ValueError("Invalid arguments")

        if chipselect < 0:
            chipselect = 255

        cmd = f"spistream({countWrite},{countRead},{chipselect})"
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()

        if not res.success:
            return False

        while countWrite > 0 or countRead > 0:
            num = countRead

            if countWrite < countRead:
                num = countWrite

            if countWrite == 0 :
                num = countRead

            if countRead == 0 :
                num = countWrite

            if (num > self.serialPort.TransferBlockSizeMax) :
                num = self.serialPort.TransferBlockSizeMax

            if countWrite > 0:
                self.serialPort.WriteRawData(dataWrite, offsetWrite, num)
                offsetWrite += num
                countWrite -= num

            if countRead > 0:
                self.serialPort.ReadRawData(dataRead, offsetRead, num)
                offsetRead += num
                countRead -= num            

        res = self.serialPort.ReadRespone()
        return res.success
    
    def Write4bpp(self, dataWrite: Optional[bytes], offsetWrite: int, countWrite: int,  chipselect: int = -1) -> bool:   
        if chipselect >= self.serialPort.DeviceConfig.MaxPinIO:
            raise ValueError("InvalidPin")
        
        if (dataWrite is None ) or (countWrite == 0):
            raise ValueError("Invalid arguments")
        
        cmd = f"spi4bpp({countWrite},{chipselect})"
        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()

        if not res.success:
            return False

        self.serialPort.WriteRawData(dataWrite, offsetWrite, countWrite)

        res = self.serialPort.ReadRespone()
        return res.success
    
    def Pallete(self, id:int, color: int) -> bool:
        if id > 16:
            raise ValueError("Pallete supports 16 color index only.")
        
        cmd = f"palette({id},{color})"

        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()
        return res.success
    
    def Configuration(self,mode: int,  frequencyKHz: int)-> bool:
        if mode > 3 or mode < 0:
            raise ValueError("Mode must be in range 0...3.")
        
        if frequencyKHz < 200  or frequencyKHz > 20000:
            raise ValueError("FrequencyKHz must be in range 200KHz to 20MHz.")
        
        cmd = f"palette({mode},{frequencyKHz})"

        self.serialPort.WriteCommand(cmd)

        res = self.serialPort.ReadRespone()
        return res.success
    

