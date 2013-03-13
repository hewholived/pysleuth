from PyQt4 import uic
from sleuth import RESOURCES_DIR
import logging
import os


logger = logging.getLogger(__name__)

class AutoLayoutMixin(object):
    # TODO: LAYOUT_FILE_DIR needs to be configurable (or at least made relative to this file)
    LAYOUT_FILE_DIR = os.path.join(RESOURCES_DIR, 'layouts')
    LAYOUT_FILE_NAME = None

    def __init__(self, *args, **kwargs):
        super(AutoLayoutMixin, self).__init__(*args, **kwargs)

        layoutFilePath = os.path.join(self.LAYOUT_FILE_DIR, self.LAYOUT_FILE_NAME)
        logger.debug('AutoLayoutMixin object created. Layout file: {0}'.format(layoutFilePath))

    def loadUi(self):
        '''Load the ui file for this widget.

        Most of this logic would normally be located in an __init__ method, but
        PyQt4 objects don't seem to call super() properly, which prevents __init__
        from being called. To simplify the use of the mixin, the appropriate logic
        is simply buried in this method instead.
        '''
        if self.LAYOUT_FILE_NAME is None:
            raise AssertionError('The %s class must define a LAYOUT_FILE_NAME class member.' % self.__class__.__name__)

        layoutFilePath = os.path.join(self.LAYOUT_FILE_DIR, self.LAYOUT_FILE_NAME)
        logger.debug('Loading ui file: {0}'.format(layoutFilePath))

        if not os.path.exists(layoutFilePath):
            raise AssertionError('Could not find the layout file for %s: %s' % (self.__class__.__name__,
                                                                                layoutFilePath))

        symbolsBeforeLoad = set(dir(self))
        loaded = uic.loadUi(layoutFilePath, self)
        symbolsAfterLoad = set(dir(self))

        newSymbols = symbolsAfterLoad - symbolsBeforeLoad
        message = ', '.join(i for i in newSymbols)

        logger.debug('Loading added symbols: %s' % message)

        return loaded
