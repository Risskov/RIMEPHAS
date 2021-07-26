import math

res1 = (640,480)
res2 = (960,720)
res3 = (1280,960)

class EyeAngles():
    def __init__(self, windowedFaceTracking):
        self.res = res1 if windowedFaceTracking else res1
        self.pupilL = 0
        self.pupilR = 0
        self.pupilV = 0
        self.WIDTH = self.res[0]/2
        self.HEIGHT = self.res[1]/2
        self.EYE_DEPTH = 2
        self.hFOV = 62/2
        self.vFOV = 49/2
        self.ppcm = self.WIDTH*2/15.5# * 1.5
    # Calculating the gaze angles to detected face
    def calculateAngles(self, x, y, w, h, topOption):
        center = (int(x+w*0.5), int(y+h*0.5))
        hAngle = (1 - center[0]/self.WIDTH) * self.hFOV
        vAngle = (1 - center[1]/self.HEIGHT) * self.vFOV            
        c = -0.26*w+103
        if c < 30: c = 30
        
        # horizontal
        b = 4
        angleA = (90 - hAngle)*math.pi/180
        a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
        angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
        self.pupilL = int((angleC - math.pi/2) * self.EYE_DEPTH * self.ppcm)
        
        b_hat = 2*b
        c_hat = math.sqrt(a*a + b_hat*b_hat - 2*a*b_hat*math.cos(angleC))
        angleA_hat = math.acos((b_hat*b_hat + c_hat*c_hat - a*a)/(2*b_hat*c_hat))
        self.pupilR = int((math.pi/2 - angleA_hat) * self.EYE_DEPTH * self.ppcm)
        
        # vertical
        b = 6
        angleA = (90 - vAngle)*math.pi/180
        a = math.sqrt(b*b + c*c - 2*b*c*math.cos(angleA))
        angleC = math.acos((a*a + b*b - c*c)/(2*a*b))
        self.pupilV = int((angleC - math.pi/2) * self.EYE_DEPTH * self.ppcm)
        if topOption == 2:
            self.pupilV = -60
