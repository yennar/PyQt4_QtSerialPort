#!/usr/bin/env python

import sys
sys.path.append('../')

from QtSerialPort import *

try:
    user_defined_name = sys.argv[1]
except:
    user_defined_name = None

if user_defined_name is None:
    print "Usage ",sys.argv[0],"<portname>"
    print "<portname> in"

    for p in QSerialPortInfo.availablePorts():
        print p.portName()
    exit()
    
p = QSerialPort(user_defined_name)
if p.open(QSerialPort.ReadWrite):
    p.write("Hello Serial")
