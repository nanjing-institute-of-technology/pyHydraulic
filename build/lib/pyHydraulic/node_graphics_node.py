 # !/usr/bin/env python3
 # coding=utf-8
"""
    Author: lee
    Time: 2020-01-06, 14:41
    File: node_graphics_node.py
    Function: 基本元件节点的绘制文件
"""
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import math

DEBUG = True
# 控件的名称,每一个类型应该独一无二
NODE_TYPES = ["pressure sensor",
              "flow meter",
              "tank",
              "simple tank",
              "gauge",
              "servo valve",
              "piston dual",
              "piston right",
              "piston left",
              "pump",
              "filter",
              "accumulator",
              "one-way valve",
              "relief valve",
              "text"
              ]
# 所有的节点类的父类
class QAbstractGraphicsNode(QGraphicsItem):
    def __init__(self, node):
        super().__init__()
        # 下面是公共的变量放在下面
        self.node = node
        self.width = 500  # 这两个属性可以根据具体控件在子类中修改
        self.height = 120

        # 修改选中和不选中的线型
        self._pen_default = QPen(Qt.white)# QPen(QColor("#7F000000"))
        self._pen_default.setWidth(8)
        self._pen_selected = QPen(Qt.green) #QPen(QColor("#FFFFA637"))
        self._pen_selected.setWidth(8)

        # init UI
        self.initUI()
        # 自己被移动表示位
        self.wasMoved = False
        # 下面可以添加一个通用变量
        # 最大值最小值
        self._minValue = 0
        self._maxValue = 100.0
        self._value = 00.0  # 当前值
        self._percent = 0.0  # 占比
        self._text = " "  # 显示的文本数值，不想显示，赋值为空即可
        self._unit = " "  # 显示的文本单位，不想显示，赋值为空即可
        self.textEnable = True  # 是否显示文本开关
        self.textFont = "微软雅黑"
        # 下面存放本node中的socket的信息：包括1.socket位置坐标，2.socket的个数, 默认只有1个socket，在正中间
        self.socketInfo = []  # 默认没有socket信息，就没有socket

        # self.socketInfo = [[QPointF(1 / 2 * self.width, 1 / 2 * self.height), 0]]  # 后面0为socket颜色样式，取值0-5


    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, int) or isinstance(value, float):
            if (value >= self._minValue) and (value <= self._maxValue):
                self._value = value
                self._percent = (self._value - self.minValue) / (self.maxValue - self.minValue)  # 0-1取值 百分数
                self.update()  # 这个会调用下面的paint()函数

    @property
    def maxValue(self):
        return self._maxValue
    @maxValue.setter
    def maxValue(self, value):
        if value >= self.value:
            self._maxValue = value
        else:
            if DEBUG:
                print("不能赋值最大值，对象%s 最大值:%f,赋值最大的值:%f!\n" % (self.node._node_type, self.maxValue, value))

    @property
    def minValue(self):
        return self._minValue
    @minValue.setter
    def minValue(self, value):
        if value<= self.value:
            self._minValue = value
        else:
            if DEBUG:
                raise Exception("不能赋值最小值，最小值还大于当前值！")

    # 显示文本的内容
    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, value):
        if type(value) == str:
            self._text = value
        else:
            if DEBUG:
                raise Exception("必须赋值文本！")


    @property
    def unit(self):
        return self._unit
    @unit.setter
    def unit(self, value):
        if isinstance(value, str):  # 判断为字符串形式
            self._unit = value
        else:#
            if DEBUG:
                print("node的单位不能为非字符串形式\n")

    # 拖拽node使之移动，触发该事件
    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        # 鼠标变成十字箭头
        self.setCursor(Qt.SizeAllCursor)
        # optimize me! just update the selected nodes
        for node in self.scene().scene.nodes:
            if node.grNode.isSelected():
                node.updateConnectedEdges()
        self.wasMoved = True




    # 拖拽node后，释放鼠标, 触发该事件
    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # 鼠标还原成正常箭头
        self.setCursor(Qt.ArrowCursor)

        if self.wasMoved:
            self.wasMoved = False
            self.node.scene.history.storeHistory("Node moved", setModified=True)

    # 双击弹出输入框
    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent):
        # 第一个参数就是父控件，这里是Qgrahicsview
        class_name = str(type(self))
        # 文字类型
        if class_name.find("GraphicsNode_text") >=0:
            text,ok = QInputDialog.getText(self.node.scene.grScene.views()[0], "修改文字对话框","请输入修改文字",QLineEdit.Normal, self.text)
            if ok:
                self.text = text
        # 数字类型控件
        elif class_name.find("GraphicsNode_flow_meter") >=0 or \
                class_name.find("GraphicsNode_tank") >=0 or \
                class_name.find("GraphicsNode_gauge") >= 0 or \
                class_name.find("GraphicsNode_servo_valve") >= 0 or \
                class_name.find("GraphicsNode_pistion") >=0:
            step = (self.maxValue - self.minValue) / 100.0 #每次拨动的步长
            value,ok = QInputDialog.getDouble(self.node.scene.grScene.views()[0], "修改当前值对话框", ("修改范围:%.2f / %.2f"%(self.minValue, self.maxValue)), self.value, self.minValue, self.maxValue,  step)
            if ok:
                self.value = value

    # 定义控件的区域
    def boundingRect(self):
        return QRectF(
            -self.width/2,
            -self.height/2,
            self.width,
            self.height
        )

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    # 该函数只是在选中的时候，绘制一个框框和原点十字，需要在子类中重写
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None): #自己在子类中重新实现这个函数
        if self.isSelected():
            painter.save()
            painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)  # 把笔给画家
            # 1.画出整个控件的轮廓
            pen = painter.pen()
            painter.setOpacity(0.5)
            pen.setWidth(1)
            pen.setStyle(Qt.DashDotLine)
            pen.setColor(Qt.red)
            pen.setWidth(4)
            painter.setPen(pen)  # 把笔给画家
            painter.drawLine(-self.width / 5,0, self.width / 5,0)
            painter.drawLine(0, -self.height/10, 0, self.height/10)
            painter.drawRect(-self.width/2, -self.height/2, self.width, self.height)

            painter.restore()
# 1.静止的压力传感器，继承自子上面的node
class GraphicsNode_pressure_sensor(QAbstractGraphicsNode):
    def __init__(self, node=None):
        super().__init__(node)
        self.unit = "MPa"
        # 自己独特的变量，或者对父类变量进行篡改
        self.width = 250  # 整个控件边界的宽度
        self.height = self.width * 3.0 /2  # 整个控件边界的高度
        # 修改 socket信息
        self.socketInfo = [[QPointF(0, self.height/2), 2]]


    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)  # 把笔给画家

        # 1.画出整个控件的轮廓
        # painter.drawRect(0, 0, self.width, self.height)

        # 1. 绘制一个圆 QtGui.QPainter.drawEllipse(center, rx, ry)
        r = self.height / 3.0
        painter.drawEllipse(QPoint(0, - self.height/6), r, r)  #
        # 2.绘制一条竖线,作为支架
        painter.drawLine(0, self.height/6, 0, self.height/2)  #
        # 3.绘制叉叉
        painter.drawLine(r * (1 - math.sin(math.pi / 180 * 45))- self.width /2, r * (1 - math.cos(math.pi / 180 * 45)) - self.height /2,
                         r * (1 + math.cos(math.pi / 180 * 45)) - self.width /2 , r * (1 + math.sin(math.pi / 180 * 45)) - self.height /2)  #
        painter.drawLine(r * (1 - math.sin(math.pi / 180 * 45)) - self.width /2 , r * (1 + math.cos(math.pi / 180 * 45))- self.height /2 ,
                         r * (1 + math.cos(math.pi / 180 * 45)) - self.width /2 , r * (1 - math.sin(math.pi / 180 * 45)) - self.height /2 )  #
        #
        # index =0
        # for socket in self.node.sockets:
        #     self.socketInfo[index][0] = QPointF(socket.grSocket.x(), socket.grSocket.y())
        #     index +=1
# 2.静止的流量传感器
class GraphicsNode_flow_meter(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "mL"
        self.width = 200  # 整个控件边界的宽度
        self.height = self.width * 2  # 整个控件边界的高度
        # 修改 socket信息
        self.socketInfo = [[QPointF(0, - self.height/2), 2],
                           [QPointF(0, self.height/2), 2]
                           ]

    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        # 根据获取的坐标，更新要绘制的路径
        path = QPainterPath()

        # 画2个竖线
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.drawLine(0, - self.height / 2, 0, - self.height * 1 / 4)
        painter.drawLine(0, self.height * 1 / 4, 0, self.height / 2)
        painter.drawEllipse(QPointF(0, 0), self.height / 4,
                            self.height / 4)
        # 画1个圆上个两个弧形

        painter.drawArc(
            QRect(-self.width * 9 / 10, - self.height * 4/ 24, self.height / 3, self.height / 3),
            -60 * 16, 120 * 16)
        painter.drawArc(QRect(self.width * 2.3 / 10, - self.height * 4 / 24, self.height /3, self.height / 3),
            120 * 16, 120 * 16)

        # 画1个圆，圆心，直径
        # path.addEllipse(QPointF(self.width / 2, self.height / 2), self.height / 6, self.height /6)

        # 画1个圆上个两个弧形
        # path.arcTo(self.width* 8/ 24, self.height *5/ 12, self.height / 4 , self.height / 4, -45, 90)

        # 路径
        # self.setPath(path)
        # painter.setBrush(Qt.lightGray)
        # painter.drawPath(path)

        #  添加文字路径
        # 4.显示文本
        if self.textEnable:
            self.text = str(round(self.value, 1)) + self.unit
            # painter.setPen(self._pen_default)
            painter.setFont(QFont(self.textFont, self.width / 4, QFont.Medium))  # 第二个参数是字体大小
            # painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
            painter.drawText(QPointF(0, self.height * 0.45), self.text)
# 3.tank：液面会动的油箱
class GraphicsNode_tank(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "cm"
        self.width = 1000  # 整个控件边界的宽度
        self.height = self.width*1 # 整个控件边界的高度

        # 波浪相关的变量
        self._frequency = 0.0015  # 波浪的频率,Hz
        self._amplitude = self.width / 50  # 像素，波浪幅值
        self._phase1 = 0  # 像素，波浪1相位
        self._phase2 = 0  # 像素，波浪2相位
        self._deepth = 0  # 水位高度
        # 修改父类变量
        self.maxValue = 100
        self.minValue = 0
        self.value = 20  # _value为内部变量，此句话意思要调用一下value函数，更新初始状态


        # 定义一个Timer，刷新波浪用的
        # 定时器初始化
        self.timer = QTimer()

        self.t = 0  # 时间
        self.sampleTime = 0.1 # s
        self.timer.setInterval(self.sampleTime * 1000)  # ms
        self.timer.timeout.connect(self.time_out)
        self.timer.start()

        # 修改 socket信息
        self.socketInfo = [[QPointF(0,- self.height /2), 2]]


    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        waterPath1 = QPainterPath()

        # 1.开始画波浪线
        # 第一条波浪路径集合
        waterPath1 = QPainterPath()
        # 第二条波浪路径集合
        waterPath2 = QPainterPath()

        self._deepth = self._percent * self.height * 3 / 4  # 像素单位的深度
        y_deep = self.height - self._deepth - self._amplitude - self.height/2  # 液面的中值坐标
        waterPath1.moveTo(-self.width/2, y_deep)
        waterPath2.moveTo(-self.width / 2, y_deep)

        self._phase1 = self.width / 400 * self.t  # 每次更新相位自动加
        self._phase2 = self.width / 400 * self.t + 2 * math.pi * self._frequency * self.width /5 # 每次更新相位自动加
        # 开始填充波浪
        startDraw = -self.width //2
        endDraw =  self.width // 2
        stepDraw = self.width // 50
        for x_wave in range(startDraw, endDraw, stepDraw):
            y_wave1 = self._amplitude * math.sin(2 * math.pi * self._frequency * x_wave + self._phase1) + y_deep  # 计算波浪点y坐标
            y_wave2 = self._amplitude * math.sin(2 * math.pi * self._frequency * x_wave + self._phase2) + y_deep  # 计算波浪点y坐标

            waterPath1.lineTo(x_wave, y_wave1)
            waterPath2.lineTo(x_wave, y_wave2)

        waterPath1.lineTo(self.width / 2, y_deep)  # 移动到右下角结束点,整体形成一个闭合路径
        waterPath1.lineTo(self.width / 2, self.height / 2)  # 移动到右下角结束点,整体形成一个闭合路径
        waterPath2.lineTo(self.width / 2, y_deep)
        waterPath2.lineTo(self.width / 2, self.height / 2)  # 移动到右下角结束点,整体形成一个闭合路径

        waterPath1.lineTo(-self.width / 2, self.height/2)
        waterPath2.lineTo(-self.width / 2, self.height/2)

        waterPath1.lineTo(-self.width / 2, y_deep)
        waterPath2.lineTo(-self.width / 2, y_deep)

        # 大路径
        bigPath = QPainterPath()
        #后背景
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#008B8B"))
        # painter.setOpacity(0.3)
        painter.drawPath(waterPath1)

        painter.setBrush(QColor("#40E0D0"))
        painter.setOpacity(0.5)
        painter.drawPath(waterPath2)
         # 2.画出整个tank的轮廓
        painter.setOpacity(1)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)

        painter.drawLine(-self.width/2, - self.height * 1 / 4, -self.width/2, self.height/2)
        painter.drawLine(-self.width/2, self.height/2, self.width/2, self.height/2)
        painter.drawLine(self.width/2, self.height/2, self.width/2, -self.height * 1 / 4)
        # 画出最后的中间管路
        painter.drawLine(0, - self.height/2, 0, self.height * 2 / 5)
        # 4.显示文本
        if self.textEnable:
            self.text = str(round(self.value, 1)) + self.unit + "(" + format(self._percent, '.0%') + ")"
            # painter.setPen(self._pen_default)
            painter.setFont(QFont(self.textFont, self.width / 12, QFont.Medium))  # 第二个参数是字体大小
            # painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
            # 波浪的总高度，也就深度，不是幅值，从液面顶到油箱底的深度
            painter.drawText(- self.width *3/ 8, self.height * 0.46, self.text)

    def time_out(self):
        self.t += self.sampleTime
        self.update()
# 3.simple_tank：静止的简单tank符号
class GraphicsNode_simple_tank(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "cm"
        self.width = 250  # 整个控件边界的宽度
        self.height = self.width/2  # 整个控件边界的高度

         # 修改父类变量
        self.maxValue = 100
        self.minValue = 0
        self.value = 50  # _value为内部变量，此句话意思要调用一下value函数，更新初始状态

        self.textEnable = False

        # 修改 socket信息
        self.socketInfo = [[QPointF(0, -self.height/2), 2]]


    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
        # self._deepth = self._percent * self.height * 1 / 2  # 像素单位的深度
        # y_deep = self.height - self._deepth - self._amplitude  # 液面的中值坐标
        # path.moveTo(0, y_deep)
        #
        # self._phase1 = self.width / 50 * self.t  # 每次更新相位自动加
        # for x_wave in range(self.width):
        #     y_wave = self._amplitude * math.sin(2 * math.pi * self._frequency * x_wave + self._phase1) + y_deep  # 计算波浪点y坐标
        #     path.lineTo(x_wave, y_wave)
        # path.lineTo(self.width, self.height)
        # path.lineTo(0, self.height)
        # path.lineTo(0, y_deep)
        #
        # painter.setBrush(Qt.darkRed)
        # painter.setOpacity(0.2)
        # painter.drawPath(path)
        # 2.画出整个tank的轮廓
        painter.setOpacity(1)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)

        painter.drawLine(-self.width /2, 0, -self.width /2, self.height/2)
        painter.drawLine(-self.width /2, self.height/2, self.width /2, self.height/2)
        painter.drawLine(self.width/2, self.height/2, self.width/2, 0)
        # 画出最后的中间管路
        painter.drawLine(0, -self.height/2, 0, self.height * 2 / 5)
        # 4.显示文本
        if self.textEnable:
            self._text = str(round(self.value, 1)) + self.unit + "(" + format(self._percent, '.0%') + ")"
            painter.setPen(self._pen_default)
            painter.setFont(QFont(self.textFont, self.width / 10, QFont.Medium))  # 第二个参数是字体大小
            # painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
            # 波浪的总高度，也就深度，不是幅值，从液面顶到油箱底的深度
            painter.drawText(self.width / 4, self.height * 0.95, self._text)
# 4.Gauge：会转动的仪表盘
class GraphicsNode_gauge(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "MPa"
        self.width = 300  # 整个控件边界的宽度
        self.height = self.width*2  # 整个控件边界的高度

        # 与偏转相关的物理量
        self.maxValue = 30
        self.minValue = 0
        self.value = 0  # _value为内部变量，此句话意思要调用一下value函数，更新初始状态

        self._angel = 0  # 偏转的角度：protected
        # 修改 socket信息
        self.socketInfo = [[QPointF(0, self.height/2), 2]]


    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)# 把笔给画家
        # 1.画出整个控件的轮廓
        # painter.drawRect(0, 0, self.width, self.height)

        # 1. 绘制一个圆 QtGui.QPainter.drawEllipse(center, rx, ry)
        r = self.height / 4
        painter.drawEllipse(QPoint(r-self.width / 2, r - self.height / 2), r, r)  #
        # 2.绘制一条竖线,作为支架
        painter.drawLine(0, 0, 0, self.height/2)  #
        # 绘制旋转点
        painter.save()
        painter.setBrush(Qt.black)
        painter.drawEllipse(QPointF(r -self.width / 2, r - self.height / 2), self.width / 40, self.width / 40)
        painter.restore()
        # painter.drawPoint(r -self.width / 2, r - self.height / 2)
        # 3.绘制指针
        painter.save()
        # min-max 对应 0-360°转角
        pen = painter.pen()
        pen.setWidth(8)
        painter.setPen(pen)
        self._angel = self._percent * 360  # 度
        self._angel = 240 / 360 * self._angel + 60  # 只从60-300转换

        painter.drawLine(r * (1 - math.sin(math.pi / 180 * self._angel) * 3 / 5) -self.width / 2,
                         r * (1 + math.cos(math.pi / 180 * self._angel) * 3 / 5) - self.height / 2,
                         r * (1 + math.sin(math.pi / 180 * self._angel) / 5) - self.width / 2,
                         r * (1 - math.cos(math.pi / 180 * self._angel) / 5)- self.height / 2 )  #

        painter.restore()
        # 4.绘制刻盘圆弧
        # （实际单位为1 / 16度），QPainter.drawArc(rect, a（起始角度）, alen（划过的圆角，单位为1/16度）)
        # 画绿色圆弧
        painter.save()
        pen = QPen()
        # painter.setOpacity(0.4)
        pen.setWidth(30)
        pen.setColor(QColor("#7B68EE"))
        painter.setPen(pen)  # 把笔给画家
        painter.drawArc(QRect(r * 1 / 5 -self.width / 2, r * 1 / 5 - self.height / 2, r * 8 / 5, r * 8 / 5), 210 * 16, -180 * 16)  # 绘画角度为30°~(330°)
        # 画红色圆弧
        pen.setWidth(30)
        pen.setColor(QColor("#FF0000"))
        painter.setPen(pen)  # 把笔给画家
        painter.drawArc(QRect(r * 1 / 5 -self.width / 2, r * 1 / 5 - self.height / 2, r * 8 / 5, r * 8 / 5), 30 * 16, -60 * 16)  # 绘画角度为30°~(330°)

        painter.restore()
        # 4.显示文本
        if self.textEnable:
            self._text = str(round(self.value, 1)) + self.unit
            # painter.setPen(self._pen_default)
            painter.setFont(QFont(self.textFont, self.width/6, QFont.Medium))  # 第二个参数是字体大小
            # painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
            painter.drawText(-self.width*1/4, -self.height*0.3/7, self._text)
# 5.Gauge：伺服阀
class GraphicsNode_servo_valve(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.node_type = "servo valve"
        self.unit = "mA"
        self.width = 2500  # 整个控件边界的宽度
        self.height = self.width/4  # 整个控件边界的高度
        self._OffsetPix = 0  # 阀芯偏移的像素点
        # 与偏转相关的物理量
        self.maxValue = 100
        self.minValue = -100
        self.value = 0  # _value为内部变量，此句话意思要调用一下value函数，更新初始状态
        # 修改 socket坐标信息
        self.socketInfo = [[QPointF(1 / 20 * self.width, self.height/2), 2],
                           [QPointF(-1 / 20 * self.width, self.height/2), 2],
                           [QPointF(-1 / 20 * self.width, -self.height/2), 2],
                           [QPointF(1 / 20 * self.width, -self.height/2), 2]
                           ]
        # 箭头子类嵌入到本控件中
        self._arrow_left = MyArrowItem(self, QPointF(self.width * -11.5 / 25, self.height * 4.5 / 10), QPointF(self.width * -7.5 / 25, 0))
        self._arrow_left.arrowLength = self.width / 50

        self._arrow_right = MyArrowItem(self, QPointF(self.width * 11.5 / 25, self.height * 4.5 / 10), QPointF(self.width * 7.5 / 25, 0))
        self._arrow_right.arrowLength = self.width / 50

    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        # 根据获取的坐标，更新要绘制的路径

        path = QPainterPath()

        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        # 画2个横线
        painter.save()
        pen = painter.pen()
        pen.setWidth(20)
        painter.setPen(pen)
        path.moveTo(self.width *-1.5 / 5, -self.height/2)
        path.lineTo(self.width * 1.5 / 5,  -self.height/2)
        path.moveTo(self.width * -1.5 / 5, self.height/2)
        path.lineTo(self.width * 1.5 / 5, self.height/2)
        painter.drawPath(path)
        path.clear()
        painter.restore()
        # 添加矩形阀芯，从下面开始就是要整体偏移的绘图
        # 计算出杆和隔离柱整体的像素偏移, 距离正中间偏移为0，左边为负，右为正
        self._OffsetPix = (self._percent - 0.5) * self.width * (2 / 5)

        path.addRect(self.width * -1.5 / 5 + self._OffsetPix, self.height *-4 / 10, self.width * 3 / 5,
                     self.height * 8 / 10)
        # 添加矩形电磁线圈
        path.addRect(-self.width / 2 + self._OffsetPix, self.height * 2 / 10, self.width * 1 / 5, self.height * 2 / 10)
        path.addRect(self.width * 1.5 / 5 + self._OffsetPix, self.height * 2 / 10, self.width * 1 / 5,
                     self.height * 2 / 10)

        # 画线左线圈上的线
        path.moveTo(self.width * -11.5/ 25 + self._OffsetPix, self.height * 4 / 10)
        path.lineTo(self.width * -10.5 / 25 + self._OffsetPix, self.height * 2 / 10)
        path.moveTo(self.width * -8.5 / 25 + self._OffsetPix, self.height * 4 / 10)
        path.lineTo(self.width * -9.5 / 25 + self._OffsetPix, self.height * 2 / 10)
        # 画线右线圈上的线
        path.moveTo(self.width * 8.5 / 25 + self._OffsetPix, self.height * 4 / 10)
        path.lineTo(self.width * 9.5 / 25 + self._OffsetPix, self.height * 2 / 10)
        path.moveTo(self.width * 11.5 / 25 + self._OffsetPix, self.height * 4 / 10)
        path.lineTo(self.width * 10.5 / 25 + self._OffsetPix, self.height * 2 / 10)
        # 画中间的竖线
        path.moveTo(self.width * -0.5 / 5 + self._OffsetPix, self.height * - 4 / 10)
        path.lineTo(self.width * -0.5 / 5 + self._OffsetPix, self.height * 4 / 10)

        path.moveTo(self.width * -1 / 20 + self._OffsetPix, self.height * -4 / 10)
        path.lineTo(self.width * -1 / 20 + self._OffsetPix, self.height * 4 / 10)

        path.moveTo(self.width * 1 / 20 + self._OffsetPix, self.height * -4 / 10)
        path.lineTo(self.width * 1 / 20 + self._OffsetPix, self.height * 4 / 10)

        path.moveTo(self.width * 0.5 / 5 + self._OffsetPix, self.height * -4 / 10)
        path.lineTo(self.width * 0.5 / 5 + self._OffsetPix, self.height * 4 / 10)
        # 中间横线
        path.moveTo(self.width * -1 / 20 + self._OffsetPix, 0)
        path.lineTo(self.width * 1 / 20 + self._OffsetPix, 0)

        # 画左边的竖线
        path.moveTo(self.width * -5 / 20 + self._OffsetPix, self.height * -4 / 10)
        path.lineTo(self.width * -5 / 20 + self._OffsetPix, self.height * 4 / 10)

        path.moveTo(self.width * -3 / 20 + self._OffsetPix, self.height * -4 / 10)
        path.lineTo(self.width * -3 / 20 + self._OffsetPix, self.height * 4 / 10)

        # 画右边的斜线
        path.moveTo(self.width * 3 / 20 + self._OffsetPix, self.height * -4 / 10)
        path.lineTo(self.width * 5 / 20 + self._OffsetPix, self.height * 4 / 10)

        path.moveTo(self.width * 3 / 20 + self._OffsetPix, self.height * 4 / 10)
        path.lineTo(self.width * 5 / 20 + self._OffsetPix, self.height * -4 / 10)

        painter.setBrush(Qt.black)
        painter.drawPath(path)

        # 中间添加两个点.点的直径为3
        path.addEllipse(QPointF(self.width * -1 / 20 + self._OffsetPix, 0), 3, 3)
        path.addEllipse(QPointF(self.width * 1 / 20 + self._OffsetPix, 0), 3, 3)

        # path.setFillRule(Qt.WindingFill)  # 所有闭合曲线全部填充
        # 路径
        painter.setBrush(Qt.darkGreen)
        painter.drawPath(path)

        # 两个箭头移动位置,下面self._arrow_right.update()比较耗时,父控件更新，子空间也默认更新
        self._arrow_left.source = QPointF(self.width * -11.5 / 25 + self._OffsetPix, self.height * 4.5 / 10)
        self._arrow_left.dest = QPointF(self.width * -7.5 / 25 + self._OffsetPix, 0)

        self._arrow_right.source = QPointF(self.width * 11.5 / 25 + self._OffsetPix, self.height * 4.5 / 10)
        self._arrow_right.dest = QPointF(self.width * 7.5 / 25 + self._OffsetPix, 0)


        #  添加文字路径
        # 4.显示文本
        if self.textEnable:
            self._text = str(round(self.value, 1)) + self.unit
            painter.setPen(self._pen_default)
            painter.setFont(QFont(self.textFont, self.width / 20, QFont.Medium))  # 第二个参数是字体大小
            # painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
            painter.drawText(QPointF(-self.width/2 + self._OffsetPix, 0), self._text)
# 6.piston：会伸缩的液压缸
class GraphicsNode_pistion(QAbstractGraphicsNode):
    # Piston_type_dual = 0  # 对称缸
    # Piston_type_right = 1  # 右出杆缸
    # Piston_type_left = 2  # 左出杆缸

    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "cm"
        self.width = 5000  # 整个控件边界的宽度
        self.height = self.width/8  # 整个控件边界的高度
        self._OffsetPix = 0  # 阀芯偏移的像素点

        # 修改 socket信息
        self.socketInfo = [[QPointF(-9 / 40 * self.width, self.height/2), 2], [QPointF(9 / 40 * self.width, self.height/2), 2]]

        # 计算加速度方向的属性，即连续三个缸的位置采样点
        self.x1 = 0
        self.x2 = 0
        self.x3 = 0
        self.acceleration = 0  # 加速度方向默认为0

        # 与偏转相关的物理量
        self.maxValue = 100
        self.minValue = -100
        self.value = 0  # _value为内部变量，此句话意思要调用一下value函数，更新初始状态


    # 做的玩，判断缸加速度方向，加速度向右，返回正，否则返回负
    def jugde_acceleration(self, position):
        self.x1 = self.x2
        self.x2 = self.x3
        self.x3 = position
        acceleration = self.x3 - 2 * self.x2 + self.x1
        return acceleration  # 加速度大于零，即方向向右

    # 重写父类value赋值属性，赋值的时候才更新加速度状态
    @QAbstractGraphicsNode.value.setter
    def value(self, value):
        self.acceleration = self.jugde_acceleration(value)
        super(GraphicsNode_pistion, GraphicsNode_pistion).value.__set__(self, value)

    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        pen = QPen()
        pen.setStyle(Qt.DashDotLine)
        pen.setWidth(2)
        pen.setColor(Qt.black)




        # 1.画出整个缸体的轮廓(起始x,起始y,宽，高),缸整体宽度为1/2控件宽度
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)# 把笔给画家
        painter.drawRect(self.width *-1/4, -self.height/2, self.width/2, self.height)
        # 2.画出各个腔室
        pen.setStyle(Qt.NoPen)
        painter.setOpacity(0.6)
        painter.setPen(pen)  # 把笔给画家

        # 计算偏移的像素点和加速度
        self._OffsetPix = (self._percent - 0.5) * self.width * (1 / 2 - 1 / 20)
        # self.acceleration = self.jugde_acceleration(self.value)

        if self.acceleration > 0:  # 表示缸偏右
            # 左腔室轮廓
            painter.setBrush(Qt.red)  # 填充颜色
            painter.drawRect(self.width *(-1/ 4), -self.height / 2, self.width / 4 + self._OffsetPix, self.height)
            # 右腔室轮廓
            painter.setBrush(QColor("#40E0D0"))  # 填充颜色
            painter.drawRect(0 + self._OffsetPix, -self.height / 2, self.width / 4 - self._OffsetPix,
                             self.height)
        elif self.acceleration < 0:  # 表示缸偏左边
            painter.setBrush(QColor("#40E0D0"))  # 填充颜色
            painter.drawRect(self.width * -1 / 4, -self.height/2, self.width / 4 + self._OffsetPix, self.height)
            # 右腔室轮廓
            painter.setBrush(Qt.red)  # 填充颜色
            painter.drawRect(0 + self._OffsetPix, -self.height/2, self.width / 4 - self._OffsetPix,
                             self.height)
        elif self.acceleration == 0:  # 表示缸偏右边
            painter.setBrush(QColor("#40E0D0"))  # 填充颜色
            painter.drawRect(self.width *-1/ 4, -self.height/2, self.width / 4 + self._OffsetPix, self.height)
            # 右腔室轮廓
            painter.setBrush(QColor("#40E0D0"))  # 填充颜色
            painter.drawRect(0 + self._OffsetPix, -self.height/2, self.width / 4 - self._OffsetPix,
                             self.height)

        # painter.drawRect(self.width * 1 / 4, 0, self.width * 2 / 4, self.height)
        # 3.画缸中间的隔离柱，隔离柱厚度取1/20的控件宽度
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)# 把笔给画家
        painter.setBrush(QColor("#B8860B"))  # 填充颜色
        painter.setOpacity(1)
        painter.drawRect(self.width * - 1 / 80 + self._OffsetPix, - self.height/2, self.width * 2 / 80,
                         self.height)
        # 3.根据缸的类型，画缸左右出杆，中位出杆伸出缸外面长度为1/40控件宽度，杆的上下高度为1/10控件高度
        if self.node._node_type == "piston dual":  # 对称缸
            # 3.画缸左出杆，中位出杆伸出缸外面长度为1/40控件宽度，杆的上下高度为1/10控件高度
            painter.drawRect(self.width * (-1 / 4 - 1 / 80) + self._OffsetPix, self.height *  - 1 / 20,
                             self.width * 1 / 4, self.height * 1 / 10)
            # 4.画缸右出杆，中位出杆伸出缸外面长度为1/40控件宽度，杆的上下高度为1/10控件高度
            painter.drawRect(self.width * (1 / 80) + self._OffsetPix, self.height * (- 1 / 20),
                             self.width * 1 / 4, self.height * 1 / 10)
        elif self.node._node_type == "piston right":  # 右出杆
            painter.drawRect(self.width * (1 / 80) + self._OffsetPix, self.height * (- 1 / 20),
                             self.width * 1 / 4, self.height * 1 / 10)
        elif self.node._node_type == "piston left":  # 左出杆
            painter.drawRect(self.width * (-1 / 4 - 1 / 80) + self._OffsetPix, self.height * (- 1 / 20),
                             self.width * 1 / 4, self.height * 1 / 10)

        # 5.显示文本
        if self.textEnable:
            self._text = str(round(self.value, 1)) + self.unit
            painter.setPen(self._pen_default)
            painter.setFont(QFont(self.textFont, self.width / 20, QFont.Medium))  # 第二个参数是字体大小
            # painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
            painter.drawText(-self.width/3.8 + self._OffsetPix, -self.width/100, self._text)
# 7.filter:静止的定量泵
class GraphicsNode_pump(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "L/min"
        self.width = 300  # 整个控件边界的宽度
        self.height = self.width * 2  # 整个控件边界的高度
        self.textEnable = False
        # 修改 socket信息
        self.socketInfo = [[QPointF(0, -self.height/2), 2],
                           [QPointF(0, self.height/2), 2]
                           ]

    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
        # 根据获取的坐标，更新要绘制的路径


        # 画2个竖线
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.drawLine(0, -self.height/2, 0, self.height * -1 / 4)
        painter.drawLine(0, self.height * 1 / 4, 0, self.height/2)
        painter.drawEllipse(QPointF(0, 0), self.height / 4,
                            self.height / 4)
        # 画1个圆上个1个箭头
        tranglePath = QPainterPath()
        tranglePath.moveTo(0, self.height *-1/ 4)
        tranglePath.lineTo(self.width / 8, self.height *-1/ 8)
        tranglePath.lineTo(-self.width / 8, self.height *-1/ 8)
        tranglePath.lineTo(0, self.height * -1/ 4)
        painter.setBrush(Qt.black)
        painter.drawPath(tranglePath)
        #  添加文字路径
        # 4.显示文本
        if self.textEnable:
            self._text = str(round(self.value, 1)) + self.unit
            painter.setPen(self._pen_default)
            painter.setFont(QFont(self.textFont, self.width / 4, QFont.Medium))  # 第二个参数是字体大小
            # painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
            painter.drawText(QPointF(self.width * 2 / 3, self.height), self._text)
# 8.filter:静止的油滤
class GraphicsNode_filter(QAbstractGraphicsNode):
    def __init__(self,parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "L/min"
        self.width = 200  # 整个控件边界的宽度
        self.height = self.width * 1.6  # 整个控件边界的高度
        self.textEnable = False
        # 修改 socket信息
        self.socketInfo = [[QPointF(0, -self.height/2), 2],
                           [QPointF(0, self.height/2), 2]
                           ]

    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
        # 根据获取的坐标，更新要绘制的路径


        # 画2个竖线
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.drawLine(0, -self.height/2, 0, self.height * - 1.5 / 5)
        painter.drawLine(0, self.height * 1.5 / 5, 0, self.height/2)
         # 画1个个正方形
        Path = QPainterPath()
        Path.moveTo(0, self.height * -1.5/ 5)
        Path.lineTo(-self.width / 2, 0)
        Path.lineTo(0, self.height * 1.5 / 5)
        Path.lineTo(self.width/2 , 0)
        Path.lineTo(0, self.height *-1.5/ 5)

        painter.setBrush(QColor("#B8860B"))
        painter.drawPath(Path)
        # 画中间虚线
        pen = painter.pen()
        pen.setStyle(Qt.DotLine)
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawLine(-self.width/2, 0, self.width/2, 0)



        # painter.drawArc(
        #     QRect(-self.width * 2 / 5, self.height * 9.2 / 24, self.height / 4, self.height / 4),
        #     -60 * 16, 120 * 16)
        # painter.drawArc(
        #     QRect(self.width * 3.5 / 5, self.height * 9.2 / 24, self.height / 4, self.height / 4),
        #     120 * 16, 120 * 16)

        # 画1个圆，圆心，直径
        # path.addEllipse(QPointF(self.width / 2, self.height / 2), self.height / 6, self.height /6)

        # 画1个圆上个两个弧形
        # path.arcTo(self.width* 8/ 24, self.height *5/ 12, self.height / 4 , self.height / 4, -45, 90)

        # 路径
        # self.setPath(path)
        # painter.setBrush(Qt.lightGray)
        # painter.drawPath(path)

        #  添加文字路径
        # 4.显示文本
        if self.textEnable:
            self._text = str(round(self.value, 1)) + self.unit
            painter.setPen(self._pen_default)
            painter.setFont(QFont(self.textFont, self.width / 4, QFont.Medium))  # 第二个参数是字体大小
            # painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
            painter.drawText(QPointF(self.width * 0.5 / 3, self.height/2), self._text)
# 9.accumulator:静止的蓄能器
class GraphicsNode_accumulator(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "mL"
        self.width = 300  # 整个控件边界的宽度
        self.height = self.width * 2.5  # 整个控件边界的高度
        self.textEnable = False
        # 修改 socket信息
        self.socketInfo = [[QPointF(0, self.height/2), 2]]

    # 重写node绘制函数
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
        # 根据获取的坐标，更新要绘制的路径

        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)

        # 画1个个正方形
        radius_corner = self.width/2
        painter.drawRoundedRect(-self.width/2, -self.height/2, self.width, self.height*4/5, radius_corner, radius_corner)  # 后面两个参数为xround – int, yround – int,拐角的圆度
        # 画中间横线
        painter.drawLine(-self.width/2, self.height*-0.5/5, self.width/2, self.height*-0.5/5)
        # 画下面竖线
        painter.drawLine(0, self.height * 1.5/5, 0, self.height/2)
        # 画弹簧
        path = QPainterPath()
        path.moveTo(self.width *-0.5/ 3, self.height* -1.5/5)
        path.lineTo(self.width * 0.5 / 3, self.height/5 + self.height/20 - self.height/2)
        path.lineTo(self.width * -0.5 / 3, self.height / 5 + self.height * 2 / 30 - self.height/2)
        path.lineTo(self.width * 0.5 / 3, self.height / 5 + self.height * 3 / 30 - self.height/2)
        path.lineTo(self.width * -0.5 / 3, self.height / 5 + self.height * 4 / 30 - self.height/2)
        path.lineTo(self.width * 0.5 / 3, self.height / 5 + self.height * 5 / 30 - self.height/2)
        path.lineTo(self.width * -0.5 / 3, self.height / 5 + self.height * 6 / 30 - self.height/2)
        painter.drawPath(path)
        # 4.显示文本
        # if self.textEnable:
        #     self._text = str(round(self.value, 1)) + self.unit
        #     painter.setPen(self._pen_default)
        #     painter.setFont(QFont(self.textFont, self.width / 4, QFont.Medium))  # 第二个参数是字体大小
        #     painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
        #     painter.drawText(QPointF(self.width * 2 / 3, self.height), self._text)
# 10.one-way valve:静止的单向阀
class GraphicsNode_oneway_valve(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "mL"
        self.width = 150  # 整个控件边界的宽度
        self.height = self.width * 2  # 整个控件边界的高度
        # 修改 socket信息
        self.socketInfo = [[QPointF(0, -self.height/2), 2],
                           [QPointF(0, self.height/2), 2]
                           ]

    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
        # 画2个竖线和圆
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.drawLine(0, -self.height/2, 0, self.height * (-1 / 4 - 1/20))
        painter.drawLine(0, self.height * (1 / 4 - 1/20), 0, self.height/2)
        painter.drawEllipse(QPointF(0, self.height * ( - 2/20)), self.height / 5,
                            self.height / 5)
        # 画1个圆上个楔形切线直线
        painter.drawLine(-self.width/2,  self.height*( - 1 / 20), 0, self.height * (1 / 4 - 1 / 20))
        painter.drawLine(self.width/2,  self.height*(- 1 / 20), 0, self.height * (1 / 4 - 1 / 20))
        # 4.显示文本
        # if self.textEnable:
        #     self._text = str(round(self.value, 1)) + self.unit
        #     painter.setPen(self._pen_default)
        #     painter.setFont(QFont('Times New Roman', self.width / 4, QFont.Medium))  # 第二个参数是字体大小
        #     painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
        #     painter.drawText(QPointF(self.width * 2 / 3, self.height), self._text)
# 11.静止的溢流阀
class GraphicsNode_relief_valve(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.unit = "mL"
        self.width = 500  # 整个控件边界的宽度
        self.height = self.width * 1  # 整个控件边界的高度
        # 修改 socket信息
        self.socketInfo = [[QPointF(1 / 8 * self.width, -self.height/2), 2],
                           [QPointF(1 / 8 * self.width, self.height/2), 2]
                           ]
        # 箭头子类嵌入到本控件中
        self._arrow_left = MyArrowItem(self, QPointF(0, self.height * -2 / 6),
                                       QPointF(0, self.height * 1.8 / 6))
        self._arrow_left.arrowLength = self.width / 20

    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)
        # 根据获取的坐标，更新要绘制的路径
        path = QPainterPath()

        # 1. 画2个竖线
        pen = self._pen_default if not self.isSelected() else self._pen_selected
        painter.setPen(pen)
        painter.drawLine(self.width * 1 / 8, - self.height/2, self.width * 1 / 8, self.height * -2 / 6)
        painter.drawLine(self.width * 1 / 8, self.height * 2 / 6, self.width * 1 / 8, self.height/2)

        painter.save()
        painter.setBrush(QColor("#B8860B"))
        painter.drawRect(self.width * (1 / 8 - 2 / 6), self.height * -2 / 6, self.width * 4 / 6, self.height * 4 / 6)
        painter.restore()
        # 2.画弹簧
        # 画弹簧
        path = QPainterPath()
        path.moveTo(self.width * (1 / 8 + 2 / 6), self.height * -2 / 6)
        path.lineTo(self.width * (1 / 8 + 2 / 6 + 1 / 20), 0)
        path.lineTo(self.width * (1 / 8 + 2 / 6 + 2 / 20), self.height * -2 / 6)
        path.lineTo(self.width * (1 / 8 + 2 / 6 + 3 / 20), 0)
        path.lineTo(self.width * (1 / 8 + 2 / 6 + 4 / 20), self.height * -2 / 6)
        path.lineTo(self.width * (1 / 8 + 2 / 6 + 5 / 20), 0)

        painter.drawPath(path)

        # 3.画虚线，下面是拐角的集合
        points = [QPointF(self.width * (1 / 8 - 2 /6), self.height * 1 / 6),
                  QPointF(-self.width/2,self.height * 1 / 6),
                  QPointF(-self.width/2, -self.height/2),
                  QPointF(self.width * -1/8, -self.height/2),
                  QPointF(self.width * 1 / 8, self.height * -2 / 6),
                  ]
        path = QPainterPath(points[0])  # 先到 第一个点
        for point in points:
            path.lineTo(point)
        pen.setStyle(Qt.DotLine)

        painter.setPen(pen)
        painter.drawPath(path)
        pen.setStyle(Qt.SolidLine)  # 还原画笔原有的实线状态，为下一次绘图做准备








        # #  添加文字路径
        # # 4.显示文本
        # if self.textEnable:
        #     self._text = str(round(self.value, 1)) + self.unit
        #     painter.setPen(self._pen_default)
        #     painter.setFont(QFont('Times New Roman', self.width / 4, QFont.Medium))  # 第二个参数是字体大小
        #     painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
        #     painter.drawText(QPointF(self.width * 2 / 3, self.height), self._text)
# 12.静止的文本
class GraphicsNode_text(QAbstractGraphicsNode):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自己独特的变量，或者对父类变量进行篡改
        self.text = "Hello world!"
        self.height = 100  # 整个控件边界的高度

        self.textEnable = True









    # 重写node绘制函数，画压力传感器
    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        self.width = self.height * (len(self.text) + 1) / 2  # 整个控件边界的宽度

        pen = self._pen_default if not self.isSelected() else self._pen_selected
        painter.setPen(pen)
        # painter.drawRect(0,0,self.width,self.height)
    #  添加文字路径
        # 4.显示文本
        if self.textEnable:
            # self._text = str(round(self.value, 1)) + self.unit
            painter.setFont(QFont(self.textFont, self.height, QFont.Medium))  # 第二个参数是字体大小
            # painter.setOpacity(0.6)  # 0：完全透明，1：完全不透明
            painter.drawText(QPointF(- self.width/2, self.height/2), self.text)
# 0.箭头，用来嵌入其他控件中, 仅用来在本文件使用
class MyArrowItem(QGraphicsLineItem):
    # source箭头线段起始，dest箭头线段终止
    def __init__(self, parent=None, source=QPointF(0, 0), dest=QPointF(0, 0)):
        super().__init__(parent)
        self.source = source
        self.dest = dest

        self.arrowLength = 20  # 单个箭头的长度
        # 修改选中和不选中的线型
        self._pen_default = QPen(Qt.white)  # QPen(QColor("#7F000000"))
        self._pen_default.setWidth(8)
        self._pen_default.setJoinStyle(Qt.MiterJoin)

        self._pen_selected = QPen(Qt.green)  # QPen(QColor("#FFFFA637"))
        self._pen_selected.setWidth(8)
        self._pen_selected.setJoinStyle(Qt.MiterJoin)




    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):

        self.line = QLineF(self.source, self.dest)
        self.line.setLength(self.line.length() - self.arrowLength)

        # pen = self._pen_default if not self.isSelected() else self._pen_selected

        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)  # 把笔给画家

        # setBrush
        brush = QBrush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)
        painter.setBrush(brush)

        v = self.line.unitVector()
        v.setLength(self.arrowLength)
        v.translate(QPointF(self.line.dx(), self.line.dy()))

        n = v.normalVector()
        n.setLength(n.length() * 0.5)
        n2 = n.normalVector().normalVector()

        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()

        # 方法1
        painter.drawLine(self.line)
        painter.drawPolygon(p1, p2, p3)
#  *************基本元件节点的绘制文件************** End