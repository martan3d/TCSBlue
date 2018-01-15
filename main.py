import pygame
import math
from pygame import Color, Rect, Surface
from bt import Bluetooth

try:
   import android
except:
   android = None

TIMEREVENT = pygame.USEREVENT
COLORA = (255, 0, 0, 255)
COLORB = (0, 255, 0, 255)
WHITE = (255,255,255)
FPS = 30

MAINX = 480
MAINY = 854
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

SPBX = 166
SPBY = 73

KEYS = 13

##
## Screen - Knob with Function Keys  TCS WOW VERSION  ******************************************
##          

class mainScreen:
    def __init__(self, surface):
        self.surface = surface
        self.keys = []
        self.downkeys = []
        self.posThrottle = 649
        self.lastThrottle = 500
        self.adapterName = ""
        self.coupler0 = False
        self.coupler1 = False
        self.BlueDevices = None
        self.bluenames = ["no device"]
        self.nameindex = 0
        
        for i in range(0,25):
            self.downkeys.append(False)

    def setDevices(self, devices):
        self.BlueDevices = devices
        self.bluenames = []
        for d in devices:
            self.bluenames.append(d.getName())

    def getBlueName(self):
        try:
           name = self.bluenames[self.nameindex]
        except:
           name = "no device"
           self.bluenames.append(name)
        return name

    def setupDevice(self):
        self.screen0 = pygame.image.load('images/blank.png').convert()
        self.smb1    = pygame.image.load('images/sm-button0.png').convert()
        self.smb0    = pygame.image.load('images/sm-button1.png').convert()
        self.keydn   = pygame.image.load('images/sm-button-down.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()
        self.b9      = pygame.image.load('images/button-right.png').convert()
        self.b10     = pygame.image.load('images/button-left.png').convert()
        self.prg     = pygame.image.load('images/select.png').convert()
        self.prgdn   = pygame.image.load('images/select-down.png').convert()
        
        self.keys.append([ [20,  270], self.smb0, 0, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 3
        self.keys.append([ [400, 270], self.smb1, 1, False, [SBUTTONX, SBUTTONY], self.keydn ] )  # cfg 4
        self.keys.append([ [160, 370], self.prg,  2, False, [SPBX, SPBY],         self.prgdn ] )  # cfg prg

            
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
        #self.b7      = pygame.image.load('images/button7.png').convert()
        self.b8      = pygame.image.load('images/button8.png').convert()
        self.b9      = pygame.image.load('images/button-right.png').convert()
        self.keydown = pygame.image.load('images/button-blank.png').convert()

        self.keys.append([ [160, 600], self.b0, 100, False, [BUTTONX, BUTTONY], self.keydown ] )   # direction
        self.keys.append([ [315, 600], self.b5, 101, False, [BUTTONX, BUTTONY], self.keydown ] )   # stop

        self.keys.append([ [160, 450], self.b1, 0xf0, False, [BUTTONX, BUTTONY], self.keydown ] )  # Lights
        self.keys.append([ [315, 450], self.b2, 0xf1, False, [BUTTONX, BUTTONY], self.keydown ] )  # Bell

        self.keys.append([ [160, 300], self.b4, 0xf3, False, [BUTTONX, BUTTONY], self.keydown ] )  # Horn blue
        self.keys.append([ [315, 300], self.b8, 0xf7, False, [BUTTONX, BUTTONY], self.keydown ] )  # Brake

        self.keys.append([ [160, 150], self.b6, 0xf4, False, [BUTTONX, BUTTONY], self.keydown ] )  # horn green (quill?)
        self.keys.append([ [315, 150], self.b9, 7,  False, [BUTTONX, BUTTONY], self.keydown ] )  # next screen

        
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
        
        self.keys.append([ [160, 600], self.cfront, 200, False, [BUTTONX, BUTTONY], self.keydown ] )  # coupler
        self.keys.append([ [315, 600], self.cback,  201, False, [BUTTONX, BUTTONY], self.keydown ] )  # 

        self.keys.append([ [160, 450], self.fan1, 0xf3, False, [BUTTONX, BUTTONY], self.keydown ] )  # fan f3
        self.keys.append([ [315, 450], self.fan2, 0xf4, False, [BUTTONX, BUTTONY], self.keydown ] )  # fan f4

        self.keys.append([ [160, 300], self.mode, 0xf8, False, [BUTTONX, BUTTONY], self.keydown ] )   # mode
        self.keys.append([ [315, 300], self.radio,  16, False, [BUTTONX, BUTTONY], self.keydown ] )   # radio

        self.keys.append([ [160, 150], self.left,  6, False, [BUTTONX, BUTTONY], self.keydown ] )  # left
        self.keys.append([ [315, 150], self.right, 7, False, [BUTTONX, BUTTONY], self.keydown ] )  # right    
        
     
        
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

        self.keys.append([ [163, 614], self.cfg, 0xf8, False, [SMBCFGX, SMBTY],   self.cfgdn ] ) # f8
        self.keys.append([ [363, 614], self.b0,  0xf0, False, [SMBTX, SMBTY], self.smkeydown ] ) # f0

        self.keys.append([ [163, 509], self.b1, 0xf1, False, [SMBTX, SMBTY], self.smkeydown ] )  # f1
        self.keys.append([ [263, 509], self.b2, 0xf2, False, [SMBTX, SMBTY], self.smkeydown ] )  # f2
        self.keys.append([ [363, 509], self.b3, 0xf3, False, [SMBTX, SMBTY], self.smkeydown ] )  # f3

        self.keys.append([ [163, 405], self.b4, 0xf4, False, [SMBTX, SMBTY], self.smkeydown ] )  # f4
        self.keys.append([ [263, 405], self.b5, 0xf5, False, [SMBTX, SMBTY], self.smkeydown ] )  # f5
        self.keys.append([ [363, 405], self.b6, 0xf6, False, [SMBTX, SMBTY], self.smkeydown ] )  # f6

        self.keys.append([ [163, 300], self.b7, 0xf7, False, [SMBTX, SMBTY], self.smkeydown ] )  # f7
        self.keys.append([ [263, 300], self.b8, 0xf8, False, [SMBTX, SMBTY], self.smkeydown ] )  # f8
        self.keys.append([ [363, 300], self.b9, 0xf9, False, [SMBTX, SMBTY], self.smkeydown ] )  # f9

        self.keys.append([ [160, 150], self.left,  6, False, [SMBTX, SMBTY], self.keydown ] )  # left
        self.keys.append([ [315, 150], self.right, 7, False, [SMBTX, SMBTY], self.keydown ] )  # right    

       
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
        self.surface.blit(txt, (x, 40) )

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
        
    def setBlueNames(self, devices):
        for d in devices:
            self.bluenames.append(d.getName())
        print self.bluenames

    def getBlueName(self):
        try:
           name = self.bluenames[self.nameindex]
        except:
           name = "no device"
           self.bluenames.append(name)
        return name


    def updateName(self, key):
        if key == 1:
           self.nameindex = self.nameindex + 1
           if self.nameindex >= len(self.bluenames):
              self.nameindex = 0
        if key == 0:
           self.nameindex = self.nameindex - 1
           if self.nameindex < 0:
              self.nameindex = len(self.bluenames) - 1

        
    def drawConfigItem(self, p, text):
        txt = self.statfont.render(text, True, (255, 255, 255), (0,64,0) )
        self.surface.blit(txt, (100, p*60+280) )
       
    def updateKnob(self, x, y):
        # reject inputs totally out of bounds
        if x < 20:
           return
        if x > 140:
           return
        if y > self.posThrottle + 200:
           return
        if y < self.posThrottle - 200:
           return
        self.posThrottle = y
#        print "throttle y", y
        
    def getThrottle(self):
        return self.posThrottle
        
    def setThrottle(self, t):
        self.posThrottle = t

    def drawKnob(self):
        if self.posThrottle > 649:
           self.posThrottle = 649

        if self.posThrottle < 137:
           self.posThrottle = 137

        self.surface.blit(self.knob, [13, self.posThrottle-10])

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
               return self.keys[i][2], True
            i = i + 1
        return 0, False

    def setKnob(self, x, y):
        t = self.posThrottle
        a = (630-t)/5
        if a < 0:
           a = 0
        return a

    def setServos(self):
        # 00 - command code = 10
        tstr = chr(10)
        # 01 - throttle - Servo 0
        t = self.posThrottle
        a = abs( (620-t)/5 )
        tstr = tstr + chr(a)
        # 02 - Servo 1
        u = self.posKnob1
        b = abs( (620-u)/2 )
        tstr = tstr + chr(b)
        # 03 - Servo 2
        v = self.posKnob2
        c = abs( (620-v)/2 )
        tstr = tstr + chr(c)

        for i in range(4,16):
            tstr = tstr + chr(0)
        return tstr 

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
        self.saveString = "0123456789012345"
        self.sendString = ""
        self.adapterName = ""
        self.displayscreen = 10
        self.mousedown = False
        self.devices = None
        self.direction = 0
        self.updateServo1 = False
        self.updateServo0 = False
        self.updateThrottle = False
        self.servoCounter1 = 0
        self.servoCounter0 = 0
        self.servoIncrement1 = 1
        self.servoIncrement0 = 1
        self.servoMax1 = 100
        self.servoMin1 = 0
        self.servoMax0 = 100
        self.servoMin0 = 0
        self.watchdog = 0
        self.maxx = 0
        self.maxy = 0        

 
    def setup(self):
        pygame.init()
        pygame.time.set_timer(TIMEREVENT, 1000 / FPS)
        
#        infoObject = pygame.display.Info()
        # fill all screen area with background color
#        self.surface  = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
#        self.surface.fill( (0,0,0))
        
#        print infoObject.current_w, infoObject.current_h
#        self.maxx = infoObject.current_w
#        self.maxy = infoObject.current_h
        
        # resize to our bitmap resolution
#        self.surface  = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))
        self.surface  = pygame.display.set_mode((MAINX, MAINY))
        self.surface.fill( (0,0,0))
        
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
           self.Bluetooth = Bluetooth()
           self.devices = self.Bluetooth.getDevices()
           self.devicescreen.setBlueNames(self.devices) 
       
##
## Read and Write BT data to/from phone
##
            
    def writeBluetooth(self):
        if android:
           self.Bluetooth.write(self.transmitString)

    def readBluetooth(self):
        if android:
           t = self.Bluetooth.read()
           if t != "":
              self.receiveString = t

    def setOutputs(self, k):
        self.transmitString = self.mainscreen.setOutputs(k)
        self.writeBluetooth()

    def setEstop(self):
        self.transmitString = chr(18) + chr(0) + '              '
        self.writeBluetooth()
        
    def setDCCThrottle(self, s):
        self.transmitString = chr(13) + chr(s) + '              '
        self.writeBluetooth()
        print "throttle actual", s
        
    def setDCCFunc(self, f):
        self.transmitString = chr(14) + chr(f) + '              '
        self.writeBluetooth()

    def setExtendedDCCFunc(self, f):
        self.transmitString = chr(15) + chr(f) + '              '
        self.writeBluetooth()

    def updateServoCoupler0(self, f):
        self.transmitString = chr(19) + chr(f) + '              '
        self.writeBluetooth()

    def updateServoCoupler1(self, f):
        self.transmitString = chr(20) + chr(f) + '              '
        self.writeBluetooth()
        
    def setServoThrottle(self, s):
        self.transmitString = chr(21) + chr(s) + '              '
        self.writeBluetooth()

    def setCV(self, a, d):
        h = ( a & 0xff00 ) >> 8
        l = ( a & 0x00ff )
        self.transmitString = chr(16) + chr(l) + chr(h) + chr(d) + '            '
        self.writeBluetooth()
        
    def setServos(self):
        self.transmitString = self.mainscreen.setServos()
        self.writeBluetooth()  

    def setKnob(self, x, y):
        self.transmitString = self.mainscreen.setKnob( x, y )
        self.writeBluetooth()  
           
    def setDirection(self):
        if self.direction == 1:
           self.direction = 0
        else:
           self.direction = 1
        self.transmitString = chr(17) + chr(self.direction) + '              '
        self.writeBluetooth()
        
    def resetWatchDog(self):
        s = 0
        self.transmitString = chr(23) + chr(s) + '              '
        self.writeBluetooth()

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
                   
            ##########################################################################################                   
            #
            # Update things based on the FPS timer
            
            if ev.type == TIMEREVENT:
                if self.displayscreen == 10:
                   self.devicescreen.drawDeviceScreen()
                if self.displayscreen == 0:
                   self.mainscreen.drawScreen()
                elif self.displayscreen == 1:
                   self.auxscreen.drawScreen()
                elif self.displayscreen == 2:
                   self.auxscreen2.drawScreen()
                elif self.displayscreen == 3:
                   self.configTwo.drawScreenTwo()

                # be sure bytes are not backing up in the BT interface
                
                self.readBluetooth()
   
                # update the throttle if needed

                if self.updateThrottle == True:
                   if self.displayscreen == 0:
                      self.mainscreen.updateKnob(x,y)
                      a = self.mainscreen.setKnob(x, v)
                   elif self.displayscreen == 1:
                      self.auxscreen.updateKnob(x,y)
                      a = self.auxscreen.setKnob(x, v)
                   elif self.displayscreen == 2:
                      self.auxscreen2.updateKnob(x,y)
                      a = self.auxscreen2.setKnob(x, v)
                   self.setDCCThrottle(a)
                # Coupler Servos
                   
                elif self.updateServo1 == True:
                   self.servoCounter1 = self.servoCounter1 + self.servoIncrement1
                   if self.servoCounter1 > self.servoMax1:
                      self.servoCounter1 = self.servoMax1
                      self.updateServo1 = False
                      self.servoIncrement1 = -2
                   if self.servoCounter1 <= self.servoMin1:
                      self.updateServo1 = False
                      self.servoIncrement1 = 2
                   self.updateServoCoupler1(self.servoCounter1)
                   
                elif self.updateServo0 == True:
                   self.servoCounter0 = self.servoCounter0 + self.servoIncrement0 
                   if self.servoCounter0 > self.servoMax0:
                      self.servoCounter0 = self.servoMax0
                      self.updateServo0 = False
                      self.servoIncrement0 = -2
                   if self.servoCounter0 <= self.servoMin0:
                      self.updateServo0 = False
                      self.servoIncrement0 = 2                      
                   self.updateServoCoupler0(self.servoCounter0)
                   
                else:
                   self.watchdog = self.watchdog + 1
                   if self.watchdog > 30:
                      self.watchdog = 0
                      self.resetWatchDog()

            ###########################################################################################################
            #
            # process any user input
            
            elif ev.type == pygame.MOUSEBUTTONDOWN and self.mousedown == False:
                self.mousedown = True
                x, y = pygame.mouse.get_pos()
                
                if self.displayscreen == 10:                   ## Bluetooth select screen
                   self.devicescreen.checkKeys(x,y, True)
                   k,v = self.devicescreen.getKeyValue()
                   self.devicescreen.updateName(k)

                   if v == True and k == 2:
                      name = self.devicescreen.getBlueName()
                      self.mainscreen.setAdapterName(name)
                      self.auxscreen.setAdapterName(name)
                      self.auxscreen2.setAdapterName(name)
                      try:
                         self.BTValid = self.Bluetooth.prepare(name)
                         self.setDCCThrottle(0)
                      except:
                         pass
                      self.displayscreen = 0
                   elif v == True:
                      self.devicescreen.updateName(k)
                      
            ###########################################################################################################
     
                # Main display - read button presses, build transmit string     
                if self.displayscreen == 0:
                   self.mainscreen.checkKeys(x,y, True)
                   k,v = self.mainscreen.getKeyValue()

                   if v == True and k == 7:                     ## screen change keys, no need to send data for these
                      t = self.mainscreen.getThrottle()         ## just move to next screen state
                      self.auxscreen.setThrottle(t)             ## keep both screen throttles in sync
                      self.displayscreen = 1
                   elif v == True:
                      if k > 239:
                         self.setDCCFunc(k)      # Function codes from screen 0
                      elif k == 100:
                         self.setDirection()
                      elif k == 101:
                         self.setEstop()

            ###########################################################################################################
                 
                # Second Screen, harvest input, build string for transmit
                elif self.displayscreen == 1:
                   self.auxscreen.checkKeys(x,y, True)
                   k,v = self.auxscreen.getKeyValue()

                   # screen navigation first, check these
                   if v == True and k == 6:
                      t = self.auxscreen.getThrottle()
                      self.mainscreen.setThrottle(t)
                      self.displayscreen = 0
                      
                   if v == True and k == 7:
                      self.displayscreen = 2
                      t = self.auxscreen.getThrottle()
                      self.auxscreen2.setThrottle(t)
                   if v == True:
                      if k > 239:
                         self.setDCCFunc(k)
                      elif k == 200:
                         self.updateServo0 = True
                      elif k == 201:
                         self.updateServo1 = True
                      elif k == 16:
                         self.setExtendedDCCFunc(k)
                      
            ###########################################################################################################
                            
                ## TCS screen 2
                elif self.displayscreen == 2:
                   self.auxscreen2.checkKeys(x,y, True)
                   k,v = self.auxscreen2.getKeyValue()
 
                   if v == True and k == 6:
                      self.displayscreen = 1
                      t = self.auxscreen2.getThrottle()
                      self.auxscreen.setThrottle(t)
                      
                   elif v == True and k == 7:
                      self.displayscreen = 0       
                      t = self.auxscreen2.getThrottle()
                      self.mainscreen.setThrottle(t)

                   elif v == True:
                      if k > 239:
                         self.setDCCFunc(k)
                      
            ###########################################################################################################
                     
            # Check mouse motion for knob
            elif ev.type == pygame.MOUSEMOTION and self.mousedown == True:
               if self.mousedown:
                   x, y = pygame.mouse.get_pos()
                   if self.displayscreen == 0:
                      self.mainscreen.updateKnob(x,y)
                      self.updateThrottle = True
                    
                   elif self.displayscreen == 1:
                      self.auxscreen.updateKnob(x,y)
                      self.updateThrottle = True

                   elif self.displayscreen == 2:
                      self.auxscreen2.updateKnob(x,y)
                      self.updateThrottle = True
                
            # Mouse up event, check keys
            elif ev.type == pygame.MOUSEBUTTONUP and self.mousedown == True:
                self.mousedown = False
                self.updateThrottle = False
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
#                self.setDCCThrottle(0)
                if android:
                   self.Bluetooth.close()
                break

mainApp = mainLoop()
mainApp.setup()
mainApp.runLoop()













        
