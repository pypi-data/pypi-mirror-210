import socket
import unittest
import time
import logging
import os
import re

class ElpaSine:
    def __init__(self, addr):
        self.TIMEOUT = 10
        self.BUFFER_SIZE = 4096
        self.connection = None
        self.addr = addr
        self.numeric = re.compile("(\+|-)([0-9\.]+)")
        self.measurementType = "RMS"
        self.measurementTypeList = ["PEAK", "RMS"]
        self.maxCurrentLimit = 8.0
        self.isOpen = False
        self.commandDelay = 0.05 # It errors on back to back comms, delay needed.
        self.lastResult = None

    def openConnection (self, connectionString = None):
        #print("DEBUG: openConnection")
        if (connectionString is not None):
            self.conString = connectionString
        else:
            self.conString = self.addr
        self.connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.connection.settimeout(self.TIMEOUT)
        self.connection.connect((self.conString,4001))
        self.isOpen = True

        # ELPA-SINE ignores first command, so send a dummy command to wake it up
        self.sendCommandQuery("MEAS:TYPE "+self.measurementType, response=False)


    def closeConnection (self):
        #print("DEBUG: closeConnection")
        self.connection.close()
        self.isOpen = False

    def sendCommandQuery (self, commandString, response=True):
        if not self.isOpen:
            self.openConnection()
        retries = 1
        while retries < 2:
            try:
                time.sleep(self.commandDelay)
                # Send the command
                startTime= int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": sending command: " + commandString)
                self.connection.send((commandString + "\r\n").encode('latin-1'))

                if not response: return
                # Read back the response data
                self.connection.settimeout(self.TIMEOUT)
                resultStr = self.connection.recv(self.BUFFER_SIZE).decode("utf-8")
                self.lastResult = resultStr
                endTime = int(round(time.time() * 1000))
                logging.debug(os.path.basename(__file__) + ": received: " + resultStr)
                logging.debug(os.path.basename(__file__) + ": Time Taken : " + str(endTime-startTime) + " mS")
                resultStr = resultStr.strip ('\r\n\t')
                # If no response came back
                if (resultStr is None or resultStr == ""):
                    logging.error("resultStr = "+ resultStr)
                    raise ValueError ("The ELPA-SINE did not return a response")
                return resultStr
            except socket.timeout:
                logging.debug(os.path.basename(__file__) + ": ELPA-SINE command timed out: " + commandString + ", closing connection and retrying")
                # reset connections on ELPA-SINE
                if self.isOpen:
                    self.closeConnection()
                self.closeDeadConnections()
                # reopen connection
                self.openConnection()
               # increment retry counter
                retries = retries + 1
        raise TimeoutError (os.path.basename(__file__) + ": timed out while expecting a response")

    def getMeasurement(self, command, measType="RMS"):
        # If selected measurement type is not the current measurement type, then switch the measurement mode
        if self.measurementType != measType and measType in self.measurementTypeList:
            self.measurementType = measType
            self.sendCommandQuery("MEAS:TYPE {}".format(measType), response=False)

        result = self.sendCommandQuery(command)
        mobj = self.numeric.match(result.strip())
        if mobj:
            if mobj.group(1) == "-":
                return - float(mobj.group(2))
            else:
                return float(mobj.group(2))
        else:
            raise ValueError(os.path.basename(__file__) + ": unable to parse numeric value {} from ELPA-SINE".format(result.strip()))

    def getVoltageMeasurement(self, measType="RMS"):
        self.sendCommandQuery("PRES:AVG 16", response=False)
        return self.getMeasurement("MEAS:VOLT?", measType=measType)

    def getCurrentMeasurement(self, measType="RMS"):
        self.sendCommandQuery("PRES:AVG 16", response=False)
        rv = self.getMeasurement("MEAS:CURR?", measType=measType)
        if rv == 0.0:
            print("Warning: ELPA returned measurement of {0:4.2f} from response of {1:s}".format(rv, self.lastResult))
        return rv

    def getPowerMeasurement(self, measType="Active"):
        self.sendCommandQuery("PRES:AVG 16", response=False)
        rv = self.getMeasurement("MEAS:POW?")
        if rv == 0.0:
            print("Warning: ELPA returned measurement of {0:4.2f} from response of {1:s}".format(rv, self.lastResult))
        return rv

    def setLoadCurrent(self, value):
        if value > self.maxCurrentLimit:
            raise ValueError("ERROR - ELPA-SINE should not be set to more than {} A".format(self.maxCurrentLimit))
        else:
            self.sendCommandQuery("STAT:MODE:CC", response=False)
            self.sendCommandQuery("PRES:FREQ AUTO", response=False)       
            self.sendCommandQuery("PRES:CC:A {0:3.1f}".format(value), response=False)

    '''
    Enable/disable the outputs
    '''
    def setOutputEnable (self, enableState):
        if (enableState == True):
            result = self.sendCommandQuery("STAT:LOAD ON", response=False)
        else:
            result = self.sendCommandQuery("STAT:LOAD OFF", response=False)
            
        return result
        
    '''
    Return the output enable state as a boolean
    '''
    def getOutputEnable (self):
        result = self.sendCommandQuery ("OUTP?")
        if (int(result) == 1):
            return True
        else:
            return False

    # Added for compatability with Keithley
    def reset(self):
        pass

    # Discover Elpa-sine devices through UDP broadcast
    # returns ???
    # This function makes a lot of assumptions about the data and certainly could be a lot more robust
    @staticmethod
    def discover():

        logging.debug(os.path.basename(__file__) + ": Searching for Elpa-Sine AC loads: ")

        devices = []

        ipList = socket.gethostbyname_ex(socket.gethostname())
        logging.debug(os.path.basename(__file__) + ": Discovered the following interfaces: " + str(ipList))

        # broadcast/listen on each interface

        responses = []

        for ip in ipList[2]:

            logging.debug(os.path.basename(__file__) + ": Broadcasting on : " + ip)

            tsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            tsock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            # wait 1 second for a response
            tsock.settimeout(1)
            tsock.bind((ip,56732))
            tsock.sendto(b'C!09               \n', ('255.255.255.255', 36))

            # Receive messages until timeout.
            while True:
                try:
                    responses.append(tsock.recvfrom(1024))
                except:
                    break

            tsock.close()


        logging.debug(os.path.basename(__file__) + ": Received the following responses: " + str(responses))

        # for each response received
        for response in responses:
            try:
                prefix = response[0][0:4]
                ip_addr = ".".join([str(x) for x in response[0][4:8]])
                mask = ".".join([str(x) for x in response[0][8:12]])
                mac = ":".join([format(x,'02X') for x in response[0][12:18]])
                device = int(response[0][18])<<8 + int(response[0][19])
                if prefix == b'C!09':
                    devices.append({"prefix":prefix,"ip":ip_addr,"mask":mask,"mac":mac,"device":device})
            except:
                # malformed data received
                break

        return devices

class testElpaSine(unittest.TestCase):
    def test_connect(self):
        elpa = elpaSine()

        elpa.openConnection(self.addr)
        response = elpa.sendCommandQuery ("*IDN?")
        self.assertEqual("ELPA-SINE 3750", response)

        elpa.closeConnection()

    def test_set_preset(self):
        elpa = elpaSine()

        elpa.openConnection("192.168.1.239")
        elpa.sendCommandQuery("MEAS:TYPE PEAK", response=False)
        voltage = elpa.getMeasurement("MEAS:VOLT?")
        print("Voltage=", voltage)
        current = elpa.getMeasurement("MEAS:CURR?")

        self.assertEqual(voltage, 0.0)
        self.assertEqual(current, 0.0)
        elpa.closeConnection()

    def test_set_load(self):
        elpa = elpaSine()

        elpa.openConnection("192.168.1.239")
        time.sleep(0.1)
        elpa.sendCommandQuery("STAT:MODE:LIN", response=False)
        elpa.sendCommandQuery("MEAS:TYPE PEAK", response=False)
        elpa.sendCommandQuery("STAT:LOAD ON", response=False)
        for current in [0.5, 0.75, 1.0, 1.5, 2.0]:
            elpa.sendCommandQuery("PRES:LIN:A {0:3.1f}".format(current), response=False)
            time.sleep(0.5)
            measCurrent = elpa.getMeasurement("MEAS:CURR?")
            print("Expected peak: {0:4.2f} measured peak: {1:4.2f}".format(current * 1.4, measCurrent))

        elpa.sendCommandQuery("STAT:LOAD OFF", response=False)
        elpa.closeConnection()

    def test_get_name(self):
        elpa = elpaSine()

        elpa.openConnection()
        name = elpa.sendCommandQuery("NAME?")
        print(name)
        elpa.closeConnection()


if __name__ == "__main__":
    unittest.main()