from sleuth.common.exception import NestedException, TypeException
from sleuth.common.signal import Signal
from sleuth.desk.analysis import AnalysisInterface, WorklistInfo, NodeInfo
from sleuth.lingo.parser import LingoParser, LingoException
from sleuth.lingo.typecheck import TypeCheck
from sleuth.tracks.cfg import ProgramBlock
from threading import Thread
import imp
import logging
import sys
logger = logging.getLogger(__name__)


#
# Exceptions
#

class AnalysisControllerException(NestedException):
    pass

class CannotOpenSourceFile(AnalysisControllerException):
    def __init__(self, source_file):
        super(CannotOpenSourceFile, self).__init__('Unable to open source file: {0}.'.format(source_file))

class CannotParseSource(AnalysisControllerException):
    def __init__(self, source_file):
        super(CannotParseSource, self).__init__('Unable to parse source file: {0}.'.format(source_file))

class CannotOpenAnalysisFile(AnalysisControllerException):
    def __init__(self, analysis_file):
        super(CannotOpenAnalysisFile, self).__init__('Unable to open analysis file: {0}.'.format(analysis_file))

class MissingAnalysisException(AnalysisControllerException):
    def __init__(self, analysis_module_path):
        super(MissingAnalysisException, self).__init__('No AnalysisInterface found in module at {0}.'.format(analysis_module_path))

class IncompleteAnalysisException(AnalysisControllerException):
    def __init__(self, analysis_class, analysis_module_path):
        super(IncompleteAnalysisException, self).__init__('Analysis implementation {0} in {1} is not complete.'.format(analysis_class.__name__, analysis_module_path))

class ClientAnalysisException(AnalysisControllerException):
    def __init__(self, analysis_instance, method_name):
        super(ClientAnalysisException, self).__init__('Unhandled exception in {0}.{1}.'.format(analysis_instance.__class__.__name__,
                                                                                               method_name))


#
# Controller
#

class AnalysisController(object):
    '''Manages the analysis of a particular program.'''

    class signals(object):
        #
        # Application-initiated Signals
        #    Applications should fire these signals to drive the analysis
        #

        # Drive the analysis one step forward
        ANALYSIS_STEP = Signal('worklist_label')

        # Request info about the specified node
        CFG_NODE_REQUEST_INFO = Signal('node_label', 'info_direction', 'info_encoding')

        # Request that sorting for the worklist be enabled or disabled (default is enabled)
        SET_WORKLIST_SORTING_ENABLED = Signal('enabled')

        #
        # Controller-initiated Signals
        #    Applications should register for these signals to receive
        #    events from the executing analysis
        #

        # The given items have been added to the worklist        
        WORKLIST_UPDATED = Signal('worklist_nodes')

        # An exception has occured in the client analysis
        CLIENT_ANALYSIS_EXCEPTION = Signal('exception')

        # Delivers requested node information
        CFG_NODE_DISPLAY_INFO = Signal('node_info')

        ANALYSIS_COMPLETE = Signal()

        #
        # Gui-only Signals
        #    These signals are relevant only to the GUI-based application 
        #    

        # A node has been selected
        CFG_NODE_SELECTED = Signal('node')

        # A worklist entry has been clicked
        WORKLIST_ITEM_CLICKED = Signal('worklist_label')

        # The given item should be visible
        ENSURE_ITEM_VISIBLE = Signal('graphics_item')

    _instance = None

    @classmethod
    def getInstance(cls):
        '''Get the singleton instance of the controller.'''

        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def __init__(self):
        '''Setup the controller.
        
        This will fail if an instance of the controller already exists. Use
        AnalysisController.getInstance() to create/retrieve the singleton
        instance of the class. 
        '''
        assert self._instance is None, '{name} is a singleton -- use {name}.getInstance() instead of constructing directly.'.format(name = self.__class__.__name__)

        self.program_source = None
        self.program_component = None
        self.program_block = None

        self.node_id_map = {}
        self.node_label_map = {}

        self.worklist = []
        self.worklist_label_cache = {}
        self.sort_worklist = True

        self.client_analysis = None

        self.cfg_edge_pairs = None

        self.signals.CFG_NODE_REQUEST_INFO.register(self._on_signal_cfg_node_request_info)
        self.signals.ANALYSIS_STEP.register(self._on_signal_analysis_step)
        self.signals.WORKLIST_ITEM_CLICKED.register(self._on_signal_worklist_node_clicked)
        self.signals.SET_WORKLIST_SORTING_ENABLED.register(self._on_signal_set_worklist_sorting_enabled)

    #
    # Analysis Preparation Methods
    #

    def setup_analysis(self,
                       source_file_path,
                       module_file_path,
                       arguments):
        '''Setup the analysis.
        
        This method is responsible for preparing everything required
        to run the analysis.
        
        @param source_file_path: The path to the source file to be analyzed.
        @param module_file_path: The path to the module file where the client
            analysis to be run is implemented.
        '''
        assert source_file_path
        assert module_file_path

        # Parse the source code to be analyzed
        self._parse_source_file(source_file_path)
        if arguments.typecheck_enabled:
            self._type_check_ast(arguments.annotate_types_enabled)
        self.get_cfg_edge_pairs()

        # Setup the client analysis
        self._setup_client_analysis(module_file_path)

        # Invoke the client preparation method
        self._client_analysis__prepare_analysis(self.program_block, self.node_id_map)


    def _parse_source_file(self, source_file_path):
        parser = LingoParser()

        try:
            with open(source_file_path, 'r') as source_file:
                self.program_source = source_file.read()
                self.program_component = parser.parse(self.program_source)
        except IOError as e:
            raise CannotOpenSourceFile(source_file_path).from_exception(e)

        except LingoException as e:
            raise CannotParseSource(source_file_path).from_exception(e)

        self.program_block = ProgramBlock(self.program_component)

    def _type_check_ast(self, annotate_types):
        try:
            typecheck = TypeCheck(annotate_types)
            typecheck.visit_program(self.program_component)
        except TypeException :
            if not annotate_types:
                sys.exit(1)
        #self.program_component.accept(TypeCheck(annotate_types))
        
    def _setup_client_analysis(self, analysis_module_path):
        '''Setup the client analysis.
        
        Attempt to import the client analysis module and find and create
        an instance of the client analysis class (which must derive from
        sleuth.desk.AnalysisInterface).
        '''
        assert self.client_analysis is None, self.client_analysis

        # Attempt to import the client analysis module
        try:
            analysis_module = imp.load_source('sleuth.client_analysis', analysis_module_path)
        except IOError as e:
            raise CannotOpenAnalysisFile(analysis_module_path).from_exception(e)

        # Search the symbols in the imported module for an appropriate
        # client analysis implementation to construct
        for value in analysis_module.__dict__.values():
            # Only look at "classes"
            if not isinstance(value, type):
                continue

            # Skip the found value if it's just the imported interface.
            if value is AnalysisInterface:
                continue

            # Check to see if this class is our implementation
            if issubclass(value, AnalysisInterface):
                try:
                    self.client_analysis = value()
                except TypeError as e:
                    raise IncompleteAnalysisException(value, analysis_module_path).from_exception(e)

                break

        # If we didn't successfully create an analysis, die with an error
        if not self.client_analysis:
            raise MissingAnalysisException(analysis_module_path)

    #
    # Rendering Methods
    #

    def get_program_source(self):
        '''Get the source code being analyzed.'''
        assert self.program_source is not None, 'Call setup_analysis first.'
        return self.program_source

    def get_cfg_edge_pairs(self):
        '''Get the edge pairs that make up the CFG.'''
        if self.cfg_edge_pairs is not None:
            return self.cfg_edge_pairs

        assert self.program_block is not None, 'Call setup_analysis first.'
        edge_pairs = self._get_edge_pairs_for_block(self.program_block)

        for function_block in self.program_block.functions.values():
            edge_pairs.extend(self._get_edge_pairs_for_block(function_block))

        self.cfg_edge_pairs = edge_pairs
        return self.cfg_edge_pairs

    def get_node_id_map(self):
        '''Get the mapping of node ids to command nodes.'''
        assert self.node_id_map is not None, 'Call get_cfg_edge_pairs first.'
        return self.node_id_map

    def _get_edge_pairs_for_block(self, block):
        '''Recursively gather edge pairs for the given block.'''
        edge_pairs = list(block.command_node.get_paths())

        # Since we know we're going to see every "connected" node in the "edge pairs",
        # we can build some canonical maps here.

        # Build a map of "id" to node and "label" to node
        for src, dst in edge_pairs:
            self.node_id_map[src.get_identifier()] = src
            self.node_label_map[str(src)] = src

            if dst is not None:
                self.node_id_map[dst.get_identifier()] = dst
                self.node_label_map[str(dst)] = dst

        return edge_pairs


    #
    # Client Analysis Method Calls
    #

    def _client_analysis__prepare_analysis(self, program_block, node_id_map):
        '''Call the prepare_analysis method of the client analysis.'''

        def handle_prepare_analysis():
            worklist_nodes = self.client_analysis.prepare_analysis(program_block, node_id_map)
            self._update_worklist(worklist_nodes)

        return self._with_exception_handling('prepare_analysis', handle_prepare_analysis)

    def _client_analysis__process_worklist_info(self, node):
        '''Call the process_worklist_info method of the client analysis.'''

        def handle_process_worklist_info():
            worklist_nodes = self.client_analysis.process_worklist_info(node)
            self._update_worklist(worklist_nodes)

        self._with_exception_handling('process_worklist_info', handle_process_worklist_info)

    def _client_analysis__get_node_info(self, node):
        '''Call the get_node_info method of the client analysis.'''

        def handle_get_node_info():
            node_info = self.client_analysis.get_node_info(node)
            assert isinstance(node_info, NodeInfo), 'get_node_info did not return a NodeInfo instance. Got: {0}'.format(node_info)

            return node_info

        return self._with_exception_handling('get_node_info', handle_get_node_info)

    def _with_exception_handling(self, name, callable, *args, **kwargs):
        '''Call the specified callable with safe exception handling.'''
        try:
            return callable(*args, **kwargs)

        except BaseException as e:
            logger.exception(e)

            wrapped = ClientAnalysisException(self.client_analysis, name).from_exception(e)

            self.signals.CLIENT_ANALYSIS_EXCEPTION.fire(self,
                                                        wrapped)

    def _update_worklist(self, new_worklist_infos, from_analysis = True):
        '''Handles worklist updates from the client analysis.
        
        Update the current state of the worklist and notify listeners with the
        updated list.
        
        @param new_worklist_infos: New information to add to the worklist. 
        '''
        # Update the worklist
        for info in new_worklist_infos:
            assert isinstance(info, WorklistInfo), info

            if info in self.worklist:
                continue

            # Maintain the label cache
            self.worklist_label_cache[str(info)] = info

            # Add the info to the worklist
            self.worklist.append(info)

        # If sorting is enabled, sort the current worklist
        if self.sort_worklist:
            self.worklist.sort()

        # Notify listeners of the new worklist
        self.signals.WORKLIST_UPDATED.fire(self, [str(info) for info in self.worklist])

        # If the worklist is empty after the analysis gives us updates,
        # we're done -- notify any listeners. 
        if from_analysis and not self.worklist:
            self.signals.ANALYSIS_COMPLETE.fire(self)

    #
    # Signal Handlers
    #
    def _on_signal_analysis_step(self, source, worklist_label):
        worklist_info = self.worklist_label_cache[worklist_label]
        self.worklist.remove(worklist_info)

        node = worklist_info.node

        self.signals.CFG_NODE_SELECTED.fire(self, node)
        self._client_analysis__process_worklist_info(worklist_info)

    def _on_signal_cfg_node_request_info(self, source, node_label, node_info_direction, node_info_encoding):
        try:
            node = self.node_label_map[str(node_label)]
        except KeyError:
            node = self.worklist_label_cache[str(node_label)].node

        node_info = self._client_analysis__get_node_info(node)

        # Don't rely on the client to set these properties
        node_info.node = node
        node_info.direction = node_info_direction
        node_info.encoding = node_info_encoding

        self.signals.CFG_NODE_DISPLAY_INFO.fire(self, node_info)

    def _on_signal_worklist_node_clicked(self, source, worklist_label):
        worklist_info = self.worklist_label_cache[worklist_label]
        node = worklist_info.node

        self.signals.CFG_NODE_SELECTED.fire(self, node)

    def _on_signal_set_worklist_sorting_enabled(self, source, enabled):
        self.sort_worklist = enabled

        # Trigger a worklist update to ensure the application is informed of the change
        self._update_worklist(self.worklist, from_analysis = False)
