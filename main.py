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

class Bluetooth:
    def __init__(self):
        self.BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter') 
        self.BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
        self.BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
        self.UUID = autoclass('java.util.UUID')
        self.deviceValid = False
        
    def getDevices(self):
        paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        for p in paired_devices:
            print p.getName()
        return paired_devices
        
    def prepare(self, name):
        paired_devices = self.BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        for device in paired_devices:
            print device.getName()
            if name == device.getName():
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
## Screen - Knob with Function Keys  TCS WOW VERSION  ******************************************
##          

class mainScreen:
    def __init__(self, surface):
        self.surface = surface
        self.keys = []
        self.downkeys = []
        self.posThrottle = 630
        self.lastThrottle = 500
        self.adapterName = ""
        self.coupler0 = False
        self.coupler1 = False
        self.BlueDevices = None
        self.bluenames = []
        self.nameindex = 0
        
        for i in range(0,25):
            self.downkeys.append(False)

    def setDevices(self, devices):
        self.BlueDevices = devices
        self.bluenames = []
        for d in devices:
            self.bluenames.append(d.getName())

    def getBlueName(self):
        return self.bluenames[self.nameindex]
            
    def setupDevice(self):
        self.screen0 = pygame.image.load('images/blank.png').convert()
        self.smb1    = pygame.image.load('images/sm-button0.png').convert()
        self.smb0    = pygame.image.load('images/sm-button1.png').convert()
        self.keydn   = pygame.image.load('images/sm-button-down.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()
        self.b9      = pygame.image.load('images/button-right.png').convert()
        self.b10     = pygame.image.load('images/button-left.png').convert()
        self.prg     = pygame.image.load('images/prg.png').convert()
        self.prgdn   = pygame.image.load('images/prg-down.png').convert()
        
        self.keys.append([ [20,  270], self.smb0, 123,  False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 3
        self.keys.append([ [330, 270], self.smb1, 0xf4, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 4
        self.keys.append([ [390, 270], self.prg, 0xf4, False,  [PBX, PBY],           self.prgdn ] )  # cfg prg
          
            
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

        self.keys.append([ [160, 550], self.b0, 100, False, [BUTTONX, BUTTONY], self.keydown ] )   # direction
        self.keys.append([ [315, 550], self.b5, 101, False, [BUTTONX, BUTTONY], self.keydown ] )   # stop

        self.keys.append([ [160, 400], self.b1, 0xf0, False, [BUTTONX, BUTTONY], self.keydown ] )  # Lights
        self.keys.append([ [315, 400], self.b2, 0xf1, False, [BUTTONX, BUTTONY], self.keydown ] )  # Bell

        self.keys.append([ [160, 250], self.b4, 0xf3, False, [BUTTONX, BUTTONY], self.keydown ] )  # Horn blue
        self.keys.append([ [315, 250], self.b8, 0xf7, False, [BUTTONX, BUTTONY], self.keydown ] )  # Brake

        self.keys.append([ [160, 100], self.b6, 0xf4, False, [BUTTONX, BUTTONY], self.keydown ] )  # horn green (quill?)
        self.keys.append([ [315, 100], self.b9, 102,  False, [BUTTONX, BUTTONY], self.keydown ] )  # next screen

        
    def setupSecond(self):
        self.screen0 = pygame.image.load('images/main.png').convert()
        self.knob    = pygame.image.load('images/knob.png').convert()
        self.right   = pygame.image.load('images/button-right.png').convert()
        self.left    = pygame.image.load('images/button-left.png').convert()

        # couplers and fans
        self.cback  = pygame.image.load('images/button-14.png').convert()
        self.cfront = pygame.image.load('images/button-13.png').convert()
        self.fan1   = pygame.image.load('images/button-fan1.png').convert()
        self.fan2   = pygame.image.load('images/button-fan2.png').convert()
        self.radio  = pygame.image.load('images/button-walkie.png').convert()

        self.mode   = pygame.image.load('images/button-18.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()

        #                   display    png         keyvalue         size                down image
        
        self.keys.append([ [160, 550], self.cfront,  80, False, [BUTTONX, BUTTONY], self.keydown ] )  # coupler
        self.keys.append([ [315, 550], self.cback,   81, False, [BUTTONX, BUTTONY], self.keydown ] )  # 

        self.keys.append([ [160, 400], self.fan1, 0xf3, False, [BUTTONX, BUTTONY], self.keydown ] )  # fan f3
        self.keys.append([ [315, 400], self.fan2, 0xf4, False, [BUTTONX, BUTTONY], self.keydown ] )  # fan f4

        self.keys.append([ [160, 250], self.mode, 0xf8, False, [BUTTONX, BUTTONY], self.keydown ] )   # mode
        self.keys.append([ [315, 250], self.radio,  16, False, [BUTTONX, BUTTONY], self.keydown ] )   # radio

        self.keys.append([ [160, 100], self.left,  110, False, [BUTTONX, BUTTONY], self.keydown ] )  # left
        self.keys.append([ [315, 100], self.right, 112, False, [BUTTONX, BUTTONY], self.keydown ] )  # right    
        
     
        
    ### unique bitmaps for Aux screen - TCS audio assist and Generic Function Code Screen
    def setupAux(self):
        self.screen0 = pygame.image.load('images/main.png').convert()
        self.knob    = pygame.image.load('images/knob.png').convert()
        self.right    = pygame.image.load('images/button-right.png').convert()
        self.left     = pygame.image.load('images/button-left.png').convert()

        self.cfg    = pygame.image.load('images/button-long-cfg.png').convert()
        self.b0     = pygame.image.load('images/sm-0.png').convert()
        self.b1     = pygame.image.load('images/sm-1.png').convert()
        self.b2     = pygame.image.load('images/sm-2.png').convert()
        self.b3     = pygame.image.load('images/sm-3.png').convert()
        self.b4     = pygame.image.load('images/sm-4.png').convert()
        self.b5     = pygame.image.load('images/sm-5.png').convert()
        self.b6     = pygame.image.load('images/sm-6.png').convert()
        self.b7     = pygame.image.load('images/sm-7.png').convert()
        self.b8     = pygame.image.load('images/sm-8.png').convert()
        self.b9     = pygame.image.load('images/sm-9.png').convert()
        self.cfgdn  = pygame.image.load('images/button-long-cfg-blank.png').convert()

        self.smkeydown = pygame.image.load('images/sm-blank.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()
        
        SMBTX = 97
        SMBTY = 106   
        
        SMBCFGX = 197

        self.keys.append([ [163, 564], self.cfg, 0xf8, False, [SMBCFGX, SMBTY],   self.cfgdn ] ) # f8
        self.keys.append([ [363, 563], self.b0,  0xf0, False, [SMBTX, SMBTY], self.smkeydown ] ) # f0

        self.keys.append([ [163, 459], self.b1, 0xf1, False, [SMBTX, SMBTY], self.smkeydown ] )  # f1
        self.keys.append([ [263, 459], self.b2, 0xf2, False, [SMBTX, SMBTY], self.smkeydown ] )  # f2
        self.keys.append([ [363, 459], self.b3, 0xf3, False, [SMBTX, SMBTY], self.smkeydown ] )  # f3

        self.keys.append([ [163, 355], self.b4, 0xf4, False, [SMBTX, SMBTY], self.smkeydown ] )  # f4
        self.keys.append([ [263, 355], self.b5, 0xf5, False, [SMBTX, SMBTY], self.smkeydown ] )  # f5
        self.keys.append([ [363, 355], self.b6, 0xf6, False, [SMBTX, SMBTY], self.smkeydown ] )  # f6

        self.keys.append([ [163, 250], self.b7, 0xf7, False, [SMBTX, SMBTY], self.smkeydown ] )  # f7
        self.keys.append([ [263, 250], self.b8, 0xf8, False, [SMBTX, SMBTY], self.smkeydown ] )  # f8
        self.keys.append([ [363, 250], self.b9, 0xf9, False, [SMBTX, SMBTY], self.smkeydown ] )  # f9

        self.keys.append([ [160, 100], self.left,  110, False, [SMBTX, SMBTY], self.keydown ] )  # left
        self.keys.append([ [315, 100], self.right, 112, False, [SMBTX, SMBTY], self.keydown ] )  # right    

       
    def setFonts(self):
        self.font = pygame.font.Font(None, 46)
        self.statfont = pygame.font.Font("fonts/impact.ttf", 26)
        self.infofont = pygame.font.Font("fonts/impact.ttf", 40)
        self.locofont = pygame.font.Font("fonts/impact.ttf", 60)

    def setAdapterName(self, name):
        self.adapterName = name

    def drawAdapterName(self):
        rtext = self.adapterName
        txt =  self.infofont.render( rtext, True, ( 225,225,225), (0,64,0) )
        x = (MAINX/3)+45 - len(rtext)/2
        self.surface.blit(txt, (x, 21) )

    def drawScreen(self):
        self.surface.blit(self.screen0, (0,0))                       # draw main screen
        self.drawAdapterName()
        self.drawKnob()
        self.drawKeys()
        pygame.display.flip()
        
    def drawDeviceScreen(self):
        self.surface.blit(self.screen0, (0,0))                       # draw device main screen
        txt =  self.locofont.render( "Bluetooth", True, ( 225,225,225), (0,64,0) )
        self.surface.blit(txt, (124, 60) )
        txt =  self.infofont.render( "Choose Device", True, ( 225,225,225), (0,64,0) )
        self.surface.blit(txt, (124, 150) )
        try:
           self.drawConfigItem(0, self.bluenames[self.nameindex])
        except:
           self.drawConfigItem(0, "no devices found!")
        self.drawKeys()
        pygame.display.flip()

    def updateName(self, key):
        if key == 1:
           self.nameindex = self.nameindex + 1
           if self.nameindex > len(self.bluenames):
              self.nameindex = 0
        if key == 0:
           self.nameindex = self.nameindex - 1
           if self.nameindex < 0:
              self.nameindex = len(self.bluenames)
        if key == 2:
           pass        
        
    def drawConfigItem(self, p, text):
        txt = self.statfont.render(text, True, (255, 255, 255), (0,64,0) )
        self.surface.blit(txt, (100, p*60+280) )
       
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
        for i in range(0,len(self.downkeys)):
            if self.downkeys[i]:
               fcode = self.keys[i]
               break
        if fcode != [0,0,0]:
           transmitString = transmitString + chr(fcode[2])
           #print fcode[2]
        else:
           transmitString = transmitString + chr(0)

        # servo 1    
        if self.downkeys[0] == True:
           transmitString = transmitString + chr(101)   ## servo 1
           print "transmit 101"
        else:    
           transmitString = transmitString + chr(0)     ## servo 1

        # servo 1    
        if self.downkeys[1] == True:
           transmitString = transmitString + chr(102)   ## servo 2
           print "transmit 102"
        else:    
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
#####
#########################################################################################################
#####
#

class mainLoop:
    def __init__(self):
        self.initialized = True
        self.running = True
        self.toggle = 0
        self.transmitString = "---initialize---"
        self.receiveString  = "0123456789012345"
        self.adapterName = "TCS 501 Demo"
        self.displayscreen = 10
        self.mousedown = False
        self.devices = None
         
    def setup(self):
        pygame.init()
        pygame.time.set_timer(TIMEREVENT, 1000 / FPS)
        
        self.surface  = pygame.display.set_mode((MAINX, MAINY))
        
        ### Bluetooth Device Select Screen
        self.devicescreen = mainScreen(self.surface)
        self.devicescreen.setupDevice()
        self.devicescreen.setFonts()
        
        ### first screen
        self.mainscreen = mainScreen(self.surface)
        self.mainscreen.setupMain()
        self.mainscreen.setFonts()
        self.mainscreen.setAdapterName(self.adapterName)
        
        ### second screen
        self.auxscreen = mainScreen(self.surface)
        self.auxscreen.setupSecond()
        self.auxscreen.setFonts()
        self.auxscreen.setAdapterName(self.adapterName)
        
        ## third screen
        self.auxscreen2 = mainScreen(self.surface)
        self.auxscreen2.setupAux()
        self.auxscreen2.setFonts()
        self.auxscreen2.setAdapterName(self.adapterName) 

        if android:
           android.init()
           android.map_key(android.KEYCODE_BACK, pygame.K_ESCAPE)
           
           # DEMO controls if Bluetooth is enabled
#           if DEMO == True: 
#              return

           self.Bluetooth = Bluetooth()
           self.devices = self.Bluetooth.getDevices()       # get all devices we are paired with so we can choose one
           self.devicescreen.setDevices(self.devices)
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
            
                if self.displayscreen == 10:
                   self.devicescreen.drawDeviceScreen()
                
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
                
                if self.displayscreen == 10:
                   self.devicescreen.checkKeys(x,y, True)
                   k,v = self.devicescreen.getKeyValue()
                   self.devicescreen.updateName(k)
                   print k, v
                   if v == True and k == 2:
                      name = self.devicescreen.getBlueName()
                      print name
                      self.Bluetooth.prepare(name)
                      self.displayscreen = 0
                      
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
                   #print k,v
                   if v == True and k == 11:
                      self.displayscreen = 1
                      t = self.auxscreen2.getThrottle()
                      self.auxscreen.setThrottle(t)
                   elif v == True and k == 12:
                      self.displayscreen = 0       
                      t = self.auxscreen2.getThrottle()
                      self.mainscreen.setThrottle(t)

                elif self.displayscreen == 3:
                   self.configTwo.checkKeys(x,y, True)
                   k,v = self.configTwo.getKeyValue()
                   #if v == True: print k
                   if v == True and k == 11:
                      self.displayscreen = 2
                   elif v == True and k == 12:
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
                
                if self.displayscreen == 10:
                   self.devicescreen.checkKeys(x,y, False)
                   k,v = self.devicescreen.getKeyValue()

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













        
