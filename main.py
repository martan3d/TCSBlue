import sys
import time
import pygame
import math
from pygame import Color, Rect, Surface

# set demo to True to remove bluetooth I/O, 
# set demo to False for normal operation

DEMO = False

try:
   import android
   from array import array                                                                                                          
   from jnius import autoclass
   from jnius import cast 
except:
   android = None

# Class for serial communication using USB-OTG cable in an Android OS.                                                               
class Serial:                                                                                                                        
    def __init__(self,port,speed):                                                                                                   
        self.Context             = autoclass('android.content.Context')                                                              
        self.UsbConstants        = autoclass('android.hardware.usb.UsbConstants')                                                    
        self.UsbDevice           = autoclass('android.hardware.usb.UsbDevice')                                                       
        self.UsbDeviceConnection = autoclass('android.hardware.usb.UsbDeviceConnection')                                             
        self.UsbEndpoint         = autoclass('android.hardware.usb.UsbEndpoint')                                                     
        self.UsbInterface        = autoclass('android.hardware.usb.UsbInterface')                                                    
        self.UsbManager          = autoclass('android.hardware.usb.UsbManager')                                                      
        self.UsbRequest          = autoclass('android.hardware.usb.UsbRequest')                                                      
        self.PythonActivity      = autoclass('org.renpy.android.PythonActivity')                                                     
        self.activity            = self.PythonActivity.mActivity                                                                     
        self.speed               = speed                                                                                             
        self.port                = port                                                                                              
        self.ReadCache           = []                                                                                                
        self.usb_mgr             = cast(self.UsbManager, self.activity.getSystemService(self.Context.USB_SERVICE))                   
        print [d.getKey() for d in self.usb_mgr.getDeviceList().entrySet().toArray()]
        self.device              = self.usb_mgr.getDeviceList().get(port)
        self.cmd                 = 'k00'
        if self.device:
            Intent                = autoclass('android.content.Intent')
            PendingIntent         = autoclass('android.app.PendingIntent')
            ACTION_USB_PERMISSION = "com.access.device.USB_PERMISSION"
            intent                = Intent(ACTION_USB_PERMISSION)
            pintent               = PendingIntent.getBroadcast(self.activity,0,intent,0)
            self.usb_mgr.requestPermission(self.device,pintent)
            if self.usb_mgr.hasPermission(self.device):
                print 'Device permission granted!'
                print 'InterfaceCount: ', self.device.getInterfaceCount()
                self.intf          = cast(self.UsbInterface, self.device.getInterface(0))
                self.UsbConnection = cast(self.UsbDeviceConnection,self.usb_mgr.openDevice(self.device))
                print self.UsbConnection
                self.UsbConnection.claimInterface(self.intf, True)
                print 'SerialNumber: ', self.UsbConnection.getSerial()
                self.UsbConnection.controlTransfer(0x40, 0, 0, 0, None, 0, 0)
                self.UsbConnection.controlTransfer(0x40, 0, 1, 0, None, 0, 0)
                self.UsbConnection.controlTransfer(0x40, 0, 2, 0, None, 0, 0)
                self.UsbConnection.controlTransfer(0x40, 2, 0, 0, None, 0, 0)               
                self.UsbConnection.controlTransfer(0x40, 3, 0x0034, 0, None, 0, 0)               
                self.UsbConnection.controlTransfer(0x40, 4, 8, 0, None, 0, 0)               
                for i in xrange(0, self.intf.getEndpointCount()):
                    if self.intf.getEndpoint(i).getType() == self.UsbConstants.USB_ENDPOINT_XFER_BULK:
                        if self.intf.getEndpoint(i).getDirection() == self.UsbConstants.USB_DIR_IN:
                            self.epIN  = self.intf.getEndpoint(i)
                        elif self.intf.getEndpoint(i).getDirection() == self.UsbConstants.USB_DIR_OUT:
                            self.epOUT = self.intf.getEndpoint(i)
            else:
                print 'Device permission not granted!'
        else:
            print 'Device not found.'
            sys.exit()
        return
    def send(self,msg):   
        MsgOut    = msg
        MsgOutHex = map(ord,MsgOut)
        self.UsbConnection.bulkTransfer(self.epOUT, MsgOutHex, len(MsgOutHex), 0)
        return True
    def read(self,BufSize=35):
        time.sleep(0.03)
        response = [0]*BufSize
        length   = self.UsbConnection.bulkTransfer(self.epIN, response, len(response), 50)
        if length >= 0:
            self.ReadCache = response
        return True
    def asyncRead(self):
        self.send(self.cmd)
        self.read()
        return
    def disconnet(self):
        self.UsbConnection.close()
        return True
   
   
   
class Bluetooth:
    def __init__(self):
        self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter') 
        self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        self.UUID = autoclass('java.util.UUID')
        self.deviceValid = False

    def prepare(self, name):
        paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        print 'Looking for paired devices'    
        print "Items ", len(paired_devices)
        
        for device in paired_devices:
            name = device.getName()
            print name
            if True:                          # connect to first device found for now device.getName() == name:
               try:
                  self.socket = device.createRfcommSocketToServiceRecord(self.UUID.fromString("00001101-0000-1000-8000-00805F9B34FB"))
               except:
                  print "cannot make connection"
                  return False
               try:
                  self.recv_stream = self.socket.getInputStream()
               except:
                  print "failed getInputStream"
                  return False
               try:
                  self.send_stream = self.socket.getOutputStream()
               except:
                  print "failed getOutputStream"
                  return False
               try:
                  self.socket.connect()
                  self.deviceValid = True
                  return True
               except:
                  print "Failed to Connect to BT"
                  return False
                  
                  
    def connected(self):
        return self.deviceValid
        
    def write(self, sendString):
        if self.deviceValid:
           self.send_stream.write([ord(b) if ord(b) <= 127 else ord(b)-256 for b in sendString])
           self.send_stream.flush()
           
    def read(self):
        datastring = ""
        if self.deviceValid:
           c = self.recv_stream.available() 
           if c > 0:
              for i in range(c):
                  datastring = datastring + chr(self.recv_stream.read())
        return datastring
        
    def close(self):
        if self.deviceValid:
           self.send_stream.flush()
           self.socket.close()
           
TIMEREVENT = pygame.USEREVENT
COLORA = (255, 0, 0, 255)
COLORB = (0, 255, 0, 255)
WHITE = (255,255,255)
FPS = 30

MAINX = 480
MAINY = 720
SPDX  = MAINX/4 + 15
SPDY  = MAINX/3

BUTTONX = 145
BUTTONY = 149

SBUTTONX = 51
SBUTTONY = 49

RBX = 145
RBY = 93

PBX = 81
PBY = 49

KEYS = 13

##
## Screen - Knob with Function Keys
##          

class mainScreen:
    def __init__(self, surface):
        self.surface = surface
        self.keys = []
        self.downkeys = []
        self.posThrottle = 630
        self.lastThrottle = 500
        self.adapterName = ""

        for i in range(0,25):
            self.downkeys.append(False)

    #### unique bitmaps for main screen
    def setupMain(self):
        self.screen0 = pygame.image.load('images/main.png').convert()
        self.knob    = pygame.image.load('images/knob.png').convert()

        self.b0      = pygame.image.load('images/button0.png').convert()
        self.b1      = pygame.image.load('images/button1.png').convert()
        self.b2      = pygame.image.load('images/button2.png').convert()
        self.b3      = pygame.image.load('images/button3.png').convert()
        self.b4      = pygame.image.load('images/button4.png').convert()
        self.b5      = pygame.image.load('images/button5.png').convert()
        self.b6      = pygame.image.load('images/button6.png').convert()
        self.b7      = pygame.image.load('images/button7.png').convert()
        self.b8      = pygame.image.load('images/button8.png').convert()
        self.b9      = pygame.image.load('images/button-right.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()

        self.keys.append([ [163, 550], self.b0, 100, False, [BUTTONX, BUTTONY], self.keydown ] )   # direction
        self.keys.append([ [312, 550], self.b5, 101, False, [BUTTONX, BUTTONY], self.keydown ] )   # stop

        self.keys.append([ [163, 400], self.b1, 0xf0, False, [BUTTONX, BUTTONY], self.keydown ] )  # Lights
        self.keys.append([ [312, 400], self.b2, 0xf1, False, [BUTTONX, BUTTONY], self.keydown ] )  # Bell

        self.keys.append([ [163, 250], self.b4, 0xf3, False, [BUTTONX, BUTTONY], self.keydown ] )  # Horn blue
        self.keys.append([ [312, 250], self.b8, 0xf7, False, [BUTTONX, BUTTONY], self.keydown ] )  # Brake

        self.keys.append([ [163, 100], self.b6, 0xf4, False, [BUTTONX, BUTTONY], self.keydown ] )  # horn green (quill?)
        self.keys.append([ [312, 100], self.b9, 102,  False, [BUTTONX, BUTTONY], self.keydown ] )  # next screen

    ### unique bitmaps for Aux screen
    def setupAux(self):
        self.screen0 = pygame.image.load('images/main.png').convert()
        self.knob    = pygame.image.load('images/knob.png').convert()
        self.b9      = pygame.image.load('images/button-right.png').convert()
        self.b10     = pygame.image.load('images/button-left.png').convert()

        self.b0     = pygame.image.load('images/button-f0.png').convert()
        self.b1     = pygame.image.load('images/button-f1.png').convert()
        self.b2     = pygame.image.load('images/button-f2.png').convert()
        self.b3     = pygame.image.load('images/button-f3.png').convert()
        self.b4     = pygame.image.load('images/button-f4.png').convert()
        self.b5     = pygame.image.load('images/button-f5.png').convert()
        self.b18    = pygame.image.load('images/button-18.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()

        self.keys.append([ [163, 550], self.b1, 0xf1, False, [BUTTONX, BUTTONY], self.keydown ] )  # f1
        self.keys.append([ [312, 550], self.b2, 0xf2, False, [BUTTONX, BUTTONY], self.keydown ] )  # f2

        self.keys.append([ [163, 400], self.b3, 0xf3, False, [BUTTONX, BUTTONY], self.keydown ] )  # f3
        self.keys.append([ [312, 400], self.b4, 0xf4, False, [BUTTONX, BUTTONY], self.keydown ] )  # f4

        self.keys.append([ [163, 250], self.b18, 0xf8, False, [BUTTONX, BUTTONY], self.keydown ] )   # mode
        self.keys.append([ [312, 250], self.b0, 0xf0, False, [BUTTONX, BUTTONY], self.keydown ] )  # f0

        self.keys.append([ [163, 100], self.b10, 110, False, [BUTTONX, BUTTONY], self.keydown ] )  # left
        self.keys.append([ [312, 100], self.b9,  112, False, [BUTTONX, BUTTONY], self.keydown ] )  # right

    def setupAux2(self):
        self.screen0 = pygame.image.load('images/main.png').convert()
        self.knob    = pygame.image.load('images/knob.png').convert()
        self.b11      = pygame.image.load('images/button-right.png').convert()
        self.b12     = pygame.image.load('images/button-left.png').convert()

        self.b5     = pygame.image.load('images/button-f5.png').convert()
        self.b6     = pygame.image.load('images/button-f6.png').convert()
        self.b7     = pygame.image.load('images/button-f7.png').convert()
        self.b8     = pygame.image.load('images/button-f8.png').convert()
        self.b9     = pygame.image.load('images/button-f9.png').convert()
        self.b19     = pygame.image.load('images/button-19.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()
        
        self.keys.append([ [163, 550], self.b5, 0xf5, False, [BUTTONX, BUTTONY], self.keydown ] )  # f5
        self.keys.append([ [312, 550], self.b6, 0xf6, False, [BUTTONX, BUTTONY], self.keydown ] )  # f6

        self.keys.append([ [163, 400], self.b7, 0xf7, False, [BUTTONX, BUTTONY], self.keydown ] )  # f7
        self.keys.append([ [312, 400], self.b8, 0xf8, False, [BUTTONX, BUTTONY], self.keydown ] )  # f8

        self.keys.append([ [163, 250], self.b9, 0xf9, False, [BUTTONX, BUTTONY], self.keydown ] )  # f9
        self.keys.append([ [312, 250], self.b19,  16, False, [BUTTONX, BUTTONY], self.keydown ] )  # f16

        self.keys.append([ [163, 100], self.b12, 110, False, [BUTTONX, BUTTONY], self.keydown ] )  # left
        self.keys.append([ [312, 100], self.b11,  112, False, [BUTTONX, BUTTONY], self.keydown ] )  # right
        
        
    def setFonts(self):
        self.font = pygame.font.Font(None, 46)
        self.statfont = pygame.font.Font("fonts/impact.ttf", 26)
        self.infofont = pygame.font.Font("fonts/impact.ttf", 40)
        self.locofont = pygame.font.Font("fonts/impact.ttf", 100)

    def setAdapterName(self, name):
        self.adapterName = name

    def drawAdapterName(self):
        rtext = self.adapterName
        txt =  self.infofont.render( rtext, True, ( 225,225,225), (0,64,0) )
        self.surface.blit(txt, (MAINX/2+24, MAINY/42+4) )

    def drawScreen(self):
        self.surface.blit(self.screen0, (0,0))                       # draw main screen
        self.drawAdapterName()
        self.drawKnob()
        self.drawKeys()
        pygame.display.flip()

    def updateKnob(self, x, y):
        if x < 145:
           self.posThrottle = y
           
    def getThrottle(self):
        return self.posThrottle
        
    def setThrottle(self, t):
        self.posThrottle = t

    def drawKnob(self):
        if self.posThrottle > self.lastThrottle + 300 or self.posThrottle < self.lastThrottle - 300:
           self.posThrottle = self.lastThrottle

        self.lastThrottle = self.posThrottle

        if self.posThrottle > 620:
           self.posThrottle = 620

        if self.posThrottle < 115:
           self.posThrottle = 115

        t = self.posThrottle
        self.surface.blit(self.knob, [13, self.posThrottle-50])

    def drawKeys(self):
        i = 0
        for k in self.keys:
            x,y = k[0]
            bmp = k[1]
            dnbmp = k[5]
            if self.downkeys[i] == False:
               self.surface.blit(bmp, [x, y])
            else:
               self.surface.blit( dnbmp, [x, y])
            i = i + 1

    def checkKeys(self, x, y, value):
        i = 0
        self.downkeys = []
        for k in self.keys:
            xb, yb = k[0]
            maxx, maxy = k[4]
            if ( (x > xb) and (x < xb + maxx) ) and ( (y > yb) and (y < yb + maxy) ):
                self.downkeys.append(value)
            else:
                self.downkeys.append(False)
            i = i + 1

    def getKeyValue(self):
        i = 0
        for k in self.downkeys:
            if k == True:
               return i, True
            i = i + 1
        return 0, False

    def buildStringMain(self, transmitString):
        # 01 - direction
        if self.downkeys[0]:
           transmitString = transmitString + chr(1)
        else:
           transmitString = transmitString + chr(0)
        # 02 - ESTOP
        if self.downkeys[1]:
           transmitString = transmitString + chr(1)
        else:
           transmitString = transmitString + chr(0)
        fcode = [0,0,0]
        for i in range(2,7):
            if self.downkeys[i]:
               fcode = self.keys[i]
               break
        if fcode != [0,0,0]:
           transmitString = transmitString + chr(fcode[2])
        else:
           transmitString = transmitString + chr(0)
        # 04 - Servo 0
        transmitString = transmitString + chr(0)
        # 05 - Servo 1
        transmitString = transmitString + chr(0)
        # 06 - CVADDR HI
        transmitString = transmitString + chr(0)
        # 07 - CVADDR
        transmitString = transmitString + chr(0)
        # 08 - CVDATA
        transmitString = transmitString + chr(0)
        for i in range(8,15):
           transmitString = transmitString + chr(0)

        return transmitString    
                
    def buildStringAux(self, transmitString):
        transmitString = transmitString + chr(0)     ## direction postion not used
        transmitString = transmitString + chr(0)     ## estop not used
        fcode = [0,0,0]                              
        for i in range(0,6):
            if self.downkeys[i]:
               fcode = self.keys[i]
               break
        if fcode != [0,0,0]:
           transmitString = transmitString + chr(fcode[2])
        else:
           transmitString = transmitString + chr(0)

        transmitString = transmitString + chr(0)     ## servo 1
        transmitString = transmitString + chr(0)     ## servo 2
           
        for i in range(6,15):
           transmitString = transmitString + chr(0)

        return transmitString    
                
    def getBTData(self, displayscreen):
        # 00 - Throttle
        t = self.posThrottle
        t = abs( (620-t)/5 )
        transmitString = chr(t)

        if displayscreen == 0:
           return self.buildStringMain(transmitString)
        elif displayscreen == 1:
           return self.buildStringAux(transmitString)
        elif displayscreen == 2:
           return self.buildStringAux(transmitString)

        return transmitString

#
# Configuration Screen Class
#

class configScreen:
    def __init__(self, surface):
        self.surface = surface
        self.keys = []
        self.downkeys = []
        self.adapterName = ""
        self.primemover = []
        self.airhorn = []
        self.bell = []
        self.mastervolume = 50
        self.airhornvolume = 50
        self.bellvolume = 50
        self.primevolume = 50
        self.pm = 0
        self.ah = 0
        self.bl = 0
        
        for i in range(0,25):
            self.downkeys.append(False)
            
    def setupTwo(self):
        self.screen0 = pygame.image.load('images/blank.png').convert()
        self.smb1    = pygame.image.load('images/sm-button0.png').convert()
        self.smb0    = pygame.image.load('images/sm-button1.png').convert()
        self.keydn   = pygame.image.load('images/sm-button-down.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()
        self.b9      = pygame.image.load('images/button-right.png').convert()
        self.b10     = pygame.image.load('images/button-left.png').convert()
        self.reset   = pygame.image.load('images/button-reset.png').convert()
        self.rpress  = pygame.image.load('images/button-rdown.png').convert()
        self.prg     = pygame.image.load('images/prg.png').convert()
        self.prgdn   = pygame.image.load('images/prg-down.png').convert()

        self.acceleration = 20
        self.deceleration = 20
        self.vstart = 0
        self.vhigh = 0
        self.vmid = 0
        
        # navigation
        self.keys.append([ [163, 100], self.b10,  120, False, [BUTTONX, BUTTONY], self.keydown ] )   # left
        self.keys.append([ [312, 100], self.b9,   121, False, [BUTTONX, BUTTONY], self.keydown ] )   # right

        self.keys.append([ [20,  510], self.smb0, 123,  False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 3
        self.keys.append([ [330, 510], self.smb1, 0xf4, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 4
        self.keys.append([ [390, 510], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  450], self.smb0, 100, False, [SBUTTONX, SBUTTONY], self.keydn ] )   # cfg 1
        self.keys.append([ [330, 450], self.smb1, 101, False, [SBUTTONX, SBUTTONY], self.keydn ] )   # cfg 2
        self.keys.append([ [390, 450], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  390], self.smb0, 123,  False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 3
        self.keys.append([ [330, 390], self.smb1, 0xf4, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 4
        self.keys.append([ [390, 390], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  330], self.smb0, 0xfd, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 5
        self.keys.append([ [330, 330], self.smb1, 0xfb, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 6
        self.keys.append([ [390, 330], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  270], self.smb0, 0xfd, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 5
        self.keys.append([ [330, 270], self.smb1, 0xfb, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 6
        self.keys.append([ [390, 270], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [170,  600], self.reset, 8, False, [RBX, RBY], self.rpress ] )  # reset
        

    def setupOne(self):
        self.screen0 = pygame.image.load('images/blank.png').convert()
        self.smb1    = pygame.image.load('images/sm-button0.png').convert()
        self.smb0    = pygame.image.load('images/sm-button1.png').convert()
        self.keydn   = pygame.image.load('images/sm-button-down.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()
        self.b9      = pygame.image.load('images/button-right.png').convert()
        self.b10     = pygame.image.load('images/button-left.png').convert()
        self.prg     = pygame.image.load('images/prg.png').convert()
        self.prgdn   = pygame.image.load('images/prg-down.png').convert()

        self.bell.append("Bell 0")
        self.bell.append("Bell 1")
        self.bell.append("Bell 2")
        self.bell.append("Bell 3")
        self.bell.append("Bell 4")
        self.bell.append("Bell 5")
        self.bell.append("Bell 6")
        self.bell.append("Bell 7")
        self.bell.append("Bell 8")
        self.bell.append("Bell 9")
        self.bell.append("Bell 10")
        self.bell.append("Bell 11")
        self.bell.append("Bell 12")
        self.bell.append("Bell 13")
        self.bell.append("Bell 14")
        self.bell.append("Bell 15")
        self.bell.append("Bell 16")
        self.bell.append("Bell 17")
        self.bell.append("Bell 18")
        self.bell.append("Bell 19")
        self.bell.append("Bell 20")
        self.bell.append("Bell 21")

        self.primemover.append("EMD 567 Non Turbo")
        self.primemover.append("EMD 645 Turbo")
        self.primemover.append("EMD 710 Turbo")
        self.primemover.append("GE FDL-16 Modern")
        self.primemover.append("ALCO 244")

        self.airhorn.append("Nathan K5LA")
        self.airhorn.append("Nathan K5LLA")
        self.airhorn.append("Nathan K5HL")
        self.airhorn.append("Nathan P5")
        self.airhorn.append("Nathan P3")
        self.airhorn.append("Nathan M5")
        self.airhorn.append("Nathan M3")
        self.airhorn.append("Wabco E2")
        self.airhorn.append("Wabco A2")
        self.airhorn.append("Holden M3H")
        self.airhorn.append("Holden K5H")
        self.airhorn.append("Leslie A200")
        self.airhorn.append("Leslie A125")
        self.airhorn.append("Leslie A125/A200")
        self.airhorn.append("Leslie S3L")
        self.airhorn.append("Leslie S3M")
        
        self.keys.append([ [163, 100], self.b10,  120, False, [BUTTONX, BUTTONY], self.keydown ] )   # left
        self.keys.append([ [312, 100], self.b9,   121, False, [BUTTONX, BUTTONY], self.keydown ] )   # right

        self.keys.append([ [20,  630], self.smb0, 100, False, [SBUTTONX, SBUTTONY], self.keydn ] )   # cfg 1
        self.keys.append([ [330, 630], self.smb1, 101, False, [SBUTTONX, SBUTTONY], self.keydn ] )   # cfg 2
        self.keys.append([ [390, 630], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  570], self.smb0, 100, False, [SBUTTONX, SBUTTONY], self.keydn ] )   # cfg 1
        self.keys.append([ [330, 570], self.smb1, 101, False, [SBUTTONX, SBUTTONY], self.keydn ] )   # cfg 2
        self.keys.append([ [390, 570], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  510], self.smb0, 123,  False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 3
        self.keys.append([ [330, 510], self.smb1, 0xf4, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 4
        self.keys.append([ [390, 510], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  450], self.smb0, 0xfd, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 5
        self.keys.append([ [330, 450], self.smb1, 0xfb, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 6
        self.keys.append([ [390, 450], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  390], self.smb0, 0xfd, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 5
        self.keys.append([ [330, 390], self.smb1, 0xfb, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 6
        self.keys.append([ [390, 390], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  330], self.smb0, 0xfd, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 5
        self.keys.append([ [330, 330], self.smb1, 0xfb, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 6
        self.keys.append([ [390, 330], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

        self.keys.append([ [20,  270], self.smb0, 0xfd, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 5
        self.keys.append([ [330, 270], self.smb1, 0xfb, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 6
        self.keys.append([ [390, 270], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg

    def setFonts(self):
        self.font = pygame.font.Font(None, 46)
        self.statfont = pygame.font.Font("fonts/impact.ttf", 26)
        self.infofont = pygame.font.Font("fonts/impact.ttf", 40)
        self.locofont = pygame.font.Font("fonts/impact.ttf", 100)

    def setAdapterName(self, name):
        self.adapterName = name

    def drawAdapterName(self):
        rtext = self.adapterName
        txt =  self.infofont.render( rtext, True, ( 225,225,225), (0,64,0) )
        self.surface.blit(txt, (10, MAINY/42+4) )

    def drawLocoNumberCfg(self):
        rtext = self.adapterName
        txt =  self.infofont.render( rtext, True, ( 225,225,225), (0,64,0) )
        self.surface.blit(txt, (MAINX/3+18, MAINY/42+4) )

    def drawConfigString(self):
        rtext = "Economi"
        txt =  self.statfont.render( rtext, True, ( 255,255,255), (0,64,0) )
        self.surface.blit(txt, (10, 110) )
        rtext = "Setup"
        txt = self.statfont.render( rtext, True, (255, 255, 255), (0,64,0) )
        self.surface.blit(txt, (10, 140) )
        rtext = "Version 1.0"
        txt = self.statfont.render( rtext, True, (255, 255, 255), (0,64,0) )
        self.surface.blit(txt, (10, 210) )

    def drawConfigItem(self, p, text):
        txt = self.statfont.render(text, True, (255, 255, 255), (0,64,0) )
        self.surface.blit(txt, (100, p*60+280) )

    def drawConfigVolume(self, p, text, v):
        txt = self.statfont.render(text, True, (255, 255, 255), (0,64,0) )
        self.surface.blit(txt, (100, p*60+280) )
        vol = self.statfont.render(v, True, (255, 255, 255), (0,64,0) )
        self.surface.blit(vol, (290, p*60+280) )

    def drawScreenTwo(self):
        self.surface.blit(self.screen0, (0,0))                       # draw main screen
        self.drawLocoNumberCfg()
        self.drawConfigString()
        text = "Acceleration"
        v = "%d" % self.acceleration
        self.drawConfigVolume(0, text, v)
        text = "Deceleration"
        v = "%d" % self.deceleration
        self.drawConfigVolume(1, text, v)
        text = "VStart"
        v = "%d" % self.vstart
        self.drawConfigVolume(2, text, v)
        text = "VMid"
        v = "%d" % self.vmid
        self.drawConfigVolume(3, text, v)
        text = "VHigh"
        v = "%d" % self.vhigh
        self.drawConfigVolume(4, text, v)

        self.drawKeys()
        pygame.display.flip()

    def drawScreen(self):
        self.surface.blit(self.screen0, (0,0))                       # draw main screen
        self.drawLocoNumberCfg()
        self.drawConfigString()
        self.drawConfigItem(0, self.primemover[self.pm])
        self.drawConfigItem(1, self.airhorn[self.ah])
        self.drawConfigItem(2, self.bell[self.bl])
        text = "Master Volume"
        vol  = "%d" % self.mastervolume
        self.drawConfigVolume(3, text, vol)
        text = "Airhorn Volume"
        vol  = "%d" % self.airhornvolume
        self.drawConfigVolume(4, text, vol)
        text = "Bell Volume"
        vol = "%d" % self.bellvolume
        self.drawConfigVolume(5, text, vol)
        text = "Prime Mover"
        vol = "%d" % self.primevolume
        self.drawConfigVolume(6, text, vol)

        self.drawKeys()
        pygame.display.flip()

        
    def updateValuesTwo(self, value):
        # Acceleration
        if value == 15:
           self.acceleration = self.acceleration + 1
           if self.acceleration > 255:
              self.acceleration = 255
        if value == 14:
           self.acceleration = self.acceleration - 1
           if self.acceleration < 0:
              self.acceleration = 0

        # Deceleration
        if value == 12:
           self.deceleration = self.deceleration + 1
           if self.deceleration > 100:
              self.deceleration = 100
        if value == 11:
           self.deceleration = self.deceleration - 1
           if self.deceleration < 0:
              self.deceleration = 0
        
        # vstart
        if value == 9:
           self.vstart = self.vstart + 1
           if self.vstart > 255:
              self.vstart = 255
        if value == 8:
           self.vstart = self.vstart - 1
           if self.vstart < 0:
              self.vstart = 0
              
        # VMid
        if value == 6:
           self.vmid = self.vmid + 1
           if self.vmid > 255:
              self.vmid = 255
        if value == 5:
           self.vmid = self.vmid - 1
           if self.vmid < 0:
              self.vmid = 0           
        
        # VHigh
        if value == 3:
           self.vhigh = self.vhigh + 1
           if self.vhigh > 255:
              self.vhigh = 255
        if value == 2:
           self.vhigh = self.vhigh - 1
           if self.vhigh < 0:
              self.vhigh = 0           
                
        
    def updateValues(self, value):
        # prime mover select
        print value
        if value == 21:
           self.pm = self.pm + 1
           if self.pm > 4:
              self.pm = 0
        if value == 20:
           self.pm = self.pm - 1
           if self.pm < 0:
              self.pm = 4

        # horn select
        if value == 18:
           self.ah = self.ah + 1
           if self.ah > 15:
              self.ah = 0
        if value == 17:
           self.ah = self.ah - 1
           if self.ah < 0:
              self.ah = 15

        # bell select
        if value == 15:
           self.bl = self.bl + 1
           if self.bl > 21:
              self.bl = 0
        if value == 14:
           self.bl = self.bl - 1
           if self.bl < 0:
              self.bl = 21

        # master volume
        if value == 12:
           self.mastervolume = self.mastervolume + 5
           if self.mastervolume > 100:
              self.mastervolume = 0
        if value == 11:
           self.mastervolume = self.mastervolume - 5
           if self.mastervolume < 0:
              self.mastervolume = 0
               
        # airhorn volume
        if value == 9:
           self.airhornvolume = self.airhornvolume + 5
           if self.airhornvolume > 100:
              self.airhornvolume = 0
        if value == 8:
           self.airhornvolume = self.airhornvolume - 5
           if self.airhornvolume < 0:
              self.airhornvolume = 0
    
        # bell volume
        if value == 6:
           self.bellvolume = self.bellvolume + 5
           if self.bellvolume > 100:
              self.bellvolume = 0
        if value == 5:
           self.bellvolume = self.bellvolume - 5
           if self.bellvolume < 0:
              self.bellvolume = 0

        # prime mover volume
        if value == 3:
           self.primevolume = self.primevolume + 5
           if self.primevolume > 100:
              self.primevolume = 0
        if value == 2:
           self.primevolume = self.primevolume - 5
           if self.primevolume < 0:
              self.primevolume = 0
              

              
    def drawKeys(self):
        i = 0
        for k in self.keys:
            x,y = k[0]
            bmp = k[1]
            dnbmp = k[5]
            if self.downkeys[i] == False:
               self.surface.blit(bmp, [x, y])
            else:
               self.surface.blit( dnbmp, [x, y])
            i = i + 1

    def checkKeys(self, x, y, value):
        i = 0
        self.downkeys = []
        for k in self.keys:
            xb, yb = k[0]
            maxx, maxy = k[4]
            if ( (x > xb) and (x < xb + maxx) ) and ( (y > yb) and (y < yb + maxy) ):
                self.downkeys.append(value)
            else:
                self.downkeys.append(False)
            i = i + 1
        
    def getKeyValue(self):
        i = 0
        for k in self.downkeys:
            if k == True:
               return i, True
            i = i + 1
        return 0, False
        
    def getCVDataTwo(self):
        addr, v = self.getKeyValue()
        if addr == 16:
           return 3, self.acceleration
        if addr == 13:
           return 4, self.deceleration
        if addr == 10:
           return 2, self.vstart
        if addr == 7:
           return 6, self.vmid
        if addr == 4:
           return 5, self.vhigh        

        # RESET BUTTON - LEAVE THIS OFF FOR NOW
#        if addr == 17:
#           return 8, 8

        return 0, 0

    def getCVData(self):
        addr, v = self.getKeyValue()
        # check for prime mover select
        if addr == 22:
           return 123, self.pm        # prime mover CV value address
           
        if addr == 19:
           return 120, self.ah        # airhorn select
           
        if addr == 16:                # bell select
           return 122, self.bl
           
        if addr == 13:
           return 128, self.mastervolume
           
        if addr == 10:
           return 129, self.airhornvolume
           
        if addr == 7:
           return 130, self.bellvolume
           
        if addr == 4:
           return 131, self.primevolume

        return 0, 0
        
    def getBTData(self, screen):
        # 00 - Throttle
        transmitString = chr(0)   ## NOTE: set to zero in configuration screen, no movement allowed!
        # 01 - direction
        transmitString = transmitString + chr(0)   # also set to zero for forward- no movement allowed
        transmitString = transmitString + chr(0)   # estop zero
        transmitString = transmitString + chr(0)   # no function code allowed

        # 04 - Servo 0
        transmitString = transmitString + chr(0)   # no servos

        # 05 - Servo 1
        transmitString = transmitString + chr(0)

        # 06 - CVADDR HI
        transmitString = transmitString + chr(0)   ## FILL THESE IN for CV changes

        # 07 - CVADDR
        if screen == 2:
           a, v = self.getCVData()
        elif screen == 3:
           a, v = self.getCVDataTwo()
           
        #if a != 0 : print a, v, screen
        transmitString = transmitString + chr(a)

        # 08 - CVDATA
        transmitString = transmitString + chr(v)

        for i in range(8,15):
           transmitString = transmitString + chr(0)

        return transmitString


class mainLoop:
    def __init__(self):
        self.initialized = True
        self.running = True
        self.toggle = 0
        self.transmitString = "---initialize---"
        self.receiveString  = "0123456789012345"
        self.adapterName = "HC-05"
        self.displayscreen = 0
        self.mousedown = False
         
    def setup(self):
        pygame.init()
        pygame.time.set_timer(TIMEREVENT, 1000 / FPS)
        
        self.surface  = pygame.display.set_mode((MAINX, MAINY))

        ### first screen
        self.mainscreen = mainScreen(self.surface)
        self.mainscreen.setupMain()
        self.mainscreen.setFonts()
        self.mainscreen.setAdapterName(self.adapterName)
        self.mainscreen.drawScreen()
        
        ### second screen
        self.auxscreen = mainScreen(self.surface)
        self.auxscreen.setupAux()
        self.auxscreen.setFonts()
        self.auxscreen.setAdapterName(self.adapterName)
        
        ## third screen
        self.auxscreen2 = mainScreen(self.surface)
        self.auxscreen2.setupAux2()
        self.auxscreen2.setFonts()
        self.auxscreen2.setAdapterName(self.adapterName) 


        if android:
           android.init()
           android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
           
           # DEMO controls if Bluetooth is enabled
           if DEMO == True: 
              return
           
           self.Bluetooth = Bluetooth()
           for i in range(0,2):
              if self.Bluetooth.prepare(self.adapterName):
                 break
              string = "Trying to Connect to %s - %d" % (self.adapterName, i)
              print string

##
## Read and Write BT data to/from phone
##
            
    def rwBluetooth(self):                                          # read bluetooth
        self.toggle = self.toggle + 1                               # this is called 30 times per sec
        if self.toggle == 2:                                        # toggle throttles the data flow
           if android:
              self.Bluetooth.write(self.transmitString)
        if self.toggle == 4:
           self.toggle = 0
           if android:
              t = self.Bluetooth.read()
              if t != "":
                 self.receiveString = t
##
##
## Main Run Loop
##
##

    def runLoop(self):
        self.surface.fill( (0,0,0))
        while self.running:

            ev = pygame.event.wait()
            # Android-specific:
            if android:
                if android.check_pause():
                    android.wait_for_resume()

            # Update things based on the FPS timer
            if ev.type == TIMEREVENT:
                if self.displayscreen == 0:
                   self.mainscreen.drawScreen()
                   self.transmitString = self.mainscreen.getBTData(self.displayscreen)
                elif self.displayscreen == 1:
                   self.auxscreen.drawScreen()
                   self.transmitString = self.auxscreen.getBTData(self.displayscreen)
                elif self.displayscreen == 2:
                   self.auxscreen2.drawScreen()
                   self.transmitString = self.auxscreen2.getBTData(self.displayscreen)
                elif self.displayscreen == 3:
                   self.configTwo.drawScreenTwo()
                   self.transmitString = self.configTwo.getBTData(self.displayscreen)
                   
                if android:
                   if DEMO == False:
                      if self.Bluetooth.connected():
                         self.rwBluetooth()

            # process any user input
            elif ev.type == pygame.MOUSEBUTTONDOWN and self.mousedown == False:
                self.mousedown = True
                x, y = pygame.mouse.get_pos()
                if self.displayscreen == 0:
                   self.mainscreen.checkKeys(x,y, True)
                   k,v = self.mainscreen.getKeyValue()
                   if v == True and k == 7:
                      t = self.mainscreen.getThrottle()
                      self.auxscreen.setThrottle(t)             ## keep both screen throttles in sync
                      self.displayscreen = 1

                elif self.displayscreen == 1:
                   self.auxscreen.checkKeys(x,y, True)
                   k,v = self.auxscreen.getKeyValue()
                   if v == True and k == 6:
                      t = self.auxscreen.getThrottle()
                      self.mainscreen.setThrottle(t)
                      self.displayscreen = 0
                   if v == True and k == 7:
                      self.displayscreen = 2
                      t = self.auxscreen.getThrottle()
                      self.auxscreen2.setThrottle(t)

                elif self.displayscreen == 2:
                   self.auxscreen2.checkKeys(x,y, True)
                   k,v = self.auxscreen2.getKeyValue()
                   print k,v
                   if v == True and k == 6:
                      self.displayscreen = 1
                      t = self.auxscreen2.getThrottle()
                      self.auxscreen.setThrottle(t)
                   elif v == True and k == 7:
                      self.displayscreen = 0       ## back to start
                      t = self.auxscreen2.getThrottle()
                      self.mainscreen.setThrottle(t)

                elif self.displayscreen == 3:
                   self.configTwo.checkKeys(x,y, True)
                   k,v = self.configTwo.getKeyValue()
                   #if v == True: print k
                   if v == True and k == 0:
                      self.displayscreen = 2
                   elif v == True and k == 1:
                      self.displayscreen = 0
                   elif v == True:
                      self.configTwo.updateValuesTwo(k)
                      
            # Check mouse motion for knob
            elif ev.type == pygame.MOUSEMOTION and self.mousedown == True:
               if self.mousedown:
                   x, y = pygame.mouse.get_pos()
                   if self.displayscreen == 0:
                      self.mainscreen.updateKnob(x,y)
                   elif self.displayscreen == 1:
                      self.auxscreen.updateKnob(x,y)
                   elif self.displayscreen == 2:
                      self.auxscreen2.updateKnob(x,y)
                
            # Mouse up event, check keys
            elif ev.type == pygame.MOUSEBUTTONUP and self.mousedown == True:
                self.mousedown = False
                x, y = pygame.mouse.get_pos()
                if self.displayscreen == 0:
                   self.mainscreen.checkKeys(x, y, False)
                elif self.displayscreen == 1:
                   self.auxscreen.checkKeys(x, y, False)
                elif self.displayscreen == 2:
                   self.auxscreen2.checkKeys(x, y, False)
                elif self.displayscreen == 3:
                   self.configTwo.checkKeys(x, y, False)

            # Back or escape ends the app
            elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.running = False
                if android and DEMO == False:
                   self.Bluetooth.close()
                break

mainApp = mainLoop()
mainApp.setup()
mainApp.runLoop()













        
