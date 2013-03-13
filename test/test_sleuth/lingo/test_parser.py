from StringIO import StringIO
from mockito import Mock #@UnresolvedImport
from sleuth.lingo.components import * #@UnusedWildImport
from sleuth.lingo.parser import LingoParser, LingoLexingException, \
    LingoParsingException
from test_sleuth.support.testcase import TestCase
import logging
import sys


class LanguageTest(TestCase):

    def setUp(self):
        super(LanguageTest, self).setUp()

        # For these tests, restrict logging to ERROR only and
        # print to stderr. This allows the lexer/parser to inform
        # us of real problems, without complaining in tests that
        # don't use all the tokens and/or productions.
        self.withLogging(stream = sys.stderr,
                         level = logging.ERROR)

        self.parser = LingoParser()

    def run_token_match(self,
                        parser,
                        token_data):
        from ply.lex import runmain #@UnresolvedImport

        original_stdout = sys.stdout
        stdout_stringio = StringIO()

        sys.stdout = stdout_stringio

        try:
            runmain(lexer = parser.lexer, data = token_data)

            captured_io = stdout_stringio.getvalue()
            return captured_io

        finally:
            sys.stdout = original_stdout

    def assert_token_matches(self,
                             parser,
                             token_data,
                             expected_type,
                             expected_value):
        captured_io = self.run_token_match(parser,
                                           token_data)

        self.assertEqual(captured_io,
                         '({0},{1},1,0)\n'.format(expected_type,
                                                  repr(expected_value)))

    def test_recognizes_token_IDENTIFIER(self):
        self.assert_token_matches(self.parser,
                                  'foo',
                                  'IDENTIFIER',
                                  'foo')

    def test_recognizes_token_NUMBER(self):
        self.assert_token_matches(self.parser,
                                  '100',
                                  'NUMBER',
                                  100)

    def test_recognizes_token_OP_PLUS(self):
        self.assert_token_matches(self.parser,
                                  '+',
                                  'OP_PLUS',
                                  '+')

    def test_recognizes_token_OP_MINUS(self):
        self.assert_token_matches(self.parser,
                                  '-',
                                  'OP_MINUS',
                                  '-')

    def test_recognizes_token_OP_TIMES(self):
        self.assert_token_matches(self.parser,
                                  '*',
                                  'OP_TIMES',
                                  '*')

    def test_recognizes_token_OP_DIVIDE(self):
        self.assert_token_matches(self.parser,
                                  '/',
                                  'OP_DIVIDE',
                                  '/')

    def test_recognizes_token_OP_CMP_LT(self):
        self.assert_token_matches(self.parser,
                                  '<',
                                  'OP_CMP_LT',
                                  '<')

    def test_recognizes_token_OP_CMP_EQ(self):
        self.assert_token_matches(self.parser,
                                  '=',
                                  'OP_CMP_EQ',
                                  '=')

    def test_recognizes_token_OP_CMP_NE(self):
        self.assert_token_matches(self.parser,
                                  '!=',
                                  'OP_CMP_NE',
                                  '!=')


    def test_recognizes_token_OP_CMP_LTE(self):
        self.assert_token_matches(self.parser,
                                  '<=',
                                  'OP_CMP_LTE',
                                  '<=')

    def test_recognizes_token_OP_BOOL_AND(self):
        self.assert_token_matches(self.parser,
                                  '&&',
                                  'OP_BOOL_AND',
                                  '&&')

    def test_recognizes_token_OP_BOOL_OR(self):
        self.assert_token_matches(self.parser,
                                  '||',
                                  'OP_BOOL_OR',
                                  '||')

    def test_recognizes_token_OP_DEREF(self):
        self.assert_token_matches(self.parser,
                                  '!',
                                  'OP_DEREF',
                                  '!')

    def test_recognizes_token_OP_ASSIGNMENT(self):
        self.assert_token_matches(self.parser,
                                  ':=',
                                  'OP_ASSIGNMENT',
                                  ':=')

    def test_recognizes_token_LPAREN(self):
        self.assert_token_matches(self.parser,
                                  '(',
                                  'LPAREN',
                                  '(')

    def test_recognizes_token_RPAREN(self):
        self.assert_token_matches(self.parser,
                                  ')',
                                  'RPAREN',
                                  ')')

    def test_recognizes_token_LBRACE(self):
        self.assert_token_matches(self.parser,
                                  '{',
                                  'LBRACE',
                                  '{')

    def test_recognizes_token_RBRACE(self):
        self.assert_token_matches(self.parser,
                                  '}',
                                  'RBRACE',
                                  '}')

    def test_recognizes_token_SEMI(self):
        self.assert_token_matches(self.parser,
                                  ';',
                                  'SEMI',
                                  ';')

    def test_recognizes_token_KEYWORD_REF(self):
        self.assert_token_matches(self.parser,
                                  'ref',
                                  'KEYWORD_REF',
                                  'ref')

    def test_recognizes_token_KEYWORD_DEF(self):
        self.assert_token_matches(self.parser,
                                  'def',
                                  'KEYWORD_DEF',
                                  'def')

    def test_recognizes_token_KEYWORD_FUN(self):
        self.assert_token_matches(self.parser,
                                  'fun',
                                  'KEYWORD_FUN',
                                  'fun')

    def test_recognizes_token_KEYWORD_RETURN(self):
        self.assert_token_matches(self.parser,
                                  'return',
                                  'KEYWORD_RETURN',
                                  'return')

    def test_recognizes_token_KEYWORD_WHILE(self):
        self.assert_token_matches(self.parser,
                                  'while',
                                  'KEYWORD_WHILE',
                                  'while')

    def test_recognizes_token_KEYWORD_DO(self):
        self.assert_token_matches(self.parser,
                                  'do',
                                  'KEYWORD_DO',
                                  'do')

    def test_recognizes_token_KEYWORD_IF(self):
        self.assert_token_matches(self.parser,
                                  'if',
                                  'KEYWORD_IF',
                                  'if')

    def test_recognizes_token_KEYWORD_THEN(self):
        self.assert_token_matches(self.parser,
                                  'then',
                                  'KEYWORD_THEN',
                                  'then')

    def test_recognizes_token_KEYWORD_ELSE(self):
        self.assert_token_matches(self.parser,
                                  'else',
                                  'KEYWORD_ELSE',
                                  'else')

    def test_recognizes_token_KEYWORD_SKIP(self):
        self.assert_token_matches(self.parser,
                                  'skip',
                                  'KEYWORD_SKIP',
                                  'skip')

    def test_token_newline(self):
        captured_io = self.run_token_match(self.parser, '\n\n')
        self.assertEqual(captured_io, '')
        self.assertEqual(self.parser.lexer.lineno, 3)

    def test_token_ignore(self):
        captured_io = self.run_token_match(self.parser, ' \t')
        self.assertEqual(captured_io, '')

    def test_token_error(self):
        token = Mock()
        token.value = 'unknown'
        token.lexer = Mock()
        token.lexer.lineno = 10

        self.assertRaises(LingoLexingException,
                          self.parser.t_error,
                          token)

    #
    # Error Production Tests
    #

    def test_production_error(self):
        production = Mock()
        production.lexer = Mock()
        production.lexer.lexdata = 'hello\nworld'
        production.lexpos = 0
        production.lineno = 1

        self.assertRaises(LingoParsingException,
                          self.parser.p_error,
                          production)

    #
    # Program Production Tests
    #

    def test_production_program(self):
        self.parser.start = 'program'
        result = self.parser.parse('''
            def square = fun (x) {
                a := x * x;
                return a
            } 
            
            square_argument := 11;
            square_result := square( square_argument )
        ''')
        self.assertIsInstance(result, Program)
        self.assertEqual(len(result.functions), 1)
        self.assertIsInstance(result.command, AssignmentCommand)

    #
    # Function Production Tests
    #

    def test_production_function(self):
        self.parser.start = 'function_definition'
        result = self.parser.parse('fun (foo) { a := 1; return a }')
        self.assertIsInstance(result, FunctionDefinition)
        self.assertEqual(result.parameter.name, 'foo')
        self.assertIsInstance(result.body, AssignmentCommand)

    #
    # Command Production Tests
    #

    def test_production_command_sequence(self):
        self.parser.start = 'command'
        result = self.parser.parse('a := 1 ; b := 2')
        self.assertIsInstance(result, AssignmentCommand)
        self.assertEqual(result.assigned_variable.name, 'a')
        self.assertEqual(result.get_next_command().assigned_variable.name, 'b')

    def test_production_command_assignment(self):
        self.parser.start = 'command'
        result = self.parser.parse('a := 1')
        self.assertIsInstance(result, AssignmentCommand)
        self.assertEqual(result.assigned_variable.name, 'a')
        self.assertIsInstance(result.expression, Number)

    def test_production_command_dereferenced_assignment(self):
        self.parser.start = 'command'
        result = self.parser.parse('!a := 1')
        self.assertIsInstance(result, AssignmentCommand)
        self.assertEqual(result.assigned_variable.name, 'a')
        self.assertIsInstance(result.expression, Number)

    def test_production_command_if(self):
        self.parser.start = 'command'
        result = self.parser.parse('if ( a < b ) then { a := 1 } else { a := 2 }')
        self.assertIsInstance(result, IfCommand)
        self.assertIsInstance(result.expression, Expression)
        self.assertIsInstance(result.true_block, AssignmentCommand)
        self.assertIsInstance(result.false_block, AssignmentCommand)

    def test_production_command_while(self):
        self.parser.start = 'command'
        result = self.parser.parse('while ( 1 < 2 ) do { a := 1 }')
        self.assertIsInstance(result, WhileCommand)
        self.assertIsInstance(result.expression, Expression)
        self.assertIsInstance(result.loop_block, AssignmentCommand)

    def test_production_command_skip(self):
        self.parser.start = 'command'
        result = self.parser.parse('skip')
        self.assertIsInstance(result, SkipCommand)

    #
    # Assignment RHS Production Rule Tests
    #

    def test_production_assignment_rhs_expression(self):
        self.parser.start = 'assignment_rhs'
        result = self.parser.parse('1 + 2')
        self.assertIsInstance(result, BinaryExpression)

    def test_production_assignment_rhs_referenced_variable(self):
        self.parser.start = 'assignment_rhs'
        result = self.parser.parse('ref foo')
        self.assertIsInstance(result, ReferencedVariable)
        self.assertEqual(result.name, 'foo')

    def test_production_assignment_rhs_function_application(self):
        self.parser.start = 'assignment_rhs'
        result = self.parser.parse('foo(bar)')
        self.assertIsInstance(result, FunctionCall)
        self.assertEqual(result.function_variable.name, 'foo')
        self.assertEqual(result.parameter_variable.name, 'bar')

    #
    # Expression Production Rule Tests
    #

    def test_production_expression_binary_operation(self):
        self.parser.start = 'expression'
        result = self.parser.parse('a + 2')
        self.assertIsInstance(result, BinaryExpression)
        self.assertIsInstance(result.left_term, Variable)
        self.assertIsInstance(result.operator, Operator)
        self.assertIsInstance(result.right_term, Number)

    def test_production_expression_binary_operation_nested(self):
        self.parser.start = 'expression'
        result = self.parser.parse('(a + 2) <= b')
        self.assertIsInstance(result, BinaryExpression)
        self.assertIsInstance(result.left_term, BinaryExpression)
        self.assertIsInstance(result.operator, Operator)
        self.assertIsInstance(result.right_term, Variable)

    def test_production_expression_atom_number(self):
        self.parser.start = 'expression'
        result = self.parser.parse('1234')
        self.assertIsInstance(result, Number)
        self.assertEqual(result.value, 1234)

    def test_production_expression_atom_boolean(self):
        self.parser.start = 'expression'
        result = self.parser.parse('true')
        self.assertIsInstance(result, Boolean)
        self.assertEqual(result.value, True)

    def test_production_expression_atom_variable(self):
        self.parser.start = 'expression'
        result = self.parser.parse('abcd')
        self.assertIsInstance(result, Variable)
        self.assertEqual(result.name, 'abcd')

    def test_production_expression_atom_dereferenced_variable(self):
        self.parser.start = 'expression'
        result = self.parser.parse('!abcd')
        self.assertIsInstance(result, DereferencedVariable)
        self.assertEqual(result.name, 'abcd')

    #
    # Atom Production Rule Tests
    #

    def test_production_variable(self):
        self.parser.start = 'variable'
        result = self.parser.parse('foo')
        self.assertIsInstance(result, Variable)
        self.assertEqual(result.name, 'foo')

    def test_production_referenced_variable(self):
        self.parser.start = 'referenced_variable'
        result = self.parser.parse('ref foo')
        self.assertIsInstance(result, ReferencedVariable)
        self.assertEqual(result.name, 'foo')

    def test_production_dereferenced_variable(self):
        self.parser.start = 'dereferenced_variable'
        result = self.parser.parse('!foo')
        self.assertIsInstance(result, DereferencedVariable)
        self.assertEqual(result.name, 'foo')

    def test_production_bool_true(self):
        self.parser.start = 'bool'
        result = self.parser.parse('true')
        self.assertIsInstance(result, Boolean)
        self.assertEqual(result.value, True)

    def test_production_bool_false(self):
        self.parser.start = 'bool'
        result = self.parser.parse('false')
        self.assertIsInstance(result, Boolean)
        self.assertEqual(result.value, False)

    def test_production_number(self):
        self.parser.start = 'number'
        result = self.parser.parse('1234')
        self.assertIsInstance(result, Number)
        self.assertEqual(result.value, 1234)

    def test_production_arithmetic_operator_plus(self):
        self.parser.start = 'operator'
        result = self.parser.parse('+')
        self.assertIsInstance(result, OperatorPlus)

    def test_production_arithmetic_operator_minus(self):
        self.parser.start = 'operator'
        result = self.parser.parse('-')
        self.assertIsInstance(result, OperatorMinus)

    def test_production_arithmetic_operator_times(self):
        self.parser.start = 'operator'
        result = self.parser.parse('*')
        self.assertIsInstance(result, OperatorTimes)

    def test_production_arithmetic_operator_divide(self):
        self.parser.start = 'operator'
        result = self.parser.parse('/')
        self.assertIsInstance(result, OperatorDivide)

    def test_production_comparison_operator_lt(self):
        self.parser.start = 'operator'
        result = self.parser.parse('<')
        self.assertIsInstance(result, OperatorLessThan)

    def test_production_comparison_operator_eq(self):
        self.parser.start = 'operator'
        result = self.parser.parse('=')
        self.assertIsInstance(result, OperatorEqualTo)

    def test_production_comparison_operator_ne(self):
        self.parser.start = 'operator'
        result = self.parser.parse('!=')
        self.assertIsInstance(result, OperatorNotEqualTo)

    def test_production_comparison_operator_lte(self):
        self.parser.start = 'operator'
        result = self.parser.parse('<=')
        self.assertIsInstance(result, OperatorLessThanOrEqualTo)

    def test_production_operator_and(self):
        self.parser.start = 'operator'
        result = self.parser.parse('&&')
        self.assertIsInstance(result, OperatorAnd)

    def test_production_operator_or(self):
        self.parser.start = 'operator'
        result = self.parser.parse('||')
        self.assertIsInstance(result, OperatorOr)

    #
    # Tests for complete programs
    #    These aren't really "unit" tests, so much as tests
    #    that check some of the more involved features of the
    #    LingoComponent stack.
    #

    def test_program_simple(self):
        program_text = '''
            a := 1;
            b := 2;
            c := a + b
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertIsInstance(program, Program)

        self.assertEqual(len(program.functions), 0)

        cmd_assign_a = program.command
        cmd_assign_b = cmd_assign_a.get_next_command()
        cmd_assign_c = cmd_assign_b.get_next_command()

        self.assertEqual(cmd_assign_c.assigned_variable.name, 'c')

    def test_program_conditional(self):
        program_text = '''
            a := 1;
            b := 2;
            
            while ( a + b < 10 ) do {
                a := a + 1;
                b := b * 2
            };
            
            c := a + b
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertIsInstance(program, Program)

        self.assertEqual(len(program.functions), 0)

        cmd_assign_a = program.command
        cmd_assign_b = cmd_assign_a.get_next_command()

        cmd_while = cmd_assign_b.get_next_command()

        cmd_assign_c = cmd_while.get_next_command()

        self.assertEqual(cmd_assign_c.assigned_variable.name, 'c')

    def test_program_functions(self):
        program_text = '''
            def square = fun( x ) { result := x * x; return result }
            def cube = fun( x ) { result := x * x * x; return result }
            
            value := 4;
            squared := square(value);
            cubed := square(value)
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertIsInstance(program, Program)

        self.assertEqual(len(program.functions), 2)


    def test_program_all_parse_symbols(self):
        # Lengthy test demonstrating all Lingo syntax features

        program_text = '''
            def foo = fun(x) {
                skip;
                return x
            }
        
            a := 1 + 1;
            b := 2 - 2;
            c := 3 * 3; 
            d := 4 / 4;
            
            e := true;
            f := false;
            
            g := a;
            h := 0;
            
            i := ref a;
            !i := 32;
            j := !i;
            
            k := ref foo;
            l := foo(a);
            m := !l(a);
            
            if (true) then { n := a } else { n := b };
            
            o := true;
            while ( o ) do { o := false };
            
            skip;
            
            if ( 1 < 2 ) then { skip } else { skip };
            if ( 2 <= 2 ) then { skip } else { skip };
            if ( 1 = 1 ) then { skip } else { skip };
            if ( 1 != 2 ) then { skip } else { skip };
            
            if ( true && true ) then { skip } else { skip };
            if ( true || false ) then { skip } else { skip }
            
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertIsInstance(program, Program)

        self.assertEqual(len(program.functions), 1)

        a_cmd = program.command
        self.assertIsInstance(a_cmd, AssignmentCommand)
        self.assertIsInstance(a_cmd.assigned_variable, Variable)
        self.assertEqual(a_cmd.assigned_variable.name, 'a')
        self.assertIsInstance(a_cmd.expression, BinaryExpression)
        self.assertIsInstance(a_cmd.expression.left_term, Number)
        self.assertEqual(a_cmd.expression.left_term.value, 1)
        self.assertIsInstance(a_cmd.expression.operator, OperatorPlus)
        self.assertIsInstance(a_cmd.expression.right_term, Number)
        self.assertEqual(a_cmd.expression.right_term.value, 1)

        b_cmd = a_cmd.get_next_command()
        self.assertIsInstance(b_cmd, AssignmentCommand)
        self.assertIsInstance(b_cmd.expression, BinaryExpression)
        self.assertIsInstance(b_cmd.expression.left_term, Number)
        self.assertEqual(b_cmd.expression.left_term.value, 2)
        self.assertIsInstance(b_cmd.expression.operator, OperatorMinus)
        self.assertIsInstance(b_cmd.expression.right_term, Number)
        self.assertEqual(b_cmd.expression.right_term.value, 2)

        c_cmd = b_cmd.get_next_command()
        self.assertIsInstance(c_cmd, AssignmentCommand)
        self.assertIsInstance(c_cmd.expression, BinaryExpression)
        self.assertIsInstance(c_cmd.expression.left_term, Number)
        self.assertEqual(c_cmd.expression.left_term.value, 3)
        self.assertIsInstance(c_cmd.expression.operator, OperatorTimes)
        self.assertIsInstance(c_cmd.expression.right_term, Number)
        self.assertEqual(c_cmd.expression.right_term.value, 3)

        d_cmd = c_cmd.get_next_command()
        self.assertIsInstance(d_cmd, AssignmentCommand)
        self.assertIsInstance(d_cmd.expression, BinaryExpression)
        self.assertIsInstance(d_cmd.expression.left_term, Number)
        self.assertEqual(d_cmd.expression.left_term.value, 4)
        self.assertIsInstance(d_cmd.expression.operator, OperatorDivide)
        self.assertIsInstance(d_cmd.expression.right_term, Number)
        self.assertEqual(d_cmd.expression.right_term.value, 4)

        e_cmd = d_cmd.get_next_command()
        self.assertIsInstance(e_cmd, AssignmentCommand)
        self.assertIsInstance(e_cmd.expression, Boolean)
        self.assertTrue(e_cmd.expression.value)

        f_cmd = e_cmd.get_next_command()
        self.assertIsInstance(f_cmd, AssignmentCommand)
        self.assertIsInstance(f_cmd.expression, Boolean)
        self.assertFalse(f_cmd.expression.value)

        g_cmd = f_cmd.get_next_command()
        self.assertIsInstance(g_cmd, AssignmentCommand)
        self.assertIsInstance(g_cmd.expression, Variable)
        self.assertEqual(g_cmd.expression.name, 'a')

        h_cmd = g_cmd.get_next_command()
        self.assertIsInstance(h_cmd, AssignmentCommand)
        self.assertIsInstance(h_cmd.expression, Number)
        self.assertEqual(h_cmd.expression.value, 0)

        i_cmd = h_cmd.get_next_command()
        self.assertIsInstance(i_cmd, AssignmentCommand)
        self.assertIsInstance(i_cmd.expression, ReferencedVariable)
        self.assertEqual(i_cmd.expression.name, 'a')

        i_deref_cmd = i_cmd.get_next_command()
        self.assertIsInstance(i_deref_cmd, AssignmentCommand)
        self.assertIsInstance(i_deref_cmd.assigned_variable, DereferencedVariable)
        self.assertEqual(i_deref_cmd.assigned_variable.name, 'i')

        j_cmd = i_deref_cmd.get_next_command()
        self.assertIsInstance(j_cmd, AssignmentCommand)
        self.assertIsInstance(j_cmd.expression, DereferencedVariable)
        self.assertEqual(j_cmd.expression.name, 'i')

        k_cmd = j_cmd.get_next_command()
        self.assertIsInstance(k_cmd, AssignmentCommand)
        self.assertIsInstance(k_cmd.expression, ReferencedVariable)
        self.assertEqual(k_cmd.expression.name, 'foo')

        l_call_cmd = k_cmd.get_next_command()
        self.assertIsInstance(l_call_cmd, AssignmentCommand)
        self.assertIsInstance(l_call_cmd.expression, FunctionCall)
        self.assertIsInstance(l_call_cmd.expression.function_variable, Variable)
        self.assertEqual(l_call_cmd.expression.function_variable.name, 'foo')
        self.assertIsInstance(l_call_cmd.expression.parameter_variable, Variable)
        self.assertEqual(l_call_cmd.expression.parameter_variable.name, 'a')

        l_ret_cmd = l_call_cmd.get_next_command()
        self.assertIsInstance(l_ret_cmd, AssignmentCommand)
        self.assertIsInstance(l_ret_cmd.expression, FunctionReturn)
        self.assertIsInstance(l_ret_cmd.expression.function_variable, Variable)
        self.assertEqual(l_ret_cmd.expression.function_variable.name, 'foo')
        self.assertIsInstance(l_ret_cmd.expression.parameter_variable, Variable)
        self.assertEqual(l_ret_cmd.expression.parameter_variable.name, 'a')

        m_call_cmd = l_ret_cmd.get_next_command()
        self.assertIsInstance(m_call_cmd, AssignmentCommand)
        self.assertIsInstance(m_call_cmd.expression, FunctionCall)
        self.assertIsInstance(m_call_cmd.expression.function_variable, DereferencedVariable)
        self.assertEqual(m_call_cmd.expression.function_variable.name, 'l')
        self.assertIsInstance(m_call_cmd.expression.parameter_variable, Variable)
        self.assertEqual(m_call_cmd.expression.parameter_variable.name, 'a')

        m_ret_cmd = m_call_cmd.get_next_command()
        self.assertIsInstance(m_ret_cmd, AssignmentCommand)
        self.assertIsInstance(m_ret_cmd.expression, FunctionReturn)
        self.assertIsInstance(m_ret_cmd.expression.function_variable, DereferencedVariable)
        self.assertEqual(m_ret_cmd.expression.function_variable.name, 'l')
        self.assertIsInstance(m_ret_cmd.expression.parameter_variable, Variable)
        self.assertEqual(m_ret_cmd.expression.parameter_variable.name, 'a')

        n_cmd = m_ret_cmd.get_next_command()
        self.assertIsInstance(n_cmd, IfCommand)
        self.assertIsInstance(n_cmd.expression, Boolean)
        self.assertEqual(n_cmd.expression.value, True)
        self.assertIsInstance(n_cmd.true_block, AssignmentCommand)
        self.assertIsInstance(n_cmd.true_block.assigned_variable, Variable)
        self.assertEqual(n_cmd.true_block.assigned_variable.name, 'n')
        self.assertIsInstance(n_cmd.false_block, AssignmentCommand)
        self.assertIsInstance(n_cmd.false_block.assigned_variable, Variable)
        self.assertEqual(n_cmd.false_block.assigned_variable.name, 'n')

        o_cmd = n_cmd.get_next_command()
        o_while_cmd = o_cmd.get_next_command()
        self.assertIsInstance(o_while_cmd, WhileCommand)
        self.assertIsInstance(o_while_cmd.expression, Variable)
        self.assertEqual(o_while_cmd.expression.name, 'o')
        self.assertIsInstance(o_while_cmd.loop_block, AssignmentCommand)
        self.assertIsInstance(o_while_cmd.loop_block.assigned_variable, Variable)
        self.assertEqual(o_while_cmd.loop_block.assigned_variable.name, 'o')

        skip_cmd = o_while_cmd.get_next_command()
        self.assertIsInstance(skip_cmd, SkipCommand)

        lt_if_cmd = skip_cmd.get_next_command()
        self.assertIsInstance(lt_if_cmd, IfCommand)
        self.assertIsInstance(lt_if_cmd.expression, BinaryExpression)
        self.assertIsInstance(lt_if_cmd.expression.operator, OperatorLessThan)

        le_if_cmd = lt_if_cmd.get_next_command()
        self.assertIsInstance(le_if_cmd, IfCommand)
        self.assertIsInstance(le_if_cmd.expression, BinaryExpression)
        self.assertIsInstance(le_if_cmd.expression.operator, OperatorLessThanOrEqualTo)

        eq_if_cmd = le_if_cmd.get_next_command()
        self.assertIsInstance(eq_if_cmd, IfCommand)
        self.assertIsInstance(eq_if_cmd.expression, BinaryExpression)
        self.assertIsInstance(eq_if_cmd.expression.operator, OperatorEqualTo)

        ne_if_cmd = eq_if_cmd.get_next_command()
        self.assertIsInstance(ne_if_cmd, IfCommand)
        self.assertIsInstance(ne_if_cmd.expression, BinaryExpression)
        self.assertIsInstance(ne_if_cmd.expression.operator, OperatorNotEqualTo)

        and_if_cmd = ne_if_cmd.get_next_command()
        self.assertIsInstance(and_if_cmd, IfCommand)
        self.assertIsInstance(and_if_cmd.expression, BinaryExpression)
        self.assertIsInstance(and_if_cmd.expression.operator, OperatorAnd)

        or_if_cmd = and_if_cmd.get_next_command()
        self.assertIsInstance(or_if_cmd, IfCommand)
        self.assertIsInstance(or_if_cmd.expression, BinaryExpression)
        self.assertIsInstance(or_if_cmd.expression.operator, OperatorOr)
