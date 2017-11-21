try:
   import android
   from jnius import autoclass
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
        return paired_devices
        
    def prepare(self, name):
        self.deviceValid = False
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