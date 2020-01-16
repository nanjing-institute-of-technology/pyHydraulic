import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


from pyHydraulic.node_socket import *


EDGE_CP_ROUNDNESS = 100


class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge
        self._arrowFlag = True

        self._color = Qt.white
        self._color_selected = QColor("#00ff00")
        self._pen = QPen(self._color)
        self._pen_selected = QPen(self._color_selected)
        self._pen_dragging = QPen(self._color)
        self._pen_dragging.setStyle(Qt.DashLine)
        self._pen.setWidthF(8.0)
        self._pen_selected.setWidthF(5.0)
        self._pen_dragging.setWidthF(5.0)

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setZValue(-1)

        self.posSource = [0, 0]
        self.posDestination = [200, 100]

    def setSource(self, x, y):
        self.posSource = [x, y]

    def setDestination(self, x, y):
        self.posDestination = [x, y]

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calcPath()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.setPath(self.calcPath())

        if self.edge.end_socket is None:
            painter.setPen(self._pen_dragging)
        else:
            painter.setPen(self._pen if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self.path())

    # 判断直线（p1,p2）与本edge路径是否相交
    def intersectsWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calcPath()
        return cutpath.intersects(path)

    def calcPath(self):
        """ Will handle drawing QPainterPath from Point A to B """
        raise NotImplemented("This method has to be overriden in a child class")

# 1.直接连接的线
class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    def calcPath(self):
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path

# 2.Bezier曲线连接的线
class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    def calcPath(self):
        s = self.posSource
        d = self.posDestination
        dist = (d[0] - s[0]) * 0.5
        if s[0] > d[0]: dist *= -1

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.cubicTo(s[0] + dist, s[1], d[0] - dist, d[1], self.posDestination[0], self.posDestination[1])

        # s = self.posSource
        # d = self.posDestination
        # dist = (d[0] - s[0]) * 0.5
        #
        # cpx_s = +dist
        # cpx_d = -dist
        # cpy_s = 0
        # cpy_d = 0
        #
        # if self.edge.start_socket is not None:
        #     sspos = self.edge.start_socket.position
        #
        #     if (s[0] > d[0] and sspos in (RIGHT_TOP, RIGHT_BOTTOM)) or (s[0] < d[0] and sspos in (LEFT_BOTTOM, LEFT_TOP)):
        #         cpx_d *= -1
        #         cpx_s *= -1
        #
        #         cpy_d = (
        #             (s[1] - d[1]) / math.fabs(
        #                 (s[1] - d[1]) if (s[1] - d[1]) != 0 else 0.00001
        #             )
        #         ) * EDGE_CP_ROUNDNESS
        #         cpy_s = (
        #             (d[1] - s[1]) / math.fabs(
        #                 (d[1] - s[1]) if (d[1] - s[1]) != 0 else 0.00001
        #             )
        #         ) * EDGE_CP_ROUNDNESS
        #
        #
        # path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        # path.cubicTo( s[0] + cpx_s, s[1] + cpy_s, d[0] + cpx_d, d[1] + cpy_d, self.posDestination[0], self.posDestination[1])

        return path

# 3.拐角线
class QDMGraphicsEdgePolygonal(QDMGraphicsEdge):
    def calcPath(self):
        # 计算中间转折的Y值坐标
        y_turn = (self.posSource[1] + self.posDestination[1]) / 2
        # 开始画线
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(QPointF(self.posSource[0], y_turn))
        path.lineTo(QPointF(self.posDestination[0], y_turn))
        path.lineTo(QPointF(self.posDestination[0], self.posDestination[1]))
        return path