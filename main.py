"""main controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
from vehicle import Driver
from controller import Camera,Lidar
import matplotlib.pyplot as plt
import cv2
import numpy as np
import math

# create the Robot instance.
driver = Driver()

# get the time step of the current world.
timestep = int(driver.getBasicTimeStep())

Max_hizi=80

ileri_hizi=10
fren=0
sayici=0
plot=10

camera=driver.getCamera("camera")
Camera.enable(camera,timestep)

lms291=driver.getLidar("Sick LMS 291")
Lidar.enable(lms291,timestep)

lms291_yatay=Lidar.getHorizontalResolution(lms291)

fig=plt.figure(figsize=(3,3))


# Main loop:
# - perform simulation steps until Webots is stopping the controller
while driver.step() != -1:
    
    Camera.getImage(camera)
    Camera.saveImage(camera,"camera.png",1)
    frame=cv2.imread("camera.png")
    #cv2.imshow("Camera",frame)
    #cv2.waitKey(1)
    
    image = frame
    # BGR ' yi HSV ye çevirdik
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # HSV nin içindeki renk aralıgını belirledik
    #lower_blue = np.array([160,0,0])
    #upper_blue = np.array([180,255,255])
    boundaries=[([20,0,0],[30,255,255])]
    # Yukarıda belırledıgımız eşik değerlerini gray goruntunun içinde eşleştirdik.
    for (lower,upper) in boundaries:
        lower=np.array(lower,dtype="uint8")
        upper=np.array(upper,dtype="uint8")
        mask = cv2.inRange(hsv, lower, upper)
        # bitwise and operatörü ile de ana goruntude yukarıda buldugumuz mask'i aldık.
        res = cv2.bitwise_and(image,image, mask= mask)
        #ayarladıgımız 3 görüntüyü gösterdik
    res=cv2.cvtColor(res,cv2.COLOR_BGR2GRAY) #maskelenen görüntüyü gray uzayına çeviriyoruz.
    blurred=cv2.GaussianBlur(res,(7,7),0) #Gürültüyü azaltmak için görüntüyü blurluyoruz
    ret,th1=cv2.threshold(res,40,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) #Gri tonlamalı görüntüden ikili görüntü oluşturduk.
    ret1,th2=cv2.threshold(th1,127,255,cv2.THRESH_TOZERO) 
    contours,hierarchy=cv2.findContours(th2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #Görüntüde kontuar oluşturduk

    
    if len(contours)>0:
        centroid=max(contours,key=cv2.contourArea) #Kontuar alanı belirleniyor.
        M=cv2.moments(centroid) 
        area=cv2.contourArea(centroid)
        if area>3000:
            cx=int(M['m10']/M['m00']) #x koordinatını ve y koordinatını buluyoruz.
            cy=int(M['m01']/M['m00'])

            cv2.line(image,(cx,0),(cx,720),(255,0,0),1) #bulunan bu koordinatlara göre görüntüde line çiziliyor.
            cv2.line(image,(0,cy),(1280,cy),(255,0,0),1)
            cv2.line(image,(320,0),(320,640),(255,0,0),1)
            cv2.circle(image,(cx,cy),3,(0,0,255),-1)
            cv2.drawContours(image,contours,-1,(0,255,0),2) #Kontuar alanı çiziliyor
            print(cx)
            if cx<500:
                print("sol yap") #Referans değeri(x koordinatı) 500 den küçük ise sağa dön
                driver.setSteeringAngle(-0.3)#aracın + veya - durumuna
                #göre sağa veya sola döndürür
            else: 
                print("1x")
            
            if cx>520:
                print("sag yap") #Referans değeri(y koordinatı) 520 den büyük ise sola dön
                driver.setSteeringAngle(0.3)#aracın + veya - durumuna
                #göre sağa veya sola döndürür
            else:
                print("1y")
            if 500<cx<520:
                print("Duz gıt") #Referans değeri(x-y koordinatı) 500 ile 520 arasında ise düz git
                driver.setSteeringAngle(0)
            driver.setCruisingSpeed(ileri_hizi)# aracın ileri doğru hızını
        
    driver.setDippedBeams(True)#ışığı yakma true false
    lms291_deger=[]
    lms291_deger=Lidar.getRangeImage(lms291)
    
    # if plot==10:
        # y=lms291_deger
        # x=np.linspace(math.pi,0,np.size(y))
        # plt.polar(x,y)
        # plt.pause(0.00001)
        # plt.clf()
        # plot=0
    
    # plot+=1
    cv2.imshow('Goruntu',image) #işleme yaptığımız görüntülerin framelerini yansıtıyoruz
    cv2.imshow('th1',th1)
    cv2.imshow('th2',th2)
    cv2.imshow("input", res)
    cv2.waitKey(10)

plt.show()
            
        
# Enter here exit cleanup code.
