import os
import json
from collections import OrderedDict
from pyHydraulic.utils import dumpException
from pyHydraulic.node_serializable import Serializable
from pyHydraulic.node_graphics_scene import QDMGraphicsScene
from pyHydraulic.node_node import Node
from pyHydraulic.node_edge import Edge
from pyHydraulic.node_scene_history import SceneHistory
from pyHydraulic.node_scene_clipboard import SceneClipboard
from PyQt5.QtCore import Qt


class InvalidFile(Exception): pass


class Scene(Serializable):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.scene_width = 640000
        self.scene_height = 640000

        self._has_been_modified = False
        self._has_been_modified_listeners = []

        self.initUI()
        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

    @property
    def has_been_modified(self):
        return self._has_been_modified

    @has_been_modified.setter
    def has_been_modified(self, value):
        if not self._has_been_modified and value:
            self._has_been_modified = value

            # call all registered listeners
            for callback in self._has_been_modified_listeners:
                callback()

        self._has_been_modified = value


    def addHasBeenModifiedListener(self, callback):
        self._has_been_modified_listeners.append(callback)

    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.scene_width, self.scene_height)

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes: self.nodes.remove(node)
        else: print("!W:", "Scene::removeNode", "wanna remove node", node, "from self.nodes but it's not in the list!")

    def removeEdge(self, edge):
        if edge in self.edges: self.edges.remove(edge)
        else: print("!W:", "Scene::removeEdge", "wanna remove edge", edge, "from self.edges but it's not in the list!")


    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.has_been_modified = False


    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write( json.dumps( self.serialize(), indent=4 ) )
            print("saving to", filename, "was successfull.")

            self.has_been_modified = False

    def loadFromFile(self, filename):
        with open(filename, "r", encoding='utf-8', errors='ignore') as file:
            raw_data = file.read()
            try:
                data = json.loads(raw_data, encoding='utf-8')
                self.deserialize(data)
                self.has_been_modified = False
            except json.JSONDecodeError:
                raise InvalidFile("%s is not a valid JSON file" % os.path.basename(filename))
            except Exception as e:
                dumpException(e)

    def setBackgroundColor(self, color=Qt.lightGray, grid_on = True):
        self.grScene._color_background = color
        self.grScene.setBackgroundBrush(color)
        self.grScene._grid_enble = grid_on

    def serialize(self):
        nodes, edges = [], []  # 存放序列化后的字符串
        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())
        return OrderedDict([
            ('id', self.id),
            ('scene_width', self.scene_width),
            ('scene_height', self.scene_height),
            ('nodes', nodes),
            ('edges', edges),
        ])

    def deserialize(self, data, hashmap={}, restore_id=True):
        self.clear()
        hashmap = {}  # hashmap存放的是id:对象集合，通过寻找id就能得到node和socket对象，为以后恢复连线做准备

        if restore_id: self.id = data['id']

        # create nodes 在scene层创建node，以及还原node
        for node_data in data['nodes']:
            node = Node(self, node_type=node_data["node_type"])   # 1.先还原创建的node对象, 默认没有socket, socket的创建是在下一层
            node.setPos(node_data['pos_x'], node_data['pos_y'])   # 2.再还原node的位置
            node.setRotation(node_data["rotation"])     # 3.还原绝对位置角度（顺时针）
            node.setAbsoluteScale(node_data["scale"])
            node.grNode.unit = node_data["unit"]
            node.grNode.value = node_data["value"]
            node.grNode.maxValue = node_data["maxValue"]
            node.grNode.minValue = node_data["minValue"]
            node.grNode.text = node_data["text"]
            if restore_id: node.id = node_data['id']    # 4.再还原node的id

            hashmap[node_data['id']] = node  # 4.在对象字典添加单个node的对象和id

            node.deserialize(node_data, hashmap, restore_id)  # 4.把单个node的数据传递到下一级，解析socket数据
            # Node(self).deserialize(node_data, hashmap, restore_id)

        # create edges
        for edge_data in data['edges']:
            Edge(self).deserialize(edge_data, hashmap, restore_id)

        return True