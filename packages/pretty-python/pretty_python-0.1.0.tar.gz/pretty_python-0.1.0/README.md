# pretty_python

Standard Python Shim for IPython pretty library

See [lib.pretty Docs](https://ipython.readthedocs.io/en/stable/api/generated/IPython.lib.pretty.html#) for full api.

Only differnce to use this is to import as follows:
```
from pretty_python import pretty, pprint

d = dict(Foo=[1,2,3], Bar={'a':1, 'b':2, 'c':3})

print(f"my dict: {pretty(d)}")

# -or-

pprint(d)
```

If running within IPython / Jupyter Notebook, it will load the builtin pretty library, otherwise it will load this fork which removes IPython dependency