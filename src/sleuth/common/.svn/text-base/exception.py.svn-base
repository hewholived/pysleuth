import traceback


class NestedException(Exception):
    '''Allow exceptions to be nested.
    
    This class allows us to use a syntax similar to Python 3.1's:
    
        ...
        except Exception as e:
            raise Exception() from e 
        
    The above syntax allows a user to capture context for re-raised
    exceptions (which is the "right" way to handle exceptions). This
    class allows an exception to be re-raised as:
    
        ...
        except Exception as e:
            raise NestedException().from_exception(e)
            
    Currently it only maintains the formatted exception text.
    
    TODO: Keep nested exception traceback for improved debugging.  
    '''

    def __init__(self, *args, **kwargs):
        super(NestedException, self).__init__(*args, **kwargs)

        self.nested_exception = None
        self.nested_traceback = None

    def from_exception(self, nested_exception):
        self.nested_exception = nested_exception
        self.nested_traceback = traceback.format_exc()

        return self

    def __str__(self):
        if self.nested_exception:
            return '{0}\n\n{1}'.format(super(NestedException, self).__str__(),
                                       self.nested_exception)

        return super(NestedException, self).__str__()

    def format_with_traceback(self):
        if self.nested_exception:
            return '{0}\n\n{1}\n\n{2}'.format(super(NestedException, self).__str__(),
                                              self.nested_exception,
                                              self.nested_traceback)

        return super(NestedException, self).__str__()
class TypeException(NestedException):
    pass
