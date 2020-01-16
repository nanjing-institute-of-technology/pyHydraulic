import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class QDMGraphicsScene(QGraphicsScene):
    def __init__(self, scene, parent=None):
        super().__init__(parent)

        self.scene = scene

        # settings
        self.gridSize = 50 # 每个大格子里面有几个小格子
        self.gridSquares = 5  # 每个大格子里面有几个小格子
        # 颜色选择：https://doc.qt.io/qtforpython/PySide2/QtGui/QColor.html
        self._color_background = QColor("#151550")  # QColor("#393939")
        self._color_light =  QColor("#0000CD")  # QColor("#2f2f2f")
        self._color_dark = QColor("#0000CD")  # QColor("#292929")
        # 小格子的笔
        self._pen_light = QPen(self._color_light)
        self._pen_light.setWidth(1)
        self._grid_enble = True

        # 大格子的笔
        self._pen_dark = QPen(self._color_dark)
        self._pen_dark.setWidth(2)
        # 用来画原点出的十字线的笔
        self._pen_red = QPen(Qt.red)
        self._pen_red.setStyle(Qt.SolidLine)
        self._pen_red.setWidth(5)
        # 刷背景
        self.setBackgroundBrush(self._color_background)


    def setGrScene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        if self._grid_enble:
            # here we create our grid
            left = int(math.floor(rect.left()))
            right = int(math.ceil(rect.right()))
            top = int(math.floor(rect.top()))
            bottom = int(math.ceil(rect.bottom()))

            first_left = left - (left % self.gridSize)
            first_top = top - (top % self.gridSize)

            # compute all lines to be drawn
            lines_light, lines_dark = [], []
            for x in range(first_left, right, self.gridSize):
                if (x % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(x, top, x, bottom))
                else: lines_dark.append(QLine(x, top, x, bottom))

            for y in range(first_top, bottom, self.gridSize):
                if (y % (self.gridSize*self.gridSquares) != 0): lines_light.append(QLine(left, y, right, y))
                else: lines_dark.append(QLine(left, y, right, y))


            # draw the lines
            painter.setPen(self._pen_light)
            painter.drawLines(*lines_light)

            painter.setPen(self._pen_dark)
            painter.drawLines(*lines_dark)

        # draw the orgins
        painter.setPen(self._pen_red)
        painter.setOpacity(0.5)
        painter.drawLine(-self.gridSize * self.gridSquares, 0, self.gridSize * self.gridSquares, 0)
        painter.drawLine(0, -self.gridSize  * self.gridSquares, 0, self.gridSize * self.gridSquares)
