'''
Created on Apr 20, 2010

@author: chris
'''
from PyQt4 import QtGui
from PyQt4.QtGui import QFileDialog
from sleuth.evidence.gui.autoLayout import AutoLayoutMixin
import logging
import os

logger = logging.getLogger(__name__)

class NewAnalysisDialog(QtGui.QDialog, AutoLayoutMixin):

    LAYOUT_FILE_NAME = 'new_analysis_dialog.ui'

    @classmethod
    def show_dialog(cls,
                    source_file,
                    analysis_module_path,
                    parent = None):
        dialog = cls(source_file, analysis_module_path, parent)
        result = dialog.exec_()

        if result:
            return dialog

        return None

    def __init__(self, source_file, analysis_module_path, parent = None):
        super(NewAnalysisDialog, self).__init__(parent)

        self.loadUi()

        self._configure_widgets(source_file, analysis_module_path)
        self._connect_signals()

    def get_source_file_path(self):
        if self._is_source_file_valid():
            return str(self.source_file_text.text())

        return None

    def get_analysis_module_path(self):
        if self._is_analysis_module_path_valid():
            return str(self.analysis_module_path_text.text())

        return None

    def _configure_widgets(self, source_file, analysis_module_path):
        self.source_file_text.setText(source_file)
        self.analysis_module_path_text.setText(analysis_module_path)

        self.source_file_error_label.setText('The selected file does not exist.')
        self.analysis_module_path_error_label.setText('The selected file does not exist.')

        self.source_file_error_label.hide()
        self.analysis_module_path_error_label.hide()

        self._validate_inputs()

    def _connect_signals(self):
        self.source_file_text.textChanged.connect(self._validate_inputs)
        self.source_file_browse_button.clicked.connect(self._on_source_file_browse_button_clicked)

        self.analysis_module_path_text.textChanged.connect(self._validate_inputs)
        self.analysis_module_path_browse_button.clicked.connect(self._on_analysis_module_path_browse_button_clicked)

    def _validate_inputs(self):
        source_file_valid = self._is_source_file_valid()
        analysis_module_path_valid = self._is_analysis_module_path_valid()

        self.source_file_error_label.setVisible(not source_file_valid)
        self.analysis_module_path_error_label.setVisible(not analysis_module_path_valid)

        self.button_box.button(QtGui.QDialogButtonBox.Ok).setEnabled(source_file_valid and analysis_module_path_valid);

    def _is_source_file_valid(self):
        currentPath = self.source_file_text.text()
        return os.path.exists(currentPath)

    def _is_analysis_module_path_valid(self):
        currentPath = self.analysis_module_path_text.text()
        return os.path.exists(currentPath)

    def _on_source_file_browse_button_clicked(self):
        filename = self._select_file_with_dialog('Select a source file.') #, filetype_filter = '*.lingo')
        self.source_file_text.setText(filename)

    def _on_analysis_module_path_browse_button_clicked(self):
        filename = self._select_file_with_dialog('Select an analysis module.', filetype_filter = '*.py')
        self.analysis_module_path_text.setText(filename)

    def _select_file_with_dialog(self,
                                 caption = 'Select file',
                                 initialDir = None,
                                 filetype_filter = None):
        '''Show a modal select file dialog to select a file.'''

        filename = QFileDialog.getOpenFileName(self,
                                               caption,
                                               initialDir or '',
                                               filetype_filter or '',

                                               # The remaining attributes are currently unused
                                               None, # selectedFilter
                                               QFileDialog.Options()) #options

        return filename
