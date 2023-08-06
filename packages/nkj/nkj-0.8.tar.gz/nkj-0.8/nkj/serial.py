#
# [name] nkj.serial.py
# [purpose] nkj.serial library
#
# Written by Yoshikazu NAKAJIMA (Wed Sep 23 14:38:26 JST 2020)
#

_DEBUGLEVEL = 0

CRLF = '\r\n'
CR = '\r'
LF = '\n'
EOB = '\0'

NONE = -1
DEFAULT_BAUDRATE = 9600
DEFAULT_TIMEOUT = 2.0
DEFAULT_SLEEPTIME = 0.1
DEFAULT_EOL = CRLF

import os
import sys
import serial
import time
from serial.tools import list_ports

sys.path.append(os.path.abspath(".."))
import nkj.str as ns
from nkj.str import *

if (ns.LIB_DEBUGLEVEL > 0):
	DEBUG = True
else:
	DEBUG = False

if (ns.LIB_DEBUGLEVEL > 1):
	DEBUG2 = True
else:
	DEBUG2 = False

class nkjserial:
	#-- Class variables
	_classname = "nkjserial"
	_comports = 0
	_comportlist = []
	_comport_prefix = None

	_baudrate = DEFAULT_BAUDRATE
	_timeout = DEFAULT_TIMEOUT
	_eol = DEFAULT_EOL

	_at_once = True
	#--

	def __init__(self, port=None, baudrate=-1, timeout=-1):
		ldprint(["--> nkjserial.__init__(", str_bracket(port), ")"])

		nkjserial._comports += 1

		#-- Instance variables
		self.portstr = None
		self._isopened = False

		self._timeout = nkjserial._timeout
		self._baudrate = nkjserial._baudrate

		self._eol = nkjserial._eol
		#--

		ldprint(["_at_cone: ", str(nkjserial._at_once)])

		if (nkjserial._at_once):
			nkjserial._at_once = False
			nkjserial._comportlist = nkjserial.getPortList()
			if (DEBUG):
				print("-- port list [", len(nkjserial._comportlist), "] --")
				for port in nkjserial._comportlist:
					print(port)
				print("--")

			nkjserial.getPortPrefix()

		if (ns.is_none(port)):
			return
		else:
			ldprint(["Port: ", str_bracket(port)])
			self.portstr = port

		status = self.open(port, baudrate, timeout)

		if (status):
			ldprint(["Serial opening is succeeded."])
		else:
			ldprint(["Serial opening is failed."])

		ldprint(["<-- nkjserial.__init__()"])

	def __del__(self):
		nkjserial._comports -= 1

		status = self.close()

		if (status):
			ldprint(["Serial closing is succeeded."])
		else:
			ldprint(["Serial closing is failed."])

	def __str__(self, title=None):
		mesg = None

		if (ns.is_none(title)):
			if (ns.is_none(self.portstr)):
				mesg = ns.concat(["--- ", "NONE", " ---", "\n"])
			else:
				mesg = ns.concat(["--- ", self.portstr, " ---", "\n"])
		else:
			mesg = ns.concat(["--- ", title, " ---", "\n"])
			if (ns.is_none(self.portstr)):
				mesg += "Com: NONE\n"
			else:
				mesg += ns.concat(["Com: ", self.portstr, "\n"])

		mesg += "Opened:   " + str(self.isOpened()) + "\n"
		mesg += "Baudrate: " + str(self.getBaudrate()) + "\n"
		mesg += "Timeout:  " + str(self.getTimeout()) + "\n"
		mesg += "Total ports: " + str(self.getPorts()) + "\n"
		mesg += "---"
		return mesg

	def _setPortNo(self, portno):
		self.portstr = nkjserial._comport_prefix + str(portno)

	def _sleep(self, sleeptime=DEFAULT_SLEEPTIME):
		time.sleep(sleeptime)

	def isOpened(self):
		return self._isopened

	@classmethod
	def getClassName(cls):
		return nkjserial._classname

	@classmethod
	def getClassBaudrate(cls):
		return nkjserial._baudrate

	def getBaudrate(self):
		return self._baudrate

	@classmethod
	def getClassTimeout(cls):
		return nkjserial._timeout

	def getTimeout(self):
		return self._timeout

	@classmethod
	def getClassEOL(cls):
		return nkjserial._eol

	def getEOL(self):
		return self._eol

	@classmethod
	def getClassTerminator(cls):
		return nkjserial.getClassEOL()

	def getTerminator(self):
		return self.getEOL()

	@classmethod
	def getPorts(cls):
		return nkjserial._comports

	def getPort(self):
		return self.portstr

	@classmethod
	def getPortList(cls, baudrate=-1, timeout=-1):
		ldprint(["--> nkjserial.getPortList()"])

		if (baudrate > 0):
			nkjserial._baudrate = baudrate

		if (timeout > 0):
			nkjserial._timeout = timeout

		if (len(nkjserial._comportlist) == 0):
			for comport in list_ports.comports():
				ldprint2(["Sys comport:        ", str(comport)])

				device = comport.device
				ldprint2(["Sys comport device: ", device])

				try:
					ser = serial.Serial(device, baudrate=nkjserial._baudrate, timeout=nkjserial._timeout)
					ldprint(["Opened comport device: ", str_bracket(device)])
					nkjserial._comportlist.append(device)
					ser.close()
				except:
					pass

		ldprint(["<-- nkjserial.getPortList()"])
		return nkjserial._comportlist

	@classmethod
	def getPortPrefix(cls):
		if (ns.is_none(nkjserial._comport_prefix)):
			comportlist = nkjserial.getPortList()

			if (len(comportlist) == 0):
				return None

			comport_str = comportlist[0]

			comport_prefix = None

			for i in range(len(comport_str)):
				charstr = comport_str[i]
				if (charstr.isdigit()):
					break
				else:
				 	comport_prefix = ns.concat([comport_prefix, charstr])

			ldprint(["comport_prefix: ", str_bracket(comport_prefix)])

			nkjserial._comport_prefix = comport_prefix

		return nkjserial._comport_prefix

	@classmethod
	def setClassBaudrate(cls, baudrate):
		nkjserial._baudrate = baudrate

	def setBaudrate(self, baudrate):
		self._baudrate = baudrate

	@classmethod
	def setClassTimeout(cls, timeout):
		nkjserial._timeout = timeout

	def setTimeout(self, timeout):
		self._timeout = timeout

	@classmethod
	def setClassEOL(cls, eol):
		nkjserial._eol = eol

	def setEOL(self, eol):
		self._eol = eol

	@classmethod
	def setClassTerminator(cls, terminator):
		nkjserial.setClassEOL(terminator)

	def setTerminator(self, terminator):
		self.setEOL(terminator)

	def setPort(self, port):
		self.portstr = port

	def open(self, port=None, baudrate=-1, timeout=-1):
		ldprint(["--> nkjserial.open(", str_bracket(port), ")"])

		if (self._isopened == True):
			ldprint(["ERROR: Com port has been opened."])
			return False

		if (ns.is_none(port)):
			port = self.portstr

		if (baudrate > 0):
			self._baudrate = baudrate

		if (timeout > 0):
			self._timeout = timeout

		try:
			self.ser = serial.Serial(port, baudrate=self._baudrate, timeout=self._timeout)
		except:
			return False

		self.portstr = port

		self._isopened = True

		self._sleep()

		ldprint(["<-- nkjserial.open()"])
		return True

	def connect(self, port=None, baudrate=-1, timeout=-1):
			return self.open(port, baudrate, timeout)

	def close(self):
		if (self._isopened == False):
			return False

		self.ser.close()
		return True

	def diconnect(self):
		return self.close()

	def clear(self):
		self.ser.reset_input_buffer()	# Flush input bffer, discarding all its contents. The old name is 'flushInput().'
		self.ser.reset_output_buffer()	# Clear output buffer, aborting the current output and discarding all that is in the buffer. The old name is 'flushOutput().'

	def flush(self):
		self.ser.flush()		# Flush of file like objects. In this case, wait until all data is written.

	def send(self, command):
		ldprint(["--> nkjserial.send(", str_bracket(command), ")"])

		if (self._isopened == False):
			ldprint(["ERROR: Serial port is not opened."])
			return False

		if (ns.is_none(command)):
			ldprint(["ERROR: Null command"])
			return False

		if (command == "\0"):
			ldprint(["ERROR: Null command"])
			return False

		if (len(command) < 1):
			ldprint(["ERROR: Command string is too short."])
			return False

		serstr = command + self.getEOL()

		ldprint(["Sent string:", str_bracket(serstr)])

		self.clear()

		self.ser.write(serstr.encode())

		self.flush()
		self._sleep()

		ldprint(["<-- nkjserial.send()"])
		return True

	def receive(self, chars=-1):
		ldprint(["--> nkjserial.receive(", str(chars), ")"])

		if (self._isopened == False):
			ldprint(["ERROR: Serial port is not opened."])
			return None

		if (chars < 0):
			#retstr = self.ser.read()
			retstr = self.ser.read_until(self.getEOL())
		else:
			retstr = self.ser.read(chars)

		self._sleep()

		msg = retstr.decode()

		ldprint(["Received message: ", str_bracket(msg)])

		msg = msg.strip(self.getEOL())

		ldprint(["Returning message: ", str_bracket(msg)])

		ldprint(["<-- nkjserial.receive()"])
		return msg

	def receiveline(self):
		ldprint(["--> nkjserial.receiveline()"])

		if (self._isopened == False):
			ldprint(["ERROR: Serial port is not opened."])
			return None

		retstr = self.ser.readline()

		self._sleep()

		msg = retstr.decode()

		ldprint(["Status: ", str_bracket(msg)])

		msg = msg.strip(self.getEOL())

		ldprint(["Returning message: ", str_bracket(msg)])

		ldprint(["<-- nkjserial.receiveline()"])
		return msg

#-- main

if __name__ == "__main__":
	ns.LIB_DEBUGLEVEL = _DEBUGLEVEL

	print("comport_prefix: ", str_bracket(nkjserial.getPortPrefix()))

	portlist = nkjserial.getPortList()

	print("-- port list [", len(portlist), "] --")
	for port in portlist:
		print(port)
	print("--")

	nkjserial.setClassEOL(CRLF)

	eol = nkjserial.getClassEOL()

	print("EOL: ", end=None)
	if (eol == '\r\n'):
		print("CRLF")
	elif (eol == '\r'):
		print("LF")
	elif (eol == '\n'):
		print("CR")
	else:
		print("unknown")

	ser = nkjserial("/dev/ttyS0")
	ser2 = nkjserial("/dev/ttyS1")

	print("Class name:", ser.getClassName())
	print("Ports:", ser.getPorts())
	print("Instance com port:", ser.getPort())
	print("Instance com port:", ser2.getPort())
	print("Is the instance opened:", ser.isOpened())
	print("Is the instance opened:", ser2.isOpened())

	print(ser)
	print(ser2)
