from pyHydraulic.node_graphics_edge import *


EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2
EDGE_TYPE_POLYGONAL = 3

DEBUG = False


class Edge(Serializable):
    def __init__(self, scene, start_socket=None, end_socket=None, edge_type=EDGE_TYPE_DIRECT):
        super().__init__()
        self.scene = scene

        # default init
        self._start_socket = None
        self._end_socket = None
        # 只需要如下3个信息，就可以唯一确定一个edge
        self.start_socket = start_socket
        self.end_socket = end_socket
        self.edge_type = edge_type

        self.scene.addEdge(self)

    def __str__(self):
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    @property
    def start_socket(self): return self._start_socket

    @start_socket.setter
    def start_socket(self, value):
        # if we were assigned to some socket before, delete us from the socket
        if self._start_socket is not None:
            self._start_socket.removeEdge(self)

        # assign new start socket
        self._start_socket = value
        # addEdge to the Socket class
        if self.start_socket is not None:
            self.start_socket.addEdge(self)
            # 隐藏start_socket的显示
            self.start_socket.grSocket.linkFlag = True


    @property
    def end_socket(self): return self._end_socket

    @end_socket.setter
    def end_socket(self, value):
        # if we were assigned to some socket before, delete us from the socket
        if self._end_socket is not None:
            self._end_socket.removeEdge(self)

        # assign new end socket
        self._end_socket = value
        # addEdge to the Socket class
        if self.end_socket is not None:
            self.end_socket.addEdge(self)
            # 隐藏end_socket的显示
            self.end_socket.grSocket.linkFlag = True

    @property
    def edge_type(self): return self._edge_type

    @edge_type.setter
    def edge_type(self, value):
        if hasattr(self, 'grEdge') and self.grEdge is not None:
            self.scene.grScene.removeItem(self.grEdge)

        self._edge_type = value
        if self.edge_type == EDGE_TYPE_DIRECT:
            self.grEdge = QDMGraphicsEdgeDirect(self)
        elif self.edge_type == EDGE_TYPE_BEZIER:
            self.grEdge = QDMGraphicsEdgeBezier(self)
        elif self.edge_type == EDGE_TYPE_POLYGONAL:
            self.grEdge = QDMGraphicsEdgePolygonal(self)
        else:
            self.grEdge = QDMGraphicsEdgePolygonal(self)

        self.scene.grScene.addItem(self.grEdge)

        if self.start_socket is not None:
            self.updatePositions()


    def updatePositions(self):
        # 获取socket的坐标
        # source_pos = [self.start_socket.grSocket.pos().x(), self.start_socket.grSocket.pos().y()]
        # source_pos = self.start_socket.getSocketPosition()
        # socket的坐标转化为在scene的坐标
        # source_pos[0] += self.start_socket.node.grNode.pos().x()
        # source_pos[1] += self.start_socket.node.grNode.pos().y()

        # 获取socket在scene的坐标
        source_pos = [self.start_socket.grSocket.scenePos().x(),self.start_socket.grSocket.scenePos().y()]
        self.grEdge.setSource(*source_pos)
        if self.end_socket is not None:
            # 如法炮制出end_socket的在scene的坐标
            # end_pos = self.end_socket.getSocketPosition()
            # end_pos[0] += self.end_socket.node.grNode.pos().x()
            # end_pos[1] += self.end_socket.node.grNode.pos().y()
            end_pos = [self.end_socket.grSocket.scenePos().x(), self.end_socket.grSocket.scenePos().y()]

            self.grEdge.setDestination(*end_pos)
        else:
            self.grEdge.setDestination(*source_pos)
        self.grEdge.update()


    def remove_from_sockets(self):
        self.end_socket = None
        self.start_socket = None


    def remove(self):
        if DEBUG: print("# Removing Edge", self)
        if DEBUG: print(" - remove edge from all sockets")
        self.remove_from_sockets()
        if DEBUG: print(" - remove grEdge")
        # 从scence真实移除edge对象
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        if DEBUG: print(" - remove edge from scene")
        # 删除从scene统计的edge
        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass
        if DEBUG:print(" - everything is done.")


    def serialize(self):
        return OrderedDict([
            ('id', self.id),
            ('edge_type', self.edge_type),
            ('start', self.start_socket.id),
            ('end', self.end_socket.id),
        ])

    # 下面只是赋值操作
    def deserialize(self, data, hashmap={}, restore_id=True):
        if restore_id: self.id = data['id']
        self.start_socket = hashmap[data['start']]  # hashmap装的是id对应的对象字典，这里根据id返回的是socket的对象
        self.end_socket = hashmap[data['end']]
        self.edge_type = data['edge_type']