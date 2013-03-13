from sleuth.lingo.components import * #@UnusedWildImport
from sleuth.tracks.cfg import Block, CommandNode
from test_sleuth.support.testcase import TestCase


class CFGNodeTest(TestCase):

    def create(self, component_class, arguments, after = None):
        args = [self.convert_arg(arg) for arg in arguments]

        component = component_class(*args, line_span = (0, 1), lex_span = (0, 1))

        if after is not None:
            after.set_next_command(component)

        return component

    def convert_arg(self, arg):
        if isinstance(arg, str):
            if arg == '+':
                return OperatorPlus(arg, (0, 0), (0, 0))

            return Variable(arg, (0, 0), (0, 0))

        if isinstance(arg, int):
            return Number(arg, (0, 0), (0, 0))

        if isinstance(arg, bool):
            return Boolean(arg, (0, 0), (0, 0))

        return arg

    def test_traverse_commands(self):
#        self.withLogging()

        command_a = self.create(AssignmentCommand, ('a', 1))
        command_b = self.create(AssignmentCommand, ('b', 2), after = command_a)

        command_c_true = self.create(AssignmentCommand, ('c', 3))
        command_c_false = self.create(AssignmentCommand, ('c', 4))

        command_c = self.create(
            IfCommand,
            (True, command_c_true, command_c_false),
            after = command_b)

        command_d = self.create(
            AssignmentCommand,
            ('d', self.create(BinaryExpression, ('a', '+', 'c'))),
            after = command_c)

        command_node_a = Block().scan(command_a)
        self.assertIs(command_node_a.command, command_a)
        self.assertSameElements([], command_node_a._predecessors)
        self.assertSameElements([CommandNode(command_b)], command_node_a._successors)

        command_node_b = command_node_a._successors.get()
        self.assertIs(command_node_b.command, command_b)
        self.assertSameElements([command_node_a], command_node_b._predecessors)
        self.assertSameElements([CommandNode(command_c)], command_node_b._successors)

        command_node_c = command_node_b._successors.get()
        self.assertIs(command_node_c.command, command_c)
        self.assertSameElements([command_node_b], command_node_c._predecessors)
        self.assertSameElements([CommandNode(command_c_true), CommandNode(command_c_false)], command_node_c._successors)

        x, y = command_node_c._successors
        command_node_c_true, command_node_c_false = (x, y) if x.command.expression.value == 3 else (y, x)

        self.assertIs(command_node_c_true.command, command_c_true)
        self.assertIs(command_node_c_false.command, command_c_false)
        self.assertSameElements([command_node_c], command_node_c_true._predecessors)
        self.assertSameElements([command_node_c], command_node_c_false._predecessors)
        self.assertSameElements([CommandNode(command_d)], command_node_c_true._successors)
        self.assertSameElements([CommandNode(command_d)], command_node_c_false._successors)

        command_node_d = command_node_c_true._successors.get()
        self.assertIs(command_node_d.command, command_d)
        self.assertSameElements([command_node_c_true, command_node_c_false], command_node_d._predecessors)
        self.assertSameElements([], command_node_d._successors)


    def test_get_paths_simple_duo(self):
        command_a = self.create(AssignmentCommand, ('a', 1))
        command_b = self.create(AssignmentCommand, ('b', 2), after = command_a)

        command_node = Block().scan(command_a)

        paths = list(command_node.get_paths())

        self.assertIn([command_a, command_b],
                      [[n.command for n in p] for p in paths])

    def test_get_paths_simple_branch(self):
        command_c_true = self.create(AssignmentCommand, ('c', 3))
        command_c_false = self.create(AssignmentCommand, ('c', 4))

        command_c = self.create(
            IfCommand,
            (True, command_c_true, command_c_false))

        command_node = Block().scan(command_c)

        paths = list(command_node.get_paths())

        self.assertIn([command_c, command_c_true],
                      [[n.command for n in p] for p in paths])
        self.assertIn([command_c, command_c_false],
                      [[n.command for n in p] for p in paths])

