# Created by Upendar Gareri

# -*- encoding: UTF-8 -*-
""" Perform some action when receiving a touch event
"""

import sys
import time
import vision_definitions
# Python Image Library
import Image

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import argparse

# Global variable to store the ReactToTouch module instance
ReactToTouch = None
memory = None

class ReactToTouch(ALModule):
    """ A simple module able to react
        to touch events.
    """
    def __init__(self, name):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy to ALTextToSpeech for later use
        self.tts = ALProxy("ALTextToSpeech")

        # Subscribe to TouchChanged event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("TouchChanged",
            "ReactToTouch",
            "onTouched")

    def onTouched(self, strVarName, value):
        """ This will be called each time a touch
        is detected.

        """
        # Unsubscribe to the event when talking,
        # to avoid repetitions
        memory.unsubscribeToEvent("TouchChanged",
                                  "ReactToTouch")
        touched_bodies = []

        for p in value:
            if p[1]:
                touched_bodies.append(p[0])

        # Check which body sensor part is being touched

        if "Head" in touched_bodies:
            self.captureImage()
        elif "RArm" in touched_bodies or "LArm" in touched_bodies:
            self.speak()
        elif "RFoot/Bumper/Right" in touched_bodies or "RFoot/Bumper/Left" in touched_bodies:
            self.walk()
        elif "LFoot/Bumper/Left" in touched_bodies or "LFoot/Bumper/Right" in touched_bodies:
            self.walk()

        memory.subscribeToEvent("TouchChanged",
				"ReactToTouch",
				"onTouched")

    def captureImage(self):
        camProxy = ALProxy("ALVideoDevice")

        # Register a Generic Video Module

        resolution = vision_definitions.kQQVGA
        colorSpace = vision_definitions.kYUVColorSpace
        fps = 5

        videoClient = camProxy.subscribe("python_GVM", resolution, colorSpace, fps)

        # Get a camera image.
        # image[6] contains the image data passed as an array of ASCII chars.
        naoImage = camProxy.getImageRemote(videoClient)

        camProxy.unsubscribe(videoClient)

        # Now we work with the image returned and save it as a PNG  using ImageDraw
        # package.

        # Get the image size and pixel array.
        imageWidth = naoImage[0]
        imageHeight = naoImage[1]
        array = naoImage[6]

        # Create a PIL Image from our pixel array.
        im = Image.fromstring("RGB", (imageWidth, imageHeight), array)

        # Save the image.
        im.save("camImage.png", "PNG")

        im.show()

    def speak(self):
        speech = ALProxy("ALTextToSpeech")
        speech.say("My arm has been touched")

    def walk(self):
        motionProxy  = ALProxy("ALMotion")
        postureProxy = ALProxy("ALRobotPosture")

        # Wake up robot
        motionProxy.wakeUp()
        # Send robot to Stand Zero
    	postureProxy.goToPosture("StandInit", 0.5)
        motionProxy.moveTo(0.25, 0, 0)

        # Go to rest position
    	motionProxy.rest()


ip = "nao.local"
def main(ip, port):
    """ Main entry point
    """
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       ip,          # parent broker IP
       port)        # parent broker port


    global ReactToTouch
    ReactToTouch = ReactToTouch("ReactToTouch")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print
        print "Interrupted by user, shutting down"
        myBroker.shutdown()
        sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="nao.local",
                        help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559,
                        help="Robot port number")
    args = parser.parse_args()
    main(args.ip, args.port)
