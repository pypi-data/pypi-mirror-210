#!/usr/bin/env python
'''
This example runs the calibration process for a HD PPM
It products a calibrated PPM and a calibration file for later use

########### VERSION HISTORY ###########

05/04/2019 - Andy Norrie     - First Version

########### INSTRUCTIONS ###########

1- Connect the PPM on LAN and power up
2- Connect the Keithley 2460 until on LAN, power up and check its IP address
3- Connect the calibration switch unit to the output ports of the PPM and Keithley

####################################
'''

# Global resources
from time import sleep,time
import datetime
import logging,os
import sys
import re

# Quarch device control
from quarchpy import *
from quarchpy.device import *

# Calibration control
from quarchCalibration import calCodeVersion
from quarchCalibration.QTL1944 import *
from quarchCalibration.QTL1944_06 import *
from quarchCalibration.QTL2347 import *
from quarchCalibration.QTL2525 import *
from quarchCalibration.QTL2788 import *
from quarchCalibration.QTL2887 import *
from quarchCalibration.QTL2888 import *
from quarchCalibration.QTL2621 import *
from quarchCalibration.QTL2673 import *
from quarchCalibration.QTL2674 import *
#from quarchCalibration.QTL2582 import *
#from quarchCalibration.QTL2843 import *
from quarchCalibration.PowerModuleCalibration import*
from quarchCalibration.calibrationConfig import*
# UI functions
from quarchpy.user_interface import *
# TestCenter functions
from quarchpy.utilities import TestCenter
from quarchpy.debug.SystemTest import get_quarchpy_version
from quarchCalibration.noise_test import test_main as noise_test_main
from quarchpy.qps import isQpsRunning, startLocalQps
import time
# Devices that will show up in the module scan dialog
scanFilterStr = ["QTL1999", "QTL1995", "QTL1944", "QTL2312", "QTL2098", "QTL2582", "QTL2751", "QTL2789", "QTL2843"]
my_close_qis = False

# Performs a standard calibration of the PPM
def runCalibration (loadAddress=None, calPath=None, moduleAddress=None, logLevel="warning", calAction=None, extra_args=None, streamPath=None):

    myPpmDevice = None
    listOfFailures = []
    try:
        # Display the app title to the user
        print("\n")
        displayTable(["Quarch Technology Calibration System","(C) 2019-2021, All rights reserved", "V" + calCodeVersion], align="c")

        # Process parameters
        calPath = get_check_valid_calPath(calPath)
        streamPath = check_path_write_permissions(streamPath)

        setup_logging(logLevel)

        calibrationResources["moduleString"] = moduleAddress
        calibrationResources["loadString"] = loadAddress
        calibrationResources["calPath"] = calPath
        calibrationResources["streamPath"] = streamPath


        while True: # While doing any calibration task

            if myPpmDevice == None: # If no ppmDevice for the DUT
                dut, myPpmDevice = create_dut_object()

            #Cal Action Parsing
            if (calAction == None):
                if User_interface.instance != None and User_interface.instance.selectedInterface == "testcenter":
                    return listOfFailures #Return failures to parent script for processing.
                else: # If no calibration action is selected, request one
                    # Clear the list of failures as we are starting a new action
                    listOfFailures = []
                    calAction = show_action_menu(calAction)
            if (calAction == 'quit'):
                sys.exit(0)
            elif(calAction == "noise_test"):
                listOfTestResults = dut.noiseTest()
                if listOfTestResults !=None:
                    for testResult in listOfTestResults:
                        if testResult["result"] is False:
                            listOfFailures.append(testResult)
                else:# Only reached if the DUT has no noise test.
                    skippedNoiseTestResult={'title': 'noise test skipped', 'result': False, 'worst case': 'NA', 'report': 'noise test skipped due to module not having one'}
                    listOfFailures.append(skippedNoiseTestResult)
                calAction=None
            elif (calAction == 'calibrate') or (calAction == 'verify'):
                # Perform the Calibration or Verification
                # get CalibrationTime
                calTime = datetime.datetime.now()
                # open report for writing and write system header
                fileName = calPath + "\\" + dut.filenameString + "_" + calTime.strftime("%d-%m-%y_%H-%M") + "-" + calAction + ".txt"
                printText("")
                printText("Report file: " + fileName)
                reportFile = open(fileName, "a+", encoding='utf-8')
                reportFile.write("\n")
                reportFile.write("Quarch Technology Calibration Report\n" if "cal" in str(calAction).lower() else "Quarch Technology Verification Report\n")
                reportFile.write("\n")
                reportFile.write("---------------------------------\n")
                reportFile.write("\n")
                reportFile.write("System Information:\n")
                reportFile.write("\n")
                try:
                    reportFile.write("QuarchPy Version: " + get_quarchpy_version() + "\n")
                except:
                    reportFile.write("QuarchPy Version: unknown\n")
                reportFile.write("Calibration Version: " + str(calCodeVersion) + "\n")
                reportFile.write("Calibration Time: " + str(calTime.replace(microsecond=0)) + "\n")
                reportFile.write("\n")
                reportFile.write("---------------------------------\n")
                reportFile.write("\n")
                reportFile.flush()
                # get required instruments etc
                reportFile.write("Device Specific Information:\n")
                reportFile.write("\n")
                reportFile.write(dut.specific_requirements())
                reportFile.write("\n")
                reportFile.write("---------------------------------\n")
                reportFile.write("\n")
                reportFile.flush()
    
                # Perform the Calibration or Verification
                listOfTestResults = dut.calibrateOrVerify(calAction,reportFile)
                for testResult in listOfTestResults:
                    if testResult["result"] is False:
                        listOfFailures.append(testResult)

                #reportFile = open(fileName, "a+", encoding='utf-8')#TODO Test if needed
                addOverviewSectionToReportFile(reportFile, listOfTestResults, calAction, calculateTestPass(listOfFailures))
                reportFile.close()
                if calculateTestPass(listOfFailures) ==True: # IF the test has passed go to next step.
                    if 'calibrate' in calAction:
                        calAction="verify"
                    elif 'verify' in calAction:
                        calAction="noise_test"
                    elif 'noise_test' in calAction:
                        calAction=None
                else:
                    if User_interface.instance == "testcenter":  # Cal Failed so pass back fails for DB logging
                        return listOfFailures
                    else:
                        printText("Not contiuing with next stage as failed test points found in current stage.")  # Cal Failed so
                        calAction = None
            elif(calAction == None):
                if User_interface.instance != None and User_interface.instance.selectedInterface == "testcenter":
                    return listOfFailures
                # otherwise go back to menu
                else:
                    calAction = None
            elif 'select' in calAction:
                calAction = None
                myPpmDevice.closeConnection()
                myPpmDevice = None
                calibrationResources["moduleString"] = None
            else:
                raise Exception("calAction \""+str(calAction)+ "\" not recognised")
    except Exception as thisException:
            logging.error(thisException, exc_info=True)
            try:
                dut.close_all()
                myPpmDevice.closeConnection()
            # Handle case where exception may have been thrown before instrument was set up
            except:
                logging.error("DUT connection not closed. Exception may have been thrown before instrument was set up.")
                pass







def create_dut_object():
    # Connect to the module
    while True:
        # If no address specified, the user must select the module to calibrate
        if (calibrationResources["moduleString"] == None):
            deviceString = userSelectDevice(scanFilterStr=scanFilterStr, nice=True, message="Select device for calibration")
            # quit if necessary
            if deviceString == 'quit':
                printText("no module selected, exiting...")
                sys.exit(0)
            else:
                calibrationResources["moduleString"] = deviceString

        try:
            printText("Selected Module: " + calibrationResources["moduleString"])
            myPpmDevice = quarchDevice(calibrationResources["moduleString"])
            break
        except:
            printText("Failed to connect to " + str(calibrationResources["moduleString"]))
            calibrationResources["moduleString"] = None
    serialNumber = myPpmDevice.sendCommand("*SERIAL?")
    success = False
    fixtureId = None
    # Identify and create a power module object
    # If this is an HD PPM
    if ('1944' in serialNumber):
        # is this ppm original or plus version
        # get the FPGA
        FPGAPart = myPpmDevice.sendCommand("read 0xfffe")
        if ('2899' in FPGAPart):
            # create HD Plus Power Module Object
            dut = QTL1944_06(myPpmDevice)
            success = True
        else:
            # create HD Power Module Object
            dut = QTL1944(myPpmDevice)
            success = True
    # Else if this is a Power Analysis Module
    elif ('2098' in serialNumber):
        # this is a Power Analysis Module, we need to detect the fixture
        fixtureId = myPpmDevice.sendCommand("read 0xA102")
        # PCIe x16 AIC Fixture
        if ('2347' in fixtureId):
            dut = QTL2347(myPpmDevice)
            success = True
        ## PCIE Gen 4 SFF Fixture
        if ('2525' in fixtureId):
            dut = QTL2525(myPpmDevice)
            success = True
        ## PCIE Gen 5 SFF Fixture
        if ('2788' in fixtureId):
            dut = QTL2788(myPpmDevice)
            success = True
        ## EDSFF Fixture (E1)
        if ('2673' in fixtureId):
            dut = QTL2673(myPpmDevice)
            success = True
        ## EDSFF Fixture (E3)
        if ('2674' in fixtureId):
            dut = QTL2674(myPpmDevice)
            success = True
        ## Gen5 EDSFF Fixture (E1)
        if ('2887' in fixtureId):
            dut = QTL2887(myPpmDevice)
            success = True
        ## GEN5 EDSFF Fixture (E3)
        if ('2888' in fixtureId):
            dut = QTL2888(myPpmDevice)
            success = True
        # 2-Channel PAM Mezzanine
        if ('2621' in fixtureId):
            dut = QTL2621(myPpmDevice)
            success = True
    # Else if this is a 3 phase AC PAM
    elif ('2582' in serialNumber) or ('2751' in serialNumber) or ('2789' in serialNumber):
        dut = QTL2582(myPpmDevice)
        success = True
    # Else if this is an IEC PAM
    elif ('2843' in serialNumber):
        dut = QTL2843(myPpmDevice)
        success = True
        connectionType = deviceString.split(':')
        connectionName = 'QTL' + serialNumber
        connStr = connectionType[0] + "::" + connectionName
        # myPpmDevice = quarchDevice(calibrationResources["moduleString"], ConType='QIS')
        myPpmDevice = quarchDevice(connStr, ConType='QIS')
        # version = myPpmDevice.sendCommand("$version")
        # spversion = version.split('.')
        # if not (int(spversion[1]) == 26 and int(spversion[2] >= 4) or int(spversion[1] > 26)):
        #    raise SystemError("QIS version must be > 1.26.04, current version "+version)
        dut = QTL2582(myPpmDevice)
        success = True
    if (success == False):
        if fixtureId:
            raise ValueError("ERROR - Serial number '" + fixtureId + "' not recogised as a valid power module")
        else:
            raise ValueError("ERROR - Serial number '" + serialNumber + "' not recogised as a valid power module")
    # If we're in testcenter setup the test
    if User_interface.instance != None and User_interface.instance.selectedInterface == "testcenter":
        # Store the serial number from the DUT scan for logging and verification
        TestCenter.testPoint("Quarch_Internal.StoreSerial", "Serial=" + dut.calObjectSerial);
        idnStr = str(dut.idnStr).replace("\r\n", "|")
        TestCenter.testPoint("Quarch_Internal.StoreDutActualIdn", "Idn=" + idnStr)
    return dut, myPpmDevice



def calculateTestPass(list):
    '''Simple fuction uses to determine if the overall test has passed by looking at the list of test failures '''
    if len(list) == 0:
        return True
    else:
        return False

def setup_logging(logLevel):
    # check log file is present or writeable
    numeric_level = getattr(logging, logLevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % logLevel)
    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s', datefmt='%Y-%m-%d,%H:%M:%S', level=numeric_level)


def show_action_menu(calAction):
    actionList = []
    actionList.append(["Calibrate","Calibrate the power module"])
    actionList.append(["Verify","Verify existing calibration on the power module"])
    actionList.append(["Noise_Test", "Test the noise on the module using QPS"])
    actionList.append(["Select","Select a different power module"])
    actionList.append(["Quit","Quit"])
    calAction = listSelection("Select an action", "Please select an action to perform", actionList, nice=True, tableHeaders=["Option", "Description"], indexReq=True)

    return calAction[1].lower()

# Returns a resource from the previous calibration. This is the mechanism for getting results and similar back to
# a higher level automated script.
def getCalibrationResource (resourceName):
    try:
        return calibrationResources[resourceName]
    except Exception as e:
        printText("Failed to get calibration resource : " +str(resourceName))
        printText("Exception : " + str(e))
        return None

def addOverviewSectionToReportFile(reportFile, listOfTestResults, calAction, result):
    overViewList=[]
    if calAction == "calibrate":
        if result:
            stamp = "CALIBRATION PASSED"
        else:
            stamp = "CALIBRATION FAILED"
    else:
        if result:
            stamp = "VERIFICATION PASSED"
        else:
            stamp = "VERIFICATION FAILED"

    for testResults in listOfTestResults:
        overViewList.append([testResults["title"],testResults["result"],testResults["worst case"]])
    reportFile.write("\n\n"+displayTable(overViewList,tableHeaders=["Title", "Passed", "Worst Case"], printToConsole=False, align="r")+"\n\n" + displayTable(stamp, printToConsole=True))

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

def main(argstring):
    import argparse
    # Handle expected command line arguments here using a flexible parsing system
    parser = argparse.ArgumentParser(description='Calibration utility parameters')
    parser.add_argument('-a', '--action', help='Calibration action to perform', choices=['calibrate', 'verify', 'noise_test'], type=str.lower)
    parser.add_argument('-m', '--module', help='IP Address or netBIOS name of power module to calibrate', type=str.lower)
    parser.add_argument('-i', '--instr', help='IP Address or netBIOS name of calibration instrument', type=str.lower)
    parser.add_argument('-p', '--path', help='Path to store calibration logs', type=str.lower)
    parser.add_argument('-l', '--logging', help='Level of logging to report', choices=['warning', 'error', 'debug'], type=str.lower,default='warning')
    parser.add_argument('-u', '--userMode',  help=argparse.SUPPRESS,choices=['console','testcenter'], type=str.lower,default='console') #Passes the output to testcenter instead of the console Internal Use
    parser.add_argument('-s', '--streamPath', help='Path to store QPS stream', type=str)

    args, extra_args = parser.parse_known_args(argstring)
    # Create a user interface object
    thisInterface = User_interface(args.userMode)
    if extra_args != []:
        printText("failed to Parse the following ARG/s: "+str(extra_args))
    # Call the main calibration function, passing the provided arguments
    return runCalibration(loadAddress=args.instr, calPath=args.path, moduleAddress=args.module, logLevel=args.logging, calAction=args.action, streamPath=args.streamPath)

#Command to run from terminal.
#python -m quarchCalibration -mUSB:QTL1999-01-002 -acalibrate -i192.168.1.210 -pC:\\Users\\sboon\\Desktop\\CalTesting
if __name__ == "__main__":
    main (sys.argv[1:])
    #main(["-anoise_test", "-mUSB:QTL2312-01-035",  "-pC:\\Users\\Public\\Documents\\calibrationReports", "-sQ:\\Production\\Calibration\\NoiseTestStreams"])
    #Example or args parsing
    #The argument do the following, set the action to calibrate, define the IP address of the module, defignt he IP saddress of the calibration instument, set the save location of the calibration report file, and set the logging level to warning. 
    #main (["-acalibrate", "-mTCP:192.168.1.170", "--instrREST:192.168.1.205",  "-pC:\\Users\\Public\\Document\\QuarchPythonCalibration", "-lwarning"])
