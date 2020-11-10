import random
import sys

import pygame
from pygame.locals import *

from .colors import *
from .shapes import *


class Game:
    def __init__(self):
        self.FPS = 30  # frames per second, the general speed of the program
        self.WINDOWWIDTH = 640  # size of window's width in pixels
        self.WINDOWHEIGHT = 480  # size of windows' height in pixels
        self.REVEALSPEED = 8  # speed boxes' sliding reveals and covers
        self.BOXSIZE = 40  # size of box height & width in pixels
        self.GAPSIZE = 10  # size of gap between boxes in pixels
        self.BOARDWIDTH = 10  # number of columns of icons
        self.BOARDHEIGHT = 7  # number of rows of icons
        assert (self.BOARDWIDTH * self.BOARDHEIGHT) % 2 == 0, 'Board needs to have an even number of boxes for pairs of matches.'
        assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= self.BOARDWIDTH * self.BOARDHEIGHT, "Board is too big for the number of shapes/colors defined."
        self.XMARGIN = int((self.WINDOWWIDTH - (self.BOARDWIDTH * (self.BOXSIZE + self.GAPSIZE))) / 2)
        self.YMARGIN = int((self.WINDOWHEIGHT - (self.BOARDHEIGHT * (self.BOXSIZE + self.GAPSIZE))) / 2)

        self.BGCOLOR = NAVYBLUE
        self.LIGHTBGCOLOR = GRAY
        self.BOXCOLOR = WHITE
        self.HIGHLIGHTCOLOR = BLUE

        pygame.init()
        self.FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((self.WINDOWWIDTH, self.WINDOWHEIGHT))

        self.mousex = 0  # used to store x coordinate of mouse event
        self.mousey = 0  # used to store y coordinate of mouse event
        pygame.display.set_caption('Memory Game')

        self.mainBoard = self.getRandomizedBoard()
        self.revealedBoxes = self.generateRevealedBoxesData(False)

        self.firstSelection = None  # stores the (x, y) of the first box clicked.

    def run(self):
        self.DISPLAYSURF.fill(self.BGCOLOR)
        self.startGameAnimation(self.mainBoard)

        while True:  # main game loop
            mouseClicked = False

            self.DISPLAYSURF.fill(self.BGCOLOR)  # drawing the window
            self.drawBoard(self.mainBoard, self.revealedBoxes)

            for event in pygame.event.get():  # event handling loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEMOTION:
                    mousex, mousey = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos
                    mouseClicked = True

            boxx, boxy = self.getBoxAtPixel(mousex, mousey)
            if boxx != None and boxy != None:
                # The mouse is currently over a box.
                if not self.revealedBoxes[boxx][boxy]:
                    self.drawHighlightBox(boxx, boxy)
                if not self.revealedBoxes[boxx][boxy] and mouseClicked:
                    self.revealBoxesAnimation(self.mainBoard, [(boxx, boxy)])
                    self.revealedBoxes[boxx][boxy] = True  # set the box as "revealed"
                    if self.firstSelection == None:  # the current box was the first box clicked
                        self.firstSelection = (boxx, boxy)
                    else:  # the current box was the second box clicked
                        # Check if there is a match between the two icons.
                        icon1shape, icon1color = self.getShapeAndColor(self.mainBoard, self.firstSelection[0], self.firstSelection[1])
                        icon2shape, icon2color = self.getShapeAndColor(self.mainBoard, boxx, boxy)

                        if icon1shape != icon2shape or icon1color != icon2color:
                            # Icons don't match. Re-cover up both selections.
                            pygame.time.wait(1000)  # 1000 milliseconds = 1 sec
                            self.coverBoxesAnimation(self.mainBoard, [(self.firstSelection[0], self.firstSelection[1]), (boxx, boxy)])
                            self.revealedBoxes[self.firstSelection[0]][self.firstSelection[1]] = False
                            self.revealedBoxes[boxx][boxy] = False
                        elif self.hasWon(self.revealedBoxes):  # check if all pairs found
                            self.gameWonAnimation(self.mainBoard)
                            pygame.time.wait(2000)

                            # Reset the board
                            self.mainBoard = self.getRandomizedBoard()
                            self.revealedBoxes = self.generateRevealedBoxesData(False)

                            # Show the fully unrevealed board for a second.
                            self.drawBoard(self.mainBoard, self.revealedBoxes)
                            pygame.display.update()
                            pygame.time.wait(1000)

                            # Replay the start game animation.
                            self.startGameAnimation(self.mainBoard)
                        self.firstSelection = None  # reset firstSelection variable

            # Redraw the screen and wait a clock tick.
            pygame.display.update()
            self.FPSCLOCK.tick(self.FPS)

    def generateRevealedBoxesData(self, val):
        revealedBoxes = []
        for i in range(self.BOARDWIDTH):
            revealedBoxes.append([val] * self.BOARDHEIGHT)
        return revealedBoxes

    def getRandomizedBoard(self):
        # Get a list of every possible shape in every possible color.
        icons = []
        for color in ALLCOLORS:
            for shape in ALLSHAPES:
                icons.append((shape, color))

        random.shuffle(icons)  # randomize the order of the icons list
        numIconsUsed = int(self.BOARDWIDTH * self.BOARDHEIGHT / 2)  # calculate how many icons are needed
        icons = icons[:numIconsUsed] * 2  # make two of each
        random.shuffle(icons)

        # Create the board data structure, with randomly placed icons.
        board = []
        for x in range(self.BOARDWIDTH):
            column = []
            for y in range(self.BOARDHEIGHT):
                column.append(icons[0])
                del icons[0]  # remove the icons as we assign them
            board.append(column)
        return board

    def splitIntoGroupsOf(self, groupSize, theList):
        # splits a list into a list of lists, where the inner lists have at
        # most groupSize number of items.
        result = []
        for i in range(0, len(theList), groupSize):
            result.append(theList[i:i + groupSize])
        return result

    def leftTopCoordsOfBox(self, boxx, boxy):
        # Convert board coordinates to pixel coordinates
        left = boxx * (self.BOXSIZE + self.GAPSIZE) + self.XMARGIN
        top = boxy * (self.BOXSIZE + self.GAPSIZE) + self.YMARGIN
        return (left, top)

    def getBoxAtPixel(self, x, y):
        for boxx in range(self.BOARDWIDTH):
            for boxy in range(self.BOARDHEIGHT):
                left, top = self.leftTopCoordsOfBox(boxx, boxy)
                boxRect = pygame.Rect(left, top, self.BOXSIZE, self.BOXSIZE)
                if boxRect.collidepoint(x, y):
                    return (boxx, boxy)
        return (None, None)

    def drawIcon(self, shape, color, boxx, boxy):
        quarter = int(self.BOXSIZE * 0.25)  # syntactic sugar
        half = int(self.BOXSIZE * 0.5)  # syntactic sugar

        left, top = self.leftTopCoordsOfBox(boxx, boxy)  # get pixel coords from board coords
        # Draw the shapes
        if shape == DONUT:
            pygame.draw.circle(self.DISPLAYSURF, color, (left + half, top + half), half - 5)
            pygame.draw.circle(self.DISPLAYSURF, self.BGCOLOR, (left + half, top + half), quarter - 5)
        elif shape == SQUARE:
            pygame.draw.rect(self.DISPLAYSURF, color, (left + quarter, top + quarter, self.BOXSIZE - half, self.BOXSIZE - half))
        elif shape == DIAMOND:
            pygame.draw.polygon(self.DISPLAYSURF, color, (
            (left + half, top), (left + self.BOXSIZE - 1, top + half), (left + half, top + self.BOXSIZE - 1), (left, top + half)))
        elif shape == LINES:
            for i in range(0, self.BOXSIZE, 4):
                pygame.draw.line(self.DISPLAYSURF, color, (left, top + i), (left + i, top))
                pygame.draw.line(self.DISPLAYSURF, color, (left + i, top + self.BOXSIZE - 1), (left + self.BOXSIZE - 1, top + i))
        elif shape == OVAL:
            pygame.draw.ellipse(self.DISPLAYSURF, color, (left, top + quarter, self.BOXSIZE, half))

    def getShapeAndColor(self, board, boxx, boxy):
        # shape value for x, y spot is stored in board[x][y][0]
        # color value for x, y spot is stored in board[x][y][1]
        return board[boxx][boxy][0], board[boxx][boxy][1]

    def drawBoxCovers(self, board, boxes, coverage):
        # Draws boxes being covered/revealed. "boxes" is a list
        # of two-item lists, which have the x & y spot of the box.
        for box in boxes:
            left, top = self.leftTopCoordsOfBox(box[0], box[1])
            pygame.draw.rect(self.DISPLAYSURF, self.BGCOLOR, (left, top, self.BOXSIZE, self.BOXSIZE))
            shape, color = self.getShapeAndColor(board, box[0], box[1])
            self.drawIcon(shape, color, box[0], box[1])
            if coverage > 0:  # only draw the cover if there is an coverage
                pygame.draw.rect(self.DISPLAYSURF, self.BOXCOLOR, (left, top, coverage, self.BOXSIZE))
        pygame.display.update()
        self.FPSCLOCK.tick(self.FPS)

    def revealBoxesAnimation(self, board, boxesToReveal):
        # Do the "box reveal" animation.
        for coverage in range(self.BOXSIZE, (-self.REVEALSPEED) - 1, -self.REVEALSPEED):
            self.drawBoxCovers(board, boxesToReveal, coverage)

    def coverBoxesAnimation(self, board, boxesToCover):
        # Do the "box cover" animation.
        for coverage in range(0, self.BOXSIZE + self.REVEALSPEED, self.REVEALSPEED):
            self.drawBoxCovers(board, boxesToCover, coverage)

    def drawBoard(self, board, revealed):
        # Draws all of the boxes in their covered or revealed state.
        for boxx in range(self.BOARDWIDTH):
            for boxy in range(self.BOARDHEIGHT):
                left, top = self.leftTopCoordsOfBox(boxx, boxy)
                if not revealed[boxx][boxy]:
                    # Draw a covered box.
                    pygame.draw.rect(self.DISPLAYSURF, self.BOXCOLOR, (left, top, self.BOXSIZE, self.BOXSIZE))
                else:
                    # Draw the (revealed) icon.
                    shape, color = self.getShapeAndColor(board, boxx, boxy)
                    self.drawIcon(shape, color, boxx, boxy)

    def drawHighlightBox(self, boxx, boxy):
        left, top = self.leftTopCoordsOfBox(boxx, boxy)
        pygame.draw.rect(self.DISPLAYSURF, self.HIGHLIGHTCOLOR, (left - 5, top - 5, self.BOXSIZE + 10, self.BOXSIZE + 10), 4)

    def startGameAnimation(self, board):
        # Randomly reveal the boxes 8 at a time.
        coveredBoxes = self.generateRevealedBoxesData(False)
        boxes = []
        for x in range(self.BOARDWIDTH):
            for y in range(self.BOARDHEIGHT):
                boxes.append((x, y))
        random.shuffle(boxes)
        boxGroups = self.splitIntoGroupsOf(8, boxes)

        self.drawBoard(board, coveredBoxes)
        for boxGroup in boxGroups:
            self.revealBoxesAnimation(board, boxGroup)
            self.coverBoxesAnimation(board, boxGroup)

    def gameWonAnimation(self, board):
        # flash the background color when the player has won
        coveredBoxes = self.generateRevealedBoxesData(True)
        color1 = self.LIGHTBGCOLOR
        color2 = self.BGCOLOR

        for i in range(13):
            color1, color2 = color2, color1  # swap colors
            self.DISPLAYSURF.fill(color1)
            self.drawBoard(board, coveredBoxes)
            pygame.display.update()
            pygame.time.wait(300)

    @staticmethod
    def hasWon(revealedBoxes):
        # Returns True if all the boxes have been revealed, otherwise False
        for i in revealedBoxes:
            if False in i:
                return False  # return False if any boxes are covered.
        return True
