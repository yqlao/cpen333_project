# Group#: 13A
# Student Names: Renzon Gabriel, Yuqi Lao

"""
    Snake game — PyQt5 (fully debugged)

    Bugs fixed from previous version:
    1. whenAnArrowKeyIsPressed() still used tkinter's e.keysym — 
       changed to accept a plain string direction instead.
    2. __main__ block had both tkinter (gui.root.mainloop()) and 
       PyQt5 (app.exec_()) startup code mixed together — removed 
       all tkinter remnants, kept only PyQt5 startup.
    3. createNewPrey() loop logic was broken — the inner for-loop 
       would always hit the outer break regardless of collision, 
       so prey could spawn on top of the snake. Fixed with a flag.
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
from PyQt5.QtGui  import QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QTimer, QLineF, QRectF, QObject, QEvent

# ---------------------------------------------------------------------------
KEY_MAP = {
    Qt.Key_Left:  "Left",
    Qt.Key_Right: "Right",
    Qt.Key_Up:    "Up",
    Qt.Key_Down:  "Down",
}


# ---------------------------------------------------------------------------
class KeyFilter(QObject):
    """
    Installed on QGraphicsView so arrow keys are caught even when
    the view (not the window) holds focus — required on macOS.
    """
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            direction = KEY_MAP.get(event.key())
            if direction:
                game.whenAnArrowKeyIsPressed(direction)   # pass string, not event
                return True
        return super().eventFilter(obj, event)


# ---------------------------------------------------------------------------
class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snake")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT + 30)
        self.setStyleSheet("background-color: black;")

        # QGraphicsScene = logical canvas | QGraphicsView = the widget that shows it
        self.scene = QGraphicsScene(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.scene.setBackgroundBrush(QBrush(QColor(BACKGROUND_COLOUR)))

        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 30, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setStyleSheet("border: 0px;")

        # macOS fix — intercept keys at the view level
        self._keyFilter = KeyFilter(self)
        self.view.installEventFilter(self._keyFilter)
        self.view.setFocusPolicy(Qt.StrongFocus)
        self.view.setFocus()

        # Score label lives in the 30-px header above the scene
        self.scoreLabel = QLabel("Your Score: 0", self)
        f = QFont("Helvetica", 11)
        f.setBold(True)
        self.scoreLabel.setFont(f)
        self.scoreLabel.setStyleSheet("color: white; background: black;")
        self.scoreLabel.setGeometry(5, 5, 200, 22)

        # Prey — one permanent rect item; we just move it
        self.preyIcon = self.scene.addRect(
            QRectF(0, 0, PREY_ICON_WIDTH, PREY_ICON_WIDTH),
            QPen(QColor(ICON_COLOUR)),
            QBrush(QColor(ICON_COLOUR))
        )

        # Snake — list of QGraphicsLineItems, recycled every frame
        self._snakeSegments = []

    # window-level fallback (works on Windows/Linux)
    def keyPressEvent(self, event):
        direction = KEY_MAP.get(event.key())
        if direction:
            game.whenAnArrowKeyIsPressed(direction)

    # --- GUI update helpers -------------------------------------------------
    def updateSnake(self, coordinates):
        pen = QPen(QColor(ICON_COLOUR), SNAKE_ICON_WIDTH)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        needed = max(len(coordinates) - 1, 0)

        while len(self._snakeSegments) < needed:
            item = QGraphicsLineItem()
            item.setPen(pen)
            self.scene.addItem(item)
            self._snakeSegments.append(item)

        while len(self._snakeSegments) > needed:
            self.scene.removeItem(self._snakeSegments.pop())

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
        btn.setFont(QFont("Helvetica", 14, QFont.Bold))
        btn.setFixedSize(160, 60)
        btn.clicked.connect(self.close)
        self.scene.addWidget(btn).setPos(170, 120)


# ---------------------------------------------------------------------------
class QueueHandler:
    def __init__(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self._poll)
        self.timer.start(16)          # ~60 fps

    def _poll(self):
        try:
            while True:
                task = gameQueue.get_nowait()
                if   "game_over" in task: gui.gameOver()
                elif "move"      in task: gui.updateSnake(task["move"])
                elif "prey"      in task: gui.updatePrey(task["prey"])
                elif "score"     in task: gui.updateScore(task["score"])
                gameQueue.task_done()
        except queue.Empty:
            pass


# ---------------------------------------------------------------------------
class Game:
    def __init__(self):
        self.queue = gameQueue
        self.score = 0
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        self.direction    = "Left"
        self.gameNotOver  = True
        self.createNewPrey()

    def superloop(self):
        SPEED = 0.15
        while self.gameNotOver:
            self.move()
            time.sleep(SPEED)

    # BUG FIX 1 — was: e.keysym  (tkinter Event attribute)
    #             now: direction is already a plain string passed by KeyFilter
    def whenAnArrowKeyIsPressed(self, direction: str) -> None:
        cur = self.direction
        if (cur == "Left"  and direction == "Right" or
            cur == "Right" and direction == "Left"  or
            cur == "Up"    and direction == "Down"  or
            cur == "Down"  and direction == "Up"):
            return
        self.direction = direction

    def move(self) -> None:
        new = self.calculateNewCoordinates()
        self.snakeCoordinates.append(new)

        EAT_PREY_DISTANCE = (SNAKE_ICON_WIDTH + PREY_ICON_WIDTH) // 2
        x_close = abs(new[0] - self.preyPosition[0])
        y_close = abs(new[1] - self.preyPosition[1])

        if x_close <= EAT_PREY_DISTANCE and y_close <= EAT_PREY_DISTANCE:
            self.score += 1
            self.queue.put({"score": self.score})
            self.createNewPrey()
        else:
            self.snakeCoordinates.pop(0)

        self.queue.put({"move": self.snakeCoordinates.copy()})
        self.isGameOver(new)

    def calculateNewCoordinates(self) -> tuple:
        lastX, lastY = self.snakeCoordinates[-1]
        step = 10
        if   self.direction == "Left":  return (lastX - step, lastY)
        elif self.direction == "Right": return (lastX + step, lastY)
        elif self.direction == "Up":    return (lastX, lastY - step)
        elif self.direction == "Down":  return (lastX, lastY + step)

    def isGameOver(self, snakeCoordinates) -> None:
        x, y = snakeCoordinates
        wallHit  = (x < 0 or x >= WINDOW_WIDTH or y < 0 or y >= WINDOW_HEIGHT)
        selfBite = snakeCoordinates in self.snakeCoordinates[:-1]
        if wallHit or selfBite:
            self.gameNotOver = False
            self.queue.put({"game_over": True})

    # BUG FIX 2 — previous loop always broke out after the first x/y pick
    #             regardless of collision; fixed with a proper boolean flag
    def createNewPrey(self) -> None:
        THRESHOLD        = 15
        DISTANCE_FROM_SNAKE = (SNAKE_ICON_WIDTH + PREY_ICON_WIDTH) // 2

        while True:
            x = random.randint(THRESHOLD, WINDOW_WIDTH  - THRESHOLD)
            y = random.randint(THRESHOLD, WINDOW_HEIGHT - THRESHOLD)

            too_close = False
            for (sx, sy) in self.snakeCoordinates:
                if abs(x - sx) <= DISTANCE_FROM_SNAKE and abs(y - sy) <= DISTANCE_FROM_SNAKE:
                    too_close = True
                    break

            if not too_close:
                break          # only exit when we found a safe position

        self.preyPosition = (x, y)
        self.queue.put({"prey": (
            x - PREY_ICON_WIDTH // 2, y - PREY_ICON_WIDTH // 2,
            x + PREY_ICON_WIDTH // 2, y + PREY_ICON_WIDTH // 2
        )})


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    WINDOW_WIDTH      = 500
    WINDOW_HEIGHT     = 300
    SNAKE_ICON_WIDTH  = 10
    PREY_ICON_WIDTH   = 7
    BACKGROUND_COLOUR = "black"
    ICON_COLOUR       = "white"

    # BUG FIX 3 — previous __main__ had BOTH tkinter (gui.root.mainloop())
    #             and PyQt5 (app.exec_()) startup code — only PyQt5 below
    app = QApplication(sys.argv)

    gameQueue = queue.Queue()
    game      = Game()
    gui       = Gui()
    gui.show()

    QueueHandler()

    threading.Thread(target=game.superloop, daemon=True).start()

    sys.exit(app.exec_())
