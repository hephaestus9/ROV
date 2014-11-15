import pygame
import threading
import time
from . import Comms


class Joystick():

    def __init__(self):
        pygame.init()
        self.joystick_count = pygame.joystick.get_count()
        self.joysticks = []
        self.joystickNames = []
        self.joystick = None

    def joystickStatus(self):
        axes = self.getCurrentJoystickAxes()
        buttons = self.getCurrentJoystickButtons()
        hats = self.getCurrentJoystickHats()

        def getJoystickStatus(joystick, axes, buttons, hats):
            comms = Comms.Comms()
            comms.sendSetup()
            axesPrev = {}
            buttonsPrev = {}
            hatsPrev = {}

            for i in range(axes):
                axesPrev[i] = joystick.get_axis(i)
            for i in range(buttons):
                buttonsPrev[i] = joystick.get_button(i)
            for i in range(hats):
                hatsPrev[i] = joystick.get_hat(i)

            while True:
                time.sleep(0.005)
                for event in pygame.event.get():  # User did something
                    # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
                    for i in range(axes):
                        axis = joystick.get_axis(i)
                        if axis != axesPrev[i]:
                            comms.sendUDP(str({"Axis": i, "value": axis}))
                            # print((str({"Axis": i, "value": axis})))
                            axesPrev[i] = axis

                    for i in range(buttons):
                        button = joystick.get_button(i)
                        if button != buttonsPrev[i]:
                            comms.sendUDP(str({"Button": i, "value": button}))
                            buttonsPrev[i] = button

                    for i in range(hats):
                        hat = joystick.get_hat(i)
                        if hat != hatsPrev[i]:
                            comms.sendUDP(str({"Hat": i, "value": hat}))
                            hatsPrev[i] = hat

        joystick_thread = threading.Thread(target=getJoystickStatus, args=(self.joystick, axes, buttons, hats))
        joystick_thread.daemon = True
        joystick_thread.start()

    def getJoystickCount(self):
        return self.joystick_count

    def getJoysticks(self):
        # For each joystick:
        for i in range(self.joystick_count):
            self.joysticks.append(pygame.joystick.Joystick(i))

        return self.joysticks

    def getJoystickNames(self):
        if self.joysticks == []:
            self.getJoysticks()

        for joystick in self.joysticks:
            self.joystickNames.append(joystick.get_name())

        return self.joystickNames

    def initializeJoystick(self, joystick):
        self.joystick = joystick
        self.joystick.init()

    def getCurrentJoystickName(self):
        try:
            return self.joystick.get_name()
        except:
            return "No joystick set."

    def getCurrentJoystickAxes(self):
        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        try:
            axes = self.joystick.get_numaxes()
            return axes
        except:
            return "No joystick set."

    def getCurrentJoystickButtons(self):
        try:
            buttons = self.joystick.get_numbuttons()
            return buttons
        except:
            return "No joystick set."

    def getCurrentJoystickHats(self):
        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        try:
            hats = self.joystick.get_numhats()
            return hats
        except:
            return "No joystick set."
