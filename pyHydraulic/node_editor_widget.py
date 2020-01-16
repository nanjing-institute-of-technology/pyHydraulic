import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from pyHydraulic.node_scene import Scene, InvalidFile
from pyHydraulic.node_node import Node
from pyHydraulic.node_edge import Edge, EDGE_TYPE_BEZIER,EDGE_TYPE_DIRECT, EDGE_TYPE_POLYGONAL
from pyHydraulic.node_graphics_view import QDMGraphicsView


class NodeEditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = None

        self.initUI()


    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # crate graphics scene
        self.scene = Scene()
        # self.grScene = self.scene.grScene

        self.addNodes()

        # create graphics view
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)




    def isModified(self):
        return self.scene.has_been_modified

    def isFilenameSet(self):
        return self.filename is not None

    def getUserFriendlyFilename(self):
        name = os.path.basename(self.filename) if self.isFilenameSet() else "New Graph"
        return name + ("*" if self.isModified() else "")

    def fileNew(self):
        self.scene.clear()
        self.filename = None

    def fileLoad(self, filename):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            # clear history
            return True
        except InvalidFile as e:
            print(e)
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(filename), str(e))
            return False
        finally:
            QApplication.restoreOverrideCursor()


    def fileSave(self, filename=None):
        # when called with empty parameter, we won't store the filename
        if filename is not None: self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()
        return True

    def addnode(self, node_name):
        return Node(self.scene, node_name)

    def addNodes(self):
        node1 = Node(self.scene, "pressure sensor")
        node2 = Node(self.scene, "tank")
        node3 = Node(self.scene, "flow meter")
        node4 = Node(self.scene, "gauge")
        node5 = Node(self.scene, "servo valve")
        node6 = Node(self.scene,  "piston dual")
        node7 = Node(self.scene, "simple tank")

        node1.rotate(90)

        node1.setPos(-350, -250)
        node2.setPos(-75, 0)
        node3.setPos(200, -150)
        node4.setPos(-200, -150)
        node6.setPos(-300, -250)
        print(type(node1.sockets[0]))
        edge1 = Edge(self.scene, node3.sockets[0], node2.sockets[0], edge_type= EDGE_TYPE_POLYGONAL)
        # edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[0], edge_type=EDGE_TYPE_BEZIER)


    def addDebugContent(self):
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)


        rect = self.grScene.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.grScene.addText("This is my Awesome _text!", QFont("Ubuntu"))
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))


        widget1 = QPushButton("Hello World")
        proxy1 = self.grScene.addWidget(widget1)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 30)


        widget2 = QTextEdit()
        proxy2 = self.grScene.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 60)


        line = self.grScene.addLine(-200, -200, 400, -100, outlinePen)
        line.setFlag(QGraphicsItem.ItemIsMovable)
        line.setFlag(QGraphicsItem.ItemIsSelectable)

    def getObjectByID(self, id):
        for node in self.scene.nodes + self.scene.edges:
            if node.id == id:
                return node
        return None

