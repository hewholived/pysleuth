from mockito.mock_registry import mock_registry
import logging
import sys
import unittest

class TestCase(unittest.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()

    def tearDown(self):
        mock_registry.unstub_all()
        super(TestCase, self).tearDown()

    def withLogging(self,
                    stream = None,
                    level = logging.DEBUG):
        use_stream = stream or sys.stdout
        use_stream.write('\n')
        logging.basicConfig(stream = use_stream,
                             level = level)

    def assertIs(self, instance, expected_instance, msg = None):
        message_format = '{instance} is not {expected_instance}'
        self.assert_(instance is expected_instance,
                     msg or message_format.format(instance = instance,
                                                  expected_instance = expected_instance))

    def assertIn(self, item, iterable, msg = None):
        self.assert_(item in iterable,
                     msg = msg or '{0} is not in {1}'.format(item, iterable))

    def assertSameElements(self, left, right):
        self.assertEqual(len(left), len(right), 'left and right have different lengths: {0}, {1}'.format(len(left), len(right)))

        for index, (a, b) in enumerate(zip(left, right)):
            self.assertEqual(a, b, 'Items at position {0} are not equal: {1}, {2}'.format(index, a, b))


    def assertIsInstance(self, instance, expected_type, msg = None):
        message_format = '"{instance}" with type {instance_type} is not an instance of {expected_type}'

        self.assert_(isinstance(instance, expected_type),
                     msg or message_format.format(instance = instance,
                                                  instance_type = type(instance),
                                                  expected_type = expected_type))

    def assertHasattr(self, instance, attribute, msg = None):
        message_format = '{instance} has no attribute "{attribute}".'

        self.assert_(hasattr(instance, attribute),
                     msg or message_format.format(instance = instance,
                                                  attribute = attribute))
