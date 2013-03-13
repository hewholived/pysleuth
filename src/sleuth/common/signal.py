from collections import Callable

class Signal(object):
    '''Object that dispatches events to registered listeners.'''

    def __init__(self, *signal_parameters):
        self.sinks = []
        self._enabled = True

        self._signal_parameters = signal_parameters

    def fire(self, source, *args, **kwargs):
        assert self._enabled

        expected_parameters = self._signal_parameters[:]

        for parameter in kwargs:
            if parameter not in expected_parameters:
                raise Exception('Unexpected parameter "{0}" for {1}.fire().'.format(parameter, self.__class__.__name__))

        num_parameters_expected = len(expected_parameters)
        num_parameters_received = len(args) + len(kwargs)

        if num_parameters_expected != num_parameters_received:
            raise Exception('Incorrect number of parameters to {0}.fire(). Expected {1} but got {2}.'.format(self.__class__.__name__,
                                                                                                             num_parameters_expected,
                                                                                                             num_parameters_received))


        # Make a copy of the sink list before iterating over it
        # This is a short-sighted solution to a problem that can occur when
        # the called sink unregisters itself from this event. Without copying
        # the list first, this can cause other sinks in the list to be skipped.   
        sinksCopy = list(self.sinks)
        for sink in sinksCopy:
            sink(source, *args, **kwargs)

    def register(self, sink):
        assert self._enabled

        assert isinstance(sink, Callable), sink
        self.sinks.append(sink)

    def unregister(self, sink):
        assert self._enabled

        self.sinks.remove(sink)

    def __add__(self, sink):
        self.register(sink)
        return self

    def __sub__(self, sink):
        self.unregister(sink)
        return self

    #
    # Prevent this object from attempting to pickle itself!
    #
    def __getstate__(self):
        return {'_enabled' : False}

    def __setstate__(self, namespace):
        self._enabled = False
