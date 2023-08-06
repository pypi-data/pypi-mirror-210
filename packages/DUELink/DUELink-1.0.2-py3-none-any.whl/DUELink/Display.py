class DisplayController:
    def __init__(self, serialPort):
        self.serialPort = serialPort

    def Show(self):
        cmd = "lcdshow()"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success

    def Clear(self, color):
        cmd = f"lcdclear({color})"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success

    def SetPixel(self, color, x, y):
        cmd = f"lcdpixel({color},{x},{y})"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success

    def DrawCircle(self, color, x, y, radius):
        cmd = f"lcdcircle({color},{x},{y},{radius})"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success

    def DrawRectangle(self, color, x, y, width, height):
        cmd = f"lcdrect({color},{x},{y},{width},{height})"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success
    
    def DrawFillRect(self, color, x, y, width, height):
        cmd = f"lcdfill({color},{x},{y},{width},{height})"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success

    def DrawLine(self, color, x1, y1, x2, y2):
        cmd = f"lcdline({color},{x1},{y1},{x2},{y2})"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success

    def DrawText(self, text, color, x, y):
        cmd = f"lcdtext(\"{text}\",{color},{x},{y})"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success

    def DrawTextScale(self, text, color, x, y, scalewidth, scaleheight):
        cmd = f"lcdtexts(\"{text}\",{color},{x},{y},{scalewidth},{scaleheight})"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success

    def __Stream(self, data):
        cmd = "lcdstream()"
        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()

        if res.success:
            self.serialPort.WriteRawData(data, 0, len(data))
            # time.sleep(10)
            res = self.serialPort.ReadRespone()

        return res.success
    
    def DrawBuffer(self, color):
        WIDTH = 128
        HEIGHT = 64

        offset = 0
        length = len(color)

        data = bytearray(int(WIDTH*HEIGHT/8))
        i = offset

        for y in range(0, HEIGHT):
            for x in range(0, WIDTH):

                index = (y >> 3) * WIDTH + x

                if (i < offset + length):

                    if ((color[i] & 0x00FFFFFF) != 0): # no alpha
                        data[index] |= (1 << (y & 7)) & 0xFF
                    
                    else:
                        data[index] &= (~(1 << (y & 7))) & 0xFF
                    
                    i += 1                

        return self.__Stream(data)
    
    def DrawBufferBytes(self, color):
        offset = 0
        length = len(color)
        
        if length % 4 !=0:
            raise Exception("length must be multiple of 4")
        
        data32 = [0] * int(length/4)

        for i in range (0, len(data32), 4):
            data32[i] = (color[(i + offset) * 4 + 0] << 0) | (color[(i + offset) * 4 + 1] << 8) | (color[(i + offset) * 4 + 2] << 16) | (color[(i + offset) * 4 + 3] << 24)

        return self.DrawBuffer(data32)

    
    def Configuration(self, target: int, slaveAddress: int)-> bool:
        cmd = f"lcdconfig({target},{slaveAddress})"

        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()
        return res.success

    def DrawImageS(self, img, x: int, y: int, scaleWidth: int, scaleHeight: int,  transform: int) -> bool:        
        
        width = img[0]
        height = img[1]

        if width <=0 or height <=0 or len(img) < width*height:
            raise Exception("Invalid arguments")

        cmd = f"dim a[{len(img)}]"

        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()

        
        for i in range(len(img)):
            cmd = f"a[{(i)}] = {img[i]}"
            self.serialPort.WriteCommand(cmd)
            res = self.serialPort.ReadRespone()

            if (res.success == False):
                break
        
        if (res.success == True):
            cmd = f"lcdimgs(a, {x}, {y}, {scaleWidth}, {scaleHeight}, {transform})"

            self.serialPort.WriteCommand(cmd)
            res = self.serialPort.ReadRespone()
        

        cmd = "dim a[0]"

        self.serialPort.WriteCommand(cmd)
        res = self.serialPort.ReadRespone()

        return res.success 

    def DrawImage(self, img, x: int, y: int, transform: int) -> bool:
        return self.DrawImageS(img, x, y, 1, 1, transform)

    #def DrawImageBytes(self, data, offset: int, length: int, x: int, y: int, width: int, scaleWidth: int, scaleHeight: int,  transform: int) -> bool:
    #    if length % 4 !=0:
    #        raise Exception("length must be multiple of 4")
        
    #    data32 = [0] * int(length/4)

    #    for i in range (0, len(data32), 4):
    #        data32[i] = (data[(i + offset) * 4 + 0] << 0) | (data[(i + offset) * 4 + 1] << 8) | (data[(i + offset) * 4 + 2] << 16) | (data[(i + offset) * 4 + 3] << 24)

    #    return self.DrawImage(data32, 0, len(data32),x, y, width, scaleWidth, scaleHeight, transform)
    
    def __get_transform_none(self):
        return 0
    def __get_transform_fliphorizontal(self):
        return 1
    def __get_transform_flipvertical(self):
        return 2
    def __get_transform_rotate90(self):
        return 3
    def __get_transform_rotate180(self):
        return 4
    def __get_transform_rotate270(self):
        return 5
    def __set_transform(self):
        return 
    
    TransformNone = property(__get_transform_none, __set_transform)  
    TransformFlipHorizontal = property(__get_transform_fliphorizontal, __set_transform) 
    TransformFlipVertical = property(__get_transform_flipvertical, __set_transform) 
    TransformRotate90 = property(__get_transform_rotate90, __set_transform) 
    TransformRotate180 = property(__get_transform_rotate180, __set_transform) 
    TransformRotate270 = property(__get_transform_rotate270, __set_transform) 
