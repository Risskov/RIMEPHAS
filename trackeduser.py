import pygame
import pygame.freetype
from math import sin,cos,radians


RUBTIME = 30
#IM_SIZE = 120
#PIE_SIZE1 = IM_SIZE+int(IM_SIZE*0.15)
#PIE_SIZE0 = int(IM_SIZE*0.4)

IM_SIZE = 160 #moi
PIE_SIZE1 = IM_SIZE+int(IM_SIZE*0.15) #moi


TYPE = 1
"""
TYPE:
0 for smaller clock
1 for larger edge clock

"""
myfont = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 20) #moi
fontcolor = (0,0,255) #moi
#UPDATE_HZ = 8
#BITE = 360/(30*UPDATE_HZ) #Bite pr update

#function to draw pie using parametric coordinates of circle
def pie(scr,color,center,radius,start_angle,stop_angle, inc):
    theta=start_angle
    while theta <= stop_angle:
        pygame.draw.line(scr,color,center, 
        (center[0]+radius*cos(radians(theta)),center[1]+radius*sin(radians(theta))),2)
        theta+=inc
    
class TrackedUser:
    def __init__(self, surface, frame, x, y, hz):
        self.hz = hz
        self.surface = surface      #FinalSurface
        self.bite = 360/(RUBTIME*hz)
        self.frame = frame          # Image
        self.x = x-(IM_SIZE/2)
        self.y = y-(IM_SIZE/2)
        self.timer = hz*RUBTIME
        self.frame_surf = pygame.surfarray.make_surface(frame)
        self.frame_surf = pygame.transform.rotate(self.frame_surf, 270)
        self.frame_surf = pygame.transform.scale(self.frame_surf, (IM_SIZE,IM_SIZE))
        self.frame_mask = pygame.Surface((IM_SIZE,IM_SIZE), pygame.SRCALPHA)      
        
        #Draw circle for clock
        if TYPE == 0:
            self.pieTime = pygame.Surface((PIE_SIZE0,PIE_SIZE0), pygame.SRCALPHA)
            pygame.draw.circle(self.pieTime, (76, 200, 0, 255), (int(PIE_SIZE0/2), int(PIE_SIZE0/2)), int(PIE_SIZE0/2))
        else:
            self.pieTime = pygame.Surface((PIE_SIZE1,PIE_SIZE1), pygame.SRCALPHA)
            pygame.draw.circle(self.pieTime, (0, 255, 0, 255), (int(PIE_SIZE1/2), int(PIE_SIZE1/2)), int(PIE_SIZE1/2))


        self.frame_mask.fill((255,255,255,0))
        pygame.draw.circle(self.frame_mask, (255, 255, 255, 255), (int(IM_SIZE/2), int(IM_SIZE/2)), int(IM_SIZE/2))
        self.frame_mask.blit(self.frame_surf, (0,0), special_flags=pygame.BLEND_RGBA_MIN)
        

    def update(self):
        if TYPE == 0:
            pie(self.pieTime, (0,255,0,0), (PIE_SIZE0/2, PIE_SIZE0/2), PIE_SIZE0/2 , self.timer*self.bite , (self.timer+1)*self.bite, 1)
        else:
            pie(self.pieTime, (0,255,0,0), (PIE_SIZE1/2, PIE_SIZE1/2), PIE_SIZE1/2 , self.timer*self.bite , (self.timer+1)*self.bite, 0.25)
        self.timer -= 1
       
    def show(self, x, y):
        if TYPE == 1:
            text_surface, _ = myfont.render(f"{int(self.timer/self.hz)}", fontcolor) #moi
            self.surface.blit(text_surface, (self.x+x, self.y+y)) #moi
            self.surface.blit(self.pieTime, (self.x-(PIE_SIZE1-IM_SIZE)/2+x, self.y-(PIE_SIZE1-IM_SIZE)/2+y))
        self.surface.blit(self.frame_mask, (self.x+x, self.y+y) )
        if TYPE == 0:
            self.surface.blit(self.pieTime, (self.x+(IM_SIZE*0.6)+x, self.y+int(IM_SIZE*0.6)+y))
        
    def move(self, x, y):
        self.x += x
        self.y += y
          
def updateAll(objects):
    for obj in objects:
        obj.update()
    objects[:] = (x for x in objects if (x.timer > 0))     #Removal of objects with a timer value below 1.       
            
def showAll(objects):
    i = 0
    for obj in objects[0:5]:
        obj.show(i,50)
        i += IM_SIZE*1.25
        
