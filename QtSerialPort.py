#-- package PyQt4.QtSerialPort
#-- Author yennar@github.com

'''

Depends on PyQt4,pyserial and serves for PyQt4 
PyQt5 users should use PyQt5.QtSerialPort delivered by Riverbank

Nearly full compatible with the latest QtSerialPort (git://gitorious.org/qt/qtserialport.git) and keep up-to-date
Ref to PyQt5 document https://qt-project.org/doc/qt-5/qtserialport-index.html

- Not and will not be implemented:

* QSerialPort.flowControl
* QSerialPort.setFlowControl
* All virtual method (You won't subclass QSerialPort)

- Not be implemented yet

* QSerialPort.settingsRestoredOnClose
* QSerialPort.setSettingsRestoredOnClose

'''

from PyQt4.QtCore import *
import serial
from serial.tools import list_ports

import sys

class QSerialPortInfo(QObject):
    
    @staticmethod
    def availablePorts():
        ps = []
        for p in list_ports.comports():
            pi = QSerialPortInfo(p[0])
            ps.append(pi)
        return ps
            
    @staticmethod
    def standardBaudRates():
        return [1200,2400,4800,9600,19200,38400,57600,115200]
    
    def __init__(self,pname = None):
        QObject.__init__(self)
        self._name = pname;
                
    def description(self):
        for p in list_ports.comports():
            if self._name == p[0] and not p[1] is None:
                return p[1]
        return ''
        
    def hasProductIdentifier(self):
        return False

    def hasVendorIdentifier(self):
        return False 
        
    def isBusy(self):
        pass
        
    def isNull(self):
        pass
        
    def manufacturer(self):
        pass
        
    def portName(self):
        return self._name
     
    def productIdentifier(self):
        return 0
        
    def systemLocation(self):
        for p in list_ports.comports():
            if self._name == p[0] and not p[2] is None:
                return p[2]
        return ''
    
    def vendorIdentifier(self):
        return 0
        
        
class QSerialPort(QIODevice):

    Baud1200 = 1200
    Baud2400 = 2400
    Baud4800 = 4800
    Baud9600 = 9600
    Baud19200 = 19200
    Baud38400 = 38400
    Baud57600 = 57600
    Baud115200 = 115200
    UnknownBaud = -1
    
    Data5 = 5 
    Data6 = 6 
    Data7 = 7 
    Data8 = 8 
    
    _DataBits = [0,0,0,0,0,serial.FIVEBITS,serial.SIXBITS,serial.SEVENBITS,serial.EIGHTBITS]
       
    Input = 1
    Output = 2
    AllDirections = 3
    
    NoFlowControl = 0
    HardwareControl = 1
    SoftwareControl = 2
    
    NoParity = 0
    EvenParity = 2
    OddParity = 3
    SpaceParity = 4
    MarkParity = 5
    
    _Parity = [serial.PARITY_NONE,0,serial.PARITY_EVEN,serial.PARITY_ODD,serial.PARITY_SPACE,serial.PARITY_MARK]
    
    NoSignal = 0x00
    TransmittedDataSignal = 0x01
    ReceivedDataSignal = 0x02
    DataTerminalReadySignal = 0x04
    DataCarrierDetectSignal = 0x08
    DataSetReadySignal = 0x10
    RingIndicatorSignal = 0x20
    RequestToSendSignal = 0x40
    ClearToSendSignal = 0x80
    SecondaryTransmittedDataSignal = 0x100
    SecondaryReceivedDataSignal = 0x200
    
    NoError = 0
    DeviceNotFoundError = 1
    PermissionError = 2
    OpenError = 3
    NotOpenError = 13
    ParityError = 4
    FramingError = 5
    BreakConditionError = 6
    WriteError = 7
    ReadError = 8
    ResourceError = 9
    UnsupportedOperationError = 10
    TimeoutError = 12
    UnknownError = 13
    
    OneStop = 1
    OneAndHalfStop = 3
    TwoStop = 2
    
    _StopBits = [0,serial.STOPBITS_ONE,serial.STOPBITS_TWO,serial.STOPBITS_ONE_POINT_FIVE]
    
    def __init__(self,p1 = None,p2 = None):
        
        if p2 is None:
            parent = None
            if p1 is None:                
                self._port = None
            elif type(p1).__name__ == 'str':
                self._port = p1               
            elif type(p1).__name__ == 'QSerialPortInfo':
                self._port = p1.portName()
            else:
                parent = p1
                self._port = None                                             
        else:
            parent = p2
            if p1 is None:                
                self._port = None
            elif type(p1).__name__ == 'QSerialPortInfo':
                self._port = p1.portName()
            else:
                self._port = p1              
        
        QIODevice.__init__(self)

        self._isopen = False
        self._baudRate = [0,0,0,9600]
        

            
        self._bytesize = self._DataBits[self.Data8]
        self._parity = self._Parity[self.NoParity]
        self._stopbits = self._StopBits[self.OneStop]
        self._error = self.NoError
        self._rtscts = False
        self._xonxoff = False
        self._dataTerminalReady = False
        self._requestToSend = False
        self._bufwrite = 0
        
        self.serial = serial.Serial()
        
    def _tryReOpen(self,s=''):
        self.serial.close()
        self._isopen = False
        
        self.serial.baudRate = self._baudRate[self.AllDirections]
        self.serial.port = self._port
        self.serial.bytesize = self._bytesize
        self.serial.parity = self._parity
        self.serial.stopbits = self._stopbits
        self.serial.rtscts = self._rtscts
        self.serial.xonxoff = self._xonxoff        
        
        try:
            self.serial.open()
        except ValueError:
            self._error = self.UnsupportedOperationError
            sys.stderr.write("[QSerialPort] configuration error in {} \n".format(s))
            return False            
        except SerialException:
            self._error = self.OpenError
            sys.stderr.write("[QSerialPort] open error in {} , device unavailable \n".format(s))
            return False
        
        self._isopen = True
        return True
            
    baudRateChanged = pyqtSignal(int, int)
        
    def baudRate(self,directions = 3):
        if not directions  == self.AllDirections:
            sys.stderr.write("[QSerialPort] baudRate with direction other than AllDirections is not supported\n")
            directions  = self.AllDirections
        return self._baudRate[directions]
        
    def setBaudRate(self,baudRate,directions = 3):
        if not self._isopen:
            self._error = NotOpenError
            return False
        if not directions  == self.AllDirections:
            sys.stderr.write("[QSerialPort] baudRate with direction other than AllDirections is not supported\n")
            directions  = self.AllDirections        
        old_baudRate = self._baudRate[self.AllDirections]
        self._baudRate[self.AllDirections] = baudRate
        if not self._tryReOpen('setBaudRate({})'.format(baudRate)):
            self._baudRate[self.AllDirections] = old_baudRate
            self._tryReOpen()
        else:
            self.baudRateChanged.emit(baudRate,directions)
            
            
    dataBitsChanged = pyqtSignal(int)
    
    def dataBits(self):
        return self._bytesize
        
    def setDataBits(self,dataBits):
        if not self._isopen:
            self._error = NotOpenError
            return False
            
        old_dataBits = self._bytesize
        self._bytesize = self._DataBits[dataBits]
        if not self._tryReOpen('setDataBits({})'.format(dataBits)):
            self._bytesize = old_dataBits
            self._tryReOpen()
        else:
            self.dataBitsChanged.emit(dataBits)               
        
    dataTerminalReadyChanged =  pyqtSignal(bool)
    
    def isDataTerminalReady(self):
        return self._dataTerminalReady
        
    def setDataTerminalReady(_set):
        if not self._isopen:
            self._error = NotOpenError
            return False          
        
        try:
            self.serial.setDTR(_set)
        except:
            return False
        self._dataTerminalReady = _set
        self.dataTerminalReadyChanged.emit(_set)
        return True
        
    def error(self,error = None):
        if not error is None:
            self._error = error
        
        return self._error
        
    def clearError(self):
        self._error = self.NoError
        
    flowControlChanged = pyqtSignal(int)
                    
    def flowControl(self):
        sys.stderr.write("[QSerialPort] flowControl : No implemented\n")

    def setFlowControl(self,flow):
        sys.stderr.write("[QSerialPort] setFlowControl : No implemented\n")
        
    parityChanged = pyqtSignal(int)
    
    def parity(self):
        return self._parity
        
    def setParity(self,parity):
        if not self._isopen:
            self._error = NotOpenError
            return False
        old_parity = self._parity
        self._parity = self._Parity[parity]
        if not self._tryReOpen('setParity({})'.format(parity)):
            self._parity = old_parity
            self._tryReOpen()
        else:
            self.parityChanged.emit(parity)
            
    requestToSendChanged = pyqtSignal(bool)
               
    def isRequestToSend(self):
        return self._requestToSend
        
    def setRequestToSend(self,_set):
        if not self._isopen:
            self._error = NotOpenError
            return False
        
        try:
            self.serial.setRTS(_set)
        except:
            return False
        self._requestToSend = _set
        self.requestToSendChanged.emit(_set)
        return True
        
    settingsRestoredOnClose  = pyqtSignal(bool)
                    
    def settingsRestoredOnClose(self):
        sys.stderr.write("[QSerialPort] settingsRestoredOnClose : No implemented\n")

    def setSettingsRestoredOnClose(self,restore):
        sys.stderr.write("[QSerialPort] setSettingsRestoredOnClose : No implemented\n")        
        
    stopBitsChanged = pyqtSignal(int)
    
    def stopBits(self):
        return self._stopbits
        
    def setStopBits(self,stopBits):
        if not self._isopen:
            self._error = NotOpenError
            return False
        old_stopBits = self._stopbits
        self._stopbits = self._StopBits[stopBits]
        if not self._tryReOpen('setStopBits({})'.format(stopBits)):
            self._stopbits = old_stopBits
            self._tryReOpen()
        else:
            self.stopBitsChanged.emit(stopBits)
            
    def atEnd(self):
        if not self._isopen:
            self._error = NotOpenError
            return True
        
        return not self.serial.readable()
    
    def bytesAvailable(self):
        if not self._isopen:
            self._error = NotOpenError
            return 0
        
        return self.serial.bytesAvailable()
        
    def bytesToWrite(self):
        if not self._isopen:
            self._error = NotOpenError
            return 0        
        return self.serial.outWaiting()
        
    def canReadLine(self):
        sys.stderr.write("[QSerialPort] canReadLine : No implemented\n")
    
    def clear(self,directions):
        if not self._isopen:
            self._error = NotOpenError
            return 0  
            
        self.serial.flushInput() 
        self.serial.flushOutput()
        
    def close(self):
        if not self._isopen:
            self._error = NotOpenError
            return 0  
        
        self.serial.close()
        self.serial._isopen = False
        
    def flush(self):
        if not self._isopen:
            self._error = NotOpenError
            return 0 
        self.serial.flush()
        
    def handle(self):
        if not self._isopen:
            self._error = NotOpenError
            return 0 
        return -1
        
    def isSequential(self):
        return True
        
    def open(self,mode):
        return self._tryReOpen()
    
    def isOpen(self):    
        return self._isopen
        
    def pinoutSignals(self):
        if not self._isopen:
            self._error = NotOpenError
            return 0        
        r = self.NoSignal
        if self._dataTerminalReady:
            r = r | self.DataTerminalReadySignal
        if self.serial.getCD():
            r = r | self.DataCarrierDetectSignal
        if self.serial.getDSR():
            r = r | self.DataSetReadySignal
        if self.serial.getRI():
            r = r | self.RingIndicatorSignal
        if self._requestToSend:
            r = r | self.RequestToSendSignal    
        if self.serial.getCTS():
            r = r | self.ClearToSendSignal
        
        return r
    
    def portName(self):
        return self._port
    
    def readBufferSize(self):
        return 0
        
    def sendBreak(self,duration):
        if not self._isopen:
            self._error = NotOpenError
            return 0
            
        self.serial.sendBreak(duration)
    
    def setBreakEnabled(self,_set):
        if not self._isopen:
            self._error = NotOpenError
            return False
            
        self.serial.setBreak(_set)
    
    def setPort(self,serialPortInfo):
        self._port = serialPortInfo.portName()
        
    def setPortName(self,name):
        self._port = str(name)
        
    def setReadBufferSize(self,size):
        pass
        
    def read(self,size = 1):
        if not self._isopen:
            self._error = NotOpenError
            return False
            
        return self.serial.read(size)
        
    def write(self,d):
        if not self._isopen:
            self._error = NotOpenError
            return False
            
        return self.serial.write(d)                                                                             