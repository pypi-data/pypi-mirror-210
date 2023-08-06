'''
Quarch Power Module Calibration Functions
Written for Python 3.6 64 bit

M Dearman April 2019
Edited k McRobert September 2021
'''
from quarchCalibration.Keithley_DMM6500_control import KeithleyDMM6500
import quarchpy.user_interface

'''
Calibration Flow
    Connect to AC PAM Fixture 
    Connect to ELPA-SINE
    Connect to AC Power Supply
    Connect to Switch Boxes
    step through each AC phase
      - Read peak voltage value and set voltage multiplier
      - Step through current values and set current multiplier
      - Save neutral current readings
    Calibrate/verify neutral

'''

#Imports QuarchPy library, providing the functions needed to use Quarch modules
#from quarchpy import quarchDevice #, scanDevices

# Import other libraries used in the examples

from .PowerModuleCalibration import *
from .calibrationConfig import *
from .elpaSine import *
from quarchpy.device.device import *
from quarchpy.user_interface import *
from quarchpy.utilities.BitManipulation import *
from quarchpy.device import quarchPPM, quarchDevice
from quarchpy.qis import isQisRunning, startLocalQis
from quarchpy.connection_specific.connection_QIS import QisInterface as qisInterface
import csv
from collections import OrderedDict
from .threePhaseSwitchBox import ThreePhaseSwitchBox
from quarchCalibration import Keysight_AC6804B_control
from quarchCalibration.Keysight_AC6804B_control import KeysightAC6804B

def get_QIS_version():
	#TODO option var "close_qis_afer_check" to determine if qis is left open or not.
    global my_close_qis
    """
    Returns the version of QIS.  This is the version of QIS currenty running on the local system if one exists.
    Otherwise the local version within quarchpy will be exectued and its version returned.

    Returns
    -------
    version: str
        String representation of the QIS version number

    """

    qis_version = ""
    if isQisRunning() == False:
        my_close_qis = True
        startLocalQis(headless=True)

    myQis = qisInterface()
    qis_version = myQis.sendAndReceiveCmd(cmd="$version")
    if "No Target Device Specified" in qis_version:
        qis_version = myQis.sendAndReceiveCmd(cmd="$help").split("\r\n")[0]
    vmatch = re.search("v([0-9]).([0-9]+)", qis_version)
    if vmatch:
        return [int(x) for x in vmatch.groups()]

def parseFixtureData(response,start,length):

    # split the multiline response into a list
    response = response.splitlines()
    result = ""
    # for each line
    for line in response:
        # remove 0x, swap bytes
        line = line[4:6] + line[2:4]
        # convert 4 char Hex to 16 bit binary string
        line = "{0:016b}".format(int(line,16))
        # concatenate all the strings
        result += line
    # pick out the section we want
    result = int(result[start:(start+length)],2)
    # convert two's compliment
    if (result >= 2**(length-1)):
        result -= 2**length
    return result


def bcdString(bcd,padding):
    # strip off "0x" if present
    if bcd[:2] == "0x":
        bcd = bcd [2:]
    # strip off leading 0's
    # loop while we have more the required minimum number of characters left
    while(len(bcd)>padding):
        # if the leading character is 0, remove it
        if bcd[0] == '0':
            bcd = bcd[1:]
        # else exit loop
        else:
            break
    return bcd

currentPhase = None

class QTL2843 (PowerModule):
    phaseList = ['L1', 'L2', 'L3', 'Neutral']
    calTypeList = ['I', 'V', 'V2']

    # Fixture Register Addresses
    CALIBRATION_MODE_ADDR               = '0xA100'
    CALIBRATION_CONTROL_ADDR            = '0xA101'

    SERIAL_NUMBER_START_ADDR            = '0xA102'

    AIGAIN_LOW_ADDR                     = '0xA105'
    AIGAIN_HIGH_ADDR                    = '0xA106'
    AVGAIN_LOW_ADDR                     = '0xA107'
    AVGAIN_HIGH_ADDR                    = '0xA108'
    AV2GAIN_LOW_ADDR                    = '0xA109'
    AV2GAIN_HIGH_ADDR                   = '0xA10A'

    BIGAIN_LOW_ADDR                     = '0xA10B'
    BIGAIN_HIGH_ADDR                    = '0xA10C'
    BVGAIN_LOW_ADDR                     = '0xA10D'
    BVGAIN_HIGH_ADDR                    = '0xA10E'
    BV2GAIN_LOW_ADDR                    = '0xA10F'
    BV2GAIN_HIGH_ADDR                   = '0xA110'

    CIGAIN_LOW_ADDR                     = '0xA111'
    CIGAIN_HIGH_ADDR                    = '0xA112'
    CVGAIN_LOW_ADDR                     = '0xA113'
    CVGAIN_HIGH_ADDR                    = '0xA114'
    CV2GAIN_LOW_ADDR                    = '0xA115'
    CV2GAIN_HIGH_ADDR                   = '0xA116'

    NIGAIN_LOW_ADDR                     = '0xA117'
    NIGAIN_HIGH_ADDR                    = '0xA118'
    NVGAIN_LOW_ADDR                     = '0xA119'
    NVGAIN_HIGH_ADDR                    = '0xA11A'
    NV2GAIN_LOW_ADDR                    = '0xA11B'
    NV2GAIN_HIGH_ADDR                   = '0xA11C'

    CALIBRATION_COMPLETE_ADDR	        = '0xA11D'
    LOAD_VOLTAGE                        = 240000

    # Fixture Information
    PAMSerial = None
    FixtureSerial = None
    calObjectSerial = None     # The serial number of the device that is being calibrated, i.e QTL1944 in HD PPM, Fixture in PAM
    idnStr = None
    Firmware = None
    Fpga = None
    calInstrument = None
    calInstrumentId = None
    switchbox = None

    # Physical Connection Tracking (what is plugged to what)
    loadChannel = None
    hostPowerChannel = None

    # general
    waitComplete = False
    checkedWiring = False
    currentPhase = None

    def specific_requirements(self):

        reportText=""

        # select a DMM6500 to use for calibration
        if "dmm6500" in calibrationResources.keys():
            self.dmm = calibrationResources["dmm6500"]
        else:
            self.dmm = self.getDMM()
        calibrationResources["dmm6500"] = self.dmm

        # select an AC Supply to use for calibration
        if "acSupply" in calibrationResources.keys():
            self.acSupply = calibrationResources["acSupply"]
        else:
            self.acSupply = self.getAcSupply()
        calibrationResources["acSupply"] = self.acSupply

        # select an AC Supply Mux to use for calibration
        if "acSupplyMux" in calibrationResources.keys():
            self.acSupplyMux = calibrationResources["acSupplyMux"]
        else:
            self.acSupplyMux = self.getAcMux("AC Supply Mux")
        calibrationResources["acSupplyMux"] = self.acSupplyMux

        # select an AC Load Mux to use for calibration
        if "acLoadMux" in calibrationResources.keys():
            self.acLoadMux = calibrationResources["acLoadMux"]
        else:
            self.acLoadMux = self.getAcMux("AC Load Mux")
        calibrationResources["acLoadMux"] = self.acLoadMux

        # select an AC Load to use for calibration
        if "elpasine" in calibrationResources.keys():
            self.acLoad = calibrationResources["elpasine"]
        else:
            self.acLoad = self.getAcLoad()
        calibrationResources["elpasine"] = self.acLoad

        # Check connectivity to the ELPA-SINE
        elpaIdentity = self.acLoad.sendCommandQuery("*IDN?")
        if elpaIdentity.find("ELPA-SINE") == -1:
            printText("Unable to communicate with ELPA-SINE")
            raise Exception("Unable to communicate with ELPA-SINE")
        self.calInstrumentId = elpaIdentity

        # Write module specific report header to file
        reportText += "Quarch AC Power Analysis Module: "
        reportText += self.PAMSerial + "\n"
        reportText += "Quarch FW Versions: "
        reportText += "FW:" + self.Firmware + ", FPGA: " + self.Fpga + "\n"
        reportText += "\n"
        reportText += "Calibration Instruments#:\n"
        reportText += self.calInstrumentId + "\n"

        # perform uptime check and write to file
        if self.waitComplete != True:
            reportText += self.wait_for_up_time(desired_up_time=600, command="conf:runtime:fix:sec?")
            self.waitComplete = True

        return reportText

    def getDMM(self,alias=""):
        #if alias is None or alias == "":
        alias = "DMM6500"
        # Find an AC Mux
        while (True):
            devices = KeithleyDMM6500.discover()
            selectedDevice = quarchpy.user_interface.listSelection(title="Select an " + alias,message="Please select the correct " + alias,selectionList=devices,additionalOptions = [["rescan","rescan"],["quit","quit"]],nice=True)
            if str(selectedDevice[1]).lower() == "rescan":
                pass
            elif str(selectedDevice[1]).lower() == "quit":
                printText("User Quit Program")
                sys.exit(0)
            else:
                try:
                    dmm = KeithleyDMM6500(selectedDevice[2])
                    break
                except:
                    printText("Unable to communicate with selected device!")
                    printText("")
                    raise

        #print("AC Voltage: " + str(dmm.measureACVoltage()))
        #print("AC Current: " + str(dmm.measureACCurrent()))

        return dmm

    def getAcSupply(self,alias=""):
        #if alias is None or alias == "":
        alias = "AC Supply"
        # Find an AC Mux
        while (True):
            devices = KeysightAC6804B.discover()
            selectedDevice = quarchpy.user_interface.listSelection(title="Select an " + alias,message="Please select the correct " + alias,selectionList=devices,additionalOptions = [["rescan","rescan"],["quit","quit"]],nice=True)
            if str(selectedDevice[1]).lower() == "rescan":
                pass
            elif str(selectedDevice[1]).lower() == "quit":
                printText("User Quit Program")
                sys.exit(0)
            else:
                try:
                    acSupply = KeysightAC6804B(selectedDevice[2])
                    break
                except:
                    printText("Unable to communicate with selected device!")
                    printText("")
                    raise
        return acSupply

    def getAcMux(self,alias=""):
        if alias is None or alias == "":
            alias = "AC Mux"
        # Find an AC Mux
        while (True):
            devices = ThreePhaseSwitchBox.discover()
            selectedDevice = user_interface.listSelection(title="Select an " + alias,message="Please select the correct " + alias,selectionList=devices,additionalOptions = [["rescan","rescan"],["quit","quit"]],nice=True)
            if str(selectedDevice[1]).lower() == "rescan":
                pass
            elif str(selectedDevice[1]).lower() == "quit":
                printText("User Quit Program")
                sys.exit(0)
            else:
                try:
                    acMux = ThreePhaseSwitchBox(alias,selectedDevice[2])
                    break
                except:
                    printText("Unable to communicate with selected device!")
                    printText("")
                    raise
        return acMux


    def getAcLoad(self,alias=""):
        if alias is None or alias == "":
            alias = "AC Load"
        # Find an AC Mux
        while (True):
            devices = ElpaSine.discover()
            deviceList = []
            for device in devices:
                deviceList.append(device["ip"])
            selectedDevice = user_interface.listSelection(title="Select an " + alias,message="Please select the correct " + alias,selectionList=deviceList,additionalOptions = [["rescan"],["quit"]],nice=True)
            if str(selectedDevice).lower() == "rescan":
                pass
            elif str(selectedDevice).lower() == "quit":
                printText("User Quit Program")
                sys.exit(0)
            else:
                try:
                    acLoad = ElpaSine(selectedDevice)
                    break
                except:
                    printText("Unable to communicate with selected device!")
                    printText("")
                    raise
        return acLoad

    def getCoeffAddr(self, phase, calType):
        if phase not in self.phaseList:
            raise ValueError("Unknown phase " + phase)
        elif calType not in self.calTypeList:
            raise ValueError("Unknown calibration type " + calType)
        else:
            pnumber = self.phaseList.index(phase) * 3 + self.calTypeList.index(calType)
            addrLow = 0xA105 + pnumber * 2
            addrHigh = addrLow + 1
        return (addrLow, addrHigh)

    def clear_calibration(self):

        # set unit into calibration mode
        self.dut.sendCommand("write " + QTL2843.CALIBRATION_MODE_ADDR + " 0xaa55")
        self.dut.sendCommand("write " + QTL2843.CALIBRATION_MODE_ADDR + " 0x55aa")

        # clear all calibration registers
        for phase in self.phaseList:
            for t in ["V", "I", "V2"]:
                caddr = self.getCoeffAddr(phase, t)
                self.dut.sendAndVerifyCommand("write 0x{0:04x} 0x0000".format(caddr[0]))
                self.dut.sendAndVerifyCommand("write 0x{0:04x} 0x0000".format(caddr[1]))

        # Load calibration values into the ADE7978
        self.dut.sendCommand("write 0x1800 0x0000")
        self.dut.sendCommand("write 0x1800 0x0002")

        #self.loadToAde()

        # write 0xaa55 to register to calibration complete register to tell module it is calibrated
        self.dut.sendAndVerifyCommand("write " + QTL2843.CALIBRATION_COMPLETE_ADDR + " 0xaa55")
        
    def write_calibration(self):

        # write the calibration registers
        # erase the tag memory
        printText("Erasing TAG memory..")
        self.dut.sendCommand("write 0xa200 0x0020")
        # TODO: should check for completion here...
        # wait for 2 seconds for erase to complete
        # check busy
        while checkBit(self.dut.sendCommand("read 0xa200"),8):
            sleep(0.1)
        # write the tag memory
        printText("Programming TAG memory...")
        self.dut.sendCommand("write 0xa200 0x0040")        
        # check busy
        while checkBit(self.dut.sendCommand("read 0xa200"),8):
            sleep(0.1)

    def close_module(self):

        #close the connection to the calibration instrument
        self.acLoad.closeConnection()

    def close_all(self):

        #close all attached devices
        self.acLoad.setLoadCurrent(0)
        self.acLoad.closeConnection()
        self.acSupplyMux.setMux("off")
        self.acLoadMux.setMux("off")

    class QTL2843_Calibration (AcPamCalibration):

        streamFilename = ''
        iteration = 0
        streamMeasureTime = 2.0
        scaling = 1

        def __init__(self):
            super().__init__()
        
        def init_cal(self):

            self.powerModule.acSupply.setOutputEnable(False)
            self.powerModule.acSupply.setACSupplyRange("AUTO")
            self.powerModule.acSupply.setACSupplyFrequency(50)
            self.powerModule.acSupply.setSupplyCurrentLimit(10)
            self.powerModule.acSupply.setOutputEnable(True)

        def meas_volt(self,phase):

            return self.getMeasurement(phase, 'V', typ='RMS', streamTime=self.streamMeasureTime)

        def meas_current(self,phase):

            return self.getMeasurement(phase, 'I', typ='RMS', streamTime=self.streamMeasureTime)

        def streamData(self,streamMeasureTime=None):
            if streamMeasureTime is not None:
                self.streamMeasureTime = streamMeasureTime
            # Sets for a manual record trigger, so we can start the stream from the script
            self.powerModule.dut.sendCommand("record:trigger:mode manual")
            self.powerModule.dut.sendCommand("record:averaging 0")

            # In this example we write to a fixed path
            self.streamFilename = calibrationResources["calPath"] + "\\" + self.phase + '_' + '_' + self.units + '_' + str(self.iteration) + '.csv'
            self.iteration += 1
            self.powerModule.dut.startStream(self.streamFilename, 2000, 'Example stream to file')

            # Delay for a x seconds while the stream is running.  You can also continue
            # to run your own commands/scripts here while the stream is recording in the background
            time.sleep(1)

            # Check the stream status, so we know if anything went wrong during the stream
            streamStatus = self.powerModule.dut.streamRunningStatus()
            if ("Stopped" in streamStatus):
                if ("Overrun" in streamStatus):
                    print('Stream interrupted due to internal device buffer has filled up')
                elif ("User" in streamStatus):
                    print('Stream interrupted due to max file size has being exceeded')
                else:
                    print("Stopped for unknown reason")

            # Stop the stream.  This function is blocking and will wait until all remaining data has
            # been downloaded from the module
            self.powerModule.dut.stopStream()

            # check to ensure stream is fully stopped before continuing script
            stopStreamCount = 0
            while not "stopped" in str(self.powerModule.dut.streamRunningStatus()).lower():
                stopStreamCount += 1
                if stopStreamCount > 20:
                    raise TimeoutError("Failed to stop stream after {} seconds".format(stopStreamCount))
                time.sleep(1)

        def readRawValues(self):
            rawValues = {}
            with open(self.streamFilename, 'r') as fh:
                csvfile = csv.reader(fh)
                titles = None
                for row in csvfile:
                    if not titles:
                        titles = row
                        for i in range(len(row)):
                            rawValues[titles[i]] = []
                    else:
                        for i in range(len(row)):
                            try:
                                rawValues[titles[i]].append(int(row[i]))
                            except ValueError:
                                rawValues[titles[i]].append(0)
            return rawValues

        def calcRmsValues(self,samples=800):
            rawValues = self.readRawValues()
            rmsValues = {}
            for k in rawValues.keys():
                if len(rawValues[k]) >= samples:
                    items = [float(x**2) for x in rawValues[k][:samples]]
                    meanSquares = sum(items) / float(len(items))
                    rmsValues[k] = meanSquares**0.5
            self.lastMeasurement = rmsValues
            return rmsValues

        def findPeakValues(self):
            maxvalues = []
            prevValues = []
            peakList = []
            rising = []
            with open(self.streamFilename, 'r') as fh:
                csvfile = csv.reader(fh)
                titles = None
                for row in csvfile:
                    if not titles:
                        titles = row
                        for i in range(len(row)):
                            maxvalues.append(0)
                            prevValues.append(0)
                            peakList.append([])
                            rising.append(False)
                    else:
                        for i in range(len(row)):
                            value = int(row[i])
                            if value >= maxvalues[i]:
                                maxvalues[i] = value

                            # If we are in the positive have of the wave, look for the point just when values begin to fall
                            if value > 0:
                                if value > prevValues[i]:
                                    rising[i] = True
                                    prevValues[i] = value
                                else:
                                    if rising[i]:
                                        peakList[i].append(prevValues[i])
                                        rising[i] = False
                            else:
                                # On the negative half of the wave, reset the values for the next pass
                                rising[i] = False
                                prevValues[i] = 0

            mvdict = {}
            avgPeak = {}
            for i in range(len(titles)):
                mvdict[titles[i]] = maxvalues[i]

                # Throw away first and last samples, as they may have been clipped
                peakVector = np.array(peakList[i][1:-1])
                avgPeak[titles[i]] = peakVector.mean()

            return avgPeak

        def getMeasurement(self, phase, parm, typ='PEAK', streamTime=1.0):
            self.streamData(streamTime)
            if typ == 'PEAK':
                vals = self.findPeakValues()
            else:
                vals = self.calcRmsValues()

            if parm == 'V':
                key = "{0:s} mV".format(phase)
            else:
                key = "{0:s} mA".format(phase)

            if key in vals:
                return vals[key]
            else:
                raise ValueError("requested measurement not found in data")
        
        def finish_cal(self):

            #turn off supply
            self.powerModule.acSupply.setOutputEnable(False)

            #turn off switches
            self.powerModule.acSupplyMux.setMux("off")
            self.powerModule.acLoadMux.setMux("off")

            #turn off load
            self.powerModule.acLoad.setLoadCurrent(0)
            #self.powerModule.acLoad.setOutputEnable(False)

            # try to close the qis connection
            try:
                self.powerModule.dut.sendCommand("close")
            except:
                pass

        def report(self,action,data):

            report = []

            # send to report file
            report.append("          Pass Level  +/-(" + str(self.absErrorLimit) + str(self.units) +" + " + str(self.relErrorLimit) + "%) \n")


            # check errors and generate report
            report.append('\n')

            if action == "calibrate":
               report.append("\t" + '{0:>11}'.format('Reference ')+ self.units + '   ' + '{0:>10}'.format('Raw Value ')+ self.units + '   ' + '{0:>10}'.format('Result ')+ self.units + '   ' + '{0:>10}'.format('Error ')+ self.units + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + ' ' + '{0:>10}'.format('Pass'))
            elif action == "verify":
                report.append("\t" + '{0:>11}'.format('Reference ')+ self.units + '   ' + '{0:>10}'.format('Result ')+ self.units + '   ' + '{0:>10}'.format('Error ')+ self.units + '   ' + '{0:>13}'.format('+/-(Abs Error,% Error)') + '   ' + '{0:>10}'.format('Pass'))

            report.append("==================================================================================================")

            # zero worst case error vars
            worstAbsError = 0
            worstRelError = 0
            worstRef = None
            overallResult = True

            # for each calibration reference
            for thisLine in data:
                reference = thisLine[1]
                ppmValue = thisLine[0]

                # for calibration, replace value with calibrated result
                if action =="calibrate":
                    calibratedValue = self.getResult(ppmValue)
                # otherwise just use ppmValue directly
                else:
                    calibratedValue = ppmValue

                # work out errors
                (actError,errorSign,absError,relError,result) = getError(reference,calibratedValue,self.absErrorLimit,self.relErrorLimit)

                # compare/replace with running worst case
                if absError >= worstAbsError:
                    if relError >= worstRelError:
                        worstAbsError = absError
                        worstRelError = relError
                        worstCase = errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%) @ " + '{:.3f}'.format(reference) + self.units

                # update overall pass/fail
                if result != True:
                    overallResult = False

                #generate report
                passfail = lambda x: "Pass" if x else "Fail"
                if action == "calibrate":
                    report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + '{:>10.1f}'.format(calibratedValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))
                elif action == "verify":
                    report.append("\t" + '{:>11.3f}'.format(reference) + '     ' + '{:>10.1f}'.format(ppmValue) + '     ' + "{:>10.3f}".format(actError) + '     ' + '{0:>16}'.format(errorSign + "(" + str(absError) + self.units + "," + "{:.3f}".format(relError) + "%)") + '     ' + '{0:>10}'.format(passfail(result)))

            report.append("==================================================================================================")
            report.append('\n')

            if action == "calibrate":
                report.append("Calculated Multiplier: " + str(self.multiplier.originalValue()) + ", Calculated Offset: " + str(self.offset.originalValue()))
                report.append("Stored Multiplier: " + str(self.multiplier.storedValue()) + ", Stored Offset: " + str(self.offset.storedValue()))
                report.append("Multiplier Register: " + self.multiplier.hexString(4) + ", Offset Register: " + self.offset.hexString(4))

            report.append("" + '{0:<35}'.format(self.title)+ '     '  +'{0:>10}'.format("Passed : ")+ '  '  + '{0:<5}'.format(str(overallResult))+ '     ' + '{0:>11}'.format( "worst case:")+ '  '  +'{0:>11}'.format(worstCase))
            report.append("\n\n\n")
            
            #Add to Test Summary? Do this here?
            passfail = lambda x: "Passed" if x else "Failed"

            return {"title":self.title,"result":overallResult,"worst case":worstCase,"report":('\n'.join(report))}

    class QTL2843_Voltage_Calibration (QTL2843_Calibration):

        def __init__(self,powerModule,phase):

            self.title = phase + " Voltage Calibration"
            self.phase = phase
            self.powerModule = powerModule
            self.absErrorLimit = 0                  # 0mV
            self.relErrorLimit = 1                  # 1%
            self.test_min = 50000                   # 50V
            self.test_max = 280000                  # 280V
            self.test_steps = 8
            self.units = "mV"
            self.scaling = 1
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 23
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal()

            # clear the multiplier and offset registers by setting them to zero
            caddr = self.powerModule.getCoeffAddr(self.phase, "V")
            self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} 0x0000".format(caddr[0]))
            self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} 0x0000".format(caddr[1]))

            #set switches
            self.powerModule.acSupplyMux.setMux("L1")
            self.powerModule.acLoadMux.setMux(self.phase)
            
            #Enable load
            self.powerModule.acLoad.setLoadCurrent(0)
            self.powerModule.acLoad.setOutputEnable(True)

            # Check Host Power is present
#            while (super().checkLoadVoltage(500,500) != True):
#                input("Unexpected voltage detected at load, please check connections")

        def setRef(self,value):
            self.powerModule.acSupply.setACSupplyVoltage(value/1000)
            sleep(1) # Add settling time

        def readRef(self):
            print("AC Current= " + str(self.powerModule.dmm.measureACCurrent()) + "\n")
            return self.powerModule.acLoad.getVoltageMeasurement('RMS') * 1000.0

        def readVal(self):
            # Return measurement, normalize all values to Volts and Amps
            return self.getMeasurement(self.phase, 'V', typ='RMS', streamTime=self.streamMeasureTime)

        def setCoefficients(self):

            # Get Coefficient Addresses
            addrLow, addrHigh = self.powerModule.getCoeffAddr(self.phase, 'V')

            hexString = self.multiplier.hexString(8)
            result1 = self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} ".format(addrHigh) + hexString[:6]) 
            result2 = self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} ".format(addrLow) + hexString[:2] + hexString[6:])
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set L1 Current Coefficients", result)

            # load calibration values to ADE
            self.powerModule.dut.sendCommand("write 0x1800 0x0000")
            self.powerModule.dut.sendCommand("write 0x1800 0x0002")

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

    class QTL2843_Current_Calibration (QTL2843_Calibration):

        def __init__(self,powerModule,phase):

            self.title = phase + " Current Calibration"
            self.phase = phase
            self.powerModule = powerModule
            self.absErrorLimit = 0                  # 0mA
            self.relErrorLimit = 1                  # 1%
            self.test_min = 100                     # 100mA
            self.test_max = 3000                    # 3A
            self.test_steps = 8
            self.units = "mA"
            self.scaling = 1
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 23
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal()

            # clear the multiplier and offset registers by setting them to zero
            caddr = self.powerModule.getCoeffAddr(self.phase, "I")
            self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} 0x0000".format(caddr[0]))
            self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} 0x0000".format(caddr[1]))

            #turn on AC Supply
            self.powerModule.acSupply.setACSupplyVoltage(240)
            self.powerModule.acSupply.setOutputEnable(True)

            #set switches
            self.powerModule.acSupplyMux.setMux("L1")
            self.powerModule.acLoadMux.setMux(self.phase)

        def setRef(self,value):
            if value < 0 or value > 10000:
                raise ValueError("ERROR - ELPA max RMS current must be less than 10A")
            self.powerModule.acLoad.setLoadCurrent(value / 1000.0)
            self.powerModule.acLoad.setOutputEnable(True)
            sleep(1) # Add settling time

        def readRef(self):
            #return self.powerModule.acLoad.getCurrentMeasurement('RMS') * 1000.0
            return self.powerModule.dmm.measureACCurrent() * 1000.0

        def readVal(self):
            # Return measurement, normalize all values to Volts and Amps
            return self.getMeasurement(self.phase, 'I', typ='RMS', streamTime=self.streamMeasureTime)

        def setCoefficients(self):

            # Get Coefficient Addresses
            addrLow, addrHigh = self.powerModule.getCoeffAddr(self.phase, 'I')

            hexString = self.multiplier.hexString(8)
            result1 = self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} ".format(addrHigh) + hexString[:6]) 
            result2 = self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} ".format(addrLow) + hexString[:2] + hexString[6:])
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set " + self.phase + " Current Coefficients", result)

            # load calibration values to ADE
            self.powerModule.dut.sendCommand("write 0x1800 0x0000")
            self.powerModule.dut.sendCommand("write 0x1800 0x0002")

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

    # Neutral Calibration is the same as L1 Current Calibration, but we measure and calibrate the neutral current instead of L1
    class QTL2843_Neutral_Current_Calibration (QTL2843_Calibration):

        def __init__(self,powerModule,phase):

            self.title = "Neutral Calibration"
            self.phase = "Neutral"
            self.powerModule = powerModule
            self.absErrorLimit = 0                  # 0mA
            self.relErrorLimit = 1                  # 1%
            self.test_min = 100                     # 100mA
            self.test_max = 3000                    # 3A
            self.test_steps = 8
            self.units = "mA"
            self.scaling = 1
            self.multiplier_signed = False
            self.multiplier_int_width = 1
            self.multiplier_frac_width = 23
            self.offset_signed = True
            self.offset_int_width = 10
            self.offset_frac_width = 6

        def init(self):

            super().init_cal()

            # clear the multiplier and offset registers by setting them to zero
            caddr = self.powerModule.getCoeffAddr(self.phase, "I")
            self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} 0x0000".format(caddr[0]))
            self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} 0x0000".format(caddr[1]))

            #turn on AC Supply
            self.powerModule.acSupply.setACSupplyVoltage(240)
            self.powerModule.acSupply.setOutputEnable(True)

            #set switches
            self.powerModule.acSupplyMux.setMux("L1")
            self.powerModule.acLoadMux.setMux("L1")
            
            # Check Host Power is present
#            while (super().checkLoadVoltage(500,500) != True):
#                input("Unexpected voltage detected at load, please check connections")

        def setRef(self,value):
            if value < 0 or value > 10000:
                raise ValueError("ERROR - ELPA max RMS current must be less than 10A")
            self.powerModule.acLoad.setLoadCurrent(value / 1000.0)
            self.powerModule.acLoad.setOutputEnable(True)
            sleep(1) # Add settling time

        def readRef(self):
            #return self.powerModule.acLoad.getCurrentMeasurement('RMS') * 1000.0
            return self.powerModule.dmm.measureACCurrent() * 1000.0

        def readVal(self):
            # Return measurement, normalize all values to Volts and Amps
            return self.getMeasurement(self.phase, 'I', typ='RMS', streamTime=self.streamMeasureTime)

        def setCoefficients(self):

            # Get Coefficient Addresses
            addrLow, addrHigh = self.powerModule.getCoeffAddr(self.phase, 'I')

            hexString = self.multiplier.hexString(8)
            result1 = self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} ".format(addrHigh) + hexString[:6]) 
            result2 = self.powerModule.dut.sendAndVerifyCommand("write 0x{0:04x} ".format(addrLow) + hexString[:2] + hexString[6:])
            if result1 and result2:
                result = True
            else:
                result = False
            logSimpleResult("Set Neutral Current Coefficients", result)

            # load calibration values to ADE
            self.powerModule.dut.sendCommand("write 0x1800 0x0000")
            self.powerModule.dut.sendCommand("write 0x1800 0x0002")

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("calibrate",data)

    class QTL2843_Voltage_Verification (QTL2843_Calibration):

        def __init__(self,powerModule,phase):

            self.title = phase + " Voltage Verification"
            self.phase = phase
            self.powerModule = powerModule
            self.absErrorLimit = 0                  # 0mV
            self.relErrorLimit = 1                  # 1%
            self.test_min = 50000                   # 50V
            self.test_max = 280000                  # 280V
            self.test_steps = 8
            self.units = "mV"

        def init(self):

            super().init_cal()

            #set switches
            self.powerModule.acSupplyMux.setMux("L1")
            self.powerModule.acLoadMux.setMux(self.phase)

            #time.sleep(1) # attempt to sort error in first reading from elpaSine
            
            # Check Host Power is present
#            while (super().checkLoadVoltage(500,500) != True):
#                input("Unexpected voltage detected at load, please check connections")

        def setRef(self,value):
            self.powerModule.acSupply.setACSupplyVoltage(value/1000)
            sleep(1) # Add settling time

        def readRef(self):
            return self.powerModule.acLoad.getVoltageMeasurement('RMS') * 1000.0

        def readVal(self):
            # Return measurement, normalize all values to Volts and Amps
            return self.getMeasurement(self.phase, 'V', typ='RMS', streamTime=self.streamMeasureTime)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    class QTL2843_Current_Verification (QTL2843_Calibration):

        def __init__(self,powerModule,phase):

            self.title = phase + " Current Verification"
            self.phase = phase
            self.powerModule = powerModule
            self.absErrorLimit = 0                  # 0mA
            self.relErrorLimit = 1                  # 1%
            self.test_min = 100                     # 100mA
            self.test_max = 3000                    # 3A
            self.test_steps = 8
            self.units = "mA"

        def init(self):

            super().init_cal()

            #turn on AC Supply
            self.powerModule.acSupply.setACSupplyVoltage(240)
            self.powerModule.acSupply.setOutputEnable(True)

            #set switches
            self.powerModule.acSupplyMux.setMux("L1")
            self.powerModule.acLoadMux.setMux(self.phase)

        def setRef(self,value):
            if value < 0 or value > 10000:
                raise ValueError("ERROR - ELPA max RMS current must be less than 10A")
            self.powerModule.acLoad.setLoadCurrent(value / 1000.0)
            self.powerModule.acLoad.setOutputEnable(True)
            time.sleep(1) # add settling time

        def readRef(self):
            #return self.powerModule.acLoad.getCurrentMeasurement('RMS') * 1000.0
            return self.powerModule.dmm.measureACCurrent() * 1000.0

        def readVal(self):
            # Return measurement, normalize all values to Volts and Amps
            return self.getMeasurement(self.phase, 'I', typ='RMS', streamTime=self.streamMeasureTime)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    # Neutral Verification is the same as L1 Current Verification, but we measure the neutral current instead of L1
    class QTL2843_Neutral_Current_Verification (QTL2843_Calibration):

        def __init__(self,powerModule,phase):

            self.title = "Neutral Verification"
            self.phase = "Neutral"
            self.powerModule = powerModule
            self.absErrorLimit = 0                  # 0mA
            self.relErrorLimit = 1                  # 1%
            self.test_min = 100                     # 100mA
            self.test_max = 3000                    # 3A
            self.test_steps = 8
            self.units = "mA"

        def init(self):

            super().init_cal()

            #set switches
            self.powerModule.acSupplyMux.setMux("L1")
            self.powerModule.acLoadMux.setMux("L1")
            
            # Check Host Power is present
#            while (super().checkLoadVoltage(500,500) != True):
#                input("Unexpected voltage detected at load, please check connections")

        def setRef(self,value):
            if value < 0 or value > 10000:
                raise ValueError("ERROR - ELPA max RMS current must be less than 10A")
            self.powerModule.acLoad.setLoadCurrent(value / 1000.0)
            self.powerModule.acLoad.setOutputEnable(True)
            sleep(1) # Add settling time

        def readRef(self):
            #return self.powerModule.acLoad.getCurrentMeasurement('RMS') * 1000.0
            return self.powerModule.dmm.measureACCurrent() * 1000.0

        def readVal(self):
            # Return measurement, normalize all values to Volts and Amps
            return self.getMeasurement(self.phase, 'I', typ='RMS', streamTime=self.streamMeasureTime)

        def finish(self):

            super().finish_cal()

        def report(self,data):

            return super().report("verify",data)

    def __init__(self,dut):

        # We need to use QIS to get RMS etc
        # close the quarchpy connection
        dut.closeConnection()
        # and open a QIS connection
        isQisRunning()
        version = get_QIS_version()
        if not ((version[0] == 1 and version[1] >= 27) or version[0] > 1):
            raise ValueError("ERROR - Detected QIS {0[0]}.{0[1]}, Requires QIS version 1.27 or greater".format(version))

        dut = quarchDevice(dut.ConString, ConType='QIS')
        dut = quarchPPM(dut)    #mike hack

        sleep(1)

        # set the name of this module
        self.name = "IEC Mains PAM"
        self.dut = dut

        # Serial numbers (ensure QTL at start)
        self.enclosureSerial = self.dut.sendCommand("*ENCLOSURE?")
        if (self.enclosureSerial.find ("QTL") == -1):
            self.enclosureSerial = "QTL" + self.enclosureSerial
        # fetch the enclosure position
        self.PAMSerial = self.dut.sendCommand ("*SERIAL?")
        if (self.PAMSerial.find ("QTL") == -1):
            self.PAMSerial = "QTL" + self.PAMSerial
        # Fixture Serial
        # fixture serial is retrieved as BCD, we need to convert and pad it
        self.FixtureSerial = "QTL" + bcdString(dut.sendCommand("read 0xA102"),4) + "-" + bcdString(dut.sendCommand("read 0xA103"),2) + "-" + bcdString(dut.sendCommand("read 0xA104"),3) # TODO: this should be replaced with fix:serial? command when implemented
        # calObjectSerial Serial
        self.calObjectSerial = self.PAMSerial
        # Filename String
        self.filenameString = self.PAMSerial
        # Code version (FPGA)
        self.idnStr = dut.sendCommand ("*IDN?")
        pos = self.idnStr.upper().find ("FPGA 1:")
        if (pos != -1):
            versionStr = self.idnStr[pos+7:]
            pos = versionStr.find ("\n")
            if (pos != -1):
                versionStr = versionStr[:pos].strip()
            else:
                pass
        else:
            versionStr = "NOT-FOUND"    
        self.Fpga = versionStr.strip()
    
        # Code version (FW)    
        pos = self.idnStr.upper().find ("PROCESSOR:")
        if (pos != -1):
            versionStr = self.idnStr[pos+10:]
            pos = versionStr.find ("\n")
            if (pos != -1):
                versionStr = versionStr[:pos].strip()            
            else:
                pass
        else:
            versionStr = "NOT-FOUND"    
        self.Firmware = versionStr.strip()

        self.calibrations = {}
        self.calibrations["L1"] = {
            "Voltage" : self.QTL2843_Voltage_Calibration(self,"L1"),
            "Current" : self.QTL2843_Current_Calibration(self,"L1")
        }
        self.calibrations["L2"] = {
            "Voltage" : self.QTL2843_Voltage_Calibration(self,"L2"),
            "Current" : self.QTL2843_Current_Calibration(self,"L2")
        }
        self.calibrations["L3"] = {
            "Voltage" : self.QTL2843_Voltage_Calibration(self,"L3"),
            "Current" : self.QTL2843_Current_Calibration(self,"L3")
        }
        self.calibrations["Neutral"] = {
            "Current" : self.QTL2843_Neutral_Current_Calibration(self,"Neutral")
        }

        self.verifications = {}
        self.verifications["L1"] = {
            "Voltage" : self.QTL2843_Voltage_Verification(self,"L1"),
            "Current" : self.QTL2843_Current_Verification(self,"L1")
        }
        self.verifications["L2"] = {
            "Voltage" : self.QTL2843_Voltage_Verification(self,"L2"),
            "Current" : self.QTL2843_Current_Verification(self,"L2")
        }
        self.verifications["L3"] = {
            "Voltage" : self.QTL2843_Voltage_Verification(self,"L3"),
            "Current" : self.QTL2843_Current_Verification(self,"L3")
        }
        self.verifications["Neutral"] = {
            "Current" : self.QTL2843_Neutral_Current_Verification(self,"Neutral")
        }