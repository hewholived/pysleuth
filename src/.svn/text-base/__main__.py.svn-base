from sleuth.third_party import argparse
from sleuth.lingo.components import Variable
import datetime
import logging
import os.path
import sys


def add_to_path():
    this_dir = os.path.dirname(__name__)
    if this_dir not in sys.path:
        sys.path.append(this_dir)

def parse_args():
    parser = argparse.ArgumentParser(
        prog = 'PySleuth',
    )

    analysis_group = parser.add_argument_group(title = 'Analysis Parameters')

    analysis_group.add_argument('-s', '--source',
                                metavar = 'PATH',
                                help = 'The path to the Lingo source file to analyze.')

    analysis_group.add_argument('-a', '--analysis',
                                metavar = 'PATH',
                                help = 'The path to the PySleuth analysis module to use.')

    analysis_group.add_argument('-n', '--nogui',
                                action = 'store_false',
                                dest = 'gui_enabled',
                                help = 'Disable the GUI. (Does not require PyQt.)')

    analysis_group.add_argument('-ntc', '--notypecheck',
                                action = 'store_false',
                                dest = 'typecheck_enabled',
                                help = 'Disable type checking and type inference pass.')
    analysis_group.add_argument('--annotate_types', '--at',
                                action = 'store_true',
                                dest = 'annotate_types_enabled',
                                help = 'Proceed to GUI regardless of type checking to display known types.')


    utility_group = parser.add_argument_group(title = 'Utility Parameters')

    utility_group.add_argument('--dot',
                               dest = 'dot_executable',
                               metavar = 'PATH',
                               help = 'The path to the "dot" executable. (Default: "dot")',
                               default = 'dot')

    utility_group.add_argument('--loglevel',
                               metavar = '[DEBUG|INFO|WARNING|ERROR|CRITICAL]',
                               help = 'The level for logging operations. (Default: "INFO")',
                               default = 'INFO')

    utility_group.add_argument('--font',
                               dest = 'gui_font',
                               metavar = 'FONT_NAME',
                               help = 'Sets the font for the GUI. Defaults to "STIXGeneral"',
                               default = 'STIXGeneral')

    args = parser.parse_args()
    return args

def main():
    exit_code = -1

    try:
        add_to_path()

        arguments = parse_args()
        '''
            Annotating the AST with the type information, thus change the __repr__ function
            to include type information.
        '''
        if arguments.annotate_types_enabled:
            def annoted_ref(self):
                if self.type != None:
                    return '{0}<{1}>'.format(self.name, self.type)
                else:
                    return '{0}<Unknown>'.format(self.name)
            Variable.__repr__ = annoted_ref
            arguments.gui_enabled = True
            
        level = getattr(logging, arguments.loglevel)
        logging.basicConfig(stream = sys.stdout, level = level)

        logger = logging.getLogger(__name__)
        logger.info('\n\n{0}\nStarting PySleuth!\n'.format(datetime.datetime.now()))
        logger.debug('Arguments: {0}'.format(sys.argv))
        logger.debug('PYTHONPATH=\n  {0}'.format('\n  '.join(sys.path)))

        # Hide some noisy trace
        try:
            from PyQt4 import uic
            uic.uiparser.logger.setLevel(logging.INFO)
            uic.properties.logger.setLevel(logging.INFO)
        except ImportError:
            pass
        logging.getLogger('sleuth.tracks.cfg').setLevel(logging.INFO)
        logging.getLogger('sleuth.evidence.autoLayout').setLevel(logging.INFO)


        # Create the application
        from sleuth.evidence.console.application import Application #@UnusedImport

        if arguments.gui_enabled:
            from sleuth.evidence.gui.application import Application #@Reimport

        app = Application(arguments)
        exit_code = app.execute_analysis()


    finally:
        logging.shutdown()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
