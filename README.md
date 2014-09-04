<h1> Homer </h1>

Homer is a program to visualize computer simulations data (typically
Molecular Dynamics data) in an easy manner. It is developed to replace
Yaplot (https://github.com/vitroid/Yaplot), mainly because Yaplot's
code depends on now obsolete libraries that makes it hard to install
on a recent machine. Homer is thus so far a clone of Yaplot, based on
the same idea of a simple set of commands interpreted to render an
intentionally basic representation of 3D data.

Homer is still in development stage, so some bugs or early design
flaws are to be expected :) Also, so far not all of Yaplot features are available.

<h2> Installation </h2>

Homer needs a Python 2.7 interpreter and the numpy, pandas and PySide
packages.

You can run Homer as follows:

```
python path_to_homer/src/homer.py your_command_file
```

<h2> Data format </h2>

Same as Yaplot's data format, see https://github.com/vitroid/Yaplot.
