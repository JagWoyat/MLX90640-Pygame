import numpy as np
import matplotlib.pyplot as plt
import pygame
from scipy import ndimage

# mlx90640 configuration
# import board
# import busio
# import adafruit_mlx90640

# i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)
# mlx = adafruit_mlx90640.MLX90640(i2c)
# mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

# Application constants
windowRes = (800,600)
pictureRes = (640,480)
camRes = (24,32)
frame = np.zeros((24*32,))
rangeRes = (1,100)
rangeRGB = np.zeros((1,100,3))
# Change interpolation of an image
interpolation = 4

# Loading of an example image
frame = np.load("ExampleImage.npy")
frame = np.asarray(frame).reshape(-1)

# Testing color spectrum for set temperature ranges
# Set interpolation to 1
# min = 0
# max = 5
# colorSpectrum = np.arange(min,max,(max-min)/768)
# frame = colorSpectrum

class Text:
    def __init__(self,text, x, y):
        self.x=x
        self.y=y
        self.alpha = 255
        self.text = font.render(text, True, (0,0,0))
        textArray.append(self)
    def setText(self,text):
        self.text = font.render(text, True, (0,0,0))
        self.text.set_alpha(self.alpha)
    def setAlpha(self, a):
        self.alpha = a
    def render(self):
        display.blit(self.text, (self.x,self.y))

def getRGB(rgb,temperatureMatrix,tMin,tD):
    # Duration of black to blue color spectrum in °C*10
    B2BSpectrum = 20

    var = temperatureMatrix - tMin - B2BSpectrum
    # Checking if value less than 0
    var[:,:][var[:,:] < 0] = 0

    # Calculating red parameter
    rgb[:,:,0] = 255 * (var)/(tD/4)
    # Checking if value is in allowed range
    rgb[:,:,0][rgb[:,:,0] < 0] = 0
    rgb[:,:,0][rgb[:,:,0] > 255] = 255

    # Calculating green parameter
    rgb[:,:,1] = 255/(tD/2) * (var - tD/2)
    rgb[:,:,1][rgb[:,:,1] < 0] = 0
    rgb[:,:,1][rgb[:,:,1] > 255] = 255

    # Create temporal variable responsible for black to blue color spectrum
    tymB = 255*(temperatureMatrix - tMin)/B2BSpectrum
    tymB[:,:][tymB[:,:] > 255] = 255
    tymB[:,:][tymB[:,:] < 0] = 0

    # Calculating blue parameter
    rgb[:,:,2] = tymB - 255*(var)/(tD/2)
    rgb[:,:,2][rgb[:,:,2] > 255] = 255
    rgb[:,:,2][rgb[:,:,2] < 0] = 0

    rgb = np.round(rgb,1)
    return rgb

# Initialize Pygame
pygame.init()
display = pygame.display.set_mode(windowRes)

textArray = []
font = pygame.font.SysFont(None, 24)
degree = Text('[°C]', pictureRes[0] + (windowRes[0] - pictureRes[0])/2 + 18,(windowRes[1] - pictureRes[1])/2 + 20)
T1 = Text(' ', pictureRes[0] + (windowRes[0] - pictureRes[0])/2 + 18,(windowRes[1] - pictureRes[1])/2)
T2 = Text(' ', pictureRes[0] + (windowRes[0] - pictureRes[0])/2 + 18,(windowRes[1] - pictureRes[1])/2 + pictureRes[1] - 12)

loop = True
while loop:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
            
    display.fill((150,150,150))
    try:
        # Uncomment when using camera
        # mlx.getFrame(frame)
        temperatureMatrix = (np.reshape(frame,camRes)) * 10
        temperatureMatrix = np.round(temperatureMatrix)
        tMax = np.max(temperatureMatrix)
        tMin = np.min(temperatureMatrix)
        tD = tMax - tMin
        # Interpolation
        temperatureMatrix = ndimage.zoom(temperatureMatrix,interpolation)
        temperatureMatrix = np.round(temperatureMatrix)

        # Creating and rendering image
        rgb = np.zeros((24*interpolation,32*interpolation,3))
        rgb = getRGB(rgb,temperatureMatrix,tMin,tD)
        surf = pygame.surfarray.make_surface(rgb)
        surf = pygame.transform.rotate(surf, 90)
        surf = pygame.transform.scale(surf,pictureRes)
        display.blit(surf,((windowRes[0] - pictureRes[0])/2,(windowRes[1] - pictureRes[1])/2))

        colorRange = np.arange(tMin, tMax, tD/100)
        if colorRange.size == 100:
            colorRange = (np.reshape(colorRange,rangeRes))
            rangeRGB = getRGB(rangeRGB,colorRange,tMin,tD)
            range = pygame.surfarray.make_surface(rangeRGB)
            range = pygame.transform.scale(range,((10,pictureRes[1])))
            range = pygame.transform.rotate(range, 180)
            display.blit(range,(pictureRes[0] + (windowRes[0] - pictureRes[0])/2 + 5,(windowRes[1] - pictureRes[1])/2))

        # Render texts
        T1.setText(str(tMax/10))
        T2.setText(str(tMin/10))
        for x in textArray:
            x.render()

        pygame.display.update()

    except ValueError:
        print('error')
        continue
        
pygame.quit()