from DUELink.Display import DisplayController
from enum import Enum
import time

class SystemController:
    class ResetOption(Enum):
        SystemReset = 0
        Bootloader = 1

    DISPLAY_MAX_LINES = 8
    DISPLAY_MAX_CHARACTER_PER_LINE = 21

    def __init__(self, serialPort):
        self.serialPort = serialPort
        self.print_posx = 0
        self.displayText = ["", "", "", "", "", "", "", ""]

    def Reset(self, option : Enum):
        cmd = "reset({0})".format(1 if option.value == 1 else 0)
        self.serialPort.WriteCommand(cmd)
        # The device will reset in bootloader or system reset
        self.serialPort.Disconnect()

    def GetTickMicroseconds(self):
        cmd = "print(tickus())"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        if res.success:
            try:
                return int(res.respone)
            except:
                pass
        return -1
    
    def GetTickMilliseconds(self):
        cmd = "print(tickms())"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        if res.success:
            try:
                return int(res.respone)
            except:
                pass
        return -1
    
    def Beep(self, pin:int, frequency:int, duration:int)->bool:
        if frequency < 0 or frequency > 10000:
            raise ValueError("Frequency is within range[0,10000] Hz")
        if duration < 0 or duration > 1000:
            raise ValueError("duration is within range[0,1000] millisecond")
        
        cmd = "beep({0}, {1}, {2})".format(pin, frequency, duration)
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success
    
    def __PrnChar(self, c):
        if self.print_posx == SystemController.DISPLAY_MAX_CHARACTER_PER_LINE and c != '\r' and c != '\n':
            return
        
        if c ==  '\r'  or c == '\n':
            self.print_posx = 0

            for i in range (1, SystemController.DISPLAY_MAX_LINES):
                self.displayText[i-1] = self.displayText[i]

            self.displayText[SystemController.DISPLAY_MAX_LINES-1] = ""
        else:
            self.displayText[SystemController.DISPLAY_MAX_LINES-1] = self.displayText[SystemController.DISPLAY_MAX_LINES-1] + c
            self.print_posx+=1
        return
    
    def __PrnText(self, text:str, newline: bool):
        for i in range (len(text)):
            self.__PrnChar(text[i])

        display = DisplayController(self.serialPort)
        display.Clear(0)

        for i in range (len(self.displayText)):
            if self.displayText[i] != "":
                display.DrawText(self.displayText[i], 1, 0, i * 8)
        
        display.Show()

        if (newline):
            self.__PrnChar('\r')





    
    def Print(self, text)->bool:
        print(text)

        if isinstance(text, str):
            self.__PrnText(text, False)
        else:
            self.__PrnText(str(text), False)

        return True
    
    def Println(self, text)->bool:
        print(text)
        if isinstance(text, str):
            self.__PrnText(text, True)
        else:
            self.__PrnText(str(text), True)

        return True
    
    def Wait(self, millisecond: int)->bool:
        cmd = f"wait({millisecond})"       
        self.serialPort.WriteCommand(cmd)
        time.sleep(millisecond / 1000)
        res = self.serialPort.ReadRespone()
        return res.success

    






