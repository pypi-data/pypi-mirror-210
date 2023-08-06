from DUELink.SerialInterface import SerialInterface

class ServoController:
    def __init__(self, serialPort:SerialInterface):
        self.serialPort = serialPort

    def Set(self, pin, position):
        if pin < 0 or pin >= self.serialPort.DeviceConfig.MaxPinIO:
            raise ValueError('Invalid pin')
        if position < 0 or position > 180:
            raise ValueError('Position must be in the range 0..180')

        cmd = 'servoset({}, {})'.format(pin, position)
        self.serialPort.WriteCommand(cmd)

        response = self.serialPort.ReadRespone()

        return response.success
