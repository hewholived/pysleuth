from sleuth.desk.analysis import TOP, BOTTOM, NodeInfo, AnalysisInterface, WorklistInfo
from sleuth.lingo.components import AssignmentCommand, FunctionReturn

class CountInfo(NodeInfo):
    '''Store node information for the CountingAnalysis.'''

    def __init__(self, incoming_count, outgoing_count):
        super(CountInfo, self).__init__()

        self.incoming_count = incoming_count
        self.outgoing_count = outgoing_count

    def get_IN(self):
        return self.incoming_count

    def get_OUT(self):
        return self.outgoing_count


class CountingAnalysis(AnalysisInterface):
    '''Simple analysis that counts the statements that *must* occur before a node.
    
    For example, in this graph:
    
                    n1
                   /  \
                 n2    n3
                  |    |
                 n4    |
                  |    |
                   \  /
                    n5
                    
    n5 will get IN values of 3 (from n4) and 2 (from n3), so it's OUT value
    will be 4 (3 from n4 + 1 for itself), indicating that at least 4 statements
    MUST execute to pass through n5.
    
    Note: this is analysis ignores any calls to functions. (This is just an 
    implementation limitation, not a theoretical implementation.)
    '''

    def __init__(self):
        self.node_info_cache = {}

    def prepare_analysis(self, program_block, node_id_map):
        '''Start the analysis with just the starting point on the worklist.
        
        @param program_block: The program block that defines the CFG.
        @param node_id_map: A dictionary of node identifiers to nodes.
            (We don't use this in this particular analysis but it may be
             useful for other analyses.)
        @return: A list of nodes to initialize the worklist.
        '''
        return [WorklistInfo(program_block.command_node)]

    def process_worklist_info(self, worklist_info):
        '''Process the given node.
        
        A node's input is the max of it's predecessors' outputs.
        
        @param node: The CommandNode to process.
        @return: A list of nodes to add to the worklist.
        '''
        node = worklist_info.node

        # Get the current IN value for the node
        incoming_count = self._get_incoming_count(node)

        # Calculate the OUT value for the node (increment or BOTTOM)
        outgoing_count = BOTTOM if incoming_count is BOTTOM else (incoming_count + 1)

        # Store the values in the cache.
        changed = False
        try:
            cached_count = self.node_info_cache[node].outgoing_count

            # If there was a previously cached OUT value that's different
            # than our new OUT value, just widen down to BOTTOM, since 
            # we may be in a loop.
            # 
            # Note: the order in which nodes are processed may cause this
            # to widen for some nodes that it shouldn't. Processing in RPO
            # is guaranteed to avoid this problem. 
            if outgoing_count != cached_count:
                outgoing_count = BOTTOM
                changed = True

        except KeyError:
            changed = True

        self.node_info_cache[node] = CountInfo(incoming_count, outgoing_count)

        # If our cached values are changed (or created) then add our successors
        # to the worklist. 
        if changed:
            return [WorklistInfo(node) for node in node.get_successors()]

        # Otherwise, we have no worklist updates
        return []

    def _get_incoming_count(self, node):
        '''Get the maximum output of all predecessors.'''

        # If this is a RET node just return the preceeding CALL node data:
        if isinstance(node.command, AssignmentCommand) and isinstance(node.command.expression, FunctionReturn):
            predecessor = node.get_predecessors()[0]
            return self.get_node_info(predecessor).incoming_count

        # Get the OUT values for all of our predecessors
        predecessor_out_values = [self.get_node_info(predecessor).outgoing_count
                                  for predecessor in node.get_predecessors()]

        # Strip any TOP values from our IN (since they can't be processed as ints)
        predecessor_out_values = [value
                                  for value in predecessor_out_values
                                  if value is not TOP]

        # If we have no predecessor values left, then start at 0.
        if not predecessor_out_values:
            return 0

        # Return the max (where BOTTOM is infinite) value from our IN
        if BOTTOM in predecessor_out_values:
            return BOTTOM

        return max(predecessor_out_values)

    def get_node_info(self, node):
        '''Get the node info for the given node.
        
        @param node: The CommandNode to get info for.
        @return: The CountInfo for the requested node.
        '''
        try:
            return self.node_info_cache[node]

        except KeyError:
            return CountInfo(TOP, TOP)
