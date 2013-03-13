import unittest
from sleuth.lingo.parser import LingoParser
from sleuth.lingo.typecheck import TypeCheck
from sleuth.lingo.types import *
from sleuth.common.exception import TypeException

'''
    Test the unification type checker. For each case
    includes tests to check that all types are inferred
    correctly, and tests to ensure that exceptions are
    thrown when the types are incorrect.
'''
class TestTypeCheck(unittest.TestCase):
    def setUp(self):
        self.parser = LingoParser()
        self.typecheck = TypeCheck(False)
    def get_type(self, var):
        return self.typecheck.rename.get_type(self.typecheck.rename.find(self.typecheck.variables[var]))    
    def testSkip1(self):
        program_text = '''
            skip;
            a := 1;
            skip
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),Primitive))
        self.assertTrue(self.get_type('a').value == "INTEGER")
        self.typecheck.visit_program(program)
    def testWhile1(self):
        program_text = '''
            while(a) do{
                b := 1
            };
            c := 1;
            c:= 2
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),Primitive))
        self.assertTrue(isinstance(self.get_type('b'),Primitive))
        self.assertTrue(self.get_type('a').value == "BOOLEAN")
        self.assertTrue(self.get_type('b').value == "INTEGER")
    def testWhile2(self):
        program_text = '''
            while(a < b) do{
                b := 1
            };
            c := 1;
            c:= 2
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),Primitive))
        self.assertTrue(isinstance(self.get_type('b'),Primitive))
        self.assertTrue(self.get_type('a').value == "INTEGER")
        self.assertTrue(self.get_type('b').value == "INTEGER")
    def testWhile3(self):
        program_text = '''
            while(a < b) do{
                b := true
            };
            c := 1;
            c:= 2
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testWhile4(self):
        program_text = '''
            a := 1;
            while(a) do{
                b := true
            };
            c := 1;
            c:= 2
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testIf1(self):
        program_text = '''
            if(a) then{
                b := 1
            }else { b:=2 };
            c := 1;
            c:= 2
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),Primitive))
        self.assertTrue(isinstance(self.get_type('b'),Primitive))
        self.assertTrue(self.get_type('a').value == "BOOLEAN")
        self.assertTrue(self.get_type('b').value == "INTEGER")
    def testIf2(self):
        program_text = '''
            if(a < b) then{
                b := 1
            }else { b:=2 };
            c := 1;
            c:= 2
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),Primitive))
        self.assertTrue(isinstance(self.get_type('b'),Primitive))
        self.assertTrue(self.get_type('a').value == "INTEGER")
        self.assertTrue(self.get_type('b').value == "INTEGER")
    def testIf3(self):
        program_text = '''
            if(a < b) then{
                b := true
            }else { b:=false };
            c := 1;
            c:= 2
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testIf4(self):
        program_text = '''
            a := 1;
            if(a) then{
                b := true
            }else { b:=false };
            c := 1;
            c:= 2
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testCannotDetermine1(self):
        program_text = '''
            def foo = fun(a,b){ return a }
             a := 1;
             b := 1
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testCannotDetermine2(self):
        program_text = '''
            input x;
             a := 1;
             b := 1
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testCannotDetermine3(self):
        program_text = '''
             a := d;
             b := 1
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testFunctionUnification1(self):
        program_text = '''
            def foo = fun(a,b){ return a }
            def bar = fun(a,b){ return b }
            a := 1;
            b := 2;
            a := foo(a,b);
            c := ref foo;
            c := ref bar
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('foo_a'),Primitive))
        self.assertTrue(isinstance(self.get_type('foo_b'),Primitive))
        self.assertTrue(isinstance(self.get_type('bar_a'),Primitive))
        self.assertTrue(isinstance(self.get_type('bar_b'),Primitive))
        self.assertTrue(self.get_type('foo_a').value == "INTEGER")
        self.assertTrue(self.get_type('foo_b').value == "INTEGER")
        self.assertTrue(self.get_type('bar_a').value == "INTEGER")
        self.assertTrue(self.get_type('bar_b').value == "INTEGER")
    def testFunctionUnification2(self):
        program_text = '''
            def foo = fun(a,b){ c := a + b; return c }
            def bar = fun(a,b){ c := a || b; return c }
            a := 1;
            b := 2;
            a := foo(a,b);
            c := ref foo;
            c := ref bar
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testRefUnification1(self):
        program_text = '''
            a := 1;
            b := ref a;
            b := ref c
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),Primitive))
        self.assertTrue(isinstance(self.get_type('c'),Primitive))
        self.assertTrue(isinstance(self.get_type('b'),Reference))
        self.assertTrue(isinstance(self.get_type('b').value,Primitive))
        self.assertTrue(self.get_type('a').value == "INTEGER")
        self.assertTrue(self.get_type('c').value == "INTEGER")
        self.assertTrue(self.get_type('b').value.value == "INTEGER")
    def testRefUnification2(self):
        program_text = '''
             b := 1;
             c := true;
             a := ref b;
             a := ref c
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testCyclicTypes1(self):
        program_text = '''
             a := ref b;
             b := ref a
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testCyclicTypes2(self):
        program_text = '''
             a := ref b;
             b := 1;
             c := 1;
             a := ref d;
             a := ref c;
             d := ref a
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testCyclicTypes3(self):
        program_text = '''
        def foo = fun(foo1){ a := ref foo1; b := !foo1(a); return a }
        a := ref foo;
        b := 1
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testRefFunction1(self):
        program_text = '''
            def foo = fun(a,b,c){ d := !c(a,b); a := a + b; return a }
            def help = fun(a,b){ c := a < b; return c }
            a := 1;
            b := 2;
            c := ref help;
            a := foo(a, b, c)
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('foo_a'),Primitive))
        self.assertTrue(isinstance(self.get_type('foo_b'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('foo_d'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('help_a'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('help_b'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('help_c'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('foo'),
                              Function))
        self.assertTrue(isinstance(self.get_type('help'),
                              Function))
        self.assertTrue(isinstance(self.get_type('foo_c'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('foo_c').value,
                              Function))
        self.assertTrue(self.get_type('foo_a').value == "INTEGER")
        self.assertTrue(self.get_type('foo_b').value == "INTEGER")
    def testRefFunction2(self):
        program_text = '''
            def foo = fun(a,b,c){ d := !c(a,b); a := a + b; return a }
            def help = fun(a,b){ c := a || b; return c }
            a := 1;
            b := 2;
            c := ref help;
            a := foo(a, b, c)
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testRefFunction3(self):
        program_text = '''
            def foo = fun(a,b,c){ d := !c(a); a := a + b; return a }
            def help = fun(a,b){ c := a < b; return c }
            a := 1;
            b := 2;
            c := ref help;
            a := foo(a, b, c)
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testRefFunction4(self):
        program_text = '''
            def foo = fun(a,b,c){ d:= 1; d := !c(a,b); a := a + b; return a }
            def help = fun(a,b){ c := a < b; return c }
            a := 1;
            b := 2;
            c := ref help;
            a := foo(a, b, c)
        '''.strip()

        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testFunctionSignature1(self):
        program_text = '''
            def foo = fun(a,b){ a := a + b; return a }
            a := 1;
            b := 2;
            a := foo(a,b)
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('foo_a'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('foo_b'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('foo'),
                              Function))
        self.assertTrue(self.get_type('foo_a').value == "INTEGER")
        self.assertTrue(self.get_type('foo_b').value == "INTEGER")
        for sig in self.get_type('foo').signature:
            self.assertTrue(sig.value == "INTEGER")       
    def testFunctionSignature2(self):
        program_text = '''
            def foo = fun(a,b){ a := a + b; return a }
            a := 1;
            b := true;
            a := foo(a,b)
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testFunctionSignature3(self):
        program_text = '''
            def foo = fun(a,b){ a := a + b; return a }
            a := 1;
            b := ref foo;
            a := foo(a,b)
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testDereference1(self):
        program_text = '''
            a := 1;
            x :=  ref a;
            a := !x
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('x'),
                              Reference))
        self.assertTrue(self.get_type('a').value == "INTEGER")
        self.assertTrue(self.get_type('x').value.value == "INTEGER")

    def testDereference2(self):
        program_text = '''
            a := 1;
            x :=  ref a;
            y :=  ref x;
            x := !y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('x'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('y'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('x').value,
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y').value,
                              Reference))
        self.assertTrue(isinstance(self.get_type('y').value.value,
                              Primitive))
        self.assertTrue(self.get_type('a').value == "INTEGER")
        self.assertTrue(self.get_type('x').value.value == "INTEGER")
        self.assertTrue(self.get_type('y').value.value.value == "INTEGER")
    
    def testDereference3(self):
        program_text = '''
            a := 1;
            x :=  ref a;
            y :=  ref x;
            y := !x
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testDereference4(self):
        program_text = '''
            a := 1;
            b := !a
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testReference1(self):
        program_text = '''
            a := 1;
            b := 2;
            x :=  ref a;
            y :=  ref b;
            z := !x / !y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('b'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('x'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('y'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('x').value,
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y').value,
                              Primitive))
        self.assertTrue(self.get_type('a').value == "INTEGER")
        self.assertTrue(self.get_type('b').value == "INTEGER")
        self.assertTrue(self.get_type('y').value.value == "INTEGER")
        self.assertTrue(self.get_type('x').value.value == "INTEGER")
        self.assertTrue(isinstance(self.get_type('z'),
                              Primitive))
        self.assertTrue(self.get_type('z').value == "INTEGER")        

    def testReference2(self):
        program_text = '''
            a := 1;
            x :=  ref a;
            y :=  ref x
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('a'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('x'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('y'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('x').value,
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y').value,
                              Reference))
        self.assertTrue(isinstance(self.get_type('y').value.value,
                              Primitive))
        self.assertTrue(self.get_type('a').value == "INTEGER")
        self.assertTrue(self.get_type('x').value.value == "INTEGER")
        self.assertTrue(self.get_type('y').value.value.value == "INTEGER")
    
    def testReference3(self):
        program_text = '''
            a := 1;
            x :=  ref a;
            y :=  ref x;
            a := !y
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
    def testReference4(self):
        program_text = '''
            a := 1;
            b := true;
            x :=  ref a;
            b := !x
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
                
    def testNew1(self):
        program_text = '''
            x :=  new integer;
            y :=  new integer;
            z := !x * !y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('x'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('y'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('x').value,
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y').value,
                              Primitive))
        self.assertTrue(self.get_type('y').value.value == "INTEGER")
        self.assertTrue(self.get_type('x').value.value == "INTEGER")
        self.assertTrue(isinstance(self.get_type('z'),
                              Primitive))
        self.assertTrue(self.get_type('z').value == "INTEGER")        
    def testNew2(self):
        program_text = '''
            x :=  new boolean;
            y :=  new boolean;
            z := !x || !y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('x'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('y'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('x').value,
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y').value,
                              Primitive))
        self.assertTrue(self.get_type('y').value.value == "BOOLEAN")
        self.assertTrue(self.get_type('x').value.value == "BOOLEAN")
        self.assertTrue(isinstance(self.get_type('z'),
                              Primitive))
        self.assertTrue(self.get_type('z').value == "BOOLEAN")     
    def testNew3(self):
        program_text = '''
            x :=  new ref boolean;
            y :=  !x;
            z := !y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('x'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('y'),
                              Reference))
        self.assertTrue(isinstance(self.get_type('z'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('x').value,
                              Reference))
        self.assertTrue(isinstance(self.get_type('x').value.value,
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y').value,
                              Primitive))
        self.assertTrue(self.get_type('y').value.value == "BOOLEAN")
        self.assertTrue(self.get_type('x').value.value.value == "BOOLEAN")
        self.assertTrue(self.get_type('z').value == "BOOLEAN")     
    def testNew4(self):
        program_text = '''
            x := new ref integer;
            z := !x + 1
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
        
    def testOperatorLessEqual1(self):
        program_text = '''
            x := 1;
            y := 2;
            z := x <= y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('x'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y'),
                              Primitive))
        self.assertTrue(self.get_type('y').value == "INTEGER")
        self.assertTrue(self.get_type('x').value == "INTEGER")
        self.assertTrue(isinstance(self.get_type('z'),
                              Primitive))
        self.assertTrue(self.get_type('z').value == "BOOLEAN")
    def testOperatorLessEqual2(self):
        program_text = '''
            x := 1;
            y := true;
            z := x <= y
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
        
    def testOperatorLess1(self):
        program_text = '''
            x := 1;
            y := 2;
            z := x < y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('x'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y'),
                              Primitive))
        self.assertTrue(self.get_type('y').value == "INTEGER")
        self.assertTrue(self.get_type('x').value == "INTEGER")
        self.assertTrue(isinstance(self.get_type('z'),
                              Primitive))
        self.assertTrue(self.get_type('z').value == "BOOLEAN")
    def testOperatorLess2(self):
        program_text = '''
            x := false;
            y := 2;
            z := x < y
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
        
    def testOperatorDivide1(self):
        program_text = '''
            x := 1;
            y := 2;
            x := x / y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('x'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y'),
                              Primitive))
        self.assertTrue(self.get_type('y').value == "INTEGER")
        self.assertTrue(self.get_type('x').value == "INTEGER")
    
    def testOperatorDivide2(self):
        program_text = '''
            x := false;
            y := true;
            z := x / y
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
        
    def testOperatorTimes1(self):
        program_text = '''
            x := 1;
            y := 2;
            x := x * y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('x'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y'),
                              Primitive))
        self.assertTrue(self.get_type('y').value == "INTEGER")
        self.assertTrue(self.get_type('x').value == "INTEGER")        

    def testOperatorTimes2(self):
        program_text = '''
            x := 3;
            y := 1;
            z := x * y;
            z := false
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
        
        
    def testOperatorMinus1(self):
        program_text = '''
            x := 1;
            y := 2;
            x := x - y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('x'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y'),
                              Primitive))
        self.assertTrue(self.get_type('y').value == "INTEGER")
        self.assertTrue(self.get_type('x').value == "INTEGER")
    def testOperatorMinus2(self):
        program_text = '''
            x := true;
            y := 3;
            z := x - y
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
          
    def testOperatorPlus1(self):
        program_text = '''
            x := 1;
            y := 2;
            x := x + y
        '''.strip()

        program = self.parser.parse(program_text)
        self.typecheck.visit_program(program)
        self.assertTrue(isinstance(self.get_type('x'),
                              Primitive))
        self.assertTrue(isinstance(self.get_type('y'),
                              Primitive))
        self.assertTrue(self.get_type('y').value == "INTEGER")
        self.assertTrue(self.get_type('x').value == "INTEGER")
    def testOperatorPlus2(self):
        program_text = '''
            x := false;
            y := true;
            z := x + y
        '''.strip()
        program = self.parser.parse(program_text)
        self.assertRaises(TypeException, self.typecheck.visit_program, program)
        
if __name__=='__main__':
    unittest.main()