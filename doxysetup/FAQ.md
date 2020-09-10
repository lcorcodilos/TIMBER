# Frequently Asked Questions

## I get an error that looks like `clang.cindex.LibclangError: libclang.so: cannot open shared object file`

Two things could have happened. The first is that you do not have clang installed for python. You can run `which clang` to check. If it does not exist, please run `python setup.py install` if you have not or `pip3 install clang`. 

The second is that `libclang.so` is named something else in your operating system. The real location and/or name will depend on the system but for Ubuntu 18.04 for example, the needed library is `/usr/lib/x86_64-linux-gnu/libclang-6.0.so.1`.

The issue can be solved simply by creating a symbolic link in the folder where the true shared object file exists (via `sudo ln -s libclang.so.1 libclang.so`)