from PyQt4 import QtGui, QtCore
from sleuth.desk.analysis import NodeInfo
from sleuth.evidence.gui.autoLayout import AutoLayoutMixin
from sleuth.evidence.gui.cfg_widget import CFGSvgRenderer
from sleuth.hq.controller import AnalysisController
from sleuth.tracks.graphviz_svg import GraphvizSVGRenderer
import logging

logger = logging.getLogger(__name__)


class NextAnalysisStep(object):
    IN = 'in'
    OUT = 'out'

class MainWindow(QtGui.QMainWindow, AutoLayoutMixin):
    LAYOUT_FILE_NAME = 'main_window.ui'


    def __init__(self):
        super(MainWindow, self).__init__()
        self.loadUi()

        self.analysis_controller = AnalysisController.getInstance()
        self.source_text_edit = None


        self.worklist = []
        self.pending_worklist = []
        self.processing_item = None

        self.next_analysis_step = None
        self._set_next_analysis_step(NextAnalysisStep.IN)

        self._connectSignals()
        self._configureWidgets()

    def _configureWidgets(self):
        source_vbox_layout = QtGui.QVBoxLayout()
        self.source_group.setLayout(source_vbox_layout)

        self.worklist_sort_rpo_checkbox.setCheckState(QtCore.Qt.Checked)

    def _connectSignals(self):
        self.action_step_in.triggered.connect(self._on_action_step_in_triggered)
        self.action_step_out.triggered.connect(self._on_action_step_out_triggered)
        self.action_step_over.triggered.connect(self._on_action_step_over_triggered)

        self.action_full_screen.toggled.connect(self.on_action_full_screen_toggled)

        self.analysis_controller.signals.CFG_NODE_SELECTED.register(self._on_node_clicked)
        self.analysis_controller.signals.WORKLIST_UPDATED.register(self._on_worklist_updated)
        self.analysis_controller.signals.ENSURE_ITEM_VISIBLE.register(self._on_ensure_item_visible)
        self.analysis_controller.signals.CLIENT_ANALYSIS_EXCEPTION.register(self._on_client_analysis_exception)
        self.analysis_controller.signals.ANALYSIS_COMPLETE.register(self._on_analysis_complete)

        self.worklist_widget.itemClicked.connect(self._on_worklist_item_clicked)

        self.worklist_sort_rpo_checkbox.stateChanged.connect(self._on_worklist_sort_rpo_checkbox_state_changed)

    def _on_analysis_complete(self, source):
        self.menu_analysis.setEnabled(False)

        self.action_step_over.setEnabled(False)
        self.action_step_in.setEnabled(False)
        self.action_step_out.setEnabled(False)

        self.status_bar.showMessage('Analysis complete.')

    def _set_next_analysis_step(self, next_step):
        assert next_step in (NextAnalysisStep.IN, NextAnalysisStep.OUT), next_step
        self.next_analysis_step = next_step

        self.action_step_over.setEnabled(next_step == NextAnalysisStep.IN)
        self.action_step_in.setEnabled(next_step == NextAnalysisStep.IN)
        self.action_step_out.setEnabled(next_step == NextAnalysisStep.OUT)

        self.worklist_widget.setEnabled(next_step == NextAnalysisStep.IN)

    def _on_client_analysis_exception(self, source, exception):
        # Construct a presentable message to display in the dialog
        message = exception.format_with_traceback()

        QtGui.QMessageBox.critical(None,
                                   'Unhandled exception in client analysis',
                                   message)

    #
    # Rendering Methods
    #

    def render_source(self, program_source):
        self.source_text_edit = QtGui.QTextEdit()
        self.source_text_edit.setText(program_source)
        self.source_text_edit.setReadOnly(True)

        self.source_group.layout().addWidget(self.source_text_edit)

    def render_graph(self, dot_executable, edge_pairs, command_node_map):
        svg_graph_file = GraphvizSVGRenderer(dot_executable).create_graph(edge_pairs)

        scene = QtGui.QGraphicsScene()
        CFGSvgRenderer(svg_graph_file, command_node_map, scene)

        self.graphics_view.setScene(scene)


    #
    # Action Handlers
    #

    def on_action_full_screen_toggled(self, state):
        if state:
            self.showFullScreen()

        else:
            self.showNormal()

    def _on_action_step_in_triggered(self):
        self._set_next_analysis_step(NextAnalysisStep.OUT)
        self._process_selected_worklist_node(NodeInfo.Direction.IN)

    def _on_action_step_out_triggered(self):
        self._set_next_analysis_step(NextAnalysisStep.IN)

        self._on_worklist_updated(self, self.pending_worklist)
        self.pending_worklist = []

        self.analysis_controller.signals.CFG_NODE_REQUEST_INFO.fire(self, str(self.processing_item.text()), NodeInfo.Direction.OUT)

    def _on_action_step_over_triggered(self):
        self._process_selected_worklist_node(NodeInfo.Direction.BOTH)

    def _process_selected_worklist_node(self, node_info_direction):
        row = self.worklist_widget.currentRow()
        self.processing_item = self.worklist_widget.takeItem(row)

        self.analysis_controller.signals.ANALYSIS_STEP.fire(self, str(self.processing_item.text()))
        self.analysis_controller.signals.CFG_NODE_REQUEST_INFO.fire(self,
                                                                    str(self.processing_item.text()),
                                                                    node_info_direction,
                                                                    NodeInfo.Encoding.UNICODE)
    #
    # CFG Node Signal Handlers
    #

    def _on_node_clicked(self, source, node):
        cursor = self.source_text_edit.textCursor()

        lex_span = node.command.lex_span
        cursor.setPosition(lex_span[0])
        cursor.setPosition(lex_span[1], QtGui.QTextCursor.KeepAnchor)

        self.source_text_edit.setTextCursor(cursor)

    def _on_ensure_item_visible(self, source, graphics_item):
        self.graphics_view.ensureVisible(graphics_item)

    #
    # Worklist Signal Handlers
    #

    def _on_worklist_updated(self, source, worklist_labels):
        # If we're in the middle of a step, don't update the worklist immediately
        if self.next_analysis_step == NextAnalysisStep.OUT:
            self.pending_worklist = worklist_labels
            return

        self.worklist_widget.clear()

        for info in worklist_labels:
            self.worklist_widget.addItem(str(info))

        if not self.worklist_widget.currentItem():
            self.worklist_widget.setCurrentRow(0, QtGui.QItemSelectionModel.ClearAndSelect)

    def _on_worklist_current_row_changed(self, current_row):
        self.action_step_over.setEnabled(current_row != -1)

    def _on_worklist_item_clicked(self, worklist_item):
        self.analysis_controller.signals.WORKLIST_ITEM_CLICKED.fire(self, str(worklist_item.text()))
        self.analysis_controller.signals.CFG_NODE_REQUEST_INFO.fire(self, str(worklist_item.text()), NodeInfo.Direction.BOTH)

    def _on_worklist_sort_rpo_checkbox_state_changed(self, state):
        sorting_enabled = (state == QtCore.Qt.Checked)
        self.analysis_controller.signals.SET_WORKLIST_SORTING_ENABLED.fire(self, sorting_enabled)

