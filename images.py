import pygame
########## Load images ##########
normalL = pygame.image.load("images/png/normalL.png")
normalR = pygame.transform.flip(normalL, True, False)
normalwhiteL = pygame.image.load("images/png/normalLwhite.png")
normalwhiteR = pygame.transform.flip(normalwhiteL, True, False)

closedL = pygame.image.load("images/png/closedL.png")
closedR = pygame.transform.flip(closedL, True, False)

happyL = pygame.image.load("images/png/happyL.png")
happyR = pygame.transform.flip(happyL, True, False)

confusedL = pygame.image.load("images/png/confusedL.png")
confusedR = pygame.image.load("images/png/confusedR.png")
confusedLwhite = pygame.image.load("images/png/normalAltLwhite.png")
confusedRwhite = pygame.image.load("images/png/confusedRwhite.png")

onlineicon = pygame.image.load("images/png/online.png")
offlineicon = pygame.image.load("images/png/offline.png")

danishbutton = pygame.image.load("images/bg/danishicon.png")
englishbutton = pygame.image.load("images/bg/englishicon.png")
danishbutton = pygame.transform.scale(danishbutton, (120,90))
englishbutton = pygame.transform.scale(englishbutton, (120,90))

nobutton = pygame.image.load("images/png/nobutton.png")
yesbutton = pygame.image.load("images/png/yesbutton.png")

pupil = pygame.image.load("images/png/pupil.png")

colorselector = pygame.image.load("images/bg/ColorPicker.bmp")
colorselector = pygame.transform.flip(colorselector, False, True)
coloricon = pygame.transform.scale(colorselector, (120, 90))
colorselector = pygame.transform.scale(colorselector, (700, 350))

menuicon = pygame.image.load("images/png/menuicon.png")
graphicon = pygame.image.load("images/png/graphicon.png")
graphicon = pygame.transform.scale(graphicon, (90,90))

monster = pygame.image.load("images/png/monstereyes.png")
monsterpupil = pygame.image.load("images/png/monsterpupil.png")
monsterpupilsmall = pygame.image.load("images/png/monsterpupilsmall.png")
monsterblinkL = pygame.image.load("images/png/monsterclosedL.png")
monsterblinkM = pygame.image.load("images/png/monsterclosedM.png")
monsterblinkR = pygame.image.load("images/png/monsterclosedR.png")

benderL = pygame.image.load("images/bg/benderL.png")
benderR = pygame.transform.flip(benderL, True, False)
benderpupil = pygame.image.load("images/bg/benderpupil.png")

handDetectL = pygame.image.load("images/png/left_hand_detect2.png")
scalex = int(handDetectL.get_width()/1.5)
scaley = int(handDetectL.get_height()/1.5)
handDetectL = pygame.transform.scale(handDetectL, (scalex,scaley))
handDetectR = pygame.transform.flip(handDetectL, True, False)

facemask = pygame.image.load("images/png/mundbind1100.png")
sdu_tmp = pygame.image.load("images/sdu_logo.png")
sdu_logo = pygame.transform.scale(sdu_tmp, (int(sdu_tmp.get_width()/1.5),int(sdu_tmp.get_height()/1.5)))