from sleuth.common.exception import NestedException
from sleuth.desk.analysis import NodeInfo
from sleuth.hq.controller import AnalysisController
import logging
import sys

logger = logging.getLogger(__name__)


class MissingArgumentException(NestedException):
    pass

class Application(object):
    '''Manage the console-based interface for PySleuth.'''

    def __init__(self, arguments):
        self.arguments = arguments
        self.worklist = []

        self.analysis_controller = AnalysisController.getInstance()
        self._register_signals()

    def execute_analysis(self):
        try:
            source_file, analysis_module_path = self._get_analysis_files()

            self.analysis_controller.setup_analysis(source_file,
                                                    analysis_module_path,
                                                    self.arguments)

            while self.worklist:
                self.analysis_controller.signals.ANALYSIS_STEP.fire(self, self.worklist.pop(0))

            node_id_map = self.analysis_controller.get_node_id_map()
            for node in sorted(node_id_map.values()):
                self.analysis_controller.signals.CFG_NODE_REQUEST_INFO.fire(self,
                                                                            str(node),
                                                                            NodeInfo.Direction.BOTH,
                                                                            NodeInfo.Encoding.ASCII)

            return 0

        except Exception as e:
            self._exit_with_exception(e)

    def _register_signals(self):
        '''Register handlers for signals from the analysis controller.'''
        self.analysis_controller.signals.WORKLIST_UPDATED.register(self._on_worklist_updated)
        self.analysis_controller.signals.CLIENT_ANALYSIS_EXCEPTION.register(self._on_client_analysis_exception)
        self.analysis_controller.signals.CFG_NODE_DISPLAY_INFO.register(self._on_cfg_node_display_info)

    def _on_worklist_updated(self, source, worklist):
        '''Handler for the worklist updates signal.'''
        self.worklist = worklist

    def _on_client_analysis_exception(self, source, exception):
        '''Handler for the client analysis exceptions signal.
        
        Unlike the GUI-based application, an exception from the client
        analysis will cause the console application to halt.
        '''
        self._exit_with_exception(exception)

    def _on_cfg_node_display_info(self, source, node_info):
        sys.stdout.write('{0}: {1}\n'.format(node_info.node.get_identifier(),
                                             node_info.format(separator = '; ')))

    def _get_analysis_files(self):
        '''Get the paths for required analysis files.
        
        If any required arguments were not provided on the command line, 
        an exception will be raised, halting the analysis execution.
        '''
        source_file_path = self.arguments.source

        if not source_file_path:
            raise MissingArgumentException('--source')

        analysis_module_path = self.arguments.analysis

        if not analysis_module_path:
            raise MissingArgumentException('--analysis')

        return source_file_path, analysis_module_path

    def _exit_with_exception(self, exception):
        '''Log the exception and exit.'''
        logger.exception(exception)
        sys.exit(1)

