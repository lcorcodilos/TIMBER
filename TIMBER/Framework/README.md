# Framework development

## Notes to developers

Adding C++ modules for use in TIMBER is relatively simple but the code makes several
assumptions about the structure of the module if you'd like to use it as a `TIMBER.Analyzer.Correction`.

A correction module should be built as a class so that the initializer can be used to book
objects like files, histograms, etc that we want to load before looping over the RDataFrame.
A class method should be written to perform the evaluation during the event loop. This function
should be named `eval` by default. However, there is support for other function names for building 
multiple methods within the class.

The output of `eval` should be a vector organized as `[nominal,up,down]` if the function
calculates a correction and uncertainty or `[up,down]` if only calculating an uncertainty.
The name of the file is used to determine which type of output to expect for template building.
An output of the first type should have a file name that end in `_SF.cc` or `_weight.cc` and outputs of
of the second type should have a file name that ends in `_uncert.cc`.

Outputting a vector of vectors is not currently supported. One might want to do this
if, for example, all jets in a vector need the same 
correction in which case a vector of `[nominal,up,down]` vectors could be calculated where the index of each 
`[nominal,up,down]` matches the index of the matching jet in the jet vector. While this would be 
useful, some development would be needed to determine how to handle the various output value with
the automated correction tools.

The arguments to the `eval` function can be the names of the branches that you'd like to 
evaluate if you know these ahead of time (for example, if there are specific NanoAOD branches that
are used every time).
TIMBER will use clang to read the argument names defined in the function and match them to
the branches available in the RDataFrame analyzed automatically so the user does not need to provide
the arguments (this is useful if your function needs many arguments that are laborious to write out
several times). If there are no matches to available branches, the user will have to
provide the arguments (for example, if the module is very general).

Finally, the use of the module should be well documented for manipulation by [Doxygen](http://www.doxygen.nl/manual/docblocks.html)
so that users can easily understand the input and output in the TIMBER documentation.