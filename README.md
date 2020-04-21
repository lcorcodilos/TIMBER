# HAMMER {#mainpage}
[Full Documentation](http://hammer.lucascorcodilos.com/)

HAMMER is an easy-to-use and fast python analysis framework used to quickly process CMS data sets. 
Default arguments assume the use of the NanoAOD format but any ROOT TTree can be processed.

## The RDataFrame Backbone
HAMMER's speed comes from the use of 
[ROOT's RDataFrame](https://root.cern/doc/master/classROOT_1_1RDataFrame.html). 
RDataFrame offers "multi-threading and other low-level optimisations" which make analysis level
processing faster and more efficient than traditional python `for` loops. However,
RDataFrame derives its speed from its C++ back-end and while an RDataFrame object can be instantiated
and manipulated in python, any actions on it are written in C++ (even if you're using python).

## No more `for` loops
Using RDataFrame means a fundamental re-thinking of how we treat a block of data or simulation.
Instead of looping over the events or entries of a TTree (or other data format), the TTree is
converted into a table called the "data frame". A user then books a number of "lazy" actions on 
the data frame such as filtering out events or calculating new values. These actions aren't performed
though until the data frame needs to be evaluated (ex. you ask to plot a histogram from it). 

In this way, there are no more `for` loops and instead just actions on the data frame table that 
transform it into a final table of values that the analyzer cares about. 


## Anatomy of a data frame
Each row of the table is a separate event and each
column is a different variable in the event (a branch in TTree terms). Columns can be single values or
vectors (specifically [ROOT::VecOps:RVec](https://root.cern.ch/doc/v614/classROOT_1_1VecOps_1_1RVec.html)).

Since each row is an event, vectors are necessary for the case of multiple of the same physics object in 
an event - for example, multiple electrons. 

**NOTE** NanoAOD orders these vectors in \f$p_T\f$ of the objects. So if you'd like the \f$\eta\f$ of the leading electron, it is stored as `Electron_eta[0]`

This can make accessing values tricky! For example, if there's one electron in an event and the analyzer asks for `Electron_eta[1]`, the computer will return a seg fault. These are the types of problems that HAMMER attempts to solve (even if it's just by users sharing their experiences).

## Happy Analyzers
HAMMER is meant to keep both the processing fast via RDataFrame and the analyzer fast via python scripting.

To maintain python's appeal in HEP as a quick scripting language, HAMMER handles many of the 
intricacies of interfacing with RDataFrame so the analyzer can focus on writing their analysis.

HAMMER automates opening one or many ROOT files, calculating the number of events generated 
(provided the ROOT files are NanoAOD simulation), loading in C++ scripts for use while looping over
the data frame, and grouping actions for easy manipulation.

In addition, HAMMER treats each step in the RDataFrame processing as a "node" and keeps track of these nodes. Each action (or group of actions) performed on a node produces another node and nodes store information about their parents or children. This makes it possible to write tools like `Nminus1()` which takes as input a node and a group of cuts to apply and returns N new nodes, each with every cut but one applied.

Finally, the RDataFrame for each node is always kept easily accessible so that any of the [native RDataFrame tools](https://root.cern/doc/master/classROOT_1_1RDataFrame.html) are at the user's fingertips.


## Sharing is caring
HAMMER includes a repository of common algorithms used frequently in CMS 
which access scale factors, calculate pileup weights, and more. These are all written 
in C++ for use in `Cut` and `Define` arguments and are provided so that users have a common tool box to share. 
Additionally, the AnalysisModules folder welcomes additions of custom C++ modules on a 
per-analysis basis so that the code can be properly archived for future reference and for sharing
with other analyzers.

