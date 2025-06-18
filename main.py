# coding:utf-8
import sys
from PyQt5 import QtGui

from PyQt5.QtCore import Qt, QSize, QUrl, QPoint
from PyQt5.QtGui import QIcon, QDesktopServices, QColor, QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QApplication, QFrame, QWidget, QStackedWidget

from qfluentwidgets import (NavigationItemPosition, MessageBox, MSFluentTitleBar, MSFluentWindow,
                            TabBar, SubtitleLabel, setFont, TabCloseButtonDisplayMode, IconWidget,
                            TransparentDropDownToolButton, TransparentToolButton, setTheme, Theme, isDarkTheme)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import AcrylicWindow

# Error_decode 组件
from error_decode import ErrorDecode

# 变量定义存取
from data_define_manager import VariableSaver, DataDefineManager

# 使用教程字符串
usage_text = """
使用方法：
1 .解码->变量定义->输入代码中的变量定义,尽量包含 { 和 }\n
2. } 后面的变量名会自动解析;\n
3. 手动更改变量名,随后点击按钮进行保存(重名会覆盖);\n
4. 保存后的变量定义会保存到本地,新建页面或重启即可在已保存定义中看到;\n
5. 数据管理页面可对已经保存的变量进行删除操作;\n
6. 软件最上面有类似浏览器的设计,可同时打开多个标签页;\n
7. 有些按钮没实现具体功能,毕竟时间和精力有限;\n
8. 觉得好用的话,可以大喊“少爷NB!"
"""

class PhotoWidget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))
        
class TextWidget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignLeft)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignLeft)
        self.setObjectName(text.replace(' ', '-'))
        
class CustomTitleBar(MSFluentTitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)

        # add buttons
        self.toolButtonLayout = QHBoxLayout()
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(96, 96, 96)
        self.searchButton = TransparentToolButton(FIF.SEARCH_MIRROR.icon(color=color), self)
        self.forwardButton = TransparentToolButton(FIF.RIGHT_ARROW.icon(color=color), self)
        self.backButton = TransparentToolButton(FIF.LEFT_ARROW.icon(color=color), self)

        self.forwardButton.setDisabled(True)
        self.toolButtonLayout.setContentsMargins(20, 0, 20, 0)
        self.toolButtonLayout.setSpacing(15)
        self.toolButtonLayout.addWidget(self.searchButton)
        self.toolButtonLayout.addWidget(self.backButton)
        self.toolButtonLayout.addWidget(self.forwardButton)
        self.hBoxLayout.insertLayout(4, self.toolButtonLayout)

        # add tab bar
        self.tabBar = TabBar(self)

        self.tabBar.setMovable(True)
        self.tabBar.setTabMaximumWidth(220)
        self.tabBar.setTabShadowEnabled(False)
        self.tabBar.setTabSelectedBackgroundColor(QColor(255, 255, 255, 125), QColor(255, 255, 255, 50))
        # self.tabBar.setScrollable(True)
        # self.tabBar.setCloseButtonDisplayMode(TabCloseButtonDisplayMode.ON_HOVER)

        self.tabBar.tabCloseRequested.connect(self.tabBar.removeTab)
        self.tabBar.currentChanged.connect(lambda i: print(self.tabBar.tabText(i)))

        self.hBoxLayout.insertWidget(5, self.tabBar, 1)
        self.hBoxLayout.setStretch(6, 0)

        # add avatar
        self.avatar = TransparentDropDownToolButton('resource/青语.png', self)
        self.avatar.setIconSize(QSize(26, 26))
        self.avatar.setFixedHeight(30)
        self.hBoxLayout.insertWidget(7, self.avatar, 0, Qt.AlignRight)
        self.hBoxLayout.insertSpacing(8, 20)

    def canDrag(self, pos: QPoint):
        if not super().canDrag(pos):
            return False

        pos.setX(pos.x() - self.tabBar.x())
        return not self.tabBar.tabRegion().contains(pos)


class Window(MSFluentWindow):

    def __init__(self):
        self.isMicaEnabled = False

        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        self.tabBar = self.titleBar.tabBar  # type: TabBar

        # create sub interface
        self.homeInterface = QStackedWidget(self, objectName='homeInterface')
        self.appInterface = DataDefineManager('DataDefineManager Interface', self)
        self.photoInterface = PhotoWidget('Video Interface', self)
        
        pixmap = QPixmap("./resource/青语.png")  # 替换为你的图片路径
        # 调整图片大小（保持比例）
        scaled_pixmap = pixmap.scaled(
            800, 600,  # 目标尺寸
            Qt.KeepAspectRatio,  # 保持宽高比
            Qt.SmoothTransformation  # 平滑缩放
        )
        self.photoInterface.label.setPixmap(scaled_pixmap)
        
        self.libraryInterface = TextWidget('library Interface', self)
        self.libraryInterface.label.setText(usage_text)
        
        
        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '解码', FIF.HOME_FILL)
        self.addSubInterface(self.appInterface, FIF.DICTIONARY, '数据管理')
        self.addSubInterface(self.photoInterface, FIF.PHOTO, '青语')

        self.addSubInterface(self.libraryInterface, FIF.BOOK_SHELF,
                             '教程', FIF.LIBRARY_FILL, NavigationItemPosition.BOTTOM)
        self.navigationInterface.addItem(
            routeKey='Help',
            icon=FIF.HELP,
            text='帮助',
            onClick=self.showMessageBox,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(
            self.homeInterface.objectName())

        # add tab
        self.addTab('Honey', 'Honey~')

        self.tabBar.currentChanged.connect(self.onTabChanged)
        self.tabBar.tabAddRequested.connect(self.onTabAddRequested)

    def initWindow(self):
        self.resize(1100, 750)
        self.setWindowIcon(QIcon(':/qfluentwidgets/images/logo.png'))
        self.setWindowTitle('Error Dcode')

        # 设置窗口尺寸
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def showMessageBox(self):
        w = MessageBox(
            '作者:Lay.zhu',
            '本项目基于Fluent Widgets开发\n这么简单的工具还想要帮助?',
            self
        )
        w.yesButton.setText('点这个按钮')
        w.cancelButton.setText('别听他的,点我!')
        w.exec()
    # 页面切换逻辑
    def onTabChanged(self, index: int):
        objectName = self.tabBar.currentTab().routeKey()
        widget = self.findChild(ErrorDecode, objectName)
        if widget:
            self.homeInterface.setCurrentWidget(widget)
        else:
            print(f"Widget with objectName {objectName} not found in stack.")
    def onTabAddRequested(self):
        text = f'功德+{self.tabBar.count()}'
        self.addTab(text, text)

    def addTab(self, routeKey, text):
        self.tabBar.addTab(routeKey, text)
        self.homeInterface.addWidget(ErrorDecode(text, routeKey, self))


if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    # setTheme(Theme.DARK)

    app = QApplication(sys.argv)
    w = Window()
    w.show()
    app.exec_()
