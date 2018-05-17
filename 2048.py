#!/usr/bin/python3

FILENAME_HIGHSCORE = "2048highscore.txt"

KEYS_UP    = ["Up"]    # w
KEYS_RIGHT = ["Right"] # d
KEYS_DOWN  = ["Down"]  # s
KEYS_LEFT  = ["Left"]  # a

KEYS_QUIT_GAME        = "q" # "<Control-q>"
KEYS_NEW_GAME         = "n" # "<Control-n>"
KEYS_OPEN_GAME        = "o" # "<Control-o>"
KEYS_ZOOM_IN          = "+" # "<Control-plus>"
KEYS_ZOOM_OUT         = "-" # "<Control-minus>"
KEYS_ENTER_FULLSCREEN = "<F11>"
KEYS_EXIT_FULLSCREEN  = "<Escape>"

BG             = "#776e65"
BG_END_OF_GAME = "#edc22e"
FONT_FIELD     = ["Consolas", "18", "bold"]
FONT_TEXT      = ["Consolas", "16"]
FONT_2048      = ["Consolas", "64"]
FG_2048        = "#50d1f5"

DEFAULT_DESIGN = [[ 0, "#000000", "#aa9898"], #       -
                  [ 1, "#776e65", "#eee4da"], #       2
                  [ 2, "#776e65", "#ede0c8"], #       4
                  [ 3, "#f9f6f2", "#f2b179"], #       8
                  [ 4, "#f9f6f2", "#f59563"], #      16
                  [ 5, "#f9f6f2", "#f67c5f"], #      32
                  [ 6, "#f9f6f2", "#f65e3b"], #      64
                  [ 7, "#f9f6f2", "#edcf72"], #     128
                  [ 8, "#f9f6f2", "#edcc61"], #     256
                  [ 9, "#f9f6f2", "#edc850"], #     512
                  [10, "#f9f6f2", "#edc53f"], #   1.024
                  [11, "#f9f6f2", "#edc22e"], #   2.048
                  [12, "#ffffff", "#50d1f5"], #   4.096
                  [13, "#ffffff", "#7070ee"], #   8.192
                  [14, "#ffffff", "#4040ee"], #  16.384
                  [15, "#ffffff", "#484e4d"], #  32.768
                  [16, "#ffffff", "#403635"], #  65.536
                  [17, "#ffffff", "#201818"]] # 131.072

DEFAULT_WIDTH_WINDOW = 740

GRID_COLUMNS = 37
GRID_ROWS    = 25
GRID_UNIT    = 20

from tkinter import *
from tkinter import messagebox
from random import randint
from math import log2
import os

"""
Class UI
This class implements the frontend using tkinter.
"""
class UI:
    def __init__(self):
        # set keys
        self.keys = [KEYS_UP, KEYS_RIGHT,
                     KEYS_DOWN, KEYS_LEFT]

        # set colours for tiles: [ [exponent, fg, bg], ... ]
        self.colours     = DEFAULT_DESIGN

        # colours and fonts
        self.bg          = BG
        self.bgEndOfGame = BG_END_OF_GAME
        self.fontFields  = FONT_FIELD
        self.fontText    = FONT_TEXT
        self.font2048    = FONT_2048
        self.fg2048      = FG_2048

        # create a game instance
        self.game = Game()

        # create window
        self.root = Tk()
        self.root.config(bg=self.bg)
        self.root.title("2048")

        # init grid
        self.unit   = GRID_UNIT
        self.width  = GRID_COLUMNS * self.unit
        self.height = GRID_ROWS    * self.unit

        # get coefficient for fonts (dependency between font size and grid unit)
        self.coefficientFontFields = int(self.fontFields[1]) / self.unit
        self.coefficientFontText   = int(self.fontText[1])   / self.unit
        self.coefficientFont2048   = int(self.font2048[1])   / self.unit

        # initialize window
        self.setWindowSize()
        self.createUIElements()
        self.show()

        # bindings
        self.root.bind("<Enter>",     self.adjustWindowToCurrentWidth)
        self.root.bind("<Configure>", self.adjustWindowToCurrentState)
        self.root.bind("<Key>",       self.keyPressed)

        # keyboard shortcuts
        self.root.bind(KEYS_QUIT_GAME,        self.rootDestroy)
        self.root.bind(KEYS_NEW_GAME,         self.newGame)
        self.root.bind(KEYS_OPEN_GAME,        self.openGame)
        self.root.bind(KEYS_ZOOM_IN,          self.zoomIn)
        self.root.bind(KEYS_ZOOM_OUT,         self.zoomOut)
        self.root.bind(KEYS_ENTER_FULLSCREEN, self.enterFullscreen)
        self.root.bind(KEYS_EXIT_FULLSCREEN,  self.exitFullscreen)

        # call function to close gracefully
        self.root.protocol("WM_DELETE_WINDOW", self.rootDestroy)

        self.root.mainloop()

    def adjustWindowToCurrentState(self, event=None):
        """
        When state of window changes (normal <-> zoomed) the content has to
        be adjusted. Either default width or maximum width.
        """
        # zoomed to normal
        if((self.unit == self.root.winfo_screenheight()//GRID_ROWS-2 or
            self.unit == self.root.winfo_screenwidth()//GRID_COLUMNS) and
           self.root.state() == "normal"):
            width = DEFAULT_WIDTH_WINDOW
            self.setWindowSize(width)
        # normal to zoomed
        if(not (self.unit == self.root.winfo_screenheight()//GRID_ROWS-2 or
                self.unit == self.root.winfo_screenwidth()//GRID_COLUMNS) and
           self.root.state() == "zoomed"):
            width = self.root.winfo_screenwidth()
            self.setWindowSize(width)

    def adjustWindowToCurrentWidth(self, event=None):
        """
        After the user changed the window size, the window will be resized
        to new width (which includes size of content). The size of the
        window will not really change but the size of content.
        """
        width = self.root.winfo_width()
        self.setWindowSize(width)

    def setWindowSize(self, width=DEFAULT_WIDTH_WINDOW):
        """
        This function resizes the window. Depending on parameter "width" the
        size of a unit (in grid) is calculated. One unit should be at least
        5 pixels (which is actually very small, but must not be larger than
        possible. That means a maximum value for one unit is calculated
        depending on screen size and grid size. (Also some space for task bar
        should be available)
        When maximum unit size is reached the window will automatically switch
        to full screen (zoomed state).
        When window size has to be changed, also all elements in UI have to be
        adjusted.
        """
        # calculate unit, width and height
        self.unit = min(max(5, width // GRID_COLUMNS),
                        self.root.winfo_screenheight()//GRID_ROWS-2,
                        self.root.winfo_screenwidth()//GRID_COLUMNS)
        width  = GRID_COLUMNS * self.unit
        height = GRID_ROWS    * self.unit

        # set state of window (zoomed/normal)
        if(self.unit == self.root.winfo_screenheight()//GRID_ROWS-2 or
           self.unit == self.root.winfo_screenwidth()//GRID_COLUMNS):
            # max value -> full screen / zoomed
            self.root.state("zoomed")
        else:
            self.root.state("normal")

        # update window (also UI-elements if changed)
        size = str(width) + "x" + str(height)
        self.root.geometry(size)
        if(width != self.width or height != self.height):
            self.width  = width
            self.height = height
            self.hideUIElements()
            self.showUIElements()

    def labelField(self):
        """
        Factory method to create a field/tile containing the numbers.
        """
        return Label(self.root,
                     text   = "",
                     anchor = CENTER,
                     font   = self.fontFields)

    def labelText(self, text=""):
        """
        Factory method to create a text label.
        """
        return Label(self.root,
                     text = text,
                     bg   = self.bg,
                     font = self.fontText,
                     fg   = "#ffffff")

    def updateFontSize(self):
        """
        This function updates all font sizes (depending on new size of grid unit)
        and labels.
        """
        self.fontFields[1] = int(self.coefficientFontFields * self.unit)
        self.fontText[1]   = int(self.coefficientFontText   * self.unit)
        self.font2048[1]   = int(self.coefficientFont2048   * self.unit)
        
        for label in self.listLabels:
            label.config(font=self.fontText)

        self.label2048.config(font=self.font2048)
        
        for fields in self.field:
            for field in fields:
                field.config(font=self.fontFields)

    def showUIElements(self):
        """
        Labels and number fields are placed at their posiiton depending on grid.
        Afterwards fonts and content will be updated.
        """
        for i in range(4):
            self.listLabels[i].place(x =      26*self.unit,
                                     y = (6*i+1)*self.unit,
                                     width  =  9*self.unit,
                                     height =  5*self.unit)
                
        for y in range(4):
            for x in range(4):
                self.field[y][x].place(x= 6*self.unit*x+self.unit,
                                       y= 6*self.unit*y+self.unit,
                                       width  = 5*self.unit,
                                       height = 5*self.unit)

        self.updateFontSize()
        self.show()

    def hideUIElements(self):
        """
        During resize old labels and fields have to be removed.
        """
        for label in self.listLabels:
            label.place_forget()

        for fields in self.field:
            for field in fields:
                field.place_forget()

    def createUIElements(self):
        """
        This function creates all number fields and labels and sets up general
        settings for these (text, fonts, colours, bindings).
        """
        self.labelScore     = self.labelText()
        self.labelHighScore = self.labelText()
        
        self.label2048 = Label(self.root,
                               text = "2048",
                               bg   = self.bg,
                               font = self.font2048,
                               fg   = self.fg2048)

        self.labelNewGame = self.labelText("New Game")
        self.labelNewGame.config(relief=RIDGE)
        self.labelNewGame.bind("<Button-1>", self.newGame)

        self.listLabels = [self.labelScore,
                           self.labelHighScore,
                           self.label2048,
                           self.labelNewGame]
        
        self.field00 = self.labelField()
        self.field01 = self.labelField()
        self.field02 = self.labelField()
        self.field03 = self.labelField()
        
        self.field10 = self.labelField()
        self.field11 = self.labelField()
        self.field12 = self.labelField()
        self.field13 = self.labelField()

        self.field20 = self.labelField()
        self.field21 = self.labelField()
        self.field22 = self.labelField()
        self.field23 = self.labelField()

        self.field30 = self.labelField()
        self.field31 = self.labelField()
        self.field32 = self.labelField()
        self.field33 = self.labelField()

        self.field = [[self.field00, self.field01, self.field02, self.field03],
                      [self.field10, self.field11, self.field12, self.field13],
                      [self.field20, self.field21, self.field22, self.field23],
                      [self.field30, self.field31, self.field32, self.field33]]
        
        self.showUIElements()

    def confirmAction(self, msgboxHeading, msgboxText):
        """
        Critical actions need to be confirmed. This functions creates a
        message box to ask the user whether he is sure to continue.
        This will only happen if game is not finished, otherwise the action
        can continue (because a finished game is not supposed to be critical).
        """
        if(not self.game.isFinished()):
            # game is not finished yet
            answer = messagebox.askyesno(msgboxHeading,
                                         msgboxText)
            return answer

        # return True per default when game is finished
        return True

    def rootDestroy(self, event=None):
        """
        This functions closes the window gracefully when confirmed again.
        """
        if(self.confirmAction("Quit?","Do you really want to quit?")):
            self.game.writeHighScore()
            self.root.destroy()

    def newGame(self, event=None):
        """
        After confirming this action, old game will be saved and a new game
        will be created. Afterwards UI has to be updated.
        """
        if(self.confirmAction("New Game?",
                              "Do you really want to start a new game?")):
            self.game.writeHighScore()
            self.game.newGame()
            self.show()

    def openGame(self, event=None):
        return

    def zoomIn(self, event=None):
        """
        This function will increment grid unit to make content larger.
        """
        self.setWindowSize(self.width + GRID_COLUMNS)

    def zoomOut(self, event=None):
        """
        This function will decrement grid unit to make content smaller.
        """
        self.setWindowSize(self.width - GRID_COLUMNS)

    def enterFullscreen(self, event=None):
        """
        This function will switch to fullscreen mode
        """
        self.root.state("zoomed")

    def exitFullscreen(self, event=None):
        """
        This function will switch back to normal mode (default size)
        """
        self.root.state("normal")

    def keyPressed(self, event):
        """
        When a key is pressed, it will check whether pressed key should
        trigger a move.
        Also some additional keys for resize etc. can be processed here.
        """
        for direction in range(4):
            if(event.keysym in self.keys[direction]):
                self.game.move(direction)
                self.show()
                return

    def getColours(self, number):
        """
        This functions returns a list [exponent, fg, bg] for passed number.
        """
        if(number <= 0): number=1
        ix = int(log2(number))
        return self.colours[ix]

    def show(self):
        """
        This function updates content and appearence of fields.
        Also current score and highscore are shown. Depending on current game
        status (finished or not) the background colour is adjusted.
        """
        for y in range(4):
            for x in range(4):
                currentNumber = self.game.field[y][x]
                colours       = self.getColours(currentNumber)
                self.field[y][x].config(fg=colours[1], bg=colours[2])
                if(currentNumber):
                    self.field[y][x]["text"] = currentNumber
                else:
                    self.field[y][x]["text"] = ""

        self.labelScore["text"]     =     "Score:\n" + str(self.game.score)
        self.labelHighScore["text"] = "Highscore:\n" + str(self.game.highscore)

        if(self.game.isFinished()):
            for element in [self.root] + self.listLabels:
                element.config(bg = self.bgEndOfGame)
        else:
            for element in [self.root] + self.listLabels:
                element.config(bg = self.bg)

        self.root.update()

"""
Class Game
This class implements the backend including following important functions:

 - move(direction)
    0 - move north / up
    1 - move east  / right
    2 - move south / down
    3 - move west  / left
 - readHighScore()
 - writeHighScore()
 - newGame()
 - isFinished()

"""
class Game:
    def __init__(self):
        # define probability of fours when random numbers appear (in percent)
        self.probability4 = 10

        # construct filename of highscore file
        self.initFileName()

        # initialize a new game
        self.newGame()

    def newGame(self):
        # initialize/reset field and values
        self.initField()
        self.initValues()

    def initValues(self):
        """
        This function initializes all variables which are necessary beside
        the field / numbers.
        """
        self.score = 0 # max: 3932164
        self.round = 0
        self.readHighScore()

    def initFileName(self):
        """
        This function gets filepath/-name for highscore file. It has to be
        in same directory in which the script is.
        """
        # get directory in which the script/file (2048.py) is located
        pathDir = os.path.dirname(os.path.abspath(__file__))

        # append specified filename to directory of script
        self.filename = pathDir + "\\" + FILENAME_HIGHSCORE

    def initField(self):
        """
        This function creates an empty field and inserts two random numbers.
        """
        self.field  = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]

        self.insertRandomNumber()
        self.insertRandomNumber()

    def readHighScore(self):
        """
        This function tries to read a high score from file. When this is not
        possible the highscore is initalized.
        """
        try:
            with open(self.filename, "r") as f:
                self.highscore = int(f.readlines()[0].strip())
        except Exception as e:
            print("Can't read highscore from file", FILENAME_HIGHSCORE)
            print("***", e)
            self.highscore = 0

    def writeHighScore(self):
        """
        This functions tries to write the high score in the file.
        """
        self.highscore = max(self.highscore, self.score)
        try:
            with open(self.filename, "w") as f:
                f.write(str(self.highscore))
        except Exception as e:
            print("Can't write highscore", self.highscore,
                  "into file", FILENAME_HIGHSCORE)
            print("***", e)

    def move(self, direction):
        """
        This function implements the fundamental part of the game.
        It moves and merges the tiles in passed direction.
        Direction has to be 0,1,2,3 (N,E,S,W)
        When move was successful (something changed/merged) a new number
        will be inserted, round will be incremented, highscore updated and
        True will be returned.
        """
        new = [self.__move_north,
               self.__move_east,
               self.__move_south,
               self.__move_west][direction]()
        
        if(self.field != new):
            self.field = new
            self.insertRandomNumber()
            self.round += 1
            self.highscore = max(self.score, self.highscore)
            return True
        return False
    
    def __move_north(self):
        new = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for x in range(0,4):
            # 1. get list without empty fields for each column (just numbers)
            values = []
            for y in range(0,4):
                if(self.field[y][x] != 0): values.append(self.field[y][x])
            # 2. merge
            i = 0
            while(i < len(values)-1):
                if(values[i] == values[i+1]):
                    values[i] *= 2
                    self.score += values[i]
                    del values[i+1]
                i += 1
            # 3. fill numbers in new field
            y = 0
            for number in values:
                new[y][x] = number
                y += 1
        return new

    def __move_west(self):
        new = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for y in range(0,4):
            # 1. get list without empty fields for each row (just numbers)
            values = []
            for x in range(0,4):
                if(self.field[y][x] != 0): values.append(self.field[y][x])
            # 2. merge
            i = 0
            while(i < len(values)-1):
                if(values[i] == values[i+1]):
                    values[i] *= 2
                    self.score += values[i]
                    del values[i+1]
                i += 1
            # 3. fill numbers in new field
            x = 0
            for number in values:
                new[y][x] = number
                x += 1
        return new

    def __move_south(self):
        new = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for x in range(0,4):
            # 1. get list without empty fields for each column (just numbers)
            values = []
            for y in range(3,-1,-1):
                if(self.field[y][x] != 0): values.append(self.field[y][x])
            # 2. merge
            i = 0
            while(i < len(values)-1):
                if(values[i] == values[i+1]):
                    values[i] *= 2
                    self.score += values[i]
                    del values[i+1]
                i += 1
            # 3. fill numbers in new field
            y = 3
            for number in values:
                new[y][x] = number
                y -= 1
        return new

    def __move_east(self):
        new = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for y in range(0,4):
            # 1. get list without empty fields for each row (just numbers)
            values = []
            for x in range(3,-1,-1):
                if(self.field[y][x] != 0): values.append(self.field[y][x])
            # 2. merge
            i = 0
            while(i < len(values)-1):
                if(values[i] == values[i+1]):
                    values[i] *= 2
                    self.score += values[i]
                    del values[i+1]
                i += 1
            # 3. fill numbers in new field
            x = 3
            for number in values:
                new[y][x] = number
                x -= 1
        return new

    def insertRandomNumber(self):
        """
        This function inserts 2 or 4 at random field (must be free).
        Empty fields are numbered from 1 to n from top left to bottom right
        corner. A random number decides which of these fields is chosen. The
        functions loops through the field line by line and counts number of
        empty fields to find chosen field. Which number has to be inserted
        will be decided by randomness again (using previously defined
        probabilty for a 4). At the end coordinates of field where new number
        was inserted will be returned.
        """
        nulls = self.getNumNullValues()
        if(nulls == 0): return False
        r = randint(1, nulls)
        counter0 = 0
        for y in range(4):
            for x in range(4):
                if(self.field[y][x] == 0):
                    counter0 += 1
                    if(r == counter0):
                        if(randint(1,100) <= self.probability4):
                            self.field[y][x] = 4
                        else:
                            self.field[y][x] = 2
                        return (y,x)

    def getNumNullValues(self):
        """
        This function returns number of empty fields
        """
        num = 0
        for row in self.field:
            for number in row:
                if(number == 0): num += 1
        return num

    def isFinished(self):
        """
        This functions returns whether game is finshed or not.
        A game is finished when no more move can be done. This is obviously
        not the case when there are empty fields (at least one). A move is
        also possible when some adjacent fields have same values and can be
        merged (Von Neumann neighborhood).
        """
        if(self.getNumNullValues() == 0):
            # every field is filled, now check for possible merging
            for y in range(0,4):
                for x in range(0,4):
                    if(x != 3):
                        if(self.field[y][x] == self.field[y][x+1]):
                            return False # merging is possible
                    if(y != 3):
                        if(self.field[y][x] == self.field[y+1][x]):
                            return False # merging is possible
            return True
        else:
            # some empty fields
            return False

    def show(self):
        """
        This show function prints current game status and is only used
        for debugging.
        """
        print("Score:", self.score,
              "Round:", self.round,
              "HighScore:", self.highscore,
              self.field)
        # get max number
        maxnum = 0
        for row in self.field:
            for number in row:
                maxnum = max(maxnum, number)
        maxlen = len(str(maxnum))
        # print
        for row in self.field:
            for number in row:
                if(number):
                    print(" "*(maxlen-len(str(number)))+str(number), end=" ")
                else:
                    print(" "*maxlen, end=" ")
            print("")

gui = UI()
