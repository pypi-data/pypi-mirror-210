"""
Date: 12/02/2021
Author: Stuart Boon
Version: 1.0

Noise Test
"""
import sys
# Import QPS functions
from quarchpy import qpsInterface, isQpsRunning, startLocalQps, GetQpsModuleSelection, quarchDevice, quarchQPS,qps, requiredQuarchpyVersion
# OS allows us access to path data
from quarchpy.user_interface import *
import os, time
import datetime
from user_interface.user_interface import get_check_valid_calPath
from quarchpy.debug.SystemTest import get_quarchpy_version
import argparse
# TestCenter functions
from quarchpy.utilities import TestCenter
from quarchCalibration.calibrationConfig import *

current_milli_time = lambda: int(round(time.time() * 1000))


def test_main(powerModule, myQpsDevice, close_QPS=False):
    ###HardcoddedVals### TODO Delete these and have all vals passed in.
    # #These now come from dut
    # module_address ="USB:QTL2312-01-035"
    # channel_dict_max_limits={"current +3.3V Max":"250uA", "current +12V Max":"250uA", "current +3.3Vaux Max":"250uA"}
    # test_length = 2 #10
    # averaging_value="4" # 4=16us

    testName = "NoiseTest"
    startTestBlock(testName)
    ###EndHardcoddedVals###
    stream_path = calibrationResources["streamPath"]
    report_path = calibrationResources["calPath"]
    stream_path = get_check_valid_calPath(calibrationResources["streamPath"]) # Should have been checked at start of calUtil but needs checked again incase of changes during script execution such as "change stream dir"
    report_path = get_check_valid_calPath(calibrationResources["calPath"])

    if not isQpsRunning():
        raise Exception("QPS Should be started and device connected before this point.")

    # Record contype, change con type to QPS then at the end of the script change contype back to original.
    DUTserialNumber = powerModule.dut.ConString.split(":")[-1]
    #module_set_up(myQpsDevice, DUTserialNumber) # TODO Module set up is needed for HD to turn power on and set volt to 0.
    test_time = datetime.datetime.now()
    # open report for writing and write system header
    report_path = report_path + "\\"+DUTserialNumber+"_"+test_time.strftime("%d-%m-%y_%H-%M") + "_noise_test.txt"
    # write report file header.
    printText("")
    printText("Report file: " + report_path)
    reportFile = open(report_path, "a+", encoding='utf-8')
    reportFile.write("\n")
    reportFile.write("Quarch Technology Noise Test Report\n")
    reportFile.write("\n")
    reportFile.write("---------------------------------\n")
    reportFile.write("\n")
    reportFile.write("System Information:\n")
    reportFile.write("\n")
    try:
        reportFile.write("QuarchPy Version: " + get_quarchpy_version() + "\n")
    except:

        reportFile.write("QuarchPy Version: unknown\n")
    reportFile.write("Noise Test Time: " + str(test_time.replace(microsecond=0)) + "\n")
    reportFile.write("\n")
    reportFile.write("---------------------------------\n")
    reportFile.write("\n")
    reportFile.flush()

    myQpsDevice.sendCommand("RECord:AVEraging "+powerModule.averaging_value)
    stream_path += "\\tempNoiseTestStream"+time.strftime("%Y-%m-%d-%H-%M-%S", time.gmtime())
    myStream = myQpsDevice.startStream(stream_path)

    start_stream_time = current_milli_time()

    myStream.addAnnotation('Start '+testName, "e"+str(1))
    time.sleep(powerModule.test_length)#+3
    #myQpsDevice.sendCommand("Sig:12v:Volt 0") # sb db debug TODO move this HD specific
    end_test_time = current_milli_time()
    myStream.addAnnotation('End Test'+testName, "e"+str(powerModule.test_length+1))
    time.sleep(1) # lets it stream for 1 seconds
    myStream.stopStream()
    #myStream.hideAllDefaultChannels()
    time.sleep(2) #let the module unload the buffer #TODO change this to poll QPS if stopped streaming
    test_overview = []  # used to write to the report file
    myStats = myStream.get_stats(format="list")
    test_index =0
    all_tests_passed = True
    for row in myStats:
        if row[0]== "Start "+testName:
            row.index('Start '+testName)
            break
        test_index+=1
    for channel_name, max_value in powerModule.channel_dict_max_limits.items():
        #find channel_name index in myTest[0]
        i=myStats[0].index(channel_name)
        channel_unit = myStats[1][i]
        channel_value = myStats[test_index][i] + channel_unit
        channel_value,channel_unit= metric_prefix_converter(channel_value)
        max_value,max_value_unit= metric_prefix_converter(max_value)

        if max_value_unit != channel_unit or channel_value > max_value: #If the units don't match or the limit has been surpassed = Fail
            result = "FAIL"
            passed = False
            all_tests_passed = False
            time.sleep(0.1)
        else:
            result = "PASS"
            passed = True
            time.sleep(0.1)
        startTestBlock(channel_name)
        logSimpleResult(channel_name+" Channel Value:"+str(channel_value)+channel_unit+"  Max Value:"+ str(max_value)+max_value_unit, passed)
        endTestBlock()
        test_overview.append([channel_name, result, channel_value, max_value])
    # TODO do the same for min linits if any for channel_name, max_value in channel_dict_min_limits.items():
    printToConsole = True if(User_interface.instance.selectedInterface == "console") else False
    resultsTable = displayTable(tableData=test_overview, tableHeaders=("Test Name", "Result", "Value", "Limit"), printToConsole=printToConsole)
    reportFile.write(resultsTable)
    reportFile.flush()
    reportFile.close()
    endTestBlock()
    #Comment this out if you don't want to view recordings of failed tests
    if all_tests_passed == True: close_QPS =True #This should take a screenshot and save it to the same dir as the report file.
    if close_QPS == False:
        showDialog(title="Quit QPS?", message="Continue when you are you ready to close QPS.")
        close_QPS=True
    qps.closeQps()
    return test_overview

def metric_prefix_converter(input_str):
    """
    Convert a value to it's base unit

    :param input_str: String, value to change (E.g.  1.5432kW)
    :return: Float, String: Input value converted to base unit, base unit of measurement.
    :raise ValueError : If there was a float() conversion error.
    """
    prefixes = {"y": 1e-24, "z": 1e-21, "a": 1e-18, "f": 1e-15, "p": 1e-12,
              "n": 1e-9, "u": 1e-6, "m": 1e-3, "c": 1e-2, "d": 0.1,
              "h": 100, "k": 1000, "M": 1e6, "G": 1e9, "T": 1e12, "P": 1e15,
              "E": 1e18, "Z": 1e21, "Y": 1e24}
    if not input_str:
        # Catching "None" clause
        logging.error(f"Couldn't convert value to base unit : {input_str}")
        raise ValueError(f"Invalid Input str: {input_str}")
    ret_value = None
    ret_unit = None
    input_prefix = None
    # Loop through item keys
    for key in prefixes:
        # if key in value
        if key in input_str:
            # record index of key
            unit_index = input_str.index(key)
            # Get the numerical values prior to the unit
            ret_value = input_str[:unit_index]
            # get the key..?
            input_prefix = input_str[unit_index]
            # get the base unit
            ret_unit = input_str[unit_index + 1:]
            break
    else:
        # no known unit was found in input string
        # find if there's a character unit in the input
        base_unit = None
        for index, character in enumerate(input_str):
            if character.isalpha():
                ret_value = input_str[:index]
                ret_unit = input_str[index:]
                break
        else:
            # No character unit - Potential for error:
            ret_value = input_str
            ret_unit = ""
    try:
        # Try converting value input to float
        value = float(ret_value)
        # If there was an available base unit conversion, convert the value
        if input_prefix:
            value = value * prefixes[input_prefix]
        return value, ret_unit
    except ValueError as err:
        # If there was an error trying to convert input to float, then raise exception and log the error
        logging.error(f"Couldn't convert value to base unit : {input_str}")
        raise err

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')





if __name__ == "__main__":
    thisInterface = User_interface("console")
    test_main (sys.argv[1:])
    #main(["-h"])
    #main (["-mUSB::QTL1999-06-127", "-pQ:\\Production\\Calibration\\pythoncals\\NoiseTests", "-v50", "-c250","--channel_list",  "3v3", "--channel_list", "3v3 aux", "--channel_list", "12v", "-uconsole", "--close_qps", "False"])
    #PAM FIXTURE
    #main(["-v50", "-c250","--channel_list", "3.3v", "--channel_list", "3.3v aux", "--channel_list", "12v", "-uconsole", "--close_qps","True"])
    #HDPPM
    #main(["-v3.3333", "-c3000","--channel_list", "5v","--channel_list", "12v", "-uconsole", "--close_qps","True"])

