from collections import OrderedDict
from pyHydraulic.node_graphics_edge import QDMGraphicsEdge
from pyHydraulic.node_node import Node
from pyHydraulic.node_edge import Edge


DEBUG = False


class SceneClipboard():
    def __init__(self, scene):
        self.scene = scene

    def serializeSelected(self, delete=False):
        if DEBUG: print("-- COPY TO CLIPBOARD ---")
        # sle_sockets存放socket字典对象，sel_edges是要删除的edge对象
        sel_nodes, sel_edges, sel_sockets = [], [], {}

        # sort edges and nodes
        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                sel_nodes.append(item.node.serialize())  # node序列化数据放到sle_node里面
                for socket in (item.node.sockets):
                    sel_sockets[socket.id] = socket
            elif isinstance(item, QDMGraphicsEdge):
                sel_edges.append(item.edge)


        # debug
        if DEBUG:
            print("  NODES\n      ", sel_nodes)
            print("  EDGES\n      ", sel_edges)
            print("  SOCKETS\n     ", sel_sockets)


        # remove all edges which are not connected to a node in our list
        edges_to_remove = []
        for edge in sel_edges:
            if edge.start_socket.id in sel_sockets and edge.end_socket.id in sel_sockets:
                # if DEBUG: print(" edge is ok, connected with both sides")
                pass
            else:  # 如果被选中edge，两头也并没有连接被选中的socket，也算要删除的对象
                if DEBUG: print("edge", edge, "is not connected with both sides")
                edges_to_remove.append(edge)
        for edge in edges_to_remove:
            sel_edges.remove(edge)

        # make final list of edges
        edges_final = []
        for edge in sel_edges:
            edges_final.append(edge.serialize())

        if DEBUG: print("our final edge list:", edges_final)


        data = OrderedDict([
            ('nodes', sel_nodes),
            ('edges', edges_final),
        ])


        # if CUT (aka delete) remove selected dockWIdget
        if delete:
            self.scene.grScene.views()[0].deleteSelected()
            # store our history
            self.scene.history.storeHistory("Cut out elements from scene", setModified=True)

        return data

    def deserializeFromClipboard(self, data):

        hashmap = {}

        # calculate mouse pointer - scene position
        view = self.scene.grScene.views()[0]
        mouse_scene_pos = view.last_scene_mouse_position

        # calculate selected objects bbox and center,计算剪切或者复制的中心
        minx, maxx, miny, maxy = 0,0,0,0
        for node_data in data['nodes']:
            x, y = node_data['pos_x'], node_data['pos_y']
            if x < minx: minx = x
            if x > maxx: maxx = x
            if y < miny: miny = y
            if y > maxy: maxy = y
        bbox_center_x = (minx + maxx) / 2
        bbox_center_y = (miny + maxy) / 2

        # center = view.mapToScene(view.rect().center())
        # 计算目标位置和之前被剪切的一坨之间的距离
        # calculate tehe offset of the newly creating nodes
        offset_x = mouse_scene_pos.x() - bbox_center_x
        offset_y = mouse_scene_pos.y() - bbox_center_y

        # create each node
        for node_data in data['nodes']:  # 还原各个node
            new_node = Node(self.scene, node_data['node_type'])
            new_node.deserialize(node_data, hashmap, restore_id=False)

            # read just the new node's position
            pos = new_node.pos
            new_node.setPos(pos.x() + offset_x, pos.y() + offset_y)

        # create each edge
        if 'edges' in data:
            for edge_data in data['edges']:
                new_edge = Edge(self.scene)
                new_edge.deserialize(edge_data, hashmap, restore_id=False)

        # store history
        self.scene.history.storeHistory("Pasted elements in scene", setModified=True)