PySleuth is an interactive tool that aids in understanding the behavior 
of static analyses written in Python. 

Original Author: Chris Phillips
Additional Maintainers: Kyle Dewey and Madhukar N Kedlaya

PySleuth was originally developed as part of a research effort at UCSB during
the Spring 2010 quarter.


== DEPENDENCIES == 

There is no installation of PySleuth itself -- for now it just gets run from 
the command line. However, there are some dependencies that need to be installed
in order to run PySleuth:

    - Python 2.6+
    - PyQt4 4.6+
    - Ply 3.2 or 3.3
    - Graphviz 2.26.x
    
    - mockito  0.2.0 (required only for running unit tests)
    
== ADDITIONAL DOCUMENTATION ==

Three additional documents are included with PySleuth in the docs directory:

    - InstallationAndOverview.rtf
        Describes detailed installation instructions and a brief overview
        of the PySleuth application.

    - ClientAnalysis.rtf
        Describes the process of developing a client analysis to be used
        by PySleuth to analyze a program written in Lingo.
        
    - DeveloperGuide.rtf
        Describes the overall development and maintenance layout of the 
        PySleuth source code as well as additional points where future
        enhancements may eventually be developed.
