from edgetpu.detection.engine import DetectionEngine
from PIL import Image
import cv2
import pygame
from logFunction import logging
import dispenser
from clientSetup import *

res1 = (640, 480)
res2 = (960, 720)
res3 = (1280, 960)
res4 = (640, 320) # take this width, maybe different height and adjust window
res = res1        # set same res in eyeAngles
#startPoint1 = (320, 300) #start point for the first square when doing double face detection
#startPoint2 = (startPoint1[0]+320, startPoint1[1]) # start point for the second square

stackHorizontally = True
windowOffset = (0,0)
centerPoint = (windowOffset[0] + res[0]/2, windowOffset[1] + res[1]/2)
if stackHorizontally:
    startPoint1 = (int(centerPoint[0]-320), int(centerPoint[1]-320/2))
    startPoint2 = (int(centerPoint[0]), int(centerPoint[1]-320/2))
else:
    startPoint1 = (int(centerPoint[0]-320/2), int(centerPoint[1]-320))
    startPoint2 = (int(centerPoint[0]-320/2), int(centerPoint[1]))
    
def showWindow(frame, faceTrackers):
    cv2.rectangle(frame,(startPoint1[0],startPoint1[1]),(startPoint1[0]+320,startPoint1[1]+320),(0,255,0),3)
    cv2.rectangle(frame,(startPoint2[0],startPoint2[1]),(startPoint2[0]+320,startPoint2[1]+320),(0,255,0),3)
    for (x, y, w, h, _, _, _) in faceTrackers.values():
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)

    cv2.imshow('My Image', frame)
    if cv2.waitKey(1) == 27:
        print("esc")
        cv2.destroyAllWindows()
        return False
    return True

def wholeFrame(engine, currentID, faceTrackers, peopleCount, frame):
    framePIL = Image.fromarray(frame)
    faces = engine.detect_with_image(framePIL,
                                     threshold=0.05,
                                     keep_aspect_ratio=True,
                                     relative_coord=False,
                                     top_k=10,
                                     resample=4)
    for face in faces:
        (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
        w = x2-x
        h = y2-y
        center = (int(x+w*0.5), int(y+h*0.5))
        fidMatch = False
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
            if not u and tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                if n < 50: n += 1
                if n >= 35 and c == False:
                    c = True
                    peopleCount += 1                        
                faceTrackers.update({fid:(x,y,w,h,n,True,c)})
                fidMatch = True
                break
        if not fidMatch:
            faceTrackers.update({currentID:(x,y,w,h,1,True,False)})
            currentID += 1
            print("ID: ", currentID)
 
    return currentID, faceTrackers, peopleCount

def frameCutout(engine, currentID, faceTrackers, peopleCount, frame, hOff, vOff, faceAtBoundary=False):
    frameRGB = frame[vOff:320+vOff, hOff:320+hOff]   
    framePIL = Image.fromarray(frameRGB)
    faces = engine.detect_with_image(framePIL,
                                     threshold=0.05,
                                     keep_aspect_ratio=True,
                                     relative_coord=False,
                                     top_k=10,
                                     resample=4)
    for face in faces:
        (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
        w = x2-x
        h = y2-y

        if stackHorizontally:
            if hOff == startPoint1[0] and x2 > 320-10:
                faceAtBoundary = True
                w = h
            elif hOff == startPoint2[0] and faceAtBoundary and x < 5:
                continue
        else:
            if vOff == startPoint1[1] and y2 > 320-10:
                faceAtBoundary = True
                h = w
            elif vOff == startPoint2[1] and faceAtBoundary and y < 5:
                continue

        x = x+hOff
        y = y+vOff
        center = (int(x+w*0.5), int(y+h*0.5))
        fidMatch = False
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
            if not u and tx-tw <= center[0] <= tx+tw+tw and ty-th <= center[1] <= ty+th+th:
                if n < 50: n += 1
                if c == False and n >= 10:
                    c = True
                    peopleCount += 1
                    print("Unique people: ", peopleCount)
                    logging("people_count.txt", f"People count: {peopleCount}")
                faceTrackers.update({fid:(x,y,w,h,n,True,c)})
                fidMatch = True
                break
        if not fidMatch:
            faceTrackers.update({currentID:(x,y,w,h,1,True,False)})
            currentID += 1
            print("ID: ", currentID)
            #logging("people_count.txt", f"Face ID: {currentID}")
        
    return currentID, faceTrackers, peopleCount, faceAtBoundary

def histEqual(src, chl): #Histogram equalization
    frameYCrCb = cv2.cvtColor(src, cv2.COLOR_BGR2YCrCb)
    #frameYCrCb[:,:,1] = cv2.equalizeHist(frameYCrCb[:,:,1])  # Normal
    clahe = cv2.createCLAHE(clipLimit=5)                     # CLAHE
    frameYCrCb[:,:,chl] = clahe.apply(frameYCrCb[:,:,chl])
    frameRGB = cv2.cvtColor(frameYCrCb, cv2.COLOR_YCrCb2RGB) #cv2.COLOR_LAB2BGR
    return frameRGB

########## Function for tracking faces - running in seperate process ##########
def faceTracking(sender=False, dispObj=False, client=False, showCam=False):
    engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
    cap = cv2.VideoCapture(-1)
    currentID = 0
    faceTrackers = {}   
    peopleCount = 0
    lastCount = 0
    activationCount = 0    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])
    
    term = False
    while not term:
        _, frame = cap.read()
        #frame = cv2.rotate(frame, cv2.ROTATE_180)
        #frameRGB = histEqual(frame, 0)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        faceAtBoundary = False
        currentID, faceTrackers, peopleCount, faceAtBoundary = frameCutout(engine, currentID, faceTrackers, peopleCount, frameRGB, startPoint1[0], startPoint1[1], True)
        currentID, faceTrackers, peopleCount, _ = frameCutout(engine, currentID, faceTrackers, peopleCount, frameRGB, startPoint2[0], startPoint2[1], faceAtBoundary)

        fidsToDelete = []
        for fid in faceTrackers.keys():
            tx, ty, tw, th, n, u, c =  faceTrackers.get(fid)
            if not u:
                n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx,ty,tw,th,n,False,c)})

        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)   
        
        if sender:
            sender.send((faceTrackers, peopleCount, frameRGB))       
            if sender.poll():  
                term = sender.recv()
        elif showCam and not showWindow(frame, faceTrackers): # show camera input for choosing face detection area
            break                                 # break if ESC pressed
        if dispObj:
            currentActivations = dispObj.numberOfActivations
            if currentActivations != activationCount:
                logging("activation_count.txt", f"Activation! Number of activations: {currentActivations}")
                activationCount = currentActivations
        if peopleCount != lastCount and client:
            #if client:
            client.send(peopleCount)
            lastCount = peopleCount            

    print("Closing facetracking")    
    cap.release()
    
def faceTrackingWhole(sender): # not updated
    engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
    cap = cv2.VideoCapture(-1)
    currentID = 0 
    faceTrackers = {}
    term = False
    peopleCount = 0
    while not term:
        _, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        framePIL = Image.fromarray(frameRGB)
        faces = engine.detect_with_image(framePIL,
                                         threshold=0.05,
                                         keep_aspect_ratio=True,
                                         relative_coord=False,
                                         top_k=10,
                                         resample=4)
        for face in faces:
            (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
            w = x2-x
            h = y2-y
            center = (int(x+w*0.5), int(y+h*0.5))
            fidMatch = False
            for fid in faceTrackers.keys():
                (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
                if tx <= center[0] <= tx+tw and ty <= center[1] <= ty+th:
                    if n < 50: n += 1
                    if n >= 35 and c == False:
                        c = True
                        peopleCount += 1                        
                    faceTrackers.update({fid:(x,y,w,h,n,True,c)})
                    fidMatch = True
                    break
            if not fidMatch:
                faceTrackers.update({currentID:(x,y,w,h,1,True,False)})
                currentID += 1
                print("ID: ", currentID)
                logging(f"Face ID: {currentID}")
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
        fidsToDelete = []
        for fid in faceTrackers.keys():
            (tx, ty, tw, th, n, u, c) =  faceTrackers.get(fid)
            if not u:
                # if center is close to frame edge then decay faster
                #if res[0]-tw-20 < tx < 20:
                    #n-=5
                n -= 1
            if n < 1: fidsToDelete.append(fid)
            else:
                faceTrackers.update({fid:(tx,ty,tw,th,n,False,c)})

        for fid in fidsToDelete:
            faceTrackers.pop(fid, None)   
        sender.send((faceTrackers, peopleCount, frameRGB))       
        if sender.poll():  
            term = sender.recv()
        pygame.time.Clock().tick(100)
        
    cap.release()

class Snapshot():
    def __init__(self):
        self.engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
    
    def take(self):
        cap = cv2.VideoCapture(-1)
        _, frame = cap.read()
        frame = cv2.rotate(frame, cv2.ROTATE_180)
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        framePIL = Image.fromarray(frameRGB)
        faces = self.engine.detect_with_image(framePIL,
                                         threshold=0.05,
                                         keep_aspect_ratio=True,
                                         relative_coord=False,
                                         top_k=10,
                                         resample=4)
        widest = 0
        (a, b, c, d) = (0, 0, 0, 0)
        for face in faces:
            (x, y, x2, y2) = (int(i) for i in face.bounding_box.flatten().tolist())
            h = y2-y
            w = x2-x
            if w > widest:
                (a, b, c, d) = (x, y, h, w)
        print(a,b,c,d)
        return frameRGB, a, b, c, d
    
if __name__ == '__main__':
    logging("activation_count.txt", "Standard dispenser started")
    disp = dispenser.Dispenser()
    disp.init_GPIO()
    disp.gelUpdate()
    #c = Client()
    faceTracking(dispObj=disp, client=False, showCam=False)