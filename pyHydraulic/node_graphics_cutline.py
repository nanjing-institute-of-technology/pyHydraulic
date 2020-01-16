from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class QDMCutLine(QGraphicsItem):
    def __init__(self, parent=None):
        super().__init__(parent)

        # cutline的点集合，在QGraphicsview鼠标移动事件中添加
        self.line_points = []

        self._pen = QPen(Qt.yellow)
        self._pen.setWidthF(10)
        self._pen.setDashPattern([3, 3])

        self.setZValue(10)

    def boundingRect(self):
        return self.shape().boundingRect()

    # 根据self.line_ponts形成对应的path路径
    def shape(self):
        poly = QPolygonF(self.line_points)

        if len(self.line_points) > 1:
            path = QPainterPath(self.line_points[0])
            for pt in self.line_points[1:]:
                path.lineTo(pt)
        else:
            path = QPainterPath(QPointF(0,0))
            path.lineTo(QPointF(1,1))

        return path

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        # 多折线图
        poly = QPolygonF(self.line_points)
        painter.drawPolyline(poly)