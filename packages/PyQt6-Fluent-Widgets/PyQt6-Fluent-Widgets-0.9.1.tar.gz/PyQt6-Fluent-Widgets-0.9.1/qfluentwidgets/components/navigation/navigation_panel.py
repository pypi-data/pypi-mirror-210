# coding:utf-8
from enum import Enum
from typing import Dict, Union

from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, QSize, QEvent, QEasingCurve, pyqtSignal, QObject
from PyQt6.QtGui import QResizeEvent, QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFrame, QApplication

from .navigation_widget import (NavigationTreeWidgetBase, NavigationToolButton, NavigationWidget, NavigationSeparator,
                                NavigationTreeWidget)
from ..widgets.scroll_area import SingleDirectionScrollArea
from ..widgets.tool_tip import ToolTipFilter
from ...common.router import qrouter
from ...common.deprecation import deprecated
from ...common.style_sheet import FluentStyleSheet
from ...common.icon import FluentIconBase
from ...common.icon import FluentIcon as FIF


class NavigationDisplayMode(Enum):
    """ Navigation display mode """
    MINIMAL = 0
    COMPACT = 1
    EXPAND = 2
    MENU = 3


class NavigationItemPosition(Enum):
    """ Navigation item position """
    TOP = 0
    SCROLL = 1
    BOTTOM = 2


class NavigationToolTipFilter(ToolTipFilter):
    """ Navigation tool tip filter """

    def _canShowToolTip(self) -> bool:
        isVisible = super()._canShowToolTip()
        parent = self.parent()  # type: NavigationWidget
        return isVisible and parent.isCompacted


class RouteKeyError(Exception):
    """ Route key error """


class NavigationItem:
    """ Navigation item """

    def __init__(self, routeKey: str, parentRouteKey: str, widget: NavigationWidget):
        self.routeKey = routeKey
        self.parentRouteKey = parentRouteKey
        self.widget = widget


class NavigationPanel(QFrame):
    """ Navigation panel """

    displayModeChanged = pyqtSignal(NavigationDisplayMode)

    def __init__(self, parent=None, isMinimalEnabled=False):
        super().__init__(parent=parent)
        self._parent = parent   # type: QWidget
        self._isMenuButtonVisible = True
        self._isReturnButtonVisible = False

        self.scrollArea = SingleDirectionScrollArea(self)
        self.scrollWidget = QWidget()

        self.menuButton = NavigationToolButton(FIF.MENU, self)
        self.returnButton = NavigationToolButton(FIF.RETURN, self)

        self.vBoxLayout = NavigationItemLayout(self)
        self.topLayout = NavigationItemLayout()
        self.bottomLayout = NavigationItemLayout()
        self.scrollLayout = NavigationItemLayout(self.scrollWidget)

        self.items = {}   # type: Dict[str, NavigationItem]
        self.history = qrouter

        self.expandAni = QPropertyAnimation(self, b'geometry', self)
        self.expandWidth = 322

        self.isMinimalEnabled = isMinimalEnabled
        if isMinimalEnabled:
            self.displayMode = NavigationDisplayMode.MINIMAL
        else:
            self.displayMode = NavigationDisplayMode.COMPACT

        self.__initWidget()

    def __initWidget(self):
        self.resize(48, self.height())
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        self.window().installEventFilter(self)

        self.returnButton.hide()
        self.returnButton.setDisabled(True)

        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setWidget(self.scrollWidget)
        self.scrollArea.setWidgetResizable(True)

        self.expandAni.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.expandAni.setDuration(150)

        self.menuButton.clicked.connect(self.toggle)
        self.expandAni.finished.connect(self._onExpandAniFinished)
        self.history.emptyChanged.connect(self.returnButton.setDisabled)
        self.returnButton.clicked.connect(self.history.pop)

        # add tool tip
        self.returnButton.installEventFilter(ToolTipFilter(self.returnButton, 1000))
        self.returnButton.setToolTip(self.tr('Back'))

        self.menuButton.installEventFilter(ToolTipFilter(self.menuButton, 1000))
        self.menuButton.setToolTip(self.tr('Open Navigation'))

        self.setProperty('menu', False)
        self.scrollWidget.setObjectName('scrollWidget')
        FluentStyleSheet.NAVIGATION_INTERFACE.apply(self)
        self.__initLayout()

    def __initLayout(self):
        self.vBoxLayout.setContentsMargins(0, 5, 0, 5)
        self.topLayout.setContentsMargins(4, 0, 4, 0)
        self.bottomLayout.setContentsMargins(4, 0, 4, 0)
        self.scrollLayout.setContentsMargins(4, 0, 4, 0)
        self.vBoxLayout.setSpacing(4)
        self.topLayout.setSpacing(4)
        self.bottomLayout.setSpacing(4)
        self.scrollLayout.setSpacing(4)

        self.vBoxLayout.addLayout(self.topLayout, 0)
        self.vBoxLayout.addWidget(self.scrollArea, 1, Qt.AlignmentFlag.AlignTop)
        self.vBoxLayout.addLayout(self.bottomLayout, 0)

        self.vBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.topLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scrollLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bottomLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.topLayout.addWidget(self.returnButton, 0, Qt.AlignmentFlag.AlignTop)
        self.topLayout.addWidget(self.menuButton, 0, Qt.AlignmentFlag.AlignTop)

    def widget(self, routeKey: str):
        if routeKey not in self.items:
            raise RouteKeyError(f"`{routeKey}` is illegal.")

        return self.items[routeKey].widget

    def addItem(self, routeKey: str, icon: Union[str, QIcon, FluentIconBase], text: str, onClick=None, selectable=True,
                position=NavigationItemPosition.TOP, tooltip: str = None, parentRouteKey: str = None):
        """ add navigation item

        Parameters
        ----------
        routeKey: str
            the unique name of item

        icon: str | QIcon | FluentIconBase
            the icon of navigation item

        text: str
            the text of navigation item

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        selectable: bool
            whether the item is selectable

        tooltip: str
            the tooltip of item

        parentRouteKey: str
            the route key of parent item, the parent widget should be `NavigationTreeWidget`
        """
        return self.insertItem(-1, routeKey, icon, text, onClick, selectable, position, tooltip, parentRouteKey)

    def addWidget(self, routeKey: str, widget: NavigationWidget, onClick=None, position=NavigationItemPosition.TOP,
                  tooltip: str = None, parentRouteKey: str = None):
        """ add custom widget

        Parameters
        ----------
        routeKey: str
            the unique name of item

        widget: NavigationWidget
            the custom widget to be added

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        tooltip: str
            the tooltip of widget

        parentRouteKey: str
            the route key of parent item, the parent item should be `NavigationTreeWidget`
        """
        self.insertWidget(-1, routeKey, widget, onClick, position, tooltip, parentRouteKey)

    def insertItem(self, index: int, routeKey: str, icon: Union[str, QIcon, FluentIconBase], text: str, onClick=None,
                   selectable=True, position=NavigationItemPosition.TOP, tooltip: str = None, parentRouteKey=None):
        """ insert navigation tree item

        Parameters
        ----------
        index: int
            the insert position of parent widget

        routeKey: str
            the unique name of item

        icon: str | QIcon | FluentIconBase
            the icon of navigation item

        text: str
            the text of navigation item

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        selectable: bool
            whether the item is selectable

        tooltip: str
            the tooltip of item

        parentRouteKey: str
            the route key of parent item, the parent item should be `NavigationTreeWidget`
        """
        if routeKey in self.items:
            return

        w = NavigationTreeWidget(icon, text, selectable, self)
        self.insertWidget(index, routeKey, w, onClick, position, tooltip, parentRouteKey)
        return w

    def insertWidget(self, index: int, routeKey: str, widget: NavigationWidget, onClick=None,
                     position=NavigationItemPosition.TOP, tooltip: str = None, parentRouteKey: str = None):
        """ insert custom widget

        Parameters
        ----------
        index: int
            insert position

        routeKey: str
            the unique name of item

        widget: NavigationWidget
            the custom widget to be added

        onClick: callable
            the slot connected to item clicked signal

        position: NavigationItemPosition
            where the button is added

        tooltip: str
            the tooltip of widget

        parentRouteKey: str
            the route key of parent item, the parent item should be `NavigationTreeWidget`
        """
        if routeKey in self.items:
            return

        self._registerWidget(routeKey, parentRouteKey, widget, onClick, tooltip)
        if parentRouteKey:
            self.widget(parentRouteKey).insertChild(index, widget)
        else:
            self._insertWidgetToLayout(index, widget, position)

    def addSeparator(self, position=NavigationItemPosition.TOP):
        """ add separator

        Parameters
        ----------
        position: NavigationPostion
            where to add the separator
        """
        self.insertSeparator(-1, position)

    def insertSeparator(self, index: int, position=NavigationItemPosition.TOP):
        """ add separator

        Parameters
        ----------
        index: int
            insert position

        position: NavigationPostion
            where to add the separator
        """
        separator = NavigationSeparator(self)
        self._insertWidgetToLayout(index, separator, position)

    def _registerWidget(self, routeKey: str, parentRouteKey: str, widget: NavigationWidget, onClick, tooltip: str):
        """ register widget """
        widget.clicked.connect(self._onWidgetClicked)

        if onClick is not None:
            widget.clicked.connect(onClick)

        widget.setProperty('routeKey', routeKey)
        widget.setProperty('parentRouteKey', parentRouteKey)
        self.items[routeKey] = NavigationItem(routeKey, parentRouteKey, widget)

        if self.displayMode in [NavigationDisplayMode.EXPAND, NavigationDisplayMode.MENU]:
            widget.setCompacted(False)

        if tooltip:
            widget.setToolTip(tooltip)
            widget.installEventFilter(NavigationToolTipFilter(widget, 1000))

    def _insertWidgetToLayout(self, index: int, widget: NavigationWidget, position: NavigationItemPosition):
        """ insert widget to layout """
        if position == NavigationItemPosition.TOP:
            widget.setParent(self)
            self.topLayout.insertWidget(index, widget, 0, Qt.AlignmentFlag.AlignTop)
        elif position == NavigationItemPosition.SCROLL:
            widget.setParent(self.scrollWidget)
            self.scrollLayout.insertWidget(index, widget, 0, Qt.AlignmentFlag.AlignTop)
        else:
            widget.setParent(self)
            self.bottomLayout.insertWidget(index, widget, 0, Qt.AlignmentFlag.AlignBottom)

        widget.show()

    def removeWidget(self, routeKey: str):
        """ remove widget

        Parameters
        ----------
        routeKey: str
            the unique name of item
        """
        if routeKey not in self.items:
            return

        item = self.items.pop(routeKey)

        if item.parentRouteKey is not None:
            self.widget(item.parentRouteKey).removeChild(item.widget)

        if isinstance(item.widget, NavigationTreeWidgetBase):
            for child in item.widget.findChildren(NavigationWidget, options=Qt.FindChildrenRecursively):
                key = child.property('routeKey')
                if key is None:
                    continue

                self.items.pop(key)
                child.deleteLater()
                self.history.remove(key)

        item.widget.deleteLater()
        self.history.remove(routeKey)

    def setMenuButtonVisible(self, isVisible: bool):
        """ set whether the menu button is visible """
        self._isMenuButtonVisible = isVisible
        self.menuButton.setVisible(isVisible)

    def setReturnButtonVisible(self, isVisible: bool):
        """ set whether the return button is visible """
        self._isReturnButtonVisible = isVisible
        self.returnButton.setVisible(isVisible)

    def setExpandWidth(self, width: int):
        """ set the maximum width """
        if width <= 42:
            return

        self.expandWidth = width
        NavigationWidget.EXPAND_WIDTH = width - 10

    def expand(self):
        """ expand navigation panel """
        self._setWidgetCompacted(False)
        self.expandAni.setProperty('expand', True)
        self.menuButton.setToolTip(self.tr('Close Navigation'))

        # determine the display mode according to the width of window
        # https://learn.microsoft.com/en-us/windows/apps/design/controls/navigationview#default
        expandWidth = 1007 + self.expandWidth - 322
        if self.window().width() > expandWidth and not self.isMinimalEnabled:
            self.displayMode = NavigationDisplayMode.EXPAND
        else:
            self.setProperty('menu', True)
            self.setStyle(QApplication.style())

            self.displayMode = NavigationDisplayMode.MENU
            if not self._parent.isWindow():
                pos = self.parent().pos()
                self.setParent(self.window())
                self.move(pos)

            self.show()

        self.displayModeChanged.emit(self.displayMode)
        self.expandAni.setStartValue(
            QRect(self.pos(), QSize(48, self.height())))
        self.expandAni.setEndValue(
            QRect(self.pos(), QSize(self.expandWidth, self.height())))
        self.expandAni.start()

    def collapse(self):
        """ collapse navigation panel """
        if self.expandAni.state() == QPropertyAnimation.State.Running:
            return

        for item in self.items.values():
            w = item.widget
            if isinstance(w, NavigationTreeWidgetBase) and w.isRoot():
                w.setExpanded(False)

        self.expandAni.setStartValue(
            QRect(self.pos(), QSize(self.width(), self.height())))
        self.expandAni.setEndValue(
            QRect(self.pos(), QSize(48, self.height())))
        self.expandAni.setProperty('expand', False)
        self.expandAni.start()

        self.menuButton.setToolTip(self.tr('Open Navigation'))

    def toggle(self):
        """ toggle navigation panel """
        if self.displayMode in [NavigationDisplayMode.COMPACT, NavigationDisplayMode.MINIMAL]:
            self.expand()
        else:
            self.collapse()

    def setCurrentItem(self, routeKey: str):
        """ set current selected item

        Parameters
        ----------
        routeKey: str
            the unique name of item
        """
        if routeKey not in self.items:
            return

        for k, item in self.items.items():
            item.widget.setSelected(k == routeKey)

    def _onWidgetClicked(self):
        widget = self.sender()  # type: NavigationWidget
        if not widget.isSelectable:
            return

        self.setCurrentItem(widget.property('routeKey'))
        if widget is not self.menuButton and self.displayMode == NavigationDisplayMode.MENU \
                and not (isinstance(widget, NavigationTreeWidgetBase) and not widget.isLeaf()):
            self.collapse()

    def resizeEvent(self, e: QResizeEvent):
        if e.oldSize().height() == self.height():
            return

        th = self.topLayout.minimumSize().height()
        bh = self.bottomLayout.minimumSize().height()
        h = self.height()-th-bh-20
        self.scrollArea.setFixedHeight(max(h, 36))

    def eventFilter(self, obj, e: QEvent):
        if obj is not self.window():
            return super().eventFilter(obj, e)

        if e.type() == QEvent.Type.MouseButtonRelease:
            if not self.geometry().contains(e.pos()) and self.displayMode == NavigationDisplayMode.MENU:
                self.collapse()
        elif e.type() == QEvent.Type.Resize:
            w = e.size().width()
            if w < 1008 and self.displayMode == NavigationDisplayMode.EXPAND:
                self.collapse()
            elif w >= 1008 and self.displayMode == NavigationDisplayMode.COMPACT and \
                    not self._isMenuButtonVisible:
                self.expand()

        return super().eventFilter(obj, e)

    def _onExpandAniFinished(self):
        if not self.expandAni.property('expand'):
            if self.isMinimalEnabled:
                self.displayMode = NavigationDisplayMode.MINIMAL
            else:
                self.displayMode = NavigationDisplayMode.COMPACT

            self.displayModeChanged.emit(self.displayMode)

        if self.displayMode == NavigationDisplayMode.MINIMAL:
            self.hide()
            self.setProperty('menu', False)
            self.setStyle(QApplication.style())
        elif self.displayMode == NavigationDisplayMode.COMPACT:
            self.setProperty('menu', False)
            self.setStyle(QApplication.style())

            for item in self.items.values():
                item.widget.setCompacted(True)

            if not self._parent.isWindow():
                self.setParent(self._parent)
                self.move(0, 0)
                self.show()

    def _setWidgetCompacted(self, isCompacted: bool):
        """ set whether the navigation widget is compacted """
        for item in self.findChildren(NavigationWidget):
            item.setCompacted(isCompacted)

    def layoutMinHeight(self):
        th = self.topLayout.minimumSize().height()
        bh = self.bottomLayout.minimumSize().height()
        sh = sum(w.height() for w in self.findChildren(NavigationSeparator))
        spacing = self.topLayout.count() * self.topLayout.spacing()
        spacing += self.bottomLayout.count() * self.bottomLayout.spacing()
        return 36 + th + bh + sh + spacing

    @deprecated('0.9.0', alternative='qrouter.setDefaultRouteKey')
    def setDefaultRouteKey(self, key: str):
        """ set the routing key to use when the navigation history is empty """
        pass


class NavigationItemLayout(QVBoxLayout):
    """ Navigation layout """

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        for i in range(self.count()):
            item = self.itemAt(i)
            if isinstance(item.widget(), NavigationSeparator):
                geo = item.geometry()
                item.widget().setGeometry(0, geo.y(), geo.width(), geo.height())

