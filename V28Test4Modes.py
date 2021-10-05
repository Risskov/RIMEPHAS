import pygame
import pygame.freetype
import numpy as np
import random
import time
import threading
import multiprocessing as mp
import subprocess
import socket
#from pydub import AudioSegment as AS
from moviepy.editor import VideoFileClip

pygame.init()

import dispenser            #dispenser.py
import stattracker          #stattracker.py
from scrollingtext import * #scrollingtext.py
import LEDs                 #LEDs.py
import trackeduser          #trackeduser.py
import showimages           #showimages.py
import facetracking as ft   #facetracking.py
import sounds               #sounds.py
from images import *        #images.py
import clientSetup          #clientSetup.py
import speechInOut          #speechInOut.py
import eyeAngles            #eyeAngles.py
from wizardOfOz import *    #wizardOfOz.py
from logFunction import logging
import RPi.GPIO as GPIO
#import Adafruit_GPIO.SPI as SPI
from irSensorClass import irSensor

##########  Settings  ##########
testMode = 0         # 0) normal  1) logo only   2) speech+logo   3) eyes+logo   4) speech+eyes+logo
reminder30 = False    # say "remember to rub your hands for 30 seconds"
showSubtitles = True
welcomeText = True   # show "Welcome to" above SDU logo
autoSwitchModes = False
msBetweenModes = 60000 * 1

logToServer = False # send usage statistics to server (set IP in client.py)
windowedFaceTracking = True # track faces in smaller area(s) but higher resolution (res in facetracking and eyeAngles must match)
faceTrackFunction = ft.faceTracking if windowedFaceTracking else ft.faceTrackingWhole
LANGUAGE = "en-US" # en-US or da-DK
isOnline = True # is connected to internet
eyeDesign = "normal" # normal or monster eyes
topOption = 0 # show eyes (0) or images (1)
wizardOfOz = False
showScrollingImages = False
showFaceMask = False
largeScreen = True
size = (800,480)
largeSize = (800,1280)
if largeScreen:
    screenSize = largeSize
    moveScreen = (largeSize[0]-size[0])/2
else:
    screenSize = size
    moveScreen = 0

WHITE = (255,255,255)
BACKGROUND = WHITE

########## Load sounds ##########
sounds_EN, sounds_DA = sounds.loadSounds()

########## Functions ##########
# Check if connected to internet
def checkInternet():
    IP_address=socket.gethostbyname(socket.gethostname())
    if IP_address=="127.0.0.1":
        return False
    else:
        return True

def showButtons():
    screen.blit(yesbutton, (720,0))
    screen.blit(nobutton, (0,0))

def wait(ms):
    pygame.time.wait(ms)

def blitImages(left, right):
    screen.blit(left, (0,0))
    screen.blit(right, (400,0))

def playVideo():
    clip = VideoFileClip(f'videos/{eyeDesign}video.mp4')#, target_resolution=(480,800))
    clip = clip.volumex(0.05)
    clip.preview(fullscreen = True)

# Draw the pupils on the eyes
def drawPupils():
    pupilposL = (centerL[0]+pupils.pupilL, centerL[1]-pupils.pupilV)
    pupilposR = (centerR[0]+pupils.pupilR, centerR[1]-pupils.pupilV)
    screen.blit(pupil, pupilposL)
    screen.blit(pupil, pupilposR)

def drawMonsterPupils():
    centerLmonster = (158-43, 218-50)
    centerMmonster = (390-25, 250-27)
    centerRmonster = (640-43, 222-50)
    pupilposL = (centerLmonster[0]+pupils.pupilL, centerLmonster[1]-pupils.pupilV)
    pupilposR = (centerRmonster[0]+pupils.pupilR, centerRmonster[1]-pupils.pupilV)
    pupilposM = (centerMmonster[0]+int((pupils.pupilL+pupils.pupilR)/2), centerMmonster[1]-pupils.pupilV)
    screen.blit(monsterpupil, pupilposL)
    screen.blit(monsterpupil, pupilposR)
    screen.blit(monsterpupilsmall, pupilposM)

########## Text-to-Speech function ##########
def speech_out(index):
    if LANGUAGE == "da-DK":
        sounds = sounds_DA
    else:
        sounds = sounds_EN
    pygame.mixer.init()
    pygame.mixer.music.load(sounds[index])
    pygame.mixer.music.play()
    if largeScreen:
        global textList
        textList = createTextSurface(finalSurface, index, top_screen_height, top_screen_width, wizardOfOz, LANGUAGE)
    while pygame.mixer.music.get_busy():
        pass

########## Main interaction function going through interaction items to be executed ##########
def interaction(*items):
    global textList, show_buttons, state, interactionWait
    if wizardOfOz:
        for item in items:
            speech_out
    else:
        skip = False
        for item in items:
            if item == "nudge":
                speech_out(8+items[1])
            elif item == "30s":
                rand = 1
                if rand: speech_out(10)
                else: speech_out(11)
            elif item == "joke":
                speech_out(11+items[1])
                wait(2000)
                speech_out(12+items[1])
            elif item == "sanitizer":
                if len(items)<=1:
                    skip = interactionQuestion(0)
                else: skip = interactionQuestion(0)
            elif item == "video" and not skip:
                interactionQuestion(1)
            elif item == "monster":
                global eyeDesign, state
                speechNode.speech_in(items[0], items[1], LANGUAGE, isOnline)
                if speechNode.yes_detected:
                    eyeDesign = items[0]
                    state = NORMALSTATE
                elif speechNode.no_detected:
                    eyeDesign = items[1]
                    state = NORMALSTATE
            elif item == "novideo":
                skip = interactionQuestion(3)
            textList = []
            if threadevent.is_set(): break
    threadevent.clear()
    if interactionWait: state = WAITSTATE
    print("Flow ended")

########## Interaction function for two-way communication ##########
def interactionQuestion(question):
    if question == 3:
        novideo = True
        question = 0
    else: novideo = False
    global show_buttons, show_hand_detect
    skip = False
    lastNumberOfActivations = disp.numberOfActivations # reset this if multiple questions?
    speech_out(question)
    i = 0
    skipit = 0

    while not threadevent.is_set():
        listenthread = threading.Thread(target=speechNode.speech_in, args=("yes","no", LANGUAGE, isOnline))
        listenthread.start()
        while listenthread.is_alive():
            if speechNode.yes_detected or speechNode.no_detected: break
            if disp.numberOfActivations != lastNumberOfActivations:
                if reminder30: speech_out(10)
                skipit = 1
                break
        if skipit:
            skipit = 0
            break
        if speechNode.yes_detected:
            pygame.event.post(happyevent)
            speech_out(question+2)
            if question == 0:
                if novideo:
                    iwait = 200
                    while iwait:
                        if disp.numberOfActivations != lastNumberOfActivations:
                            if reminder30: speech_out(10)
                            break
                        iwait -= 1
                        if iwait < 1:
                            break
                else:
                    print("video")
                    wait(2000)
                break
            else:
                global state
                state = VIDEOSTATE
                wait(35000)
                break
        elif speechNode.no_detected:
            speech_out(6)
            skip = True
            break
        elif question == 0 and disp.numberOfActivations != lastNumberOfActivations:
            if novideo:
                speech_out(10)
            else: wait(2000)
            break
        elif question == 1:
            speech_out(6)
            break
        else:
            #wait(2000)
            #speech_out(7)
            skip = True
            break
    show_hand_detect = False
    print("Interaction ended")
    return skip

########## Set up speech recognition and interaction globals ##########
show_hand_detect = False

show_buttons = False
interactionWait = False #Indicate if waiting between interactions

offset = 800-170-100
eyeL = pygame.Rect(100, 210, 170, 170)
eyeR = pygame.Rect(offset, 210, 170, 170)
centerL = (185-30+10, 295-30)
centerR =(offset+85-30-10,295-30)
buttonL = pygame.Rect(0,0,100,70)
buttonR = pygame.Rect(800-100,0,100,70)

########## Events ##########
BLINKEVENT = pygame.USEREVENT + 1
NORMALEVENT = pygame.USEREVENT + 2
HAPPYEVENT = pygame.USEREVENT + 3
HAPPYSTARTEVENT = pygame.USEREVENT + 4
QUESTIONEVENT = pygame.USEREVENT + 5
INTERACTIONEVENT = pygame.USEREVENT + 6
GAZEEVENT = pygame.USEREVENT + 7
MONSTERBLINKEVENT = pygame.USEREVENT + 8
PHOTOEVENT = pygame.USEREVENT + 9
LOOKEVENT = pygame.USEREVENT + 10
MODESWITCHEVENT = pygame.USEREVENT + 11
happyevent = pygame.event.Event(HAPPYSTARTEVENT)
questionevent = pygame.event.Event(QUESTIONEVENT)

########## States ##########
NORMALSTATE = 0
BLINKSTATE = 1
WINKSTATE  = 2
HAPPYSTATE = 3
CONFUSEDSTATE = 4
VIDEOSTATE = 5
BLINKSTATE2 = 6
HAPPYSTATE2 = 7
MENUSTATE = 8
COLORSTATE = 9
MONSTERSTATE = 10
MONSTERBLINKSTATE = 11
MONSTERBLINKSTATE2 = 12
MONSTERBLINKSTATE3 = 13
GRAPHSTATE = 14
WAITSTATE = 15
TESTSTATE = 16
state = NORMALSTATE

textList = []
if __name__ == '__main__':
    # Initialize interprocess communication
    if not wizardOfOz:
        receiver, sender = mp.Pipe(True)
        mp.set_start_method('spawn',force=True)
        tracking_proc = mp.Process(target=faceTrackFunction, args=(sender,))
        tracking_proc.start()
        logging("activation_count.txt", "Device started")
    else:
        logging("testlog.txt", "Device started")
        sh = ft.Snapshot()

    if not largeScreen:
        subprocess.run(["xinput", "map-to-output", "8", "DSI-1"])
    #else:
    #    subprocess.run(["xinput", "map-to-output", "8", "HDMI-1"])

    if isOnline and not checkInternet():
        isOnline = False

    # Client setup
    if logToServer and isOnline:
        client = clientSetup.Client()
        print("Client connected")

    # Initialize dispenser
    disp = dispenser.Dispenser()
    disp.init_GPIO()
    # Initialize LEDs
    leds = LEDs.LEDinit()
    disp.gelUpdate()
    # Initialize IR hand sensors
    #numSensors = 2
    #sensorThreshold = 1.5
    #irSensors = irSensor(numSensors, sensorThreshold)
    #irSensors.initSensors()
    pygame.time.set_timer(BLINKEVENT, 10000, True)
    monsterblinks = [monsterblinkL, monsterblinkM, monsterblinkR]

    # Initialize interaction variables
    flow = threading.Thread(target=interaction)
    threadevent = threading.Event() #Used to terminate interaction thread
    trackID = 0 #ID of closest person
    altTrackID = 0 #ID of other random person
    gazeAtClosest = True
    pygame.time.set_timer(GAZEEVENT, 8000, True) #Start gaze event
    videoKeys = [] #IDs of people present at last video showing
    prevKeys = [] #IDs of people present last iteration
    prevInteraction = 0 #What interaction scenario was last run
    interactionIndex = 0 #What interaction was last run if repeat interaction scenario
    lastNumberOfActivations = 0 #Activation counter last iteration
    peopleAmount = 1 #len(trackedList)
    frequency = 1    #from trailing_five
    interactionItems = [] #Interaction stages
    runInteraction = False #Turn on/off interactions (r button)

    # Initialize nodes from other classes
    st = stattracker.StatTracker()
    speechNode = speechInOut.Speech(threadevent)
    pupils = eyeAngles.EyeAngles(windowedFaceTracking)

    oldNumberOfPeople = 0 #People counter last iteration
    numberOfPeople = 0 #People counter this iteration

    if largeScreen:
        ## Timer bubbles settings ##
        showPhoto = False #Show photo of person who used dispenser
        photoTimer = 0
        BubbleUpdate = 5 #Hz of trackeduser bubble update
        bubbles = []
        hScale = 1.2
        movePupilLeft = True
        if topOption == 2:
            pygame.time.set_timer(LOOKEVENT, 10000, True)
            pupils.pupilV = -60
        if showScrollingImages: showimages.imagesInit("images/info/") #Set up infographic images
    else:
        hScale = 1.0

    # Set up screen and misc
    pygame.mouse.set_visible(False) #Hide mouse from GUI
    clock = pygame.time.Clock()
    screen = pygame.Surface(size) #Initialize screen
    finalSurface = pygame.display.set_mode(screenSize)#, pygame.NOFRAME) #Final screen because large screen
    pygame.display.toggle_fullscreen()
    top_screen_height = int(size[1]*hScale)
    top_screen_width = largeSize[0]

    # Set up text
    myfont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 20)
    bubblefont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 30)
    bigfont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 60)

    yes_rect = pygame.Rect(100-50, top_screen_height+590, 170, 70)
    no_rect = pygame.Rect(offset+50, top_screen_height+590, 170, 70)
    ja_text, _ = bigfont.render("Ja", (0,0,0))
    nej_text, _ = bigfont.render("Nej", (0,0,0))

    welcomefont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 80)
    welcome_text, _ = welcomefont.render("Welcome to", (0,0,0))

    done = False
    start = time.time()
    while not done:
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            # Keyboard events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("ESC")
                    done = True
                elif event.key == pygame.K_r:
                    pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                    runInteraction = not runInteraction
                    print("Run: ", runInteraction)
                elif event.key == pygame.K_o:
                    turnOffDispenser = not turnOffDispenser
                    print(turnOffDispenser)
                elif event.key == pygame.K_a:
                    disp.numberOfActivations += 1
                    print("Activation!")
                elif event.key == pygame.K_f:
                    if frequency == 1: frequency = 10
                    else: frequency = 1
                    print("Frequency: ", frequency)
                elif event.key == pygame.K_p:
                    if peopleAmount == 1: peopleAmount = 10
                    else: peopleAmount = 1
                    print("Number of people: ", peopleAmount)
                elif event.key == pygame.K_v:
                    state = VIDEOSTATE
                elif event.key == pygame.K_t:
                    testMode = (testMode + 1) % 5
                    print("Test mode: ", testMode)

                    if testMode == 0: mode_text, _ = welcomefont.render("Normal", (0,0,0))
                    if testMode == 1: mode_text, _ = welcomefont.render("Logo only", (0,0,0))
                    if testMode == 2: mode_text, _ = welcomefont.render("Speech", (0,0,0))
                    if testMode == 3: mode_text, _ = welcomefont.render("Eyes", (0,0,0))
                    if testMode == 4: mode_text, _ = welcomefont.render("Eyes and speech", (0,0,0))
                    finalSurface.fill(BACKGROUND)
                    finalSurface.blit(mode_text, ((top_screen_width-mode_text.get_width())/2,top_screen_height))
                    pygame.display.flip()
                    wait(2000)
                elif event.key == pygame.K_y:
                    if not autoSwitchModes:
                        mode_text, _ = welcomefont.render(f"Switch every {msBetweenModes}", (0,0,0))
                        pygame.time.set_timer(MODESWITCHEVENT, msBetweenModes, True)
                    else:
                        mode_text, _ = welcomefont.render(f"Auto switch off", (0,0,0))
                        pygame.time.set_timer(MODESWITCHEVENT, 0, True)
                    finalSurface.fill(BACKGROUND)
                    finalSurface.blit(mode_text, ((top_screen_width-mode_text.get_width())/2,top_screen_height))
                    pygame.display.flip()
                    wait(2000)

                elif event.key == pygame.K_e:
                    topOption = (topOption + 1) % 3
                    if topOption == 0:
                        pygame.time.set_timer(LOOKEVENT, 0, True)
                        pupils.pupilL = 0
                        pupils.pupilR = 0
                        pupils.pupilV = 0
                        showFaceMask = True
                    elif topOption == 1:
                        showFaceMask = False
                    elif topOption == 2:
                        pupils.pupilL = 0
                        pupils.pupilR = 0
                        pupils.pupilV = -60
                        showFaceMask = True
                        pygame.time.set_timer(LOOKEVENT, 5000, True)
                elif wizardOfOz:
                    if event.key == pygame.K_w:
                        textList = []
                    else:
                        ozSpeech, textIndex = OzKeydownEvents(event, interactionItems, threadevent, flow, logfile)
                        if ozSpeech is not None and not flow.is_alive():
                            textList = createTextSurface(finalSurface, textIndex, top_screen_height, top_screen_width, wizardOfOz, LANGUAGE)
                            pygame.mixer.init()
                            pygame.mixer.music.load(ozSpeech)
                            pygame.mixer.music.play()

            elif event.type == pygame.KEYUP:
                if wizardOfOz:
                    OzKeyupEvents(event)
            # Touchscreen events
            elif event.type == pygame.FINGERDOWN:
                if show_buttons:
                    if event.x*screenSize[0] < nobutton.get_width() and event.y*screenSize[1] < nobutton.get_height()*hScale:
                        print("Left button pressed")
                        interrupted = True
                        speechNode.no_detected = True
                    if event.x*screenSize[0] > size[0]-yesbutton.get_width() and event.y*screenSize[1] < yesbutton.get_height()*hScale:
                        print("Right button pressed")
                        interrupted = True
                        speechNode.yes_detected = True
                if event.x*screenSize[0] < 5+menuicon.get_width() and int((size[1]-menuicon.get_height()-20)*hScale) < event.y*screenSize[1] < size[1]*hScale:
                    if state == MENUSTATE:
                        state = NORMALSTATE
                        pygame.time.set_timer(BLINKEVENT, 15000, True)
                    else: state = MENUSTATE
                elif state == MENUSTATE:
                    if 160 < event.x*screenSize[0] < 160+danishbutton.get_width() and int(100*hScale) < event.y*screenSize[1] < int((100+danishbutton.get_height())*hScale):
                        state = NORMALSTATE
                        if LANGUAGE == "en-US":
                            threadevent.set()
                            LANGUAGE = "da-DK"
                            pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                            interactionIndex = 0
                    elif 160 < event.x*screenSize[0] < 160+englishbutton.get_width() and int(250*hScale) < event.y*screenSize[1] < int((250+englishbutton.get_height())*hScale):
                        state = NORMALSTATE
                        if LANGUAGE == "da-DK":
                            threadevent.set()
                            LANGUAGE = "en-US"
                            pygame.time.set_timer(INTERACTIONEVENT, 1, True)
                            interactionIndex = 0
                    elif size[0]-160-coloricon.get_width() < event.x*screenSize[0] < size[0]-160 and int(250*hScale) < event.y*screenSize[1] < int((250+coloricon.get_height())*hScale):
                        state = COLORSTATE
                    elif size[0]-160-onlineicon.get_width() < event.x*screenSize[0] < size[0]-160 and int(100*hScale) < event.y*screenSize[1] < int((100+onlineicon.get_height())*hScale):
                        if isOnline: isOnline = False
                        elif not isOnline and checkInternet(): isOnline = True
                    elif (size[0]-graphicon.get_width())/2 < event.x*screenSize[0] < (size[0]+graphicon.get_width())/2 and int(370*hScale) < event.y*screenSize[1] < int((370+graphicon.get_height())*hScale):
                        plot_data, plot_size = st.get_plot()
                        plot = pygame.image.fromstring(plot_data, plot_size, "RGB")
                        state = GRAPHSTATE
                elif state == COLORSTATE:
                    BACKGROUND = screen.get_at((int(event.x*size[0]), int(size[1]*event.y)))

            ########## User Events ##########
            if state != MENUSTATE:
                if event.type == BLINKEVENT and state == NORMALSTATE and eyeDesign == "normal":
                    pygame.time.set_timer(NORMALEVENT, 300, True)
                    state = BLINKSTATE2
                elif event.type == BLINKEVENT and state == NORMALSTATE and eyeDesign == "monster":
                    pygame.time.set_timer(MONSTERBLINKEVENT, 50, True)
                    state = MONSTERBLINKSTATE
                    random.shuffle(monsterblinks)
                elif event.type == MONSTERBLINKEVENT:
                    if state == MONSTERBLINKSTATE:
                        pygame.time.set_timer(MONSTERBLINKEVENT, 50, True)
                        state = MONSTERBLINKSTATE2
                    elif state == MONSTERBLINKSTATE2:
                        pygame.time.set_timer(MONSTERBLINKEVENT, 50, True)
                        state = MONSTERBLINKSTATE3
                    elif state == MONSTERBLINKSTATE3:
                        blinktime = random.randrange(5000, 20000, 1000)
                        pygame.time.set_timer(BLINKEVENT, blinktime, True)
                        state = NORMALSTATE
                elif event.type == NORMALEVENT:
                    blinktime = random.randrange(5000, 20000, 1000)
                    pygame.time.set_timer(BLINKEVENT, blinktime, True)
                    state = NORMALSTATE
                elif event.type == HAPPYSTARTEVENT and eyeDesign == "normal":
                    pygame.time.set_timer(HAPPYEVENT, 70, True)
                    state = HAPPYSTATE
                elif event.type == HAPPYEVENT and eyeDesign == "normal":
                    pygame.time.set_timer(NORMALEVENT, 1500, True)
                    state = HAPPYSTATE2
                elif event.type == QUESTIONEVENT and eyeDesign == "normal":
                    pygame.time.set_timer(NORMALEVENT, 3000, True)
                    state = CONFUSEDSTATE
                elif event.type == MODESWITCHEVENT:
                    if not flow.is_alive():
                        testMode = (testMode + 1) % 5
                        if testMode == 0: testMode = 1
                        print("Test mode: ", testMode)
                        logging("activation_count.txt", f"Switched to mode: {testMode}")
                        pygame.time.set_timer(MODESWITCHEVENT, msBetweenModes, True)
                    else:
                        pygame.time.set_timer(MODESWITCHEVENT, 20000, True)

            if event.type == INTERACTIONEVENT:
                interactionWait = False
                if state == WAITSTATE:
                    state = NORMALSTATE
                    pupils.pupilL = 0
                    pupils.pupilR = 0
                    pupils.pupilV = 0
                    if topOption == 2:
                        pupils.pupilV = -60
                print("Interaction timer reset")
            elif event.type == GAZEEVENT:
                gazeAtClosest = not gazeAtClosest
                altTrackID = 0
                if gazeAtClosest:
                    gazeTime = 8000 + random.randrange(-3, 3)*1000
                else:
                    gazeTime = 5000 + random.randrange(-2, 2)*1000
                pygame.time.set_timer(GAZEEVENT, gazeTime, True)
            elif event.type == PHOTOEVENT:
                if bubbles:
                    trackeduser.updateAll(bubbles)
            elif event.type == LOOKEVENT:
                if movePupilLeft:
                    pupils.pupilL -= 5
                    pupils.pupilR -= 5
                else:
                    pupils.pupilL += 5
                    pupils.pupilR += 5
                if pupils.pupilL > 40 or pupils.pupilL < -50:
                    movePupilLeft = not movePupilLeft
                    pygame.time.set_timer(LOOKEVENT, 8000, True)
                else:
                    pygame.time.set_timer(LOOKEVENT, 10, True)

        ########## Interaction ##########
        #st.trailing_five_min_activations(disp.numberOfActivations)
        frequency = st.trailingFiveMinSum
        #could use pygame.timers to create variable length trailing activations - call function every event
        manyPeople = 3 # Number indicating many people being tracked
        frequentUse = 20 # Number indicating frequent use of dispenser
        waitTimer = 0
        currentActivations = disp.numberOfActivations
        dispenserActivated = True if currentActivations != lastNumberOfActivations else False

        if dispenserActivated and not wizardOfOz:
            logging("activation_count.txt", f"Activation! Number of activations: {currentActivations}")

        # If in Wizard of Oz test mode
        if wizardOfOz:
            pupils.pupilL, pupils.pupilR, pupils.pupilV = OzMovePupils(pupils.pupilL, pupils.pupilR, pupils.pupilV)
            if dispenserActivated:
                logging("testlog.txt", f"Activation! Number of activations: {currentActivations}")
                pygame.event.post(happyevent)
                frame, x, y, h, w = sh.take()
                frame = frame[y:(y+h), x-30:(x+w+30)]
                bubbles.append(trackeduser.TrackedUser(finalSurface, int(100), int(top_screen_height+60), BubbleUpdate, frame)) # Adds face to bubbles list
                pygame.time.set_timer(PHOTOEVENT, int(1000/BubbleUpdate))

        elif receiver.poll():
            trackedList, peopleCount, frame = receiver.recv()
            trackedList = {k:v for (k,v) in trackedList.items() if v[4]>3}

            if runInteraction and (testMode != 1 and testMode != 3): # if the dispenser should initiate interactions
                keys = trackedList.keys() # IDs of currently tracked people
                recurrents = set(keys) & set(prevKeys) # IDs of people present during last interaction and now
                if not interactionWait and not flow.is_alive() and trackedList:
                    recurrentsVideo = set(keys) & set(videoKeys)

                    # Scenarios
                    if frequency >= frequentUse:           # Scenario 1
                        waitTimer = 30000

                    else:                                  # Scenario 2
                        if not recurrents:
                            interactionIndex = 0
                        else:
                            interactionIndex += 1
                        numberOfNewPeople = len(keys - recurrents)
                        if numberOfNewPeople >= 1:
                            if interactionIndex >= 2: interactionIndex = 0
                            if interactionIndex == 0:      # 1
                                #interactionItems.append("novideo")
                                interactionItems.append("sanitizer")
                                #interactionItems.append("video")
                                if not recurrentsVideo or len(keys - recurrentsVideo) >= 2:
                                    #interactionItems.append("video")
                                    videoKeys = keys
                                else:
                                    interactionItems.append("countdown")
                            prevKeys = keys
                            waitTimer = 15000

                if not interactionItems and not flow.is_alive() and dispenserActivated and reminder30:
                    interactionItems.append("30s")
                    prevKeys = keys
                    waitTimer = 8000

                if interactionItems:
                        print("Arguments: ", interactionItems)
                        flow = threading.Thread(target=interaction, args=interactionItems)
                        flow.start()
                        interactionItems = []

            if waitTimer > 0:
                interactionWait = True
                pygame.time.set_timer(INTERACTIONEVENT, waitTimer, True)

            # Gaze calculation and control
            if trackedList:
                closestPerson = max(trackedList.items(), key = lambda i : i[1][2])[0]
                if largeScreen and dispenserActivated:
                    pygame.event.post(happyevent)
                    (x, y, w, h, n, u, c) = trackedList.get(closestPerson)
                    frame = frame[y:(y+h), x-30:(x+w+30)]
                    bubbles.append(trackeduser.TrackedUser(finalSurface, int(100), int(top_screen_height+60), BubbleUpdate, frame)) # Adds face to bubbles list
                    pygame.time.set_timer(PHOTOEVENT, int(1000/BubbleUpdate))

                if gazeAtClosest:
                    if altTrackID == 0: # Determine ID of closest person
                        trackID = closestPerson
                        altTrackID = trackID
                    elif trackID not in trackedList: # If we lose track of ID; look at the new closest
                        trackID = closestPerson
                else:
                    if altTrackID == 0: # Determine ID of random person
                        peopleList = list(trackedList.keys())
                        if len(peopleList) > 1: # Remove the ID of closest person, then randomly choose ID
                            maxID = closestPerson
                            peopleList.remove(maxID)
                        altTrackID = random.choice(peopleList)
                    if altTrackID in trackedList:
                        trackID = altTrackID
                    else: # If we lose track of ID; look at closest
                        trackID = closestPerson

                (x, y, w, h, n, u, c) = trackedList.get(trackID)
                if topOption == 0:
                    pupils.calculateAngles(x, y, w, h, topOption)

                if peopleCount > oldNumberOfPeople:
                    oldNumberOfPeople = peopleCount
                    if logToServer: client.send(peopleCount)

            else: # if no person in frame during activation, add bubble without photo
                if largeScreen and dispenserActivated:
                    pygame.event.post(happyevent)
                    bubbles.append(trackeduser.TrackedUser(finalSurface, int(100), int(top_screen_height+60), BubbleUpdate)) # Adds face to bubbles list
                    pygame.time.set_timer(PHOTOEVENT, int(1000/BubbleUpdate))

        lastNumberOfActivations = currentActivations
        #st.update_plot(disp.numberOfActivations, numberOfPeople)
        """
        irSensors.detectHands(ADC)
        hands = irSensors.getHandList()
        #print(hands)
        if hands[0]:
            yes_detected = True
        elif hands[1]:
            no_detected = True
        #disp.update()
        """
        ########## State Machine ########## Controls face expression and menu
        screen.fill(BACKGROUND)

        if state == NORMALSTATE:
            if eyeDesign == "normal":
                blitImages(normalwhiteL, normalwhiteR)
                drawPupils()
                blitImages(normalL, normalR)
            elif eyeDesign == "monster":
                screen.blit(monster, (0,0))
                drawMonsterPupils()
        elif state == BLINKSTATE:
            blitImages(closingwhiteL, closingwhiteR)
            drawPupils()
            blitImages(closingL, closingR)
        elif state == BLINKSTATE2:
            blitImages(closedL, closedR)
        elif state == HAPPYSTATE:
            blitImages(happyL, happyR)
        elif state == HAPPYSTATE2:
            blitImages(happyL, happyR)
        elif state == CONFUSEDSTATE:
            blitImages(confusedLwhite, confusedRwhite)
            drawPupils()
            blitImages(confusedL, confusedR)
        elif state == VIDEOSTATE:
            playVideo()
            state = NORMALSTATE
        elif state == MENUSTATE:
            screen.blit(danishbutton, (160, 100))
            screen.blit(englishbutton, (160, 250))
            screen.blit(coloricon, (size[0]-160-coloricon.get_width(), 250))
            if isOnline: screen.blit(onlineicon, (size[0]-160-onlineicon.get_width(), 100))
            else: screen.blit(offlineicon, (size[0]-160-offlineicon.get_width(), 100))
            screen.blit(graphicon, (400-graphicon.get_width()/2, 370))
            if not flow.is_alive():
                flow = threading.Thread(target=interaction, args=("monster", "normal"))
                flow.start()
            text_surface, _ = myfont.render(f"Activations: {disp.numberOfActivations}", (0,0,0))
            screen.blit(text_surface, (5,5))
        elif state == COLORSTATE:
            screen.blit(colorselector, (50, 50))
        elif state == MONSTERBLINKSTATE:
            screen.blit(monster, (0,0))
            drawMonsterPupils()
            screen.blit(monsterblinks[0], (0,0))
        elif state == MONSTERBLINKSTATE2:
            screen.blit(monster, (0,0))
            drawMonsterPupils()
            screen.blit(monsterblinks[1], (0,0))
        elif state == MONSTERBLINKSTATE3:
            screen.blit(monster, (0,0))
            drawMonsterPupils()
            screen.blit(monsterblinks[2], (0,0))
        elif state == GRAPHSTATE:
            screen.blit(plot, (0,0))
        elif state == WAITSTATE:
            print("Wait state")
            pupils.pupilL = 0
            pupils.pupilR = 0
            pupils.pupilV = -50
            blitImages(normalwhiteL, normalwhiteR)
            drawPupils()
            blitImages(normalL, normalR)
        if show_buttons:
            showButtons()

        ''' # Send notification to phone if dispenser almost empty
        if disp.numberOfActivations >= almostEmpty:
            st.pushbullet_notification(typeOfNotification, msg)
        '''
        #screen.blit(menuicon, (5, size[1]-50))
        if largeScreen:
            finalSurface.fill(BACKGROUND)
            if testMode == 0:
                if topOption == 1:
                    showimages.showImage(finalSurface, 0, 0, 100) #Infographic images
                else:
                    scalescreen = pygame.transform.smoothscale(screen, (top_screen_width,top_screen_height))
                    finalSurface.blit(scalescreen, (0,0))
                """
                if show_hand_detect:
                    finalSurface.blit(handDetectL, (0,largeSize[1]-600+150))
                    finalSurface.blit(handDetectR, (500,largeSize[1]-600+150))
                    pygame.draw.rect(finalSurface, (255,0,0), yes_rect)
                    pygame.draw.rect(finalSurface, (0,255,0), no_rect)
                    finalSurface.blit(nej_text, (100-50+50, top_screen_height+590+10))
                    finalSurface.blit(ja_text, (offset+50+40, top_screen_height+590+10))
                elif
                """
                if textList:
                    if showFaceMask:
                        text_offset = 100
                        for txt in textList:
                            finalSurface.blit(txt, ((top_screen_width-txt.get_width())/2,top_screen_height+250+text_offset))
                            text_offset += 75
                    else:
                        text_offset = 0
                        for txt in textList:
                            finalSurface.blit(txt, ((top_screen_width-txt.get_width())/2,top_screen_height+250+text_offset))
                            text_offset += 75
                elif showScrollingImages:
                    showimages.showImage(finalSurface, 0, largeSize[1]-600, 100) #Infographic images
                if showFaceMask:
                    finalSurface.blit(facemask, (-150, top_screen_height-50))

            else:
                if testMode == 1:
                    finalSurface.blit(sdu_logo, (150, top_screen_height+150))
                    if welcomeText: finalSurface.blit(welcome_text, (180, top_screen_height+50))

                elif testMode == 2:
                    finalSurface.blit(sdu_logo, (150, top_screen_height+150))
                    if welcomeText: finalSurface.blit(welcome_text, (180, top_screen_height+50))
                    if textList and showSubtitles:
                        text_offset = 100
                        for txt in textList:
                            finalSurface.blit(txt, ((top_screen_width-txt.get_width())/2,top_screen_height+250+text_offset))
                            text_offset += 75

                elif testMode == 3:
                    scalescreen = pygame.transform.smoothscale(screen, (top_screen_width,top_screen_height))
                    finalSurface.blit(scalescreen, (0,0))

                elif testMode == 4:
                    scalescreen = pygame.transform.smoothscale(screen, (top_screen_width,top_screen_height))
                    finalSurface.blit(scalescreen, (0,0))
                    if textList and showSubtitles:
                        text_offset = 100
                        for txt in textList:
                            finalSurface.blit(txt, ((top_screen_width-txt.get_width())/2,top_screen_height+250+text_offset))
                            text_offset += 75


                #if not showFaceMask and bubbles:
                #    text_surface, _ = bubblefont.render("Gnid hænderne indtil tiden er udløbet", (0,0,255)) #moi
                #    finalSurface.blit(text_surface, (200, top_screen_height+50)) #moi
                #    trackeduser.showAll(bubbles)       #Rub timer bubbles

        else: finalSurface.blit(screen, (0,0))
        pygame.display.flip()
        #disp.readPIR()

    # clean up threads/processes/etc
    interrupted = True
    threadevent.set()
    try:
        client.close()
    except:
        print("No client to close")
    if not wizardOfOz:
        receiver.send(True)
        while receiver.poll():
            (trackedList, peopleCount, frame) = receiver.recv()
        tracking_proc.terminate()
        tracking_proc.join()
    else:
        logfile.close()
    pygame.display.quit()
    pygame.quit()
    GPIO.cleanup()
    print("Cleaned up")
    exit(0)
