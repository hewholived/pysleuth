from sleuth.common.exception import TypeException
from sleuth.lingo.components import *
from sleuth.lingo.types import *
import sys
import copy

''' 
    First renames all variables within functions to prepend with function name, that way
    they do not clash.
    
    Then do standard unification as per Lecture 10 Slides CS-290C Fall 2010.
        -Rules are defined in lecture notes
        -Keep a map of variable names to the first occurrence, thus we can always
         unify that variable (as each is a separate variable in memory).
    Finally rename back to original values.
    
    If annotate_types is true, will proceed with annotating the AST with types even 
    when type inference fails, in order to provide feedback to the user.
    
    When Type inference fails, raises a TypeException to signify this.
    
'''     
    
class TypeCheck:
    def __init__(self,annotate_types):
        self.temp_count = 0
        self.variables = {}
        self.functions = []
        self.return_variable = None
        self.annotate_types = annotate_types
    '''
        Print every variable that was visited and types were not inferred.
        
        Exit if any unknown (annotating AST first if specified).
    '''
    def check_unknown(self):
        unknown_variables = ""
        for name, var in self.variables.items():
            varParent = self.find(var)
            if not isinstance(varParent, Type):#didn't infer type
                if var.name[0] != "_":#not a temporary variables
                    unknown_variables += var.name + ", "
        if len(unknown_variables) != 0:
            print >> sys.stderr, "Could not infer types for: %s" % unknown_variables[0:len(unknown_variables)-2]
            if self.annotate_types:
                self.rename.visit_program(self.program)
            raise TypeException("Could not infer all types.")
    '''
        Checking for cyclic references.
        i.e. a = ref b, check that b != ref a
    '''
    def free_var(self, var, t):    
        if isinstance(t, Reference):
            return self.free_var(var, t.value)
        if isinstance(t, Function):
            return [self.free_var(var, x) for x in t.signature]
        if isinstance(t, Primitive):
            return
        if var.name == t.name:
            print >> sys.stderr, "cyclic dependency in types involving %s" % var.name
            raise TypeException("Cyclic types error.")
        if t.name in self.variables:
            parent = self.find(self.variables[t.name])
            if parent != t:
                return self.free_var(var, parent)
    '''
        Attempt to unify x and y.
        @x & y either Variable, or some Type
        
        First find parents using standard union/find algorithm.
        
        Possible cases:
        
        1. If one is a type and other is a variable, always set the type to 
        the parent.
        
        2. If both are references, unify what they refer too, then allow the standard
           case to set who is parent. Otherwise, could not possibly resolve types.
        
        3. Same case, except now functions, so unify the signatures. Error can now also
           occur if different length signatures.
        
        4. If x_root is a primitive, then yRoot must be the same primitive.
    '''
    def unify(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        if isinstance(x_root, Type) and isinstance(y_root, Variable):
            self.free_var(y_root, x_root)
            y_root.parent = x_root
            y_root.rank = max(x_root, y_root)
            return
        elif isinstance(x_root, Variable) and isinstance(y_root, Type):
            self.free_var(x_root, y_root)
            x_root.parent = y_root
            x_root.rank = max(x_root, y_root)
            return
        elif isinstance(x_root, Reference) or isinstance(y_root, Reference):
            if isinstance(y_root, Reference) and isinstance(x_root, Reference):
                self.unify(x_root.value, y_root.value)
            else:
                self.error("Tried to unify %s and %s, found parent types which could not match: %s and %s" \
                           % (x, y, x_root, y_root), x_root, y_root)
        elif isinstance(x_root, Function) or isinstance(y_root, Function): 
            if isinstance(y_root, Function) and isinstance(x_root, Function):
                if len(x_root.signature) != len(y_root.signature):
                    self.error("Tried to unify %s and %s, found parent types with non matching signature lengths: %s and %s" \
                           % (x, y, x_root, y_root), x_root, y_root)
                for i in range(len(x_root.signature)):
                    self.unify(x_root.signature[i], y_root.signature[i]) 
            else:
                self.error("Tried to unify %s and %s, found parent types which could not match: %s and %s" \
                           % (x, y, x_root, y_root), x_root, y_root)
        elif isinstance(x_root, Primitive):
            if not isinstance(y_root, Primitive) or x_root!=y_root:
                self.error("Tried to unify %s and %s, found parent types which could not match: %s and %s" \
                           % (x, y, x_root, y_root), x_root, y_root)
                
        if x_root.rank > y_root.rank:
            y_root.parent = x_root
        elif x_root.rank < y_root.rank:
            x_root.parent = y_root
        elif x_root != y_root: # Unless x and y are already in same set, merge them
            y_root.parent = x_root
            x_root.rank = x_root.rank + 1
            
    ''' 
        If variable has not been seen before, add to the mapping,
        some variables may never be defined, just used (default 
        integer), so check the references and functions as well
        for these variables.
            
        In the case of the variable, use the mapping to find the
        parent for all instances of that variable.
    '''
    def find(self, x):

        if isinstance(x,Variable):
            if not x.name in self.variables:
                self.variables[x.name] = x
            else:
                x = self.variables[x.name]
        if isinstance(x,Reference):
            if isinstance(x.value, Variable):
                if not x.value.name in self.variables:
                    self.variables[x.value.name] = x.value
        if isinstance(x,Function):
           for var in x.signature:
               if isinstance(var, Variable):
                   if not var.name in self.variables:
                       self.variables[var.name] = var
        if x.parent == x:
            return x
        else:
            x.parent = self.find(x.parent)
            return x.parent
    '''
    Visit a Program node in the AST
    
    Visit each function declaration, then each command in the linked list of commands.
    '''
    def visit_program(self, program):
        self.program = program
        self.rename = Rename(self.variables)
        self.rename.visit_program(program)
        for functionDeclaration in program.functions:
            functionDeclaration.accept(self)
        self.visit_command_block(program.command)
        self.check_unknown()
        self.rename.visit_program(program)
        
    def visit_assignment_command(self, assignment_command):
        #FunctionReturn gives nothing extra from FunctionCall, skip it
        if isinstance(assignment_command.expression, FunctionReturn):
            return
        assigned_variable = assignment_command.assigned_variable
        expression = assignment_command.expression
        
        lhs_variable = assigned_variable
        # !LHS = RHS, unify: LHS = ref(temp)
        if isinstance(assigned_variable, DereferencedVariable):
            lhs_variable = self.get_temp(assigned_variable.line_span, assigned_variable.lex_span)
            self.unify(Variable(assigned_variable.name, assigned_variable.line_span, \
                                assigned_variable.lex_span), Reference(lhs_variable, lhs_variable.line_number) )
        # LHS = integer, unify: LHS = INTEGER
        if isinstance(expression, Number):
            self.unify(lhs_variable, Primitive("INTEGER", lhs_variable.line_number))
        # LHS = boolean, unify: LHS = BOOLEAN
        elif isinstance(expression, Boolean):
            self.unify(lhs_variable, Primitive("BOOLEAN", lhs_variable.line_number))
        # LHS = fun(a1,a2,...,an), unify: fun = t1->t2->...tn->tn+1, LHS = tn+1 or
        # LHS = !fun(a1,a2,...,an), unify: fun = ref(t1->t2->...tn->tn+1), LHS = tn+1
        elif isinstance(expression, FunctionCall) :
            parameterTypes = [self.get_temp(expression.line_span, expression.lex_span) for parameter in expression.parameter_variables]
            returnType = self.get_temp(expression.line_span, expression.lex_span)
            self.unify( returnType, lhs_variable )
            for parameter in range(len(parameterTypes)):
                self.unify( parameterTypes[parameter],\
                    expression.parameter_variables[parameter]  )
            parameterTypes.append(returnType)
            if isinstance(expression.function_variable, DereferencedVariable):
                self.unify(Variable(expression.function_variable.name, expression.function_variable.line_span, expression.function_variable.lex_span), \
                        Reference(Function(parameterTypes, expression.line_number), \
                                  expression.function_variable.line_number))
            else:
                self.unify(expression.function_variable, Function(parameterTypes, expression.line_number))
        # LHS = BinaryExpression unify: LHS = (infer type of BinaryExpression)
        elif isinstance(expression, BinaryExpression):
             self.unify(lhs_variable, self.evaluate_known( expression, None))
        # LHS = !RHS unify: LHS = temp & RHS = ref(temp)
        elif isinstance(expression, DereferencedVariable):
             temp_var_rhs = self.get_temp(expression.line_span, expression.lex_span)
             self.unify( lhs_variable, temp_var_rhs )
             self.unify( Variable(expression.name, expression.line_span, expression.lex_span), \
                                  Reference(temp_var_rhs, temp_var_rhs.line_number) )
        # LHS = ref RHS unify: LHS = ref(RHS)
        elif isinstance(expression, ReferencedVariable):
             self.unify(lhs_variable, Reference(Variable(expression.name, \
                                    expression.line_span, expression.lex_span), expression.line_number) )
        # LHS = RHS unify: LHS = RHS
        elif isinstance(expression, Variable):
            self.unify( lhs_variable,expression )
        #LHS = new Type unify: LHS = Ref(Type)
        elif isinstance(expression, New):
            self.unify(lhs_variable, Reference(expression.allocate_type, lhs_variable.line_number))

    
    ''' Check expression evaluates to a boolean, and visit both blocks'''
    def visit_if_command(self, if_command):
        self.evaluate_known(if_command.expression, Primitive("BOOLEAN", if_command.expression.line_number))
        self.visit_command_block(if_command.true_block)
        self.visit_command_block(if_command.false_block)
        
    '''Check expression evaluates to a boolean, and visit block '''
    def visit_while_command(self, while_command):
        self.evaluate_known( while_command.expression, Primitive("BOOLEAN", while_command.expression.line_number) )
        self.visit_command_block(while_command.loop_block)
    
    def visit_skip_command(self, skip_command):
        pass
    
    ''' Does not give anything to unify, but add to variables if not already present. '''
    def visit_input_command(self, input_command):
        if not input_command.variable.name in self.variables:
            self.variables[input_command.variable.name] = input_command.variable
        else:
            self.evaluate_known( input_command.variable, Primitive("INTEGER", input_command.variable.line_number) )
    '''
        Standard unification rules. self.return_variable contains the return variable from visiting 
        the actual function declaration, which can then be unified with the temporary representing
        the return type of the function.
    '''
    def visit_function_declaration(self, function_declaration):
        signature = [self.get_temp(function_declaration.line_span, function_declaration.lex_span) for parameter in range(len(function_declaration.definition.parameters)+1)]
        self.unify(Variable(function_declaration.name,function_declaration.line_span, function_declaration.lex_span), \
                                Function(signature, function_declaration.line_number) )
        for parameter in range(len(function_declaration.definition.parameters)):
            self.unify(signature[parameter], \
                                 function_declaration.definition.parameters[parameter] )
        function_declaration.definition.accept(self)
        self.unify(signature[len(signature)-1], self.return_variable)
        
    '''store return value for unification later.'''
    def visit_return_command(self, return_command):
        self.return_variable = return_command.variable
        
    def visit_function_definition(self, function_definition):
        self.visit_command_block(function_definition.body)

    def visit_command_block(self, command):
        while command!=None:
            command.accept(self)
            command = command.get_next_command()
    def get_temp(self, line_span, lex_span):
        self.temp_count = self.temp_count + 1
        return Variable("_t%d" % (self.temp_count -1), line_span, lex_span)
    
    ''' Due to the simplicity of Lingo the operator determines the types of 
        the operands, thus we take advantage of this. 
        
        Recursively check input types for the operators, then in the base
        cases unify variables with their appropriate types.
        
        @expression : expression whose type to check/infer
        @t : type to check, None if the base call 
    '''
    def evaluate_known(self, expression, t):
        #Recursively check operands of binary expression
        if isinstance(expression, BinaryExpression):
            if isinstance(expression.operator, ArithmeticOperator):
                if t != Primitive("INTEGER") and t != None:
		    self.error("%s was found when integer was expected in the expression %s" % (t, expression), expression)
		else:
                    self.evaluate_known(expression.left_term, Primitive("INTEGER", expression.left_term.line_number))
                    self.evaluate_known(expression.right_term, Primitive("INTEGER", expression.right_term.line_number))
                    return Primitive("INTEGER", expression.line_number)
            if isinstance(expression.operator, ComparisonOperator):
                if t != Primitive("BOOLEAN") and t != None:
		    self.error("%s was found when boolean was expected in the expression %s" % (t, expression), expression)
		else:
                    self.evaluate_known(expression.left_term, Primitive("INTEGER", expression.left_term.line_number))
                    self.evaluate_known(expression.right_term, Primitive("INTEGER", expression.right_term.line_number))
                    return Primitive("BOOLEAN", expression.line_number)
            elif isinstance(expression.operator, BooleanOperator):
                if t != Primitive("BOOLEAN") and t != None:
		    self.error("%s was found when boolean was expected in the expression %s" % (t, expression), expression)
		else:
                    self.evaluate_known(expression.left_term, Primitive("BOOLEAN", expression.left_term.line_number))
                    self.evaluate_known(expression.right_term, Primitive("BOOLEAN", expression.right_term.line_number))
                    return Primitive("BOOLEAN", expression.line_number)
        #t has type of the variable, add that to our type mapping, print an self.error message if type does not match
        elif isinstance(expression, DereferencedVariable):
            self.unify(expression, Reference(t, expression.line_number))
        elif isinstance(expression, ReferencedVariable):
            self.error("The referenced variable %s was found in a binary expression" % expression, expression)
        elif isinstance(expression, Variable):
            self.unify(expression, t)
        elif isinstance(expression, Number) :
            if t != Primitive("INTEGER"):
                self.error("Number literal %s was found when %s was expected" % (expression,t), expression)
            else:
                return t
        elif isinstance(expression, Boolean):
            if t!= Primitive("BOOLEAN"):
                self.error("Boolean literal %s found when %s was expected." %  (expression,t), expression)
            else:
                return t
        else:
            self.error("Unknown case %s, or type checker bug encountered" %  expression, expression)
        
    def error(self, message, expr1, expr2=None):
        if expr2 != None:
            print >> sys.stderr, message + " from lines %d and %d.  " % (expr1.line_number, expr2.line_number)
        else:
            print >> sys.stderr, message + " at line %d. " % expr1.line_number
        if self.annotate_types:
            self.rename.visit_program(self.program)
        raise TypeException("Incorrectly typed program.")

'''
    Visit a Program node in the AST
    
    Either rename with function scope if rename is true, or rename to defaults if false.
    
    Also if false, annotate types on the AST.
    
'''
    
class Rename:
    def __init__(self, variables):
        self.function_scope = ""
        self.functions=[]
        self.variables = variables
        self.rename = True
    def get_type(self, x):
        xBase = x #Maintain if we find root and don't know type
        if isinstance(x, Variable):
            if x.name in self.variables: #if encountered error, some variables were never checked
                x = self.find(self.variables[x.name])
            else:
                return None
        if isinstance(x, Primitive):
            return x
        elif isinstance(x, Reference):
            return Reference(self.get_type(x.value), 0)
        elif isinstance(x, Function):
            return Function([self.get_type(sig) for sig in x.signature], 0)
        return None #Type not known
    def find(self, x):
        if x.parent == x:
            return x
        else:
            x.parent = self.find(x.parent)
            return x.parent
    def visit_program(self, program):
        self.functions = [functionDeclaration.name for functionDeclaration in program.functions]
        for functionDeclaration in program.functions:
            functionDeclaration.accept(self)
        self.visit_command_block(program.command)
        self.rename = False
        
    def visit_assignment_command(self, assignment_command):
        #visit to rename variables
        #Already assigned when FunctionCall was visited, do not rename!
        if isinstance(assignment_command.expression, FunctionReturn):
            return
        assignment_command.expression.accept(self)
        assignment_command.assigned_variable.accept(self)

    
    def visit_if_command(self, if_command):
        if_command.expression.accept(self)
        self.visit_command_block(if_command.true_block)
        self.visit_command_block(if_command.false_block)
        
    def visit_while_command(self, while_command):
        while_command.expression.accept(self)
        self.visit_command_block(while_command.loop_block)
    
    def visit_skip_command(self, skip_command):
        pass
    
    def visit_function_declaration(self, function_declaration):
        oldScope = self.function_scope
        
        self.function_scope = self.function_scope + function_declaration.name + "_"
        for parameter in range(len(function_declaration.definition.parameters)):
            function_declaration.definition.parameters[parameter].accept(self)
        function_declaration.definition.accept(self)
        self.function_scope = oldScope
        
    def visit_return_command(self, return_command):
        return_command.variable.accept(self)
        
    def visit_input_command(self, input_command):
        input_command.variable.accept(self)
        
    def visit_new(self, new):
        pass
    
    ''' Visit both sides for renaming'''
    def visit_binary_expression(self, binary_expression):
        binary_expression.left_term.accept(self)
        binary_expression.right_term.accept(self)
    
    '''Rename variables in a function call'''
    def visit_function_call(self, function_call):
        function_call.function_variable.accept(self)
        for parameter in function_call.parameter_variables:
            parameter.accept(self)
    def visit_function_return(self, function_return):
        pass
    
    def visit_function_definition(self, function_definition):
        self.visit_command_block(function_definition.body)
    
    
    def visit_variable(self, variable):
        if not self.rename:
            variable.type = copy.deepcopy(self.get_type(variable))
        if variable.name not in self.functions:
            if self.rename:
                self.append_scope(variable)
            else:
                self.remove_scope(variable)
        
                     
    def visit_referenced_variable(self, referenced_variable):
        if not self.rename:
            var = Variable(referenced_variable.name, referenced_variable.line_span, \
                                          referenced_variable.lex_span)
            referenced_variable.type = copy.deepcopy(self.get_type(var))
        if referenced_variable.name not in self.functions:
            if self.rename:
                self.append_scope(referenced_variable)
            else:
                self.remove_scope(referenced_variable)
                
    def visit_dereferenced_variable(self, dereferenced_variable):
        if self.rename:
            self.append_scope(dereferenced_variable)
        else:
            var =Variable(dereferenced_variable.name, dereferenced_variable.line_span, \
                                          dereferenced_variable.lex_span)
            dereferenced_variable.type = copy.deepcopy(self.get_type(var))
            self.remove_scope(dereferenced_variable)
    def visit_number(self, number):
        pass
    def visit_boolean(self, boolean):
        pass
    def visit_command_block(self, command):
        while command!=None:
            command.accept(self)
            command = command.get_next_command()
    def append_scope(self, variable):
        variable.name = self.function_scope + variable.name
    def remove_scope(self, variable):
        variable.name = variable.name[len(self.function_scope):]
