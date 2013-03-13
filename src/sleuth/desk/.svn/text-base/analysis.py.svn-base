from abc import ABCMeta, abstractmethod
from sleuth.tracks.cfg import CommandNode


class _LatticePosition(object):
    def __deepcopy__(self, memo_dictionary):
        '''These objects are not "copyable" -- they should remain the same everywhere.'''
        return self

TOP = _LatticePosition()
BOTTOM = _LatticePosition()


class WorklistInfo(object):
    '''Class used to track items in the worklist. 
    
    This type is call_string-aware but does not require call_string to 
    function properly.
    '''

    def __init__(self, node, call_string = None):
        assert isinstance(node, CommandNode), node

        self.node = node
        self.call_string = call_string

    def __repr__(self):
        '''Get the string representation of the WorklistInfo.
        
        This representation is used for display in the GUI application and
        also as a key for communicating worklist events. For these reasons it
        is important that the value returned by this method uniquely identify
        this particular worklist entry.
        '''
        if self.call_string is not None:
            return '{0} {1}'.format(self.call_string, self.node)

        return str(self.node)

    #
    # Comparison and Sorting methods
    #

    def __hash__(self):
        if self.call_string is not None:
            return hash(self.call_string) ^ hash(self.node)

        return hash(self.node)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError('Cannot compare {0} and {1} instances.'.format(self.__class__, other.__class__))

        return (self.call_string == other.call_string and
                self.node == other.node)

    def __lt__(self, other):
        if not isinstance(other, self.__class__):
            raise NotImplementedError('Cannot compare {0} and {1} instances.'.format(self.__class__, other.__class__))

        # TBD: Should call_string or node order be primary?
        if self.call_string is not None:
            return (self.node < other.node and
                    self.call_string < other.call_string)

        return self.node < other.node


class NodeInfo(object):
    '''Abstract class for tracking analysis information about a node in the CFG.
    
    Analyses must provide an implementation of this class that implements the 
    get_IN and get_OUT methods which should return appropriate representations
    of the IN or OUT state of the node requested in the call to the analysis'
    get_node_info() method.
    
    It may also be convenient for the client analysis to use it's NodeInfo
    class as the local cache for storing analysis state, although this is not
    a required implementation detail.
    '''

    __metaclass__ = ABCMeta

    class Direction(object):
        '''Define the available "Directions" for an info request.
        
        This represents requesting information flowing into or out of
        the node, or both at the same time.
        '''
        IN = 'in'
        OUT = 'out'
        BOTH = 'both'

    class Encoding(object):
        ASCII = 'ascii'
        UNICODE = 'unicode'

    def __init__(self, node = None, direction = None, encoding = None):
        '''Prepare the NodeInfo object.'''
        self.node = node
        self.direction = direction or self.Direction.BOTH
        self.encoding = encoding or self.Encoding.ASCII

    @abstractmethod
    def get_IN(self):
        '''Get the IN value for the requested node.
        
        This method must be overridden by a derived class to return
        the appropriate representation of the results from a client analysis.
        '''
        pass

    @abstractmethod
    def get_OUT(self):
        '''Get the OUT value for the requested node.
        
        This method must be overridden by a derived class to return
        the appropriate representation of the results from a client analysis.
        '''
        pass

    def format(self, separator = u'\n\n'):
        '''Prepare the NodeInfo for display.
        
        This method should not be overridden by derived implementations, as it is 
        used to display node information in a fixed manner in the PySleuth front end.
        '''
        if self.direction == self.Direction.IN:
            return u'IN: {0}'.format(self.prepare(self.get_IN()))

        if self.direction == self.Direction.OUT:
            return u'OUT: {0}'.format(self.prepare(self.get_OUT()))

        return u'IN: {in_data}{separator}OUT: {out_data}'.format(in_data = self.prepare(self.get_IN()),
                                                                 out_data = self.prepare(self.get_OUT()),
                                                                 separator = separator)

    def prepare(self, value):
        '''Helper method used to translate special values.
        
        Derived versions of this class should use the special TOP and BOTTOM symbols 
        where appropriate. This method will translate those values to displayable
        values in analysis display.
        
        If a derived class must specially format values, it should call this method for
        each value that it renders.
        '''
        use_unicode = (self.encoding == self.Encoding.UNICODE)

        if value is TOP:
            if use_unicode:
                return u'\u27D9'
            else:
                return u'TOP'

        if value is BOTTOM:
            if use_unicode:
                return u'\u27D8'
            else:
                return u'BOTTOM'

        return value


class AnalysisInterface(object):
    '''Abstract interface for client analyses.'''

    __metaclass__ = ABCMeta

    @abstractmethod
    def prepare_analysis(self, program_block, node_id_map):
        '''Setup the analysis.
        
        Implementations of the interface should use the given ProgramBlock
        to prepare any necessary data structures or setup. The program 
        block represents the CFG for the parsed program.
        
        The node_id_map argument is a (unordered) dictionary of node 
        identifiers to nodes in the program. This is useful as a quick
        lookup of a particular node and also allows an analysis simple
        access to all the nodes in the program if necessary.
        
        This method should return a list of nodes that form 
        the initial worklist for the analysis.
        '''
        pass

    @abstractmethod
    def process_worklist_info(self, worklist_info):
        '''Process a single node in the analysis.
        
        Implementations of the interface should process the given
        WorklistInfo as the next step in the analysis.
        
        This method should return a list of nodes that should
        be added to the worklist.
        '''
        pass

    @abstractmethod
    def get_node_info(self, node):
        '''Return a NodeInfo for the given CommandNode at the current point in the analysis.'''
        pass

