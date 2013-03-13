import os

PACKAGE_BASE_DIR = os.path.dirname(__file__)
APPLICATION_ROOT_DIR = os.path.dirname(os.path.dirname(PACKAGE_BASE_DIR))

RESOURCES_DIR = os.path.join(APPLICATION_ROOT_DIR, 'resources')
