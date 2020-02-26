from java.lang import String
import threading
from org.myrobotlab.opencv import OpenCVFilterTranspose
from org.myrobotlab.opencv import OpenCVFilterFaceRecognizer
from org.bytedeco.javacv import IPCameraFrameGrabber
from org.myrobotlab.opencv import MJpegFrameGrabber
from org.myrobotlab.framework import Platform

#############################################################
# This is the Harry script
# Harry is an InMooved powered by a Ras PI2
# Initially we'll start simple
# It will use ProgramAB & Webkit for all interactions with
# the bot.
#############################################################
# All bot specific hardware configuration goes here.
Platform.setVirtual(True)
leftPort = "/dev/ttyACM0"
rightPort = "/dev/ttyACM1"
headPort = leftPort

gesturesPath = "/home/pi/github/pyrobotlab/home/kwatters/harry/gestures"
calibrationPath = "/home/pi/github/pyrobotlab/home/kwatters/harry/calibration.py"
aimlPath = "/home/pi/github/pyrobotlab/home/kwatters/harry"


gesturesPath = "../pyrobotlab/home/kwatters/harry/gestures"
calibrationPath = "../pyrobotlab/home/kwatters/harry/calibration.py"
aimlPath = "../pyrobotlab/home/kwatters/harry"

aimlBotName = "harry"
aimlUserName = "Kevin"
botVoice = "Brian"

# toggle to only load program ab  and skip the inmoov services
startInMoov = True

######################################################################
# helper function help debug the recognized text from webkit/sphinx
######################################################################
def heard(data):
  print "Speech Recognition Data:"+str(data)

######################################################################
#
# MAIN ENTRY POINT  - Start and wire together all the services.
#
######################################################################

# launch the swing gui?
# gui = Runtime.createAndStart("gui", "GUIService");

######################################################################
# Create ProgramAB chat bot ( This is the inmoov "brain" )
######################################################################
harry = Runtime.createAndStart("harry", "ProgramAB")
harry.setPath(aimlPath)
harry.startSession(aimlUserName, aimlBotName)

######################################################################
# Html filter to clean the output from programab.  (just in case)
htmlfilter = Runtime.createAndStart("htmlfilter", "HtmlFilter")

######################################################################
# mouth service, speech synthesis
# mouth = Runtime.createAndStart("i01.mouth", "NaturalReaderSpeech")
# mouth = Runtime.createAndStart("i01.mouth", "MarySpeech")
# mouth.setVoice(botVoice)

# TODO: a better voice?
mouth = Runtime.createAndStart("i01.mouth", "MarySpeech")
mouth.setVoice("cmu-bdl-hsmm")


######################################################################
# the "ear" of the inmoov TODO: replace this with just base inmoov ear?
ear = Runtime.createAndStart("i01.ear", "WebkitSpeechRecognition")
ear.addListener("publishText", python.name, "heard");
ear.addMouth(mouth)

######################################################################
# MRL Routing webkitspeechrecognition/ear -> program ab -> htmlfilter -> mouth
######################################################################
ear.addTextListener(harry)
harry.addTextListener(htmlfilter)
htmlfilter.addTextListener(mouth)

######################################################################
# Start up the inmoov and attach stuff.
######################################################################
i01 = Runtime.createAndStart("i01", "InMoov")
i01.setMute(False)
if startInMoov:
  i01.startAll(leftPort, rightPort)
else:
  i01.mouth = mouth
    
# Harry doesn't have a forward servo, but i'm adding it here as a 
# place holder
forwardServo = Runtime.start("forwardServo","Servo")

######################################################################
# Launch the web gui and create the webkit speech recognition gui
# This service works in Google Chrome only with the WebGui
#################################################################
# webgui = Runtime.createAndStart("webgui","WebGui")

######################################################################
# END MAIN SERVICE SETUP SECTION
######################################################################


######################################################################
# Helper functions and various gesture definitions
######################################################################

# some globals that are used by the gestures..  (they shouldn't be!)
isRightHandActivated = True
isLeftHandActivated = True
isRightArmActivated = True
isLeftArmActivated = True
isHeadActivated = True
isTorsoActivated = True
isEyeLidsActivated = False

i01.loadGestures(gesturesPath)

sleep(1)

i01.loadCalibration(calibrationPath)


# Open CV calibration / resolution
i01.opencv.width=320
i01.opencv.height=240

# now start the webgui
webgui = Runtime.create("webgui", "WebGui")

webgui.autoStartBrowser(False)
webgui.startService()
webgui.startBrowser("http://localhost:8888/#/service/i01.ear")
# TODO: figure out why this doesn't launch chromium....

# gui.undockTab("python")
# gui.undockTab("i01.opencv")


i01.headTracking.pid.setPID("x", 20,0.1,0.1)
i01.headTracking.pid.setPID("y", 20,0.1,0.1)

i01.rest()

# trackHumans()

mixer = Runtime.start("mixer", "ServoMixer")
sleep(1)
# gui.undockTab("mixer")
