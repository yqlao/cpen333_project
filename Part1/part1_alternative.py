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
import sys

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene,
    QPushButton, QGraphicsLineItem, QLabel
)
from PyQt5.QtGui import QPen, QBrush
from PyQt5.QtCore import Qt, QTimer, QLineF, QRectF, QObject, QEvent


# ── Key constants ─────────────────────────────────────────────────────────────
KEY_MAP = {
    Qt.Key_Left:  "Left",
    Qt.Key_Right: "Right",
    Qt.Key_Up:    "Up",
    Qt.Key_Down:  "Down",
}


class KeyFilter(QObject):
    """
    Event filter installed on QGraphicsView.
    Intercepts key presses so arrow keys work even when the view has focus
    (which it always does on Mac).
    """
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            direction = KEY_MAP.get(event.key())
            if direction:
                game.whenAnArrowKeyIsPressed(direction)
                return True          # swallow the event
        return super().eventFilter(obj, event)

class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)

        # ── Scene & View ──────────────────────────────────────────────────────
        self.scene = QGraphicsScene(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.scene.setBackgroundBrush(QBrush(Qt.black))

        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ── Mac fix: install key filter on the view ───────────────────────────
        self._keyFilter = KeyFilter(self)
        self.view.installEventFilter(self._keyFilter)

        # ── Score label ───────────────────────────────────────────────────────
        self.scoreLabel = QLabel("Your Score: 0", self)

        # ── Prey icon ─────────────────────────────────────────────────────────
        self.preyIcon = self.scene.addRect(
            QRectF(0, 0, PREY_ICON_WIDTH, PREY_ICON_WIDTH),
            QPen(Qt.white),
            QBrush(Qt.white)
        )

        # ── Snake segments ────────────────────────────────────────────────────
        self._snakeSegments = []

    # ── Fallback: also handle on the window itself ────────────────────────────
    def keyPressEvent(self, event):
        direction = KEY_MAP.get(event.key())
        if direction:
            game.whenAnArrowKeyIsPressed(direction)

    # ── GUI update methods ────────────────────────────────────────────────────
    def updateSnake(self, coordinates):
        pen = QPen(Qt.white, SNAKE_ICON_WIDTH)

        needed = max(len(coordinates) - 1, 0)

        while len(self._snakeSegments) < needed:
            item = QGraphicsLineItem()
            item.setPen(pen)
            self.scene.addItem(item)
            self._snakeSegments.append(item)

        while len(self._snakeSegments) > needed:
            item = self._snakeSegments.pop()
            self.scene.removeItem(item)

        for i, item in enumerate(self._snakeSegments):
            x1, y1 = coordinates[i]
            x2, y2 = coordinates[i + 1]
            item.setLine(QLineF(x1, y1, x2, y2))
            item.setPen(pen)

    def updatePrey(self, coords):
        x1, y1, x2, y2 = coords
        self.preyIcon.setRect(QRectF(x1, y1, x2 - x1, y2 - y1))

    def updateScore(self, score):
        self.scoreLabel.setText(f"Your Score: {score}")

    def gameOver(self):
        btn = QPushButton("Game Over!")
        btn.setFixedSize(160, 60)
        btn.clicked.connect(self.close)
        proxy = self.scene.addWidget(btn)
        proxy.setPos(170, 120)


class QueueHandler:
    def __init__(self):
        self.queue = gameQueue
        self.gui = gui
        self.timer = QTimer()
        self.timer.timeout.connect(self.queueHandler)
        self.timer.start(16)

    def queueHandler(self):
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

        # We remove keysym
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
        EAT_PREY_DISTANCE = (SNAKE_ICON_WIDTH + PREY_ICON_WIDTH) // 2

        #Finding distance between prey and snake of x and y coordinates
        x_closeness = abs(NewSnakeCoordinates[0] - self.preyPosition[0])
        y_closeness = abs(NewSnakeCoordinates[1] - self.preyPosition[1])
        
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

        move_basis = 10 #how much snake moves in one step
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
        wallHit = (x <= 0 or x >= WINDOW_WIDTH or y <= 0 or y >= WINDOW_HEIGHT)

        # --- Bit itself ----------
        selfBite = snakeCoordinates in self.snakeCoordinates[:-1]
    
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

        #Formula to find the maximum distance between snake and prey 
        # to ensure new prey is entirely away from snake 
        # (additional info on documentation)
        DISTANCE_FROM_SNAKE = (SNAKE_ICON_WIDTH + PREY_ICON_WIDTH) // 2

        scoreTextXLocation = 60
        scoreTextYLocation = 15

        while True:
            #Generate random x and y coordinates to choose where prey appears,
            #  with THRESHOLD for coordinates to be away from walls.
            x = random.randint(THRESHOLD, WINDOW_WIDTH - THRESHOLD)
            y = random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD)

            #x_loc = x > scoreTextXLocation or x < 200
            #y_loc = y > scoreTextYLocation or y < 25

            #while x_loc and y_loc:
                #x = random.randint(THRESHOLD, WINDOW_WIDTH - THRESHOLD)
                #y = random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD)

            #Looping all the tuples of coordinates in the snakeCoordinates list
            #  following same algorithm in the move function
            #  ensuring new prey doesn't touch snake
            for (snake_x, snake_y) in self.snakeCoordinates:
                x_closeness = abs(x - snake_x)
                y_closeness = abs(y - snake_y)
                if (x_closeness <= DISTANCE_FROM_SNAKE and y_closeness <= DISTANCE_FROM_SNAKE):
                    break # choose x and y values again
            
            #break loop when finally chosen x and y values
            break

        #After loop choosing final x and y values to choose center coordinates of prey
        self.preyPosition = (x,y)
        
        #Formula to find all preyCoordinates with constant PREY_ICON_WIDTH //2
        preyCoordinates = (
            x - PREY_ICON_WIDTH // 2, y - PREY_ICON_WIDTH // 2,
            x + PREY_ICON_WIDTH // 2, y + PREY_ICON_WIDTH // 2
        )

        #Call prey task in queue handler
        self.queue.put({"prey": preyCoordinates})

if __name__ == "__main__":
    WINDOW_WIDTH      = 500
    WINDOW_HEIGHT     = 300
    SNAKE_ICON_WIDTH  = 10
    PREY_ICON_WIDTH   = 7
    BACKGROUND_COLOUR = "black"
    ICON_COLOUR       = "white"

    app = QApplication(sys.argv)

    gameQueue = queue.Queue()
    game = Game()
    gui  = Gui()
    gui.show()

    qh = QueueHandler()

    threading.Thread(target=game.superloop, daemon=True).start()

    sys.exit(app.exec_())
