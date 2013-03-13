from PyQt4 import QtGui, QtSvg, QtCore
from sleuth.desk.analysis import NodeInfo
from sleuth.hq.controller import AnalysisController
import logging


logger = logging.getLogger(__name__)

FONT_NAME = 'STIXGeneral'

class CFGSvgRenderer(QtSvg.QSvgWidget):
    '''Render the SVG representation of the CFG.'''

    def __init__(self, graph_file_name, command_node_map, scene):
        super(CFGSvgRenderer, self).__init__(graph_file_name)

        self.setMaximumSize(self.sizeHint())
        self.setMinimumSize(self.sizeHint())

        # Add ourselves into the graphics scene
        scene.addWidget(self)

        # Add CFGRenderedNodes for each child element in the SVG graph.
        for node, element_bounds in self.get_child_node_bounds(command_node_map):
            CFGNodeProxy(node, element_bounds, scene)

    def get_child_node_bounds(self, command_node_map):
        '''Get bounds for all children described in the given node map.'''

        found_any = False
        for id, node in command_node_map.items():
            # Don't try to render elements that aren't in this scope
            if not self.renderer().elementExists(id):
                continue

            found_any = True

            bounds = self.renderer().boundsOnElement(id)
            matrix = self.renderer().matrixForElement(id)
            mapped_bounds = matrix.mapRect(bounds)

            yield node, mapped_bounds

        if not found_any:
            raise Exception('Did not find any child bounds from node map. Are you using a broken version of Graphviz? (Like the one that ships with Ubuntu?)')


class CFGNodeProxy(QtGui.QGraphicsEllipseItem):
    def __init__(self, node, bounds, scene):
        super(CFGNodeProxy, self).__init__(bounds)

        self.node = node

        # Use a transparent pen, so we don't re-draw the border from the graph
        pen = QtGui.QPen(QtCore.Qt.transparent)
        self.setPen(pen)

        # Add ourselves into the graphics scene
        self.scene = scene
        scene.addItem(self)

        # Listen for signals from the analysis controller
        controller = AnalysisController.getInstance()
        controller.signals.CFG_NODE_SELECTED.register(self._on_node_selected)
        controller.signals.CFG_NODE_DISPLAY_INFO.register(self._on_node_display_info)

        self.node_info_widget = None

    #
    # Widget Event Handlers
    #

    def mousePressEvent(self, event):
        '''Capture mouse clicks on this element.'''
        controller = AnalysisController.getInstance()
        controller.signals.CFG_NODE_SELECTED.fire(self, self.node)
        controller.signals.CFG_NODE_REQUEST_INFO.fire(self, str(self.node), NodeInfo.Direction.BOTH, NodeInfo.Encoding.UNICODE)

    #
    # Signal Handlers
    #

    def _on_node_selected(self, source, node):
        pen = QtGui.QPen(QtCore.Qt.transparent)

        if node is self.node:
            pen.setColor(QtCore.Qt.red)
            pen.setWidth(4)

            AnalysisController.getInstance().signals.ENSURE_ITEM_VISIBLE.fire(self, self)

        self.setPen(pen)

    def _on_node_display_info(self, source, node_info):
        if self.node_info_widget:
            self.node_info_widget.setVisible(False)
            self.node_info_widget = None

        if node_info.node is self.node:
            self.node_info_widget = CFGNodeInfo(node_info.format(),
                                                scene = self.scene,
                                                parent = self)

            AnalysisController.getInstance().signals.ENSURE_ITEM_VISIBLE.fire(self, self)


class CFGNodeInfo(QtGui.QGraphicsWidget):
    def __init__(self,
                 text,
                 scene,
                 parent):
        super(CFGNodeInfo, self).__init__()

        self.border_item = QtGui.QGraphicsRectItem(parent = self)
        self.text_item = QtGui.QGraphicsTextItem(text, parent = self)
        self.text_item.setFont(QtGui.QFont(FONT_NAME))

        text_rect = self.text_item.boundingRect()

        border_width = text_rect.width() + 10
        border_height = text_rect.height() + 10

        self.border_item.setRect(parent.rect().x() + (.75 * parent.rect().width()) + 5,
                                 parent.rect().y() - border_height + parent.rect().height() / 4,
                                 border_width,
                                 border_height)

        self.text_item.setPos(*self.center_rect(self.border_item.rect(),
                                                text_rect))

        self.border_item.setBrush(QtCore.Qt.yellow)
        scene.addItem(self)

    def center_rect(self, outer_rect, inner_rect):
        center_width = outer_rect.width() / 2
        center_height = outer_rect.height() / 2

        rect_width = inner_rect.width()
        rect_height = inner_rect.height()

        return (outer_rect.x() + center_width - (rect_width / 2),
                outer_rect.y() + center_height - (rect_height / 2))


