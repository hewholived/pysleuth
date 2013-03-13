'''
Provide the parser for the PySleuth language "Lingo".

The LingoParser in this module defines both the syntax and the semantics
for the "Lingo" language. The parser accepts Lingo source files and produces 
object graphs constructed of LingoComponents.

( Yes, there are other programming languages out there called "Lingo". 
    http://en.wikipedia.org/wiki/Lingo_(programming_language) 

  However, since this is a "toy" language with an extremely limited audience,
  I don't care. (I like the name and I'm sticking with it!) )
'''

from ply.lex import lex, TOKEN #@UnresolvedImport
from ply.yacc import yacc, debug_file #@UnresolvedImport
from sleuth.common.exception import NestedException
from sleuth.lingo.components import * #@UnusedWildImport
from sleuth.lingo.types import *
import logging
import os.path


logger = logging.getLogger(__name__)

class LingoParser(object):

    def __init__(self):
        self.lexer = lex(module = self, errorlog = logger)

        # Delay creating the parser to allow for runtime customizations
        self.parser = None

    def parse(self, source_text):
        # Fix up newlines!
        source_text = source_text.replace('\r\n', '\n')

        lingo_directory = os.path.dirname(__file__)
        debug_filename = os.path.join(lingo_directory, debug_file)

        self.parser = yacc(module = self,
                           tabmodule = 'yacc_parse_tables',
                           errorlog = logger,
                           outputdir = lingo_directory,
                           debugfile = debug_filename)
        return self.parser.parse(source_text,
                                 tracking = True)


    #
    # Lexer / Tokenizer
    #
    tokens = [
        # Atom tokens
        'IDENTIFIER',
        'NUMBER',

        # Expression operators
        'OP_PLUS',
        'OP_MINUS',
        'OP_TIMES',
        'OP_DIVIDE',

        'OP_CMP_LT',
        'OP_CMP_EQ',
        'OP_CMP_NE',
        'OP_CMP_LTE',

        'OP_BOOL_AND',
        'OP_BOOL_OR',

        # Non-expression operators
        'OP_ASSIGNMENT',
        'OP_DEREF',

        # Syntax tokens
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'SEMI',
        'COMMA',
    ]

    keywords = {
        'input' : 'KEYWORD_INPUT',
        'ref' : 'KEYWORD_REF',
        'integer' : 'KEYWORD_INT',
        'boolean' : 'KEYWORD_BOOLEAN',
        'new' : 'KEYWORD_NEW',

        'def' : 'KEYWORD_DEF',
        'fun' : 'KEYWORD_FUN',
        'return' : 'KEYWORD_RETURN',

        'while' : 'KEYWORD_WHILE',
        'do' : 'KEYWORD_DO',

        'if' : 'KEYWORD_IF',
        'then' : 'KEYWORD_THEN',
        'else' : 'KEYWORD_ELSE',

        'true' : 'KEYWORD_TRUE',
        'false' : 'KEYWORD_FALSE',

        'skip' : 'KEYWORD_SKIP',
    }
    tokens.extend(keywords.values())

    t_OP_PLUS = r'\+'
    t_OP_MINUS = r'-'
    t_OP_TIMES = r'\*'
    t_OP_DIVIDE = r'/'

    t_OP_CMP_LT = r'<'
    t_OP_CMP_EQ = r'='
    t_OP_CMP_NE = r'!='
    t_OP_CMP_LTE = r'<='

    t_OP_BOOL_AND = r'&&'
    t_OP_BOOL_OR = r'\|\|'

    t_OP_DEREF = r'!'
    t_OP_ASSIGNMENT = ':='

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'{'
    t_RBRACE = r'}'
    t_SEMI = r';'
    t_COMMA = r','

    @TOKEN(r'[_A-Za-z][_A-Za-z0-9]*')
    def t_IDENTIFIER(self, t):
        t.type = self.keywords.get(t.value, 'IDENTIFIER')
        return t

    @TOKEN(r'\d+')
    def t_NUMBER(self, t):
        t.value = int(t.value)
        return t

    # Define a rule so we can track line numbers
    @TOKEN(r'\n+')
    def t_newline(self, t):
        t.lexer.lineno += len(t.value)
    # Ignore spaces and tabs. (Newlines are counted in t_newline but otherwise ignored.)
    t_ignore = ' \t'

    ''' Single line comment, increase line number. 
    example: #commentcomment\n '''
    @TOKEN(r'\/\/[^\n]*(\n)')
    def t_single_line_comment(self, t):
        t.lexer.lineno += 1
    
    ''' Multi line comment, increase line number by
    number of new line characters found in comment
    example: /*multi line c style comment
               can go for multiple lines */ 
    '''
    @TOKEN(r'\/\*(\/|[^\*\/]|\*+[^\*\/])*\*+\/')
    def t_multi_line_command(self, t):
        t.lexer.lineno += t.value.count("\n")
    # Error handling rule
    def t_error(self, t):
        message = "Unrecognized character for tokenizer on line {0}: '{1}'".format(t.lexer.lineno,
                                                                                   t.value[0])
        raise LingoLexingException(message)

    #
    # Parser / Productions
    #

    # Indicate that the "program" rule is the parsing starting point
    start = 'program'

    # Define operator precedence
    #    Since the language is so restrictive, this isn't all that important,
    #    but we might as well at least go through the motions. 
    precedence = (
        # Prevent a shift/reduce parser error by indicating that the SEMI token
        # has the highest precedence.
        ('left', 'SEMI'),

        ('left', 'OP_PLUS', 'OP_MINUS'),
        ('left', 'OP_TIMES', 'OP_DIVIDE'),
    )

    # Error rule for syntax errors
    def p_error(self, t):

        # Special handling if we hit the end of the file in a rule.
        if not t:
            raise LingoParsingException('End of file encountered during rule parsing. (Do you have a trailing semicolon?)')

        def find_column(input, token):
            last_cr = input.rfind('\n', 0, token.lexpos)
            if last_cr < 0:
                last_cr = 0
            column = (token.lexpos - last_cr) + 1
            return column

        lines = t.lexer.lexdata.splitlines()

        line_position = find_column(t.lexer.lexdata, t)
        line_prefix = '  '
        line_text = lines[t.lineno - 1]
        marker_line = '{prefix_whitespace}{mask_whitespace}^'.format(prefix_whitespace = ' ' * len(line_prefix),
                                                                     mask_whitespace = ' ' * (line_position))

        format_string = 'Syntax error in line {line_number}:\n{line_prefix}"{line_text}"\n{marker_line}\n  Unexpected token: {lex_token}'

        raise LingoParsingException(format_string.format(line_number = t.lineno,
                                                         line_prefix = line_prefix,
                                                         line_text = line_text,
                                                         marker_line = marker_line,
                                                         lex_token = t))

    def lex_span(self, p, target = 0):
        if hasattr(p[target], 'lex_span'):
            return p[target].lex_span

        start = p.lexspan(0)[0]

        last_index = len(p) - 1
        last = p[last_index]

        if isinstance(last, LingoComponent):
            return (start, last.lex_span[1])


        end = start + len(str(last))
        return (start, end)

    def p_empty(self, p):
        '''empty : '''
        pass
    #
    # Program Rules
    #

    def p_program(self, p):
        '''program : function_declaration_list command'''
        p[0] = Program(p[1], p[2], line_span = p.linespan(0), lex_span = self.lex_span(p))

    #
    # Function Rules
    #

    def p_function_declaration_list_list(self, p):
        '''function_declaration_list : function_declaration_list function_declaration'''
        p[0] = p[1] + [p[2]]

    def p_function_declaration_list_single(self, p):
        '''function_declaration_list : function_declaration'''
        p[0] = [p[1]]

    def p_function_declaration_list_empty(self, p):
        '''function_declaration_list : empty'''
        p[0] = []

    def p_function_declaration(self, p):
        '''function_declaration : KEYWORD_DEF IDENTIFIER OP_CMP_EQ function_definition'''
        # Note: Due to how Ply treats tokens, we have to use the same token for both
        #    the equality comparision and binding operators.
        p[0] = FunctionDeclaration(p[2], p[4], line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_function_definition(self, p):
        '''function_definition : KEYWORD_FUN LPAREN variable_list RPAREN LBRACE function_body RBRACE'''
        p[0] = FunctionDefinition(p[3], p[6], line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_function_body(self, p):
        '''function_body : command SEMI command_return
                         | command_return
        '''
        if len(p) == 4:
            assert isinstance(p[1], Command), p[1]
            assert isinstance(p[3], ReturnCommand), p[3]

            p[1].set_next_command(p[3])
            p[0] = p[1]

        else:
            assert isinstance(p[1], ReturnCommand), p[1]
            p[0] = p[1]

    def p_function_application(self, p):
        '''function_application : variable LPAREN variable_list RPAREN
                                | dereferenced_variable LPAREN variable_list RPAREN
        '''
        p[0] = FunctionCall(p[1], p[3], line_span = p.linespan(0), lex_span = self.lex_span(p))

    #
    # Command Rules
    #

    def p_command(self, p):
        '''command : command SEMI command'''
        assert isinstance(p[1], Command), p[1]
        assert isinstance(p[3], Command), p[3]

        p[1].set_next_command(p[3])
        p[0] = p[1]

    def p_command_assignment(self, p):
        '''command : variable OP_ASSIGNMENT assignment_rhs 
                   | dereferenced_variable OP_ASSIGNMENT assignment_rhs
        '''
        p[0] = AssignmentCommand(p[1], p[3], line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_command_if(self, p):
        '''command : KEYWORD_IF LPAREN expression RPAREN KEYWORD_THEN LBRACE command RBRACE KEYWORD_ELSE LBRACE command RBRACE'''
        p[0] = IfCommand(p[3], p[7], p[11], line_span = p.linespan(0), lex_span = self.lex_span(p, target = 3))

    def p_command_while(self, p):
        '''command : KEYWORD_WHILE LPAREN expression RPAREN KEYWORD_DO LBRACE command RBRACE'''
        p[0] = WhileCommand(p[3], p[7], line_span = p.linespan(0), lex_span = self.lex_span(p, target = 3))

    def p_command_skip(self, p):
        '''command : KEYWORD_SKIP'''
        p[0] = SkipCommand(line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_command_input(self, p):
        ''' command : KEYWORD_INPUT variable'''
        p[0] = InputCommand(p[2], line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_command_return(self, p):
        '''command_return : KEYWORD_RETURN variable'''
        # According to the abstract syntax grammar, the return statement isn't really
        # a "command", but they're functionally the same, other than the syntax
        # requires them to appear only and always at the end of functions. 
        p[0] = ReturnCommand(p[2], p.linespan(0), lex_span = self.lex_span(p))


    #
    # Assignment RHS Rules
    #
    def p_assignment_rhs_new(self, p):
        '''assignment_rhs : KEYWORD_NEW type'''
        p[0] = New(p[2], line_span=p.linespan(0), lex_span = self.lex_span(p))
    def p_assignment_rhs_expression(self, p):
        '''assignment_rhs : expression'''
        assert isinstance(p[1], Expression), p[1]
        p[0] = p[1]

    def p_assignment_rhs_referenced_variable(self, p):
        '''assignment_rhs : referenced_variable'''
        assert isinstance(p[1], ReferencedVariable), p[1]
        p[0] = p[1]

    def p_assignment_rhs_function_application(self, p):
        '''assignment_rhs : function_application'''
        assert isinstance(p[1], FunctionCall), p[1]
        p[0] = p[1]

    #
    # Type Rules
    #

    def p_type(self, p):
        '''type : ref_type
                | int_type
                | bool_type
         '''
        p[0] = p[1]
    def p_ref_type(self, p):
        ''' ref_type : KEYWORD_REF type '''
        p[0] = Reference(p[2], p.linespan(0)[0])
    def p_int_type(self, p):
        ''' int_type : KEYWORD_INT '''
        p[0] = Primitive("INTEGER")
    def p_bool_type(self, p):
        ''' bool_type : KEYWORD_BOOLEAN '''
        p[0] = Primitive("BOOLEAN")
    
    #
    # Expression Rules
    #

    def p_expression_atom(self, p):
        '''expression : variable
                      | dereferenced_variable
                      | bool 
                      | number
        '''
        p[0] = p[1]

    def p_expression_binary_operation(self, p):
        '''expression : expression operator expression
                      | LPAREN expression operator expression RPAREN
        '''
        # Note: the optional parens in this rule aren't in the grammar but seem
        #  prudent to allow for non-ambiguous parsing.

        shift = 0

        if len(p) == 6:
            shift = 1

        p[0] = BinaryExpression(p[1 + shift], p[2 + shift], p[3 + shift], line_span = p.linespan(0), lex_span = self.lex_span(p))


    #
    # Atom Rules
    #
    def p_variable_list_list(self, p):
        ''' variable_list : variable_list COMMA variable'''
        p[0] =  p[1] + [p[3]]
    def p_variable_list_single(self, p):
        '''variable_list : variable '''
        p[0] = [p[1]]
    def p_variable_list_empty(self, p):
        '''variable_list : empty'''
        p[0] = []
    def p_variable(self, p):
        '''variable : IDENTIFIER'''
        p[0] = Variable(p[1], line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_referenced_variable(self, p):
        '''referenced_variable : KEYWORD_REF IDENTIFIER'''
        p[0] = ReferencedVariable(p[2], line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_dereferenced_variable(self, p):
        '''dereferenced_variable : OP_DEREF IDENTIFIER'''
        p[0] = DereferencedVariable(p[2], line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_bool(self, p):
        '''bool : KEYWORD_TRUE
                | KEYWORD_FALSE
        '''
        p[0] = Boolean(p[1] == 'true', line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_number(self, p):
        '''number : NUMBER'''
        p[0] = Number(p[1], line_span = p.linespan(0), lex_span = self.lex_span(p))

    def p_operator(self, p):
        '''operator : OP_PLUS
                    | OP_MINUS
                    | OP_TIMES
                    | OP_DIVIDE

                    | OP_CMP_LT
                    | OP_CMP_EQ
                    | OP_CMP_NE
                    | OP_CMP_LTE

                    | OP_BOOL_AND
                    | OP_BOOL_OR
        '''
        operator_map = {
            '+' : OperatorPlus,
            '-' : OperatorMinus,
            '*' : OperatorTimes,
            '/' : OperatorDivide,
            '<' : OperatorLessThan,
            '=' : OperatorEqualTo,
            '!=' : OperatorNotEqualTo,
            '<=' : OperatorLessThanOrEqualTo,
            '&&' : OperatorAnd,
            '||' : OperatorOr,
        }

        operator_class = operator_map[p[1]]
        p[0] = operator_class(p[1], line_span = p.linespan(0), lex_span = self.lex_span(p))

#
# Exceptions
#

class LingoException(NestedException):
    pass

class LingoLexingException(LingoException):
    pass

class LingoParsingException(LingoException):
    pass
