import os
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from pyHydraulic.node_editor_widget import NodeEditorWidget
from pyHydraulic.node_graphics_node import NODE_TYPES
DEBUG = False

class NodeEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.name_company = '燕山大学-南京工程学院联合研究院'
        self.name_product = '液压编辑器'
        self.version = 1.0

        self.initUI()


    def initUI(self):
        self.createActions()
        self.createMenus()

        # create node editor widget
        self.nodeeditor = NodeEditorWidget(self)
        self.nodeeditor.scene.addHasBeenModifiedListener(self.setTitle)
        self.setCentralWidget(self.nodeeditor)

        self.createStatusBar()

        # set window properties
        self.setGeometry(200, 200, 800, 600)
        self.setTitle()
        self.show()
        # 添加dock窗口
        self.createNodesDock()
        self.listWidget.doubleClicked.connect(self.listDoubleClick)

    def createStatusBar(self):
        self.statusBar().showMessage("")
        self.status_mouse_pos = QLabel("")



        self.statusBar().addPermanentWidget(self.status_mouse_pos)


        self.nodeeditor.view.scenePosChanged.connect(self.onScenePosChanged)
        self.nodeeditor.view.sceneItemSelected.connect(self.onItemSelected)

    def createActions(self):
        self.actNew = QAction('&New', self, shortcut='Ctrl+N', statusTip="Create new graph", triggered=self.onFileNew)
        self.actOpen = QAction('&Open', self, shortcut='Ctrl+O', statusTip="Open file", triggered=self.onFileOpen)
        self.actSave = QAction('&Save', self, shortcut='Ctrl+S', statusTip="Save file", triggered=self.onFileSave)
        self.actSaveAs = QAction('Save &As...', self, shortcut='Ctrl+Shift+S', statusTip="Save file as...", triggered=self.onFileSaveAs)
        self.actExit = QAction('E&xit', self, shortcut='Ctrl+Q', statusTip="Exit application", triggered=self.close)

        self.actUndo = QAction('&Undo', self, shortcut='Ctrl+Z', statusTip="Undo last operation", triggered=self.onEditUndo)
        self.actRedo = QAction('&Redo', self, shortcut='Ctrl+Shift+Z', statusTip="Redo last operation", triggered=self.onEditRedo)
        self.actCut = QAction('Cu&t', self, shortcut='Ctrl+X', statusTip="Cut to clipboard", triggered=self.onEditCut)
        self.actCopy = QAction('&Copy', self, shortcut='Ctrl+C', statusTip="Copy to clipboard", triggered=self.onEditCopy)
        self.actPaste = QAction('&Paste', self, shortcut='Ctrl+V', statusTip="Paste from clipboard", triggered=self.onEditPaste)
        self.actDelete = QAction('&Delete', self, shortcut='Del', statusTip="Delete selected dockWIdget", triggered=self.onEditDelete)
        self.actRotate = QAction('&Rotate', self, shortcut='Ctrl+R', statusTip="rotate selected dockWIdget", triggered=self.onEditRotate)
        self.actScalePlus = QAction('&Scale+', self, shortcut='Ctrl+P', statusTip="scale selected dockWIdget+", triggered=self.onEditScalePlus)
        self.actScaleMinus = QAction('&Scale-', self, shortcut='Ctrl+M', statusTip="scale selected dockWIdget-", triggered=self.onEditScaleMinus)


        self.actAbout = QAction('&About', self, shortcut='Ctrl+A', statusTip="about this program", triggered=self.onAbout)

    def onAbout(self):
        QMessageBox.warning(self,  "关于本程序:"+str(self.version), "本程序由“燕山大学-南京工程学院”采用python编写, 仅供学习，\n请勿用于商业目的，weChat联系人：leebjtu", QMessageBox.Ok)

    def createMenus(self):
        menubar = self.menuBar()

        self.fileMenu = menubar.addMenu('&File')
        self.fileMenu.addAction(self.actNew)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actOpen)
        self.fileMenu.addAction(self.actSave)
        self.fileMenu.addAction(self.actSaveAs)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.actExit)

        self.editMenu = menubar.addMenu('&Edit')
        self.editMenu.addAction(self.actUndo)
        self.editMenu.addAction(self.actRedo)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actCut)
        self.editMenu.addAction(self.actCopy)
        self.editMenu.addAction(self.actPaste)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.actDelete)
        self.editMenu.addAction(self.actRotate)
        self.editMenu.addAction(self.actScalePlus)
        self.editMenu.addAction(self.actScaleMinus)

        self.helpMenu = menubar.addMenu('&Help')
        self.helpMenu.addAction(self.actAbout)

    def setTitle(self):
        title = "[NJIT]液压元件编辑器 - "
        title += self.getCurrentNodeEditorWidget().getUserFriendlyFilename()

        self.setWindowTitle(title)


    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def isModified(self):
        return self.getCurrentNodeEditorWidget().scene.has_been_modified

    def getCurrentNodeEditorWidget(self):
        return self.centralWidget()

    def maybeSave(self):
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "About to loose your work?",
                "The document has been modified.\n Do you want to save your changes?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
              )

        if res == QMessageBox.Save:
            return self.onFileSave()
        elif res == QMessageBox.Cancel:
            return False

        return True
    #  选中node的事件
    def onItemSelected(self,node_selected_name, id):
        self.statusBar().showMessage("selected:[%s], id:[%d]" % (node_selected_name, id))



    def onScenePosChanged(self, x, y):
        self.status_mouse_pos.setText("Scene Pos: [%d, %d]" % (x, y))

    def onFileNew(self):
        if self.maybeSave():
            self.getCurrentNodeEditorWidget().fileNew()
            self.setTitle()


    def onFileOpen(self):
        if self.maybeSave():
            fname, filter = QFileDialog.getOpenFileName(self, 'Open graph from file')
            if fname != '' and os.path.isfile(fname):
                self.getCurrentNodeEditorWidget().fileLoad(fname)
                self.setTitle()

    def onFileSave(self):
        if self.getCurrentNodeEditorWidget().filename is None: return self.onFileSaveAs()
        self.getCurrentNodeEditorWidget().fileSave()
        self.statusBar().showMessage("Successfully saved %s" % self.getCurrentNodeEditorWidget().filename)
        self.setTitle()
        return True

    def onFileSaveAs(self):
        fname, filter = QFileDialog.getSaveFileName(self, 'Save graph to file')
        if fname == '':
            return False
        self.getCurrentNodeEditorWidget().fileSave(fname)
        self.statusBar().showMessage("Successfully saved as %s" % self.getCurrentNodeEditorWidget().filename)
        self.setTitle()
        return True

    def onEditUndo(self):
        self.getCurrentNodeEditorWidget().scene.history.undo()

    def onEditRedo(self):
        self.getCurrentNodeEditorWidget().scene.history.redo()

    def onEditDelete(self):
        self.getCurrentNodeEditorWidget().scene.grScene.views()[0].deleteSelected()

    def onEditRotate(self):
        self.getCurrentNodeEditorWidget().scene.grScene.views()[0].rotateSelected(90)

    def onEditScalePlus(self):
        self.getCurrentNodeEditorWidget().scene.grScene.views()[0].scaleSelected(0.01)

    def onEditScaleMinus(self):
        self.getCurrentNodeEditorWidget().scene.grScene.views()[0].scaleSelected(-0.01)

    def onEditCut(self):
        data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=True)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditCopy(self):
        data = self.getCurrentNodeEditorWidget().scene.clipboard.serializeSelected(delete=False)
        str_data = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(str_data)

    def onEditPaste(self):
        raw_data = QApplication.instance().clipboard().text()

        try:
            data = json.loads(raw_data)
        except ValueError as e:
            print("Pasting of not valid json data!", e)
            return

        # check if the json data are correct
        if 'nodes' not in data:
            print("JSON does not contain any nodes!")
            return

        self.getCurrentNodeEditorWidget().scene.clipboard.deserializeFromClipboard(data)

    def readSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(self.name_company, self.name_product)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())

    # 2019.8.12 添加
    def createNodesDock(self):
        self.dockWIdget = QDockWidget("液压元件库(双击添加)")
        self.listWidget = QListWidget()
        # 使用QListView显示图标
        self.listWidget.setViewMode(QListView.IconMode)
        self.listWidget.setIconSize(QSize(80, 80))
        self.listWidget.setGridSize(QSize(100, 100))
        # 设置QListView大小改变时，图标的调整模式，默认是固定的，但可以改成自动调整
        self.listWidget.setResizeMode(QListView.Adjust)
        # 设置图标可不可以移动，默认是可移动的，但可以改成静态的
        self.listWidget.setMovement(QListView.Static)

        for node_name in NODE_TYPES:
            addItem = QListWidgetItem(node_name)
            # addItem.setIcon(QIcon("./images/flow meter.png"))
            addItem.setIcon(QIcon("./images/"+node_name+".png"))
            self.listWidget.addItem(addItem)


        self.dockWIdget.setWidget(self.listWidget)
        self.dockWIdget.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.dockWIdget)

    def listDoubleClick(self, index):
        node_selected = self.listWidget.currentItem().text()
        self.nodeeditor.addnode(node_selected)
        if DEBUG:print("选择了第%d个项目，为%s"%(index.row(), node_selected))
