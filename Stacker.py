import cv2
import numpy as np
import time
import DoBotArm as Dbt
import win32com.client
import random
speaker = win32com.client.Dispatch("SAPI.SpVoice")
time.sleep(0.5)
homeX, homeY, homeZ = 250, 0, -20
time.sleep(1)
oldMaxX = 265
oldMinX = 140
newMaxX = 10
newMinX = 450
oldMaxY = 60
oldMinY = -55
newMaxY = 40
newMinY = 600
def mapping(i,newRangeMin,newRangeMax,oldRangeMin,oldRangeMax):
    return (((i - oldRangeMin) * (newRangeMax-newRangeMin)) /
            (oldRangeMax-oldRangeMin)) + newRangeMin
class Block:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y
class Botti:
    def __init__(self):
        self.x = 200
        self.y = 0
        self.z = 80
        self.kasi = Dbt.DoBotArm(self.x,self.y,self.z)
        self.nahdytBlockit = []
        self.nykyBlocki = Block("name",100,0)
    def seeColor(self, image, lower_color, upper_color):
        color_cd = []
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_color, upper_color)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            n_X = x + w // 2
            n_Y = y + h // 2
            color_cd.append([n_X,n_Y])
            time.sleep(0.5)
        return color_cd
    def initialize(self):
        speaker.Speak("Calibrating")
        time.sleep(13)
        speaker.Speak("Calibrating Done")
    def moveMidUp(self):
        self.kasi.moveArmXYZ(200,0,80)
    def moveHeight(self,korkeus):
        self.kasi.moveArmXYZ(200,0,korkeus)
    def kuvatilanne(self):
        speaker.Speak("Taking a photo")
        time.sleep(1)
        camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
        ret, image = camera.read()
        lower_green = np.array([50, 50, 50], np.uint8)  
        upper_green = np.array([90, 255, 255], np.uint8)
        g_cd = [self.seeColor(image, lower_green, upper_green)]
        name = "GREEN"
        for i in range(len(g_cd[0])):
            nykyblokki = Block(name + str(i), g_cd[0][i][0], g_cd[0][i][1])
            self.nahdytBlockit.append(nykyblokki)
        speaker.Speak("Detecting "+ str(len(self.nahdytBlockit))+" block.")
    def alustus(self): #alkuasento, kalibrointi ja ilmoitus (printti tai puhe) kun alkaa toimia
        time.sleep(1)
        self.moveMidUp()
        time.sleep(1)
        self.kuvatilanne()
        self.lapi = -60
        time.sleep(0.5)
        speaker.Speak("Beginning stacking process.")
    def kasaa(self,lapi,i):
        munbotti.nykyBlocki = self.nahdytBlockit[i]
        self.distanceFromNykyBlockX = int(mapping(self.nykyBlocki.y,oldMinX,oldMaxX,newMinX,newMaxX))
        self.distanceFromNykyBlockY = int(mapping(self.nykyBlocki.x,oldMinY,oldMaxY,newMinY,newMaxY))    
        time.sleep(1)
        self.liiku(self.distanceFromNykyBlockX+20,self.distanceFromNykyBlockY,80)
        time.sleep(1)
        self.liiku(self.distanceFromNykyBlockX+20,self.distanceFromNykyBlockY,-50)
        self.kasi.toggleSuction()
        time.sleep(0.5)
        self.liiku(self.distanceFromNykyBlockX+20,self.distanceFromNykyBlockY,80)
        self.moveMidUp()
        self.moveHeight(lapi)
        self.kasi.toggleSuction()
        self.moveMidUp()
    def randomize(self):
        speaker.Speak("Randomizing blocks")
        palikat = []
        palikat.append([200,0])
        for i in range(len(self.nahdytBlockit)):
            randomisointi = True
            self.moveHeight(self.lapi)
            self.kasi.toggleSuction()
            randomX = random.randint(155,245)
            randomY = random.randint(-30,30)
            self.moveMidUp()
            freeY = 0
            freeX = 0
            while randomisointi == True:
                for k in range(len(palikat)):
                    if(freeY == len(palikat) or freeX  == len(palikat)):
                        palikat.append([randomX,randomY])
                        randomisointi = False
                        freeY = 0
                        break
                    if(randomX > palikat[k][0] - 22 and randomX < palikat[k][0] + 22):
                        randomX = random.randint(155,245)
                        freeX = 0
                    else:
                        freeX += 1
                    if(randomY > palikat[k][1] - 22 and randomY < palikat[k][1] + 22):
                        randomY = random.randint(-40,40)
                        freeY = 0
                    else:
                        freeY +=1
            self.liiku(randomX,randomY,80)
            self.liiku(randomX,randomY,-40)
            self.kasi.toggleSuction()
            self.lapi -= 20
            self.liiku(randomX,randomY,80)
            self.moveMidUp()
    def tilanne(self):
        self.alustus()
        for k in range(len(self.nahdytBlockit)):
            self.lapi += 20
            self.kasaa(self.lapi,k)
        speaker.Speak("Stacking Done.")
        time.sleep(2)
        self.randomize()
    def liiku(self,x,y,z):
        self.kasi.moveArmXYZ(x,y,z)
 
munbotti = Botti()    
munbotti.initialize()
while 1:
    #munbotti.kuvatilanne()
    munbotti.tilanne()
    #for block in munbotti.nahdytBlockit:
        #tee siirto (pitaa tietaa minne)
        #tulosta tilanne kaden kannalta, kayta get_pose-funktiota
        #munbotti.kuvatilanne()  #analysoi, onko pulmia
        #jos ok, niin ilrandomisointita "Continuing"
