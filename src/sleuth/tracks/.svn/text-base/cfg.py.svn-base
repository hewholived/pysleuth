from sleuth.common.set import Set
from sleuth.lingo.components import * #@UnusedWildImport
import logging

logger = logging.getLogger(__name__)

class Random():
    def __init__(self):
        self.no = 0

    def getNo(self):
        self.no += 1
        return self.no

RandomGen = Random()

class Block(object):
    '''Converts a sequence of Commands into associated CommandNodes.
    
    The Block is the core component of PySleuth's concept of the CFG. It's
    used to sequence commands into a set of predecessor/successor relationships
    that eventually are used to create the CFG. 
    '''

    def __init__(self, exit_node = None, block_depth = 0):
        assert exit_node is None or isinstance(exit_node, CommandNode), exit_node

        self.exit_node = exit_node
        self.block_depth = block_depth

    def scan(self, command):
        '''Scan this block, creating CommandNodes for each encountered command.
        
        This method recursively calls itself to chain together paths of 
        commands, creating new blocks where necessary.
        '''
        assert isinstance(command, Command), command
        self._log('Scanning command: {0}', command)

        # Create the node for this command.
        #    Due to the recursive nature of this scan, this should be the only place
        #    we need to create CommandNode instances.
        this_command_node = CommandNode(command)

        # Check to see if there is a node immediately following this node.
        #    If there is, recursively call scan to get the command node for it.
        next_command = command.get_next_command()
        next_command_node = self.scan(next_command) if next_command else None

        # If this command is a "block" command, get the commands that form its inner blocks. 
        block_commands = command.get_block_commands()
        for block_command in block_commands:
            # Create a new block for the command and scan the block.
            exit_node = next_command_node or self.exit_node

            if isinstance(command, WhileCommand):
                exit_node = this_command_node

            inner_block = Block(exit_node = exit_node,
                                block_depth = self.block_depth + 1)
            block_command_node = inner_block.scan(block_command)

            # Connect this node to the block.
            this_command_node.add_successor(block_command_node)

        # If this is an "if" command, then it is already connected to it's children, and needs
        #    no further connections. 
        if isinstance(command, IfCommand):
            self._log('IfCommand does not connect to another node directly. (Connection is via child blocks.)')
            return this_command_node

        # Connect to the next node, if one is available.
        if next_command_node:
            this_command_node.add_successor(next_command_node)
            self._log('Next command -- connecting {0} to command node: {1}', this_command_node, next_command_node)

        # If this command is the last in a block, connect up to the exit node for the block.
        elif self.exit_node:
            self._log('End of this block -- connecting {0} to exit node: {1}', this_command_node, self.exit_node)
            this_command_node.add_successor(self.exit_node)

        # If this is the last node of a function or the top-level scope, we have nothing to connect to.
        else:
            self._log('End of this block @ {0} -- exiting a top level or function scope.', this_command_node)

        # Return this node up the recursive call chain
        return this_command_node

    def _log(self, format, *format_args, **format_kwargs):
        formatted_message = format.format(*format_args, **format_kwargs)
        logger.debug('{indent_level}{message}'.format(indent_level = '  ' * self.block_depth,
                                                      message = formatted_message))

class ProgramBlock(Block):
    '''Abstracts a Program as a block of CommandNodes.'''

    def __init__(self, program):
        assert isinstance(program, Program), program
        self.program = program

        super(ProgramBlock, self).__init__()
        self.command_node = self.scan(self.program.command)
        self.functions = dict((f.name, FunctionBlock(f)) for f in program.functions)

        counter = Counter()
        no_nodes = self.command_node.assign_post_order(counter)
        for function_block in self.functions.values():
            no_nodes = function_block.command_node.assign_post_order(counter, no_nodes)

        no_nodes -= 1
        self.command_node.reverse_the_post_order(no_nodes)
        for function_block in self.functions.values():
            function_block.command_node.reverse_the_post_order(no_nodes)

class FunctionBlock(Block):
    '''Abstracts a Function as a block of CommandNodes.'''

    def __init__(self, function_declaration):
        assert isinstance(function_declaration, FunctionDeclaration), function_declaration
        self.function_declaration = function_declaration

        super(FunctionBlock, self).__init__()
        self.command_node = self.scan(self.function_declaration)

class CommandNode(object):
    '''Represents a single command in a CFG.'''

    def __init__(self, command):
        assert isinstance(command, Command), command
	global RandomGen
        self.command = command

        self.reverse_post_order = None
        self.flag = 0
	self.nodeID = RandomGen.getNo();

        self._predecessors = Set()
        self._successors = Set()

    def get_identifier(self):
        '''Get the canonical identifier for this node.
        
        Because this identifier incorporates the RPO value, 
        it is guaranteed to be unique among all other nodes.
        '''
        return 'n{0}'.format(self.reverse_post_order)

    def get_predecessors(self):
        '''Get the predecessors of this command node.'''
        return list(self._predecessors)

    def get_successors(self):
        '''Get the successors for this command node.'''

        # For consistency, always order the True block of if commands first.
        if isinstance(self.command, IfCommand):
            return sorted(self._successors,
                          key = lambda node: node.command == self.command.true_block,
                          reverse = True)

        # For consistency, always order the block of the while loop first.
        if isinstance(self.command, WhileCommand):
            return sorted(self._successors,
                          key = lambda node: node.command == self.command.loop_block,
                          reverse = True)

        # Other nodes just return the list.
        return list(self._successors)

    def add_successor(self, successor_node):
        '''Add a successor to this node.
        
        This also makes this node a predecessor of the new successor node.
        '''
        assert isinstance(successor_node, CommandNode), successor_node
        self._successors.add(successor_node)
        successor_node._predecessors.add(self)

    def get_graph_width(self):
        '''Get the "width" of the graph below this node.
        
        This is returned as a list of widths of all successor nodes 
        below this node.
        '''
        if not self._successors:
            return [1]

        return [sum(successor.get_graph_width()) for successor in self._successors]

    def get_paths(self, _visited_pairs = None):
        '''Generator function to get the paths below this node.
        
        This recursively builds a list of "pairs" such that all edge pairs
        below this node are accounted for.
        '''
        _visited_pairs = Set() if _visited_pairs  is None else _visited_pairs

        if len(self._successors) == 0:
            edge_pair = (self, None)
            if edge_pair not in _visited_pairs:
                _visited_pairs.add(edge_pair)
                yield edge_pair

        for next in self._successors:
            edge_pair = (self, next)

            if edge_pair in _visited_pairs:
                continue

            _visited_pairs.add(edge_pair)
            yield edge_pair

            for pair in next.get_paths(_visited_pairs):
                yield pair

    def assign_post_order(self, counter, no_nodes = 0):
        '''Assign the reverse post order value for this and successive nodes.
        
        This guarantees that any successor that is "below" this node in the 
        CFG will have a RPO value greater than this node's RPO value. The
        node at the top of a "while" loop is considered "above" the nodes in
        the block it gates, even though it is a successor of the last node 
        in the block.
        
        Note that it is NOT guaranteed that numbers will be used sequentially,
        only that any node that is a transitive-successor (excluding while
        nodes) will have a higher RPO value than it's predecessors.
        
        @param counter: A counter that continuously increments values.
        @param no_nodes: Number of nodes counted untill reaching this node.
        '''
        succ = sorted(self._successors, cmp=lambda x,y: cmp(x.nodeID, y.nodeID))

        # Now tell all successors to assign RPOs
        for successor in succ:

            # But if we've already visited the successor on the current path,
            # then we're in a loop and shouldn't update the successor
            if successor.flag == 0:
	        successor.flag = 1
                # Increment the no of nodes counter
                no_nodes = successor.assign_post_order(counter, no_nodes)
        
        # Assign the next available value as our RPO
        self.reverse_post_order = counter.get_value()
        self.flag = 1
        no_nodes += 1

        return no_nodes

    def reverse_the_post_order(self, no_nodes):
        succ = sorted(self._successors, cmp=lambda x,y: cmp(hash(x), hash(y)))

        self.reverse_post_order = no_nodes - self.reverse_post_order
        self.flag = 0

        # Now tell all successors to assign RPOs
        for successor in succ:
            if successor.flag == 1:
                successor.flag = 0
                successor.reverse_the_post_order(no_nodes)

    def __repr__(self):
        '''Provide a presentable representation of the node.
        
        Because this identifier incorporates the RPO value, 
        it is guaranteed to be unique among all other nodes.
        '''
        return '[{0}] {1}'.format(self.reverse_post_order, self.command)

    def __eq__(self, other):
        if not isinstance(other, CommandNode):
            return False

        return self.command == other.command

    def __lt__(self, other):
        if not isinstance(other, CommandNode):
            return False

        return self.reverse_post_order < other.reverse_post_order


    def __hash__(self):
        return hash(self.command)


class Counter(object):
    '''Helper class providing an ever-incrementing counter.'''

    def __init__(self):
        self._value = 0

    def get_value(self):
        try:
            return self._value
        finally:
            self._value += 1
