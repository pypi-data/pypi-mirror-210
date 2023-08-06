import time
import serial
from datetime import datetime, timedelta
from DUELink.DeviceConfiguration import DeviceConfiguration

class SerialInterface:
    CommandCompleteText = ">"
    DefaultBaudRate = 115200

    DeviceConfig : DeviceConfiguration

    def __init__(self, portName):
        self.leftOver = ""        
        self.ReadTimeout = 3
        self.portName = portName
        self.echo = True        

    def Connect(self):
        self.portName = serial.Serial(self.portName, self.DefaultBaudRate, parity=serial.PARITY_NONE, bytesize=8, stopbits=serial.STOPBITS_ONE)
        self.portName.timeout = self.ReadTimeout
        self.leftOver = ""
        time.sleep(0.1)
        self.Synchronize()


    def Disconnect(self):
        try:
            self.portName.close()
        except:
            pass
        self.port = None

    def Synchronize(self):
        cmd = bytearray(1)
        cmd[0] = 127

        self.WriteRawData(cmd, 0, 1)
    
        orig = self.portName.timeout
        self.portName.timeout = 1
        tryCount = 3
        while tryCount > 0:
            time.sleep(0.01)
            self.leftOver = ""
            self.portName.reset_input_buffer()
            self.portName.reset_output_buffer()
            try:
                version = self.GetVersion()
                if version != "" and version[2] == '.' and version[4] == '.':
                    break
            except:
                pass
            tryCount -= 1
        self.portName.timeout = orig



    def TurnEchoOff(self):
        if not self.echo:
            return
        self.WriteCommand("echo(0)")
        self.ReadRespone()
        self.echo = False


    def GetVersion(self):
        command = "version()"
        self.WriteCommand(command)

        version = self.ReadRespone()

        # self.ReadCommandComplete()

        if version.success:
            if self.echo and command in version.respone:
            #if self.echo :
                # echo is on => need to turn off
                self.TurnEchoOff()
                self.portName.reset_input_buffer()
                self.portName.reset_output_buffer()
                version.respone = version.respone[len(command):]

        return version.respone

    def RemoveEchoRespone(self, respone, cmd):
        if cmd in respone:
            respone = respone[len(cmd):]

        return respone

    # def CheckResult(self, actual, expected):
    #     if actual != expected:
    #         raise Exception(f"Expected {expected}, got {actual}.")
    def DiscardInBuffer(self):
        self.portName.reset_input_buffer()

    def DiscardOutBuffer(self):
        self.portName.reset_output_buffer()

    def WriteCommand(self, command):
        self.DiscardInBuffer()
        self.DiscardOutBuffer()
        self.__WriteLine(command)

    def __WriteLine(self, string):
        string += "\n"
        # print(string)
        self.portName.write(bytes(string, 'utf-8'))

    def ReadRespone(self):
        str = self.leftOver
        end = datetime.utcnow() + timedelta(seconds=self.ReadTimeout)

        respone = CmdRespone()

        while datetime.utcnow() < end:
            data = self.portName.read(1)
            str += data.decode()

            str = str.replace("\n", "")
            str = str.replace("\r", "")
            # print(str)
            idx1 = str.find(">")
            idx2 = str.find("&")

            if idx1 == -1:
                idx1 = str.find("$")

            if idx1 == -1 and idx2 == -1:
                continue

            idx = idx2 if idx1 == -1 else idx1

            self.leftOver = str[idx + 1:]
            respone.success = True
            respone.respone = str[:idx]
            # print(respone.respone)
            idx3 = str.find("!")
            #if idx3 != -1 and 'error' in respone.respone:
            #    respone.success = False

            #if idx3 != -1 and 'unknown' in respone.respone:
            #    respone.success = False

            if idx3 != -1:
                respone.success = False


            return respone

        self.leftOver = ""

        self.portName.reset_input_buffer()
        self.portName.reset_output_buffer()

        respone.success = False
        respone.respone = ""

        return respone
    
    def ReadRespone2(self):
        str = self.leftOver
        end = datetime.utcnow() + timedelta(seconds=self.ReadTimeout)

        respone = CmdRespone()

        while datetime.utcnow() < end:
            data = self.portName.read()

            str += data.decode()

            #str = str.replace("\n", "")
            #str = str.replace("\r", "")
            # print(str)
            idx1 = str.find(">")
            idx2 = str.find("&")

            if idx1 == -1:
                idx1 = str.find("$")

            if idx1 == -1 and idx2 == -1:
                continue

            idx = idx2 if idx1 == -1 else idx1

            self.leftOver = str[idx + 1:]
            respone.success = True
            respone.respone = str[:idx]
            # print(respone.respone)
            idx3 = str.find("!")
            if idx3 != -1 and 'error' in respone.respone:
                respone.success = False

            if idx3 != -1 and 'unknown' in respone.respone:
                respone.success = False


            return respone

        self.leftOver = ""

        self.portName.reset_input_buffer()
        self.portName.reset_output_buffer()

        respone.success = False
        respone.respone = ""

        return respone

    TransferBlockSizeMax = 512
    TransferBlockDelay = 0.005

    def WriteRawData(self, buffer, offset, count):
        block = count // self.TransferBlockSizeMax
        remain = count % self.TransferBlockSizeMax

        idx = offset

        while block > 0:
            self.portName.write(buffer[idx:idx + self.TransferBlockSizeMax])
            idx += self.TransferBlockSizeMax
            block -= 1
            time.sleep(self.TransferBlockDelay)

        if remain > 0:
            self.portName.write(buffer[idx:idx + remain])

            time.sleep(self.TransferBlockDelay)

    def ReadRawData(self, buffer, offset, count):
        end = datetime.utcnow() + timedelta(seconds=self.ReadTimeout)

        if len(self.leftOver) > 0:
            raise ValueError("LeftOver size is different zero: " + str(len(self.leftOver)))

        countleft = count
        totalRead = 0

        
        #while end > datetime.utcnow():
            #read = self.portName.readinto(buffer[offset + totalRead:offset + count])
            #totalRead += read

            #if read > 0:
            #    end = datetime.utcnow() + timedelta(seconds=self.ReadTimeout)

            #if totalRead == count:
            #    break

        #return totalRead

        data = self.portName.read(count)

        if len(data) == 0:
            return 0 

        for i in range(offset,offset + count):
            buffer[i] = data[i-offset]


        return count

class CmdRespone:
    def __init__(self):
        self.respone = ""
        self.success = False
    ######################################## OLD VERSION #####################################################
    # def CmdResponse(self):
    #     self.response = ""
    #     self.success = False
    #
    # def ReadRespone(self) -> CmdResponse:
    #     str = self.leftOver
    #     end = datetime.utcnow() + timedelta(seconds=self.ReadTimeout)
    #
    #     response = SerialInterface.CmdResponse
    #
    #     while end > datetime.utcnow():
    #         data = self.portName.read()
    #
    #         str += data.decode('utf-8')
    #
    #         str = str.replace("\n", "")
    #
    #         idx1 = str.find(">")
    #         idx2 = str.find("&")
    #
    #         if idx1 == -1 and idx2 == -1:
    #             continue
    #
    #         idx = idx1 if idx1 != -1 else idx2
    #
    #         self.leftOver = str[idx + 1:]
    #         response.success = True
    #         response.response = str[:idx]
    #
    #         idx3 = str.find("!")
    #         if idx3 != -1 and "error" in response.response:
    #             response.success = False
    #
    #         return response
    #
    #     self.leftOver = ""
    #     self.portName.reset_input_buffer()
    #     self.portName.reset_output_buffer()
    #
    #     response.success = False
    #     response.response = ""
    #
    #     return response
    #
    # TransferBlockSizeMax = 256
    # TransferBlockDelay = 1
    #
    #
    #
    # def GetVersion(self):
    #     command = "version()"
    #     self.WriteCommand(command)
    #     version = self.ReadRespone()
    #     self.ReadCommandComplete()
    #     if version["success"]:
    #         if self.echo and command in version["respone"]:
    #             # echo is on => need to turn off
    #             self.TurnEchoOff()
    #             self.portName.reset_input_buffer()
    #             self.portName.reset_output_buffer()
    #             version["respone"] = version["respone"][len(command):]
    #     return version["respone"]
    #
    # def RemoveEchoRespone(self, respone, cmd):
    #     if cmd in respone:
    #         respone = respone[len(cmd):]
    #     return respone
    #
    # def WriteCommand(self, command):
    #     self.WriteCommand(command)
    #
    # def WriteCommand(self, string):
    #     string += "\n"
    #     print(string)
    #     self.portName.write(bytes(string, 'utf-8'))
    #
    # def ReadCommandComplete(self):
    #     self.check_result(str(self.ReadRespone()), self.CommandCompleteText)


    ############################### This Function delay the process too much ###########################################
    # def check_result(self,actual: str, expected: str):
    #     if actual != expected:
    #         raise ValueError(f"Expected {expected}, got {actual}.")

    ####################################################################################################################


    # class CmdResponse:
    #     def __init__(self):
    #         self.response = ""
    #         self.success = False


