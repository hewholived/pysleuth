from sleuth.lingo.types import *
'''
Provide the components of the PySleuth language "Lingo".

These components are produced in the parser module and consumed by
the various analyses implemented against PySleuth. 
'''
class Visitable(object):
    def accept(self, visitor):
        print "AST Nodes must implement accept"
        assert(False)
class LingoComponent(Visitable):
    def __init__(self, line_span, lex_span):
        # Assert that we get a valid line span and lex_span, since subclasses will 
        # default line_span to None to maintain a nice keyword-assignment interface.
        assert line_span is not None
        assert lex_span is not None
        self.line_span = line_span
        self.lex_span = lex_span
        self.type = None
        super(LingoComponent, self).__init__()
    @property
    def line_number(self):
        return self.line_span[0]
    def accept(self, visitor):
        visitor.visit_lingo_component(self)
#
# Program Component
#

class Program(LingoComponent):
    def __init__(self, function_declarations, command, line_span = None, lex_span = None):
        assert isinstance(function_declarations, list), function_declarations
        assert all([isinstance(i, FunctionDeclaration) for i in function_declarations]), function_declarations
        assert isinstance(command, Command), command

        self.functions = function_declarations
        self.command = command

        super(Program, self).__init__(line_span = line_span, lex_span = lex_span)
    def accept(self, visitor):
        visitor.visit_program(self)
#
# Command Components
#

class Command(LingoComponent):
    def __init__(self, line_span = None, lex_span = None):
        self._previous_command = None
        self._next_command = None
        self._parent_command = None

        super(Command, self).__init__(line_span = line_span, lex_span = lex_span)

    def get_display_text(self):
        return repr(self)

    def get_next_command(self):
        return self._next_command

    def set_next_command(self, next_command):
        '''Set the next command for this command.
        
        Since we can't make any guarantees about the parse tree that will be 
        generated, we have to treat the next_command as coming after this particular
        sequence of commands. So, if this command already has a next command, 
        call set_next_command on our next command.
        '''
        assert next_command is not None

        if self._next_command is not None:
            self._next_command.set_next_command(next_command)
            return

        assert self._next_command is None, '"{0}" is already followed by "{1}"; cannot change to "{2}"'.format(self, self._next_command, next_command)
        self._next_command = next_command

        # Apply the reflection as well
        next_command.set_previous_command(self)

    def get_previous_command(self):
        return self._previous_command

    def set_previous_command(self, previous_command):
        assert previous_command is not None
        assert self._previous_command is None, self._previous_command
        self._previous_command = previous_command

    def get_parent_command(self):
        '''Get the parent of this command.
        
        If this command has no immediate parent, then backtrack
        to the previous command to find it's parent.
        
        If no parent command is found, this is a top level command, 
        and None is returned.
        '''
        if self._parent_command:
            return self._parent_command

        if self.get_previous_command():
            return self.get_previous_command().parent_command

        return None

    def set_parent_command(self, parent_command):
        '''Set the parent of this command.
        
        This method should be invoked by commands that contain blocks
        of commands.
        '''
        assert parent_command is not None
        assert self._parent_command is None, self._parent_command
        self._parent_command = parent_command

        # There's no reflection to apply, since the parent command
        # already has a representation of child commands 

    def get_block_commands(self):
        '''Get the commands that this command contains in a block.
        
        By default, commands have no block commands. Commands like "while"
        and "if" may override this method to return a list containing the
        first command in their block(s).
        '''
        return []


class AssignmentCommand(Command):
    def __init__(self,
                 assigned_variable,
                 expression,
                 line_span = None, lex_span = None):
        assert isinstance(assigned_variable, Variable), assigned_variable
        assert isinstance(expression, Expression), expression

        self.assigned_variable = assigned_variable
        self.expression = expression

        super(AssignmentCommand, self).__init__(line_span = line_span, lex_span = lex_span)

    def get_next_command(self):
        '''Get the command following this command.
        
        This is something of a kludge to separate function calls into 
        CALL and RET nodes (which may make some analyses simpler).
        
        If this command's expression is a CALL, we clone this command
        with the matching RET and adjust the next command pointers
        appropriately and return the RET as the next command.
        '''
        if (isinstance(self.expression, FunctionCall) and
            not isinstance(self._next_command, FunctionReturn)):

            function_return_command = AssignmentCommand(self.assigned_variable,
                                                        self.expression.get_return_expression(),
                                                        line_span = self.line_span,
                                                        lex_span = self.lex_span)


            function_return_command._next_command = self._next_command
            self._next_command = function_return_command

        return super(AssignmentCommand, self).get_next_command()

    def __repr__(self):
        return '{0} := {1}'.format(self.assigned_variable, self.expression)
    def accept(self, visitor):
        visitor.visit_assignment_command(self)
class ConditionalCommand(Command):
    def __init__(self, expression, line_span = None, lex_span = None):
        assert isinstance(expression, Expression), expression
        self.expression = expression

        super(ConditionalCommand, self).__init__(line_span = line_span, lex_span = lex_span)

    def __repr__(self):
        return '{0}'.format(self.expression)
    def accept(self, visitor):
        visitor.visit_conditional_command(self)
class IfCommand(ConditionalCommand):
    def __init__(self,
                 expression,
                 true_block,
                 false_block,
                 line_span = None, lex_span = None):
        assert isinstance(true_block, Command), true_block
        assert isinstance(false_block, Command), false_block

        self.true_block = true_block
        self.false_block = false_block

        # Set ourselves as the parent of the conditional branches
        true_block.set_parent_command(self)
        false_block.set_parent_command(self)

        super(IfCommand, self).__init__(expression = expression, line_span = line_span, lex_span = lex_span)

    def get_block_commands(self):
        '''Get the commands that start the true and false blocks.'''
        return [self.true_block, self.false_block]
    def accept(self, visitor):
        visitor.visit_if_command(self)

class WhileCommand(ConditionalCommand):
    def __init__(self,
                 expression,
                 loop_block,
                 line_span = None, lex_span = None):
        assert isinstance(loop_block, Command), loop_block
        self.loop_block = loop_block

        # Set ourselves as the parent of the loop body
        loop_block.set_parent_command(self)

        super(WhileCommand, self).__init__(expression = expression, line_span = line_span, lex_span = lex_span)

    def get_block_commands(self):
        '''Get the command that starts the loop body.'''
        return [self.loop_block]
    def accept(self, visitor):
        visitor.visit_while_command(self)

class SkipCommand(Command):
    def __repr__(self):
        return 'skip'
    def accept(self, visitor):
        visitor.visit_skip_command(self)
class FunctionDeclaration(Command):
    def __init__(self, name, definition, line_span = None, lex_span = None):
        assert isinstance(name, str), name
        assert isinstance(definition, FunctionDefinition), definition

        self.name = name
        self.definition = definition

        super(FunctionDeclaration, self).__init__(line_span = line_span, lex_span = lex_span)

    def get_block_commands(self):
        '''Get the commands that make up the function.'''
        return [self.definition.body]

    def __repr__(self):
        return '{0} = {1}'.format(self.name, self.definition)
    def accept(self, visitor):
        visitor.visit_function_declaration(self)

class InputCommand(Command):
    def __init__(self, variable, line_span = None, lex_span = None):
        assert isinstance(variable, Variable), variable
        self.variable = variable

        super(InputCommand, self).__init__(line_span = line_span, lex_span = lex_span)

    def __repr__(self):
        return 'input {0}'.format(self.variable)
    def accept(self, visitor):
        visitor.visit_input_command(self)

class ReturnCommand(Command):
    def __init__(self, variable, line_span = None, lex_span = None):
        assert isinstance(variable, Variable), variable
        self.variable = variable

        super(ReturnCommand, self).__init__(line_span = line_span, lex_span = lex_span)

    def __repr__(self):
        return 'return {0}'.format(self.variable)
    def accept(self, visitor):
        visitor.visit_return_command(self)
#
# Expression Components
#

class Expression(LingoComponent):
    pass

class New(Expression):
    def __init__(self,
                 allocate_type,
                 line_span = None, lex_span = None):
        assert isinstance(allocate_type, Type), allocate_type
        self.allocate_type = allocate_type
        super(New, self).__init__(line_span = line_span, lex_span = lex_span)
    def __repr__(self):
        return 'new {0}'.format(self.allocate_type)
    def accept(self, visitor):
        visitor.visit_new(self)
class BinaryExpression(Expression):
    def __init__(self,
                 left_term,
                 operator,
                 right_term,
                 line_span = None, lex_span = None):
        assert isinstance(left_term, Expression), left_term
        assert isinstance(operator, Operator), operator
        assert isinstance(right_term, Expression), right_term

        self.left_term = left_term
        self.operator = operator
        self.right_term = right_term
        super(BinaryExpression, self).__init__(line_span = line_span, lex_span = lex_span)

    def __repr__(self):
        return '{0} {1} {2}'.format(self.left_term, self.operator, self.right_term)
    def accept(self, visitor):
        visitor.visit_binary_expression(self)
class FunctionCall(Expression):
    def __init__(self, function_variable, parameter_variables, line_span = None, lex_span = None):
        assert isinstance(function_variable, Variable), function_variable
        for parameter_variable in parameter_variables:
            assert isinstance(parameter_variable, Variable), parameter_variable
        self.function_variable = function_variable
        self.parameter_variables = parameter_variables

        super(FunctionCall, self).__init__(line_span = line_span, lex_span = lex_span)

    def get_return_expression(self):
        return FunctionReturn(self.function_variable,
                              self.parameter_variables,
                              line_span = self.line_span,
                              lex_span = self.lex_span)

    def __repr__(self):
        return '{0}({1}) [CALL]'.format(self.function_variable,
                                        self.parameter_variables)
    def accept(self, visitor):
        visitor.visit_function_call(self)
class FunctionReturn(Expression):
    def __init__(self, function_variable, parameter_variables, line_span = None, lex_span = None):
        assert isinstance(function_variable, Variable), function_variable
        for parameter_variable in parameter_variables:
            assert isinstance(parameter_variable, Variable), parameter_variable
        self.function_variable = function_variable
        self.parameter_variables = parameter_variables
        
        super(FunctionReturn, self).__init__(line_span = line_span, lex_span = lex_span)

    def __repr__(self):
        return '{0}({1}) [RET]'.format(self.function_variable,
                                       self.parameter_variables)
    def accept(self, visitor):
        visitor.visit_function_return(self)
class FunctionDefinition(Expression):
    def __init__(self, parameters, body, line_span = None, lex_span = None):
        for parameter in parameters:
            assert isinstance(parameter, Variable), parameter
        assert isinstance(body, Command), body

        self.parameters = parameters
        self.body = body

        super(FunctionDefinition, self).__init__(line_span = line_span, lex_span = lex_span)

    def __repr__(self):
        return 'fun({0})'.format(self.parameters)
    def accept(self, visitor):
        visitor.visit_function_definition(self)
#
# Atomic Components
#

class Atom(Expression):
    pass

class Variable(Atom):
    def __init__(self, name, line_span = None, lex_span = None):
        assert isinstance(name, str), name
        self.name = name
        self.rank = 0
        self.parent = self
        super(Variable, self).__init__(line_span = line_span, lex_span = lex_span)

    def __repr__(self):
        return '{0}'.format(self.name)
    def __eq__(self, other):
        if isinstance(other, Variable):
            return self.name == other.name
        return False
    def accept(self, visitor):
        visitor.visit_variable(self)
class ReferencedVariable(Variable):
    def __repr__(self):
        return 'ref {0}'.format(super(ReferencedVariable, self).__repr__())
    def accept(self, visitor):
        visitor.visit_referenced_variable(self)
class DereferencedVariable(Variable):
    def __repr__(self):
        return '!{0}'.format(super(DereferencedVariable, self).__repr__())
    def accept(self, visitor):
        visitor.visit_dereferenced_variable(self)
class Number(Atom):
    def __init__(self, value, line_span = None, lex_span = None):
        assert isinstance(value, int), value
        self.value = value
        self.rank = 0
        self.parent = self

        super(Number, self).__init__(line_span = line_span, lex_span = lex_span)

    def __repr__(self):
        return '{0}'.format(self.value)
    def accept(self, visitor):
        visitor.visit_number(self)
class Boolean(Atom):
    def __init__(self, value, line_span = None, lex_span = None):
        assert isinstance(value, bool), value
        self.value = value
        self.rank = 0
        self.parent = self
        super(Boolean, self).__init__(line_span = line_span, lex_span = lex_span)
    def __repr__(self):
        return '{0}'.format(self.value)
    def accept(self, visitor):
        visitor.visit_boolean(self)
#
# Operator Components
#

class Operator(LingoComponent):
    def __init__(self, token, line_span = None, lex_span = None):
        assert isinstance(token, str), token
        self.token = token
        super(Operator, self).__init__(line_span = line_span, lex_span = lex_span)

    def __repr__(self):
        return '{0}'.format(self.token)


class ArithmeticOperator(Operator): pass
class OperatorPlus(ArithmeticOperator): pass
class OperatorMinus(ArithmeticOperator): pass
class OperatorTimes(ArithmeticOperator): pass
class OperatorDivide(ArithmeticOperator): pass

class ComparisonOperator(Operator): pass
class OperatorLessThan(ComparisonOperator): pass
class OperatorEqualTo(ComparisonOperator): pass
class OperatorNotEqualTo(ComparisonOperator): pass
class OperatorLessThanOrEqualTo(ComparisonOperator): pass

class BooleanOperator(Operator): pass
class OperatorAnd(BooleanOperator): pass
class OperatorOr(BooleanOperator): pass
