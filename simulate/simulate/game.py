import random
import sys
import time

import pygame
from pygame.locals import *

from .colors import *


class Game:
    def __init__(self):
        # Initialize some variables for a new game
        self.pattern = []  # stores the pattern of colors
        self.currentStep = 0  # the color the player must push next
        self.lastClickTime = 0  # timestamp of the player's last button push
        self.score = 0
        # when False, the pattern is playing. when True, waiting for the player to click a colored button:
        self.waitingForInput = False

        self.bgColor = BLACK

        self.FPS = 30
        self.WINDOWWIDTH = 640
        self.WINDOWHEIGHT = 480
        self.FLASHSPEED = 500  # in milliseconds
        self.FLASHDELAY = 200  # in milliseconds
        self.BUTTONSIZE = 200
        self.BUTTONGAPSIZE = 20
        self.TIMEOUT = 4  # seconds before game over if no button is pushed.

        self.XMARGIN = int((self.WINDOWWIDTH - (2 * self.BUTTONSIZE) - self.BUTTONGAPSIZE) / 2)
        self.YMARGIN = int((self.WINDOWHEIGHT - (2 * self.BUTTONSIZE) - self.BUTTONGAPSIZE) / 2)

        # Rect objects for each of the four buttons
        self.YELLOWRECT = pygame.Rect(self.XMARGIN, self.YMARGIN, self.BUTTONSIZE, self.BUTTONSIZE)
        self.BLUERECT = pygame.Rect(self.XMARGIN + self.BUTTONSIZE + self.BUTTONGAPSIZE, self.YMARGIN, self.BUTTONSIZE, self.BUTTONSIZE)
        self.REDRECT = pygame.Rect(self.XMARGIN, self.YMARGIN + self.BUTTONSIZE + self.BUTTONGAPSIZE, self.BUTTONSIZE, self.BUTTONSIZE)
        self.GREENRECT = pygame.Rect(self.XMARGIN + self.BUTTONSIZE + self.BUTTONGAPSIZE, self.YMARGIN + self.BUTTONSIZE + self.BUTTONGAPSIZE, self.BUTTONSIZE, self.BUTTONSIZE)

        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))
        pygame.display.set_caption('Simulate')

        self.BASICFONT = pygame.font.Font('freesansbold.ttf', 16)
        self.infoSurf = self.BASICFONT.render('Match the pattern by clicking on the button or using the Q, W, A, S keys.', 1, DARKGRAY)
        self.infoRect = self.infoSurf.get_rect()
        self.infoRect.topleft = (10, self.WINDOWHEIGHT - 25)

        # load the sound files
        self.BEEP1 = pygame.mixer.Sound('beep1.ogg')
        self.BEEP2 = pygame.mixer.Sound('beep2.ogg')
        self.BEEP3 = pygame.mixer.Sound('beep3.ogg')
        self.BEEP4 = pygame.mixer.Sound('beep4.ogg')

    def run(self):
        while True:  # main game loop
            clickedButton = None  # button that was clicked (set to YELLOW, RED, GREEN, or BLUE)
            self.DISPLAYSURF.fill(self.bgColor)
            self.drawButtons()

            scoreSurf = self.BASICFONT.render('Score: ' + str(self.score), 1, WHITE)
            scoreRect = scoreSurf.get_rect()
            scoreRect.topleft = (self.WINDOWWIDTH - 100, 10)
            self.DISPLAYSURF.blit(scoreSurf, scoreRect)

            self.DISPLAYSURF.blit(self.infoSurf, self.infoRect)

            self.checkForQuit()
            for event in pygame.event.get():  # event handling loop
                if event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    clickedButton = self.getButtonClicked(mousex, mousey)
                elif event.type == KEYDOWN:
                    if event.key == K_q:
                        clickedButton = YELLOW
                    elif event.key == K_w:
                        clickedButton = BLUE
                    elif event.key == K_a:
                        clickedButton = RED
                    elif event.key == K_s:
                        clickedButton = GREEN

            if not self.waitingForInput:
                # play the pattern
                pygame.display.update()
                pygame.time.wait(1000)
                self.pattern.append(random.choice((YELLOW, BLUE, RED, GREEN)))
                for button in self.pattern:
                    self.flashButtonAnimation(button)
                    pygame.time.wait(self.FLASHDELAY)
                self.waitingForInput = True
            else:
                # wait for the player to enter buttons
                if clickedButton and clickedButton == self.pattern[self.currentStep]:
                    # pushed the correct button
                    self.flashButtonAnimation(clickedButton)
                    self.currentStep += 1
                    self.lastClickTime = time.time()

                    if self.currentStep == len(self.pattern):
                        # pushed the last button in the pattern
                        self.changeBackgroundAnimation()
                        self.score += 1
                        self.waitingForInput = False
                        self.currentStep = 0  # reset back to first step

                elif (clickedButton and clickedButton != self.pattern[self.currentStep]) or (
                        self.currentStep != 0 and time.time() - self.TIMEOUT > self.lastClickTime):
                    # pushed the incorrect button, or has timed out
                    self.gameOverAnimation()
                    # reset the variables for a new game:
                    self.pattern = []
                    self.currentStep = 0
                    self.waitingForInput = False
                    self.score = 0
                    pygame.time.wait(1000)
                    self.changeBackgroundAnimation()

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def terminate(self):
        pygame.quit()
        sys.exit()

    def checkForQuit(self):
        for event in pygame.event.get(QUIT):  # get all the QUIT events
            self.terminate()  # terminate if any QUIT events are present
        for event in pygame.event.get(KEYUP):  # get all the KEYUP events
            if event.key == K_ESCAPE:
                self.terminate()  # terminate if the KEYUP event was for the Esc key
            pygame.event.post(event)  # put the other KEYUP event objects back

    def flashButtonAnimation(self, color, animationSpeed=50):
        if color == YELLOW:
            sound = self.BEEP1
            flashColor = BRIGHTYELLOW
            rectangle = self.YELLOWRECT
        elif color == BLUE:
            sound = self.BEEP2
            flashColor = BRIGHTBLUE
            rectangle = self.BLUERECT
        elif color == RED:
            sound = self.BEEP3
            flashColor = BRIGHTRED
            rectangle = self.REDRECT
        elif color == GREEN:
            sound = self.BEEP4
            flashColor = BRIGHTGREEN
            rectangle = self.GREENRECT

        origSurf = self.DISPLAYSURF.copy()
        flashSurf = pygame.Surface((self.BUTTONSIZE, self.BUTTONSIZE))
        flashSurf = flashSurf.convert_alpha()
        r, g, b = flashColor
        sound.play()
        for start, end, step in ((0, 255, 1), (255, 0, -1)):  # animation loop
            for alpha in range(start, end, animationSpeed * step):
                self.checkForQuit()
                self.DISPLAYSURF.blit(origSurf, (0, 0))
                flashSurf.fill((r, g, b, alpha))
                self.DISPLAYSURF.blit(flashSurf, rectangle.topleft)
                pygame.display.update()
                self.FPSCLOCK.tick(self.FPS)
        self.DISPLAYSURF.blit(origSurf, (0, 0))

    def drawButtons(self):
        pygame.draw.rect(self.DISPLAYSURF, YELLOW, self.YELLOWRECT)
        pygame.draw.rect(self.DISPLAYSURF, BLUE, self.BLUERECT)
        pygame.draw.rect(self.DISPLAYSURF, RED, self.REDRECT)
        pygame.draw.rect(self.DISPLAYSURF, GREEN, self.GREENRECT)

    def changeBackgroundAnimation(self, animationSpeed=40):
        newBgColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        newBgSurf = pygame.Surface((self.WINDOWWIDTH, self.WINDOWHEIGHT))
        newBgSurf = newBgSurf.convert_alpha()
        r, g, b = newBgColor
        for alpha in range(0, 255, animationSpeed):  # animation loop
            self.checkForQuit()
            self.DISPLAYSURF.fill(self.bgColor)

            newBgSurf.fill((r, g, b, alpha))
            self.DISPLAYSURF.blit(newBgSurf, (0, 0))

            self.drawButtons()  # redraw the buttons on top of the tint

            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)
        self.bgColor = newBgColor

    def gameOverAnimation(self, color=WHITE, animationSpeed=50):
        # play all beeps at once, then flash the background
        origSurf = self.DISPLAYSURF.copy()
        flashSurf = pygame.Surface(self.DISPLAYSURF.get_size())
        flashSurf = flashSurf.convert_alpha()
        self.BEEP1.play()  # play all four beeps at the same time, roughly.
        self.BEEP2.play()
        self.BEEP3.play()
        self.BEEP4.play()
        r, g, b = color
        for i in range(3):  # do the flash 3 times
            for start, end, step in ((0, 255, 1), (255, 0, -1)):
                # The first iteration in this loop sets the following for loop
                # to go from 0 to 255, the second from 255 to 0.
                for alpha in range(start, end, animationSpeed * step):  # animation loop
                    # alpha means transparency. 255 is opaque, 0 is invisible
                    self.checkForQuit()
                    flashSurf.fill((r, g, b, alpha))
                    self.DISPLAYSURF.blit(origSurf, (0, 0))
                    self.DISPLAYSURF.blit(flashSurf, (0, 0))
                    self.drawButtons()
                    pygame.display.update()
                    self.FPSCLOCK.tick(self.FPS)

    def getButtonClicked(self, x, y):
        if self.YELLOWRECT.collidepoint((x, y)):
            return YELLOW
        elif self.BLUERECT.collidepoint((x, y)):
            return BLUE
        elif self.REDRECT.collidepoint((x, y)):
            return RED
        elif self.GREENRECT.collidepoint((x, y)):
            return GREEN
        return None
