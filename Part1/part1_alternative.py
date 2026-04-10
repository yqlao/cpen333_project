# Group#: 13A
# Student Names: Renzon Gabriel, Yuqi Lao

"""
    This program implements a variety of the snake 
    game. Instead of using tkinter, we use PyQt5 for GUI. 
"""

import threading
import queue
import random
import time

#PyQt5 library with modules and classes to be used 
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QPushButton, QGraphicsLineItem, QLabel
)
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt, QTimer, QLineF, QRectF, QObject, QEvent

# ----- NEW GUI CLASS TO ADJUST FOR PYQT5 -----
class Gui(QMainWindow):
    """
        This updated class takes care of the game's graphic user interface (gui)
        creation and termination with use of PyQt5 library 
        that takes the QMainWindow class for window management.
    """
    def __init__(self):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        super().__init__()
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        #Background View
        self.bg = QGraphicsScene(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.bg.setBackgroundBrush(QBrush(Qt.black))
        self.bgview = QGraphicsView(self.bg, self)
        self.bgview.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.bgview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bgview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #To install event filter for key access
        self._keyDetection = KeyDetection(self)
        self.bgview.installEventFilter(self._keyDetection)

        #Initial score Display
        self.scoreLabel = QLabel("Your Score: 0", self)

        #Initial prey display
        self.preyIcon = self.bg.addRect(
            QRectF(0, 0, PREY_ICON_WIDTH, PREY_ICON_WIDTH),
            QPen(Qt.white),
            QBrush(Qt.white)
        )

        #Initial snake coordinates list
        self.__snakelist = []

    #------For queue handler method calls---------
    #for move task 
    def updateSnake(self, coordinates):
        """
            This method is used for the move task on the queue handler
            to update the snake.
        """
        drawSnake = QPen(Qt.white, SNAKE_ICON_WIDTH)

        # if there are n points, there are n-1 segments
        maxSegments = max(len(coordinates) - 1, 0) 

        # adding line graphics when snake grows
        while len(self.__snakelist) < maxSegments:
            snake_extend = QGraphicsLineItem()  #create new line
            snake_extend.setPen(drawSnake)
            self.bg.addItem(snake_extend) # add to screen
            self.__snakelist.append(snake_extend)

        # to position new lines on the correct coordinates
        for i, snake_extend in enumerate(self.__snakelist):
            x0, y0 = coordinates[i]
            x1, y1 = coordinates[i + 1]
            snake_extend.setLine(QLineF(x0, y0, x1, y1))
            snake_extend.setPen(drawSnake) #moving line to new position

    def updatePrey(self, coordinates):
        """
            This method is used for the move task on the queue handler
            to update the snake.
        """
        x1, y1, x2, y2 = coordinates #we update 4 coordinates of the prey
        self.preyIcon.setRect(QRectF(x1, y1, x2 - x1, y2 - y1))

    def updateScore(self, score):
        """
            This method is used for the score task on the queue handler
            to update the score.
        """
        self.scoreLabel.setText(f"Your Score: {score}") 

    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        btn = QPushButton("Game Over!")
        btn.setFixedSize(125, 75)
        btn.clicked.connect(self.close) #to close window when clicked
        proxy = self.bg.addWidget(btn)
        proxy.setPos(187.5, 112.5) 

class KeyDetection(QObject):
    """
        To ensure pressing arrow keys are detected properly
        before the queue handler tasks run on the window.
    """
    def eventFilter(self, object, event):
        """
            Qt class to monitor every event 
            and know whether arrow keys are pressed
        """
        # Checking if event pressed one of the arrow keys
        if event.type() == QEvent.KeyPress:
            direction = KEY_MAP.get(event.key()) #map key to direction

            if direction: # if the key detected is an arrow key
                game.whenAnArrowKeyIsPressed(direction) #move snake to direction
                return True 
            
        #otherwise return to default 
        return super().eventFilter(object, event) 
    
class QueueHandler:
    """
        This class implements the queue handler for the game.
    """
    def __init__(self):
        self.queue = gameQueue
        self.gui = gui
        self.timer = QTimer()
        self.timer.timeout.connect(self.queueHandler)
        self.timer.start(16)

    def queueHandler(self):
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    gui.updateSnake(task["move"])
                elif "prey" in task:
                    gui.updatePrey(task["prey"])
                elif "score" in task:
                    gui.updateScore(task["score"])
                self.queue.task_done()
        except queue.Empty:
            pass

class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = gameQueue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.createNewPrey()

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15     #speed of snake updates (sec)
        
        while self.gameNotOver:
            #complete the method implementation below

            #the snake moves while the game is not over
            self.move()
            #to call the speed of the snake 
            time.sleep(SPEED)

    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction

        # We remove keysym and modify code
        if (currentDirection == "Left"  and e == "Right" or
            currentDirection == "Right" and e == "Left"  or
            currentDirection == "Up"    and e == "Down"  or
            currentDirection == "Down"  and e == "Up"):
            return
        
        self.direction = e

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        NewSnakeCoordinates = self.calculateNewCoordinates()
        #complete the method implementation below

        #Make snake longer by adding NewSnakeCoordinates to the list
        self.snakeCoordinates.append(NewSnakeCoordinates)

        #Formula to find the maximum distance between snake and prey 
        # to ensure when snake touches prey it eats it
        # (additional info on documentation)
        EAT_PREY_DISTANCE: int = (SNAKE_ICON_WIDTH + PREY_ICON_WIDTH) // 2

        #Finding distance between prey and snake of x and y coordinates
        x_closeness: int = abs(NewSnakeCoordinates[0] - self.preyPosition[0])
        y_closeness: int = abs(NewSnakeCoordinates[1] - self.preyPosition[1])
        
        #If both x and y distance fall under the maximum distance, add one point to the score
        #   and add new prey 
        if (x_closeness <= EAT_PREY_DISTANCE and y_closeness <= EAT_PREY_DISTANCE):
            self.score += 1
            #Call score task in queue handler
            self.queue.put({"score": self.score})
            self.createNewPrey()
        #Need to ensure we remove the tail when it doesn't eat prey or else it would extend
        #    from just moving
        else:
            self.snakeCoordinates.pop(0)

        #Call move task in queue handler
        self.queue.put({"move": self.snakeCoordinates.copy()})

        #To consistently check if game over 
        self.isGameOver(NewSnakeCoordinates)

    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        lastX, lastY = self.snakeCoordinates[-1]
        #complete the method implementation below

        move_basis: int = 10 #how much snake moves in one step
        currentDirection = self.direction

        #We return a tuple that represents next positioning of snake
        #   with if-else statements.
        if currentDirection == "Left":
            return (lastX - move_basis, lastY)
        elif currentDirection == "Right":
            return (lastX + move_basis, lastY)
        elif currentDirection == "Up":
            return (lastX, lastY - move_basis)
        elif currentDirection == "Down":
            return (lastX, lastY + move_basis)
        #in tkinter, y increases downward

    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates
        #complete the method implementation below

        #We use boolean to check whether the snake has:

        # --- Passed any wall -----
        wallHit: bool = (x <= 0 or x >= WINDOW_WIDTH or y <= 0 or y >= WINDOW_HEIGHT)

        # --- Bit itself ----------
        selfBite: bool = snakeCoordinates in self.snakeCoordinates[:-1]
    
        #If either is True, it's Game Over
        if selfBite or wallHit:
            #update gameNotOver field
            self.gameNotOver = False
            #call game over task in queue handler
            self.queue.put({"game_over":True})
        
    def createNewPrey(self) -> None:
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD = 15   #sets how close prey can be to borders
        #complete the method implementation below

        #constants from GUI class of coordinates for score text
        scoreTextXLocation: int = 0
        scoreTextYLocation: int = 15

        #Formula to find the maximum distance between snake and prey 
        # to ensure new prey is entirely away from snake 
        # (additional info on documentation)
        DISTANCE_FROM_SNAKE: int = (SNAKE_ICON_WIDTH + PREY_ICON_WIDTH) // 2

        while True:
            #Generate random x and y coordinates to choose where prey appears,
            #  with THRESHOLD for coordinates to be away from walls.
            x: int = random.randint(THRESHOLD, WINDOW_WIDTH - THRESHOLD)
            y: int = random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD)

            #Condition 1 :
            #     If x and y coordinates lie beneath the score text
            #     estimated to be between these location values
            x_loc: bool = x > scoreTextXLocation and x < 200
            y_loc: bool = y > scoreTextYLocation and y < 26

            #Generate new coordinates until we find coordinates out of score text
            while x_loc and y_loc:
                x = random.randint(THRESHOLD, WINDOW_WIDTH - THRESHOLD)
                y = random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD)

            #Condition 2 :
            #     Looping all the tuples of coordinates in the snakeCoordinates list
            #     following same algorithm in the move function
            #     ensuring new prey doesn't touch snake
            for (snake_x, snake_y) in self.snakeCoordinates:
                x_closeness: int = abs(x - snake_x)
                y_closeness: int = abs(y - snake_y)
                if (x_closeness <= DISTANCE_FROM_SNAKE and y_closeness <= DISTANCE_FROM_SNAKE):
                    break # choose x and y values again
            
            #break loop when finally chosen x and y values
            break

        #After loop choosing final x and y values to choose center coordinates of prey
        self.preyPosition: tuple = (x,y)
        
        #Formula to find all preyCoordinates with constant PREY_ICON_WIDTH //2
        preyCoordinates: tuple = (
            x - PREY_ICON_WIDTH // 2, y - PREY_ICON_WIDTH // 2,
            x + PREY_ICON_WIDTH // 2, y + PREY_ICON_WIDTH // 2
        )

        #Call prey task in queue handler
        self.queue.put({"prey": preyCoordinates})


if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300
    SNAKE_ICON_WIDTH = 10
    #add the specified constant PREY_ICON_WIDTH here  
    PREY_ICON_WIDTH = 7

    BACKGROUND_COLOUR = "black"   #you may change this colour if you wish
    ICON_COLOUR = "white"        #you may change this colour if you wish

    # Dictionary of arrows for direction of snake
    KEY_MAP: dict = {
        Qt.Key_Left:  "Left",
        Qt.Key_Right: "Right",
        Qt.Key_Up:    "Up",
        Qt.Key_Down:  "Down",
    }

    #create main application, required for PyQt GUI
    app = QApplication(sys.argv) 

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game()        #instantiate the game object

    gui = Gui()    #instantiate the game user interface
    gui.show()     # display gui
    
    qh = QueueHandler()  #instantiate the queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start GUI event loop 
    sys.exit(app.exec_()) 
    
