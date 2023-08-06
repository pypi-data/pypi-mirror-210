if hasattr(__builtins__, '__IPYTHON__'):
    # running in ipython, therefore we can use the included pretty module
    from pretty import *
else:
    # Running in standard python, therefore we can use this module
    from .pretty_python import *

