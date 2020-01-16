from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class QDMGraphicsSocket(QGraphicsItem):
    # socket_type为不同颜色的序号
    def __init__(self, socket, socket_type=1):
        self.socket = socket
        # 下面这句话就是自身grSocket作为grNode的子对象，嵌入在grNode中
        super().__init__(socket.node.grNode)

        self.linkFlag = False  # 标志位：只是当前socket是否有已经有连接
        self.radius = 30
        self.outline_width = 2.0
        self._colors = [
            QColor("#FFFF7700"),
            QColor("#FF52e220"),
            QColor("#FF0056a6"),
            QColor("#FFa86db1"),
            QColor("#FFb54747"),
            QColor("#FFdbe220"),
        ]
        self._color_background = self._colors[socket_type]
        self._color_outline = QColor("#FF000000")

        self._pen = QPen(self._color_outline)
        self._pen.setWidthF(self.outline_width)
        self._brush = QBrush(self._color_background)

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, QGraphicsSceneHoverEvent):
        super().hoverEnterEvent(QGraphicsSceneHoverEvent)
        # 在socket上hover的时候，变成十字形
        QApplication.setOverrideCursor(Qt.CrossCursor)
        # 如果现在是隐形的，强制现身
        if self.linkFlag == True:
            self.linkFlag = False

    def hoverLeaveEvent(self, QGraphicsSceneHoverEvent):
        super().hoverLeaveEvent(QGraphicsSceneHoverEvent)
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        # hover出来了，就隐身
        if self.linkFlag == False:
            self.linkFlag = True

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        # 重绘之前，都判断当前socket有没有edge链接，如果有，则隐身，没有的话，就现身
        if len(self.socket.edges) ==0:
            self.linkFlag = False
        # 没有edge,则现身
        if self.linkFlag == False:
        # painting circle
            painter.setBrush(self._brush)
            painter.setPen(self._pen)
            painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def boundingRect(self):
        return QRectF(
            - self.radius - self.outline_width,
            - self.radius - self.outline_width,
            2 * (self.radius + self.outline_width),
            2 * (self.radius + self.outline_width),
        )
