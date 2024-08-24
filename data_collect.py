import csv
import time
from smbus2 import SMBus
import serial
import select
import sys

# configurations
serialPort = "/dev/ttyACM0"
baudRate = 9600
byteSize = 8
parityType = serial.PARITY_NONE
stopBits = serial.STOPBITS_ONE
sensorAddress = 0x28
leftBusNum = 1
rightBusNum = 3

# Dictates how many readings to take or how long to take readings for
readingMode = input("Take readings based on time (T) or number of readings (N): ").upper()
readingTime = 0
readings = 0
if  readingMode == "N":
    readings = int(input("Specify number of readings to take: "))
elif readingMode == "T":
    readingTime = float(input("Enter amount of time to take readings for (s): "))
else:
    quit()

# Open serial port w/ above configs
ser = serial.Serial()
while(not ser.is_open): #continuously try to connect to port until it succeeds
    print("Attempting connection ", end='')
    ser = serial.Serial(serialPort, baudrate=baudRate, bytesize=byteSize, parity=parityType,stopbits=stopBits)
    print(">", end='')
print("")
print("Connection successful. Connected to " + ser.name)
print("Connection settings: " + str(ser.get_settings()))

#open i2c buses
leftbus = SMBus(leftBusNum)
rightbus = SMBus(rightBusNum)

def calcPressure(data):
    digital = data[0]<<8 | data[1]
    return (digital - 1638)*100.0/13108.0

def getData():
    textOut = []
    ser.write('read\r\n'.encode("utf-8")) #sends command to print
    while(ser.in_waiting == 0): #wait until data available
        pass
    dataOut = []
    badFlag = False
    for i in range(6):
        line = ser.readline().decode("utf-8")
        textOut.append(line)
        if line.startswith("Error"): #skips errors
            badFlag = True
            break
        if(not i == 0):
            if(i == 5):
                dataOut.append(float(line.split(":")[1].strip()))
            else:
                dataOut.append(float((line.split(":")[1]).split(",")[1]))
    data = leftbus.read_i2c_block_data(40,0,2)
    leftPress = calcPressure(data)
    data = rightbus.read_i2c_block_data(sensorAddress,0,2)
    rightPress = calcPressure(data)
    textOut.append("Left Pressure Sensor (psi): " + str(leftPress))
    textOut.append("Right Pressure Sensor (psi): " + str(rightPress))
    dataOut.append(leftPress)
    dataOut.append(rightPress)
    return [textOut, dataOut]

while select.select([sys.stdin],[],[],0) == ([],[],[]):
    [textOut,dataOut] = getData()
    for line in textOut:
        print(line)


with open('data.csv', 'w', newline='') as f: #setup csv writer
    writer = csv.writer(f)
    writer.writerow(["Time (s)", "02 Purity (%)", "Flow Rate (lpm)", "Temperature (C)", "Relative Humidity (%)", "Pressure (psi)"]) #header/labels

    start = time.time() #time at beginning of data collection
    j = 0
    while (j < readings and readingMode == "N") or (time.time() - start < readingTime and readingMode == "T"):
        textOut = []
        current = (time.time() -start)
        [textOut,csvRow] = getData()
        textOut.insert(0,current)
        csvRow.insert(0,current)
        textOut.append(csvRow)
        for line in textOut:
            print(line)
         
        writer.writerow(csvRow)
        j += 1
ser.close()
leftbus.close()
rightbus.close()
