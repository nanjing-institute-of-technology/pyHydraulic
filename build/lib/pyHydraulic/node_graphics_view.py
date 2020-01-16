from PyQt5.QtWidgets import QGraphicsView, QApplication
from PyQt5.QtCore import *
from PyQt5.QtGui import *


from pyHydraulic.node_graphics_socket import QDMGraphicsSocket
from pyHydraulic.node_graphics_edge import QDMGraphicsEdge
from pyHydraulic.node_edge import Edge, EDGE_TYPE_BEZIER, EDGE_TYPE_POLYGONAL
from pyHydraulic.node_graphics_cutline import QDMCutLine
from pyHydraulic.node_graphics_node import QAbstractGraphicsNode

MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3

EDGE_DRAG_START_THRESHOLD = 10


DEBUG = True


class QDMGraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)
    sceneItemSelected = pyqtSignal(str, int)

    def __init__(self, grScene, parent=None):
        super().__init__(parent)
        self.grScene = grScene

        self.initUI()

        self.setScene(self.grScene)

        self.mode = MODE_NOOP
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False

        self.zoomInFactor = 1.25  # 每次放大的因子
        self.zoomClamp = True  # 指示放大缩小是否有效标志位
        self.zoom = 10  # 初始的倍数值
        self.zoomStep = 1  # 每次滚轮，self.zoom的变化值
        self.zoomRange = [-1, 7]  # self.zoom的变化值的变化范围，超过范围，zoomInFactor为False

        # cutline
        self.cutline = QDMCutLine()
        self.grScene.addItem(self.cutline)


    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing | QPainter.HighQualityAntialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)


    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonPress(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)


    def middleMouseButtonPress(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)



    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                Qt.LeftButton, event.buttons() & ~Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.RubberBandDrag)


    def leftMouseButtonPress(self, event):
        # get item which we clicked on
        item = self.getItemAtClick(event)

        # we store the position of last LMB click
        self.last_lmb_click_scene_pos = self.mapToScene(event.pos())

        # if DEBUG: print("LMB Click on", item, self.debug_modifiers(event))

        # logic
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return


        if type(item) is QDMGraphicsSocket:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.edgeDragStart(item)
                QApplication.setOverrideCursor(Qt.CrossCursor)  # 拖动鼠标图标换成可编辑状态
                return

        if self.mode == MODE_EDGE_DRAG:
            res = self.edgeDragEnd(item)
            if res: return

        if item is None:
            # 如果按住ctrl键盘情况下，左键鼠标
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT  # 处于剪断连接线模式，方便在鼠标移动事件中添加鼠标移动的坐标到linePoints
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        item = self.getItemAtClick(event)
        if isinstance(item, QAbstractGraphicsNode):   # 如果选中的是node对象或者子对象
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)  #选中后变成移动图标
            self.sceneItemSelected.emit(item.node._node_type, item.node.id)  # "选中的node的类型为%s, id为%d,"
        elif isinstance(item, QDMGraphicsEdge):  # 如果选中的是edge对象
            self.sceneItemSelected.emit("edge"+str(item.edge.edge_type), item.edge.id)
        else:
            self.sceneItemSelected.emit("", 0) # 如果选中的是空对象

        super().mousePressEvent(event)


    def leftMouseButtonRelease(self, event):
        # get item which we release mouse button on
        item = self.getItemAtClick(event)
        # 不管什么操作，只要左键释放，鼠标图标都还原成默认
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        # logic
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return

        if self.mode == MODE_EDGE_DRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)

                if res: return

        if self.mode == MODE_EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutline.line_points = []
            self.cutline.update()
            self.mode = MODE_NOOP


            return


        if self.rubberBandDraggingRectangle:
            self.grScene.scene.history.storeHistory("Selection changed")
            self.rubberBandDraggingRectangle = False

        super().mouseReleaseEvent(event)



    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

        item = self.getItemAtClick(event)

        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print('RMB DEBUG:', item.edge, ' connecting sockets:',
                                            item.edge.start_socket, '<-->', item.edge.end_socket)
            if type(item) is QDMGraphicsSocket: print('RMB DEBUG:', item.socket, 'has edges:', item.socket.edges)

            if item is None:
                print('SCENE:')
                print('  Nodes:')
                for node in self.grScene.scene.nodes: print('    ', node)
                print('  Edges:')
                for edge in self.grScene.scene.edges: print('    ', edge)


    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)


    def mouseMoveEvent(self, event):
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.drag_edge.grEdge.setDestination(pos.x(), pos.y())
            self.drag_edge.grEdge.update()

        # 添加鼠标当前点进入line_points
        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos()) # 移动一下，就添加一个点
            self.cutline.line_points.append(pos)
            self.cutline.update()

        self.last_scene_mouse_position = self.mapToScene(event.pos())
        # 这里发射鼠标移动点信号
        self.scenePosChanged.emit(
            int(self.last_scene_mouse_position.x()), int(self.last_scene_mouse_position.y())
        )

        super().mouseMoveEvent(event)


    def keyPressEvent(self, event):
        # Use this code below if you wanna have shortcuts in this widget.
        # You want to use this, when you don't have a window which handles these shortcuts for you

        # if event.key() == Qt.Key_Delete:
        #     if not self.editingFlag:
        #         self.deleteSelected()
        #     else:
        #         super().keyPressEvent(event)
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.saveToFile("graph.json")
        # elif event.key() == Qt.Key_L and event.modifiers() & Qt.ControlModifier:
        #     self.grScene.scene.loadFromFile("graph.json")
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and not event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.undo()
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
        #     self.grScene.scene.history.redo()
        # elif event.key() == Qt.Key_H:
        #     print("HISTORY:     len(%d)" % len(self.grScene.scene.history.history_stack),
        #           " -- current_step", self.grScene.scene.history.history_current_step)
        #     ix = 0
        #     for item in self.grScene.scene.history.history_stack:
        #         print("#", ix, "--", item['desc'])
        #         ix += 1
        # else:
        super().keyPressEvent(event)

    # 判断cutLine与当前scene中每个edge是否相交，如果相交，就切断相交的edge
    def cutIntersectingEdges(self):
        for ix in range(len(self.cutline.line_points) - 1):
            p1 = self.cutline.line_points[ix]
            p2 = self.cutline.line_points[ix + 1]

            for edge in self.grScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    # 删除edge
                    edge.remove()

        self.grScene.scene.history.storeHistory("Delete cutted edges", setModified=True)



    def deleteSelected(self):
        # 选中的只能是gr对象
        for item in self.grScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):  # 如果是grEdge对象
                item.edge.remove()
            elif isinstance(item, QAbstractGraphicsNode): #hasattr(item, 'node'):  # 如果是grNode对象，具有属性'node'
                item.node.remove()
        self.grScene.scene.history.storeHistory("Delete selected", setModified=True)

    def rotateSelected(self, angle):
        # 选中的只能是grnode对象
        for item in self.grScene.selectedItems():
            if isinstance(item, QAbstractGraphicsNode): #hasattr(item, 'node'):  # 如果是grNode对象，具有属性'node'
                item.node.rotate(angle)
        self.grScene.scene.history.storeHistory("Rotate selected", setModified=True)

    def scaleSelected(self, scale):
        # 选中的只能是grnode对象
        for item in self.grScene.selectedItems():
            if isinstance(item, QAbstractGraphicsNode):  # hasattr(item, 'node'):  # 如果是grNode对象，具有属性'node'
                item.node.setRelativeScale(scale)
        self.grScene.scene.history.storeHistory("Scale selected", setModified=True)




    def debug_modifiers(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.ShiftModifier: out += "SHIFT "
        if event.modifiers() & Qt.ControlModifier: out += "CTRL "
        if event.modifiers() & Qt.AltModifier: out += "ALT "
        return out

    def getItemAtClick(self, event):
        """ return the object on which we've clicked/release mouse button """
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj


    def edgeDragStart(self, item):
        if DEBUG: print('View::edgeDragStart ~ Start dragging edge')
        if DEBUG: print('View::edgeDragStart ~   assign Start Socket to:', item.socket)
        self.drag_start_socket = item.socket
        self.drag_edge = Edge(self.grScene.scene, item.socket, None, EDGE_TYPE_POLYGONAL)
        if DEBUG: print('View::edgeDragStart ~   dragEdge:', self.drag_edge)


    def edgeDragEnd(self, item):
        """ return True if skip the rest of the code """
        self.mode = MODE_NOOP

        if DEBUG: print('View::edgeDragEnd ~ End dragging edge')
        self.drag_edge.remove()
        self.drag_edge = None

        if type(item) is QDMGraphicsSocket: # 如果拖到了一个socket之上
            if item.socket != self.drag_start_socket: # 如果拖到了另外一个socket之上
                # if we released dragging on a socket (other then the beginning socket)

                # we wanna keep all the edges comming from target socket
                if not item.socket.is_multi_edges:
                    item.socket.removeAllEdges()

                # we wanna keep all the edges comming from start socket
                if not self.drag_start_socket.is_multi_edges:
                    self.drag_start_socket.removeAllEdges()

                new_edge = Edge(self.grScene.scene, self.drag_start_socket, item.socket, edge_type=EDGE_TYPE_POLYGONAL)
                if DEBUG: print("View::edgeDragEnd ~  created new edge:", new_edge, "connecting", new_edge.start_socket, "<-->", new_edge.end_socket)


                self.grScene.scene.history.storeHistory("Created new edge by dragging", setModified=True)


                return True
        # # 如果拖到一半松手了，drag_start_socket之前被隐藏了，现在必须显示出来
        # else:
        #     if len(self.drag_start_socket.edges) ==0: #如果起始的socket其他edge线链接
        #         self.drag_start_socket.grSocket.linkFlag = False


        if DEBUG: print('View::edgeDragEnd ~ everything done.')
        return False


    def distanceBetweenClickAndReleaseIsOff(self, event):
        """ measures if we are too far from the last LMB click scene position """
        new_lmb_release_scene_pos = self.mapToScene(event.pos())
        dist_scene = new_lmb_release_scene_pos - self.last_lmb_click_scene_pos
        edge_drag_threshold_sq = EDGE_DRAG_START_THRESHOLD*EDGE_DRAG_START_THRESHOLD
        return (dist_scene.x()*dist_scene.x() + dist_scene.y()*dist_scene.y()) > edge_drag_threshold_sq



    def wheelEvent(self, event):
        # calculate our zoom Factor
        zoomOutFactor = 1 / self.zoomInFactor

        # calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep


        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        # set scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)

