# Frequently Asked Questions

## I tried to use `PrintNodeTree()` but got an output file with extension `.dot`. How do I view it?
Short answer: Make sure `graphviz-dev` is installed (`sudo apt-get install graphviz-dev`) on
your machine. Then use `dot myfile.dot -T png -o myfilename.png` to convert to `png`. If you
get errors that `png` is not supported, consult Google to check what requirements are needed
for your system. Linux also has the `xdot` to view the files dynamically without generating
an image.

Long answer: The node tree is organized and drawn with a tool called `networkx` which builds and manipulates
the graph depending on your needs. There are various ways to draw this graph from `networkx` but all of the ones
that are preferred by TIMBER developers require `graphviz` (installed as `dot`). Unfortunately, the LXPLUS and LPC servers
do not have versions of `dot` installed with support for rendering modern image formats such as PNG. These systems can export
to `.dot` though and so this is what TIMBER supports generically. These files can be interpreted on a system where you
have the ability to install `graphviz-dev` (for Ubuntu, consult Google for other OSes).

Being able to view the .dot files is not a strict dependency of TIMBER so that TIMBER can work as smoothly
as possible for the most users.

## I get an error that looks like `clang.cindex.LibclangError: libclang.so: cannot open shared object file`

Two things could have happened. The first is that you do not have clang installed for python. You can run ``which clang`` to check. If it does not exist, please run ``python setup.py install`` if you have not or ``pip install clang`` (``pip3`` if using Python 3). 

The second is that `libclang.so` is named something else in your operating system. The real location and/or name will depend on the system but for Ubuntu 18.04 for example, the needed library is `/usr/lib/x86_64-linux-gnu/libclang-6.0.so.1`.

The issue can be solved simply by creating a symbolic link in the folder where the true shared object file exists (via ``sudo ln -s libclang.so.1 libclang.so``)