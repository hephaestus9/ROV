# -*- coding: utf-8 -*-
import Adafruit_BBIO.UART as uart
import socket
import serial
import threading
import ast


class ROV():

    def __init__(self):
        self.UDP_IPReceive = ""
        self.UDP_IPSend = "192.168.1.19"
        self.UDP_PORT_RECV = 5005
        self.UDP_PORT_SEND = 5006

        self.receiveSock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
        self.receiveSock.bind((self.UDP_IPReceive, self.UDP_PORT_RECV))

        self.sendSock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP

        uart.setup("UART2")  # Sensor Board
        self.telemetry = serial.Serial(port="/dev/ttyO2", baudrate=115200)
        self.telemetry.close()
        self.telemetry.open()

        uart.setup("UART1")  # Motor Driver Board
        self.thrusters = serial.Serial(port="/dev/ttyO1", baudrate=115200)
        self.thrusters.close()
        self.thrusters.open()

        self.vert = 0
        self.port = 0
        self.stbd = 0
        self.port1 = 0
        self.stbd1 = 0
        self.port2 = 0
        self.stbd2 = 0

        self.receiver()
        self.telemetryStatus()

    def telemetryStatus(self):
        def getTelemetryStatus(serialPort, processData):
            while True:
                line = serialPort.readline()
                processData(line)

        receiver_thread = threading.Thread(target=getTelemetryStatus, args=(self.telemetry, self.processData))
        receiver_thread.daemon = True
        receiver_thread.start()

    def processData(self, sensorData):
        try:
            sensorData = sensorData.split(":")
            endData = sensorData[9]
            sensorData[9] = endData[:-2]
            sensorData = str({"sensor stick": {"G_Dt": sensorData[0],
                          "Accel": [sensorData[1], sensorData[2], sensorData[3]],
                          "Magnetom": [sensorData[4], sensorData[5], sensorData[6]],
                          "Gyro": [sensorData[7], sensorData[8], sensorData[9]]}, "depth sensor": [], "altimeter": []})
            # print(sensorData)
            self.sendUDP(sensorData)
        except:
            self.sendUDP(str(sensorData))

    def sendUDP(self, sensorData):
        # print(sensorData)
        self.sendSock.sendto(sensorData, (self.UDP_IPSend, self.UDP_PORT_SEND))

    def receiver(self):
        def receiverListen(sock, stringCreator):
            while True:
                data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                # print(("received message:", data))
                stringCreator(data)

        receiver_thread = threading.Thread(target=receiverListen, args=(self.receiveSock, self.createCommandString))
        receiver_thread.daemon = True
        receiver_thread.start()

    def createCommandString(self, data):
        data = ast.literal_eval(data)
        for key, val in list(data.items()):
            if "Axis" in key:
                # For Logitech Extreme 3D: Axis 0 - Lateral, Axis 1 - Fwd/Rev, Axis 2 - Turn, Axis 3 - Elevation
                if data['Axis'] == 0:  # Lateral
                    pass  # can't do lateral right now'
                elif data['Axis'] == 1:  # Fwd -, Rev +
                    self.port1 = int(round(data['value'] * 255))
                    self.stbd1 = int(round(data['value'] * 255))
                elif data['Axis'] == 3:  # Turn ***Sent from Linux: 2, Sent from Windows: 3
                    if data['value'] < 0:  # Turn Left
                        self.port2 = int(round(-1 * data['value'] * 255))
                        self.stbd2 = int(round(data['value'] * 255))
                    else:  # Turn Right
                        self.port2 = int(round((-1 * data['value']) * 255))
                        self.stbd2 = int(round(data['value'] * 255))
                elif data['Axis'] == 2:  # Vert Up -, Dwn + ***Sent from Linux: 3, Sent from Windows: 2
                    self.vert = int(round(data['value'] * 255))
                else:
                    print(('Error in Axis Data!'))

                if self.port1 > self.port2:
                    # print(("port1 > port2: "))
                    # print((self.port1, self.port2))
                    if self.port2 >= 0 and self.port1 > 0:
                        port = self.port1 + self.port2
                        if port > 255:
                            port = 255
                        self.port = port
                    elif self.port2 < 0 and self.port1 > 0:
                        self.port = self.port1 + self.port2
                    elif self.port1 <= 0 and self.port2 < 0:
                        port = self.port2 + self.port1
                        if port < -255:
                            port = -255
                        self.port = port
                    else:
                        self.port = self.port2 - self.port1

                elif self.port2 > self.port1:
                    # print(("port2 > port1: "))
                    # print((self.port2, self.port1))
                    if self.port1 >= 0 and self.port2 > 0:
                        port = self.port2 + self.port1
                        if port > 255:
                            port = 255
                        self.port = port
                    elif self.port1 < 0 and self.port2 > 0:
                        self.port = self.port2 + self.port1
                    elif self.port2 <= 0 and self.port1 < 0:
                        port = self.port1 + self.port2
                        if port < -255:
                            port = -255
                        self.port = port
                    else:
                        self.port = self.port1 - self.port2

                elif self.port1 == self.port2:
                    self.port = self.port1
                else:
                    print(("There is a problem in the way port thrust is being calculated!"))

                if self.stbd1 > self.stbd2:
                    # print(("stbd1 > stbd2: "))
                    # print((self.stbd1, self.stbd2))
                    if self.stbd2 >= 0 and self.stbd1 > 0:
                        stbd = self.stbd1 + self.stbd2
                        if stbd > 255:
                            stbd = 255
                        self.stbd = stbd
                    elif self.stbd2 < 0 and self.stbd1 > 0:
                        self.stbd = self.stbd1 + self.stbd2
                    elif self.stbd1 <= 0 and self.stbd2 < 0:
                        stbd = self.stbd2 + self.stbd1
                        if stbd < -255:
                            stbd = -255
                        self.stbd = stbd
                    else:
                        self.stbd = self.stbd2 - self.stbd1

                elif self.stbd2 > self.stbd1:
                    # print(("stbd2 > stbd1: "))
                    # print((self.stbd2, self.stbd1))
                    if self.stbd1 >= 0 and self.stbd2 > 0:
                        stbd = self.stbd2 + self.stbd1
                        if stbd > 255:
                            stbd = 255
                        self.stbd = stbd
                    elif self.stbd1 < 0 and self.stbd2 > 0:
                        self.stbd = self.stbd2 + self.stbd1
                    elif self.stbd2 <= 0 and self.stbd1 < 0:
                        stbd = self.stbd1 + self.stbd2
                        if stbd < -255:
                            stbd = -255
                        self.stbd = stbd
                    else:
                        self.stbd = self.stbd1 - self.stbd2

                elif self.stbd1 == self.stbd2:
                    self.stbd = self.stbd1
                else:
                    print(("There is a problem in the way stbd thrust is being calculated!"))

                command = str(self.vert) + ', ' + str(self.port) + ', ' + str(self.stbd) + '\n'
                self.sendThrusterCommand(command)

            elif "Button" in key:
                pass

            elif "Hat":
                pass

            else:
                print(("Error in Data Keys!"))

    def sendThrusterCommand(self, command):
        if self.thrusters.isOpen():
            # print((command))
            self.thrusters.write(command)
        else:
            print(('Communication Error! - sendThrusterCommand'))
