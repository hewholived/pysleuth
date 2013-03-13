from sleuth.common.exception import NestedException
from sleuth.common.set import Set
from tempfile import NamedTemporaryFile, SpooledTemporaryFile
import logging
import subprocess

logger = logging.getLogger(__name__)

class GraphvizSVGRenderer(object):
    '''Call out to Graphviz to construct "svg" graphs.'''

    def __init__(self, dot_executable_path = 'dot'):
        '''Setup the GraphvizRenderer.
        
        By default, this object assumes that the 'dot' executable
        is on the path. 
        '''
        self.dot_executable_path = dot_executable_path

    def create_graph(self, edge_pairs):
        with self._create_dot_file(edge_pairs) as dot_file:
            svg_graph_output = self._create_svg_graph(dot_file)

        with NamedTemporaryFile('wb', suffix = '.svg', delete = False) as graph_file:
            graph_file.write(svg_graph_output)
            return graph_file.name

    def _create_dot_file(self, edge_pairs):
        '''Create a file suitable for use with dot.
        
        @param edge_pairs: A list of tuples of edges to be rendered.
        @return: A file object containing contents to be rendered by dot.
        '''
        file = SpooledTemporaryFile(mode = 'w')

        file.write('digraph G {\n')

        unique_nodes = Set()

        def add_node(node):
            if node not in unique_nodes:
                attributes = '[id={id},label="{label}"]' \
                .format(id = node.get_identifier(),
                        label = repr(node))

                file.write('{id} {attrs}\n' \
                    .format(id = node.get_identifier(),
                            attrs = attributes))

        for src, dst in edge_pairs:
            if dst is None:
                add_node(src)
                continue

            add_node(src)
            add_node(dst)

            unique_nodes.add(src)
            unique_nodes.add(dst)

            file.write('{src} -> {dst} {attr}\n' \
                .format(src = src.get_identifier(),
                        dst = dst.get_identifier(),
                        attr = ''))
        file.write('}\n')

        file.seek(0)
        return file

    def _create_svg_graph(self, dot_file):
        '''Call out to dot to create a svg graph.
        
        Returns a string with the contents of the rendered graph.
        '''

        args = [
            self.dot_executable_path,
            '-Tsvg',
        ]

        try:
            with NamedTemporaryFile('w') as buffer:
                p = subprocess.Popen(args, stdin = dot_file, stdout = subprocess.PIPE)
                stdoutdata, _stderrdata = p.communicate()

                if p.returncode != 0:
                    raise subprocess.CalledProcessError(p.returncode, ' '.join(args))

                return stdoutdata

        except Exception as e:
            raise NestedException('Failed to execute "{0}": {1}'.format(' '.join(args), e)).from_exception(e)
