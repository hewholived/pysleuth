from PyQt4 import QtGui
from PyQt4.QtGui import QApplication
from sleuth.evidence.gui import cfg_widget
from sleuth.evidence.gui.new_analysis_dialog import NewAnalysisDialog
from sleuth.hq.controller import AnalysisController, AnalysisControllerException
import logging
import sys

logger = logging.getLogger(__name__)

class Application(QApplication):
    '''Manage the GUI-based interface for PySleuth.'''

    def __init__(self, arguments):
        super(Application, self).__init__(sys.argv[1:])

        self.arguments = arguments
        self.main_window = None

        self.set_application_info()
        self.register_resources()

        # The idea way to set the font is with:
        #     self.setFont(QtGui.QFont(arguments.gui_font))
        # But that has strange scaling issues.

        # Instead we'll cheat and set a global symbol where the font is needed
        cfg_widget.FONT_NAME = self.arguments.gui_font

    def set_application_info(self):
        '''Set some constant info for the application.'''
        self.setOrganizationName('UCSB Computer Science')
        self.setOrganizationDomain('cs.ucsb.edu')
        self.setApplicationName('PySleuth')

    def register_resources(self):
        '''Register any resources by importing the relevant files.
        
        These files must be created with the pyrcc executable that comes with
        PyQT4.
        
        A batch script is located at PyAnalysis/resources/createResources.bat that can
        be used to properly create this file.
        '''
        import sleuth.evidence.resources.icons #@UnresolvedImport @UnusedImport

    def execute_analysis(self):
        source_file, analysis_module_path = self._get_analysis_files()

        if not (source_file and analysis_module_path):
            sys.exit(0)

        try:
            # Construct the main window
            from sleuth.evidence.gui.main_window import MainWindow
            self.main_window = MainWindow()

            # Prepare the analysis
            analysis_controller = AnalysisController.getInstance()
            analysis_controller.setup_analysis(source_file,
                                               analysis_module_path,
                                               self.arguments)

            # Render analysis details into the main window
            program_source = analysis_controller.get_program_source()
            self.main_window.render_source(program_source)

            edge_pairs = analysis_controller.get_cfg_edge_pairs()
            node_id_map = analysis_controller.get_node_id_map()
            self.main_window.render_graph(self.arguments.dot_executable,
                                          edge_pairs,
                                          node_id_map)

            # Display the main window
            self.main_window.show()

            # Enter the PyQt event loop
            return self.exec_()

        except AnalysisControllerException as e:
            self._exit_with_exception('Analysis Error', e)

        except Exception as e:
            self._exit_with_exception('Unhandled Exception', e)


    def _exit_with_exception(self, title, exception):
        logger.exception(exception)

        # Construct a presentable message to display in the dialog
        message = str(exception)

        QtGui.QMessageBox.critical(None,
                                   title,
                                   message)

        sys.exit(1)

    def _get_analysis_files(self):
        '''Get the paths for required files.
        
        If the files weren't completely specified as command line 
        parameters, invoke a dialog to collect them.
        '''
        source_file_path = self.arguments.source
        analysis_module_path = self.arguments.analysis

        if source_file_path and analysis_module_path:
            return source_file_path, analysis_module_path

        dialog = NewAnalysisDialog.show_dialog(source_file_path or '',
                                               analysis_module_path or '',
                                               parent = None)

        if not dialog:
            return (None, None)

        return dialog.get_source_file_path(), dialog.get_analysis_module_path()
