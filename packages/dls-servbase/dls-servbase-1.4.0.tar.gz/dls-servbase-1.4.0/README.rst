dls-servbase
=======================================================================

Simple HTTP service for database operations.

Intended advantages:

- agnostic of type of underlying sql client
- single-connection access to database
- hosts a few predefined common database schema

Installation
-----------------------------------------------------------------------
::

    pip install git+https://gitlab.diamond.ac.uk/kbp43231/dls-servbase.git 

    dls-servbase --version

Documentation
-----------------------------------------------------------------------

See https://www.cs.diamond.ac.uk/dls-servbase for more detailed documentation.

Building and viewing the documents locally::

    git clone git+https://gitlab.diamond.ac.uk/kbp43231/dls-servbase.git 
    cd dls-servbase
    virtualenv /scratch/$USER/venv/dls-servbase
    source /scratch/$USER/venv/dls-servbase/bin/activate 
    pip install -e .[dev]
    make -f .dls-servbase/Makefile validate_docs
    browse to file:///scratch/$USER/venvs/dls-servbase/build/html/index.html

Topics for further documentation:

- TODO list of improvements
- change log


..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

