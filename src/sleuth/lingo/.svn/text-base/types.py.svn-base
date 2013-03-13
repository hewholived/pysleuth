'''
Type Objects:

Primitive: Either a boolean, or an integer, with values "BOOLEAN" and "INTEGER" respectively.

Reference: Reference to some sort of type, value holds either primitive, function, reference, etc.

Function: Function type, signature is a list, last argument is return type, the remaining are parameters. 

__eq__ and __neq__ are defined to recursively compare two types.


Type: primitive 
|     ref Type 
|     Function (Type+) 


+ denotes one or more types
'''
class Type(object):
    def __str__(self):
        return self.__repr__()
class Unknown(Type):
    def __str__(self):
        return "Unknown"
class Primitive(Type):
    def __init__(self, value, line_number=0):
        self.value = value
        self.line_number = line_number
        self.rank = 0
        self.parent = self
    def __eq__(self,other):
        if isinstance(other, Primitive):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
    def __repr__(self):
        return self.value.lower()
class Reference(Type):
    def __init__(self, value, line_number):
        self.value = value
        self.line_number =line_number
        self.rank = 0
        self.parent = self
    def __eq__(self, other):
        if isinstance(other, Reference):
            return self.value == other.value
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
    def __repr__(self):
        return "ref (%s)" % self.value
class Function(Type):
    def __init__(self, signature, line_number):
        self.signature = signature
        self.line_number = line_number
        self.rank = 0
        self.parent = self
    def __eq__(self, other):
        if isinstance(other, Function):
            if len(self.signature) == len(other.signature):
                for index in range(len(self.signature)):
                    if self.signature[index] != other.signature[index]:
                        return False
                return True
            else:
                return False
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
    '''String with unicode arrows between each entry in the signature'''
    def __repr__(self):
        signatureString = ""
        for i in range(len(self.signature)):
            argument = u"%s\u2192" % self.signature[i]
            signatureString = signatureString + argument
        return signatureString[0:len(signatureString)-1]
