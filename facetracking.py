from edgetpu.detection.engine import DetectionEngine
from PIL import Image
import cv2
import pygame

########## Function for tracking faces - running in seperate process ##########
def faceTracking(sender):
    engine = DetectionEngine("ssd_mobilenet_v2_face_quant_postprocess_edgetpu.tflite")
    cap = cv2.VideoCapture(-1)
    currentID = 1   
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
        #self.cap = cv2.VideoCapture(-1)
    
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
    
    