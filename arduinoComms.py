import serial
import time
import numpy as np
from func_timeout import FunctionTimedOut, func_timeout

class arduinoComms:
    def __init__(self, port, baud, exit_event, sendTarget, targetStep1, targetStep2, targetStep3, targetStep4, currentStep1, currentStep2, currentStep3, currentStep4):
        self.port = port
        self.baud = baud
        self.exit_event = exit_event
        self.sendTarget = sendTarget
        self.targetStep1 = targetStep1
        self.targetStep2 = targetStep2
        self.targetStep3 = targetStep3
        self.targetStep4 = targetStep4
        self.currentStep1 = currentStep1
        self.currentStep2 = currentStep2
        self.currentStep3 = currentStep3
        self.currentStep4 = currentStep4

        #declared constants
        self.serial_delay = 0.001
    
    def sendString(self, ser, input):
        try:
            comma_separated_string = ",".join(map(str, input)) + "\n"
            ser.write(comma_separated_string.encode())
        except:
            print('error with sending string')

    def readString(self, ser):
        try:
            response = ser.readline().decode().strip()
            responseList = response.strip().split(',')
            integer_list = [int(element) for element in responseList]
            return integer_list
        except:
            print('error reading string from arduino')
            return [0, 0, 0, 0]

    def updateMotors(self):
        #send motor values
        if self.sendTarget.value:
            self.sendTarget.value = False
            targetStepString = [0, 0, 0, 0]
            targetStepString[0]= self.targetStep1.value
            targetStepString[1]= self.targetStep2.value
            targetStepString[2]= self.targetStep3.value
            targetStepString[3]= self.targetStep4.value
            self.sendString(targetStepString)

        #read encoder values
        receivedValues = self.readString()
        self.currentStep1.value = receivedValues[0]
        self.currentStep2.value = receivedValues[1]
        self.currentStep3.value = receivedValues[2]
        self.currentStep4.value = receivedValues[3]

    def maintainCommunications(self):
        ser=serial.Serial(self.port, self.baud, timeout=1)
        print('serial connected')
        
        while not self.exit_event.is_set():
            try:
                #send motor values
                if self.sendTarget.value:
                    self.sendTarget.value = False
                    targetStepString = [0, 0, 0, 0]
                    targetStepString[0]= self.targetStep1.value
                    targetStepString[1]= self.targetStep2.value
                    targetStepString[2]= self.targetStep3.value
                    targetStepString[3]= self.targetStep4.value
                    self.sendString(ser, targetStepString)
                    time.sleep(0.01)
                    receivedValues = self.readString(ser)
                    #return value is not needed, it alters the sendTarget value!
                    self.passChecker(targetStepString, receivedValues)
                    # print('wrote some values')

                #read encoder values
                try:
                    receivedValues = self.readString(ser)
                    self.currentStep1.value = receivedValues[0]
                    self.currentStep2.value = receivedValues[1]
                    self.currentStep3.value = receivedValues[2]
                    self.currentStep4.value = receivedValues[3]
                except KeyboardInterrupt:
                    self.exit_event.set()
                except FunctionTimedOut:
                    print('serial read timed out')
                except:
                    pass
            except KeyboardInterrupt:
                self.exit_event.set()
        
        ser.close()
        print('closing arduino Comms gracefully')

    
    def passChecker(self, targetStepString, receivedValues):
        # print('pass checker values:')
        # print(targetStepString)
        # print(receivedValues)
        #margin of error, should be zero ideally
        margin = 5
        #checks if the values were written correctly, if incorrect, resends
        if (abs(targetStepString[0]-receivedValues[0])>margin):
            # print('target step was written incorrectly!')
            self.sendTarget.value = True
            return False
        if (abs(targetStepString[1]-receivedValues[1])>margin):
            # print('target step was written incorrectly!')
            self.sendTarget.value = True
            return False
        if (abs(targetStepString[2]-receivedValues[2])>margin):
            # print('target step was written incorrectly!')
            self.sendTarget.value = True
            return False
        if (abs(targetStepString[3]-receivedValues[3])>margin):
            # print('target step was written incorrectly!')
            self.sendTarget.value = True
            return False
        
        #if it reaches here, then the sent and received steps agree within margin
        return True


        