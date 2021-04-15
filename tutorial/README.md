# CMS Tutorial on RDataFrame with TIMBER and NanoAOD

Welcome! This tutorial is being prepared for the CMS B2G Spring 2021 Workshop but
one may find it generally useful in standalone. The goal of this tutorial is to 
introduce you to the combination of Python+RDataFrame+NanoAOD+TIMBER.
If you are attending the tutorial "in person", you can use this document as a 
reference. Any additions are welcomed.

## Exercise 1 - Installation and Setup *(10 min)*
----------------------------
To start, lets setup an environment to work in and install TIMBER for use. The main
TIMBER documentation page has some instructions for installation. For this tutorial,
we will focus on setup inside of CMSSW so that there are no issues with
dependencies. We'll also be able to submit some condor jobs at some point.

### CMSSW
First, get a clean working directory on either CMSLPC or LXPLUS (or another
CMSSW-friendly computing resource). Then grab `CMSSW_11_1_4`.
```
cmsrel CMSSW_11_1_4
cd CMSSW_11_1_4/src
cmsenv
```
The choice of CMSSW version is based on the available ROOT versions.
Because RDataFrame is relatively new and actively developed,
it's not rare for features to be missing from relatively new
CMSSW versions.

Note that we've `cmsenv`'ed here to set all of the CMSSW environment variables.
We'll come back to this in a moment.

### Python virtual environment
Next, create a python virtual environment with
```
python -m virtualenv <name>
```
I use `timber-env` for my `<name>` but you can use whatever you'd like.

Note that the above command will set your environment to use the python version
pointed to by `python`. For `CMSSW_11_1_4`, this is Python 2.7.

Activate the environment with 
```
source timber-bin/bin/activate
```
Note that if you are not using bash, you should instead grab the `activate` script that is friendly to your shell.

A python virtualenv is a way to create an area to install python packages and
versions without disrupting the system install. They are good to use in general but
are necessary in this case because, in all likelihood, you are don't have permission
to modify the system python install.

When we activate the environment, we are overriding system variables that were set by `cmsenv`. This is good - the other way around would be bad (we don't want `cmsenv` to override the python path to our new environment).

### TIMBER
Clone TIMBER and checkout the tutorial branch
```
git clone https://github.com/lcorcodilos/TIMBER.git
cd TIMBER
git checkout tutorial
```
Run the setup/installation with
```
source setup.sh
```
This will begin a process that will take several minutes. Again if you're not using
bash, there is a csh equivalent.

While we wait, let's talk about the anatomy of TIMBER `analyzer` object which is
the main interface of TIMBER.

## Exercise 2 - Open a file and draw *(10 min)*
------------------------------
In this directory, you should find a `locations/` folder. Inside are some .txt
files prepared already with the locations of raw NanoAOD samples. The sets chosen
are based on our performing a dijet search with two tops where the benchmark signal
will be Z' -> ttbar. To avoid any conflicts with the actual analysis, we won't be
looking at any data - just MC simulation. 

For the sake of testing our scripts, I'll be using `locations/Zprime1500_18.txt`. Eventually we'll
submit tasks to condor to process everything together and we can get an idea of the
processing times in a real scenario.

Now we can actually do something!

Lets open a file, make a cut, define a new variable/column, and plot a histogram of
the new variable:
```python
from TIMBER.Analyzer import analyzer
a = analyzer('locations/Zprime1500_18.txt') # open file
a.Cut('myNFatJetCut', 'nFatJet>0') # Make a cut
a.Define('pt0','FatJet_pt[0]') # Define a variable
h = a.DataFrame.Histo1D('pt0') # Draw the variable (note we cannot draw 'FatJet_pt[0]')
h.Draw('histe') # Actions won't execute until here since it's the first time we're "measuring"
raw_input('') # Hold for input so we can wait for system to draw
```

Useful RDataFrame notes:
- The most basic RDataFrame manipulations are `Cut`s/`Filter`s and `Define`s.
- A "branch" in a TTree is a "column" in an RDataFrame
- Many of the columns/branches in the NanoAOD are vectors and with RDataFrame,
these are cast to the [`RVec`](https://root.cern/doc/master/classROOT_1_1VecOps_1_1RVec.html) type
   - The `RVec` is "std::vector"-like (for the C++ analogy) and "numpy array"-like (for the python analogy)
   and you can convert RVecs between these. 
- Applying an action returns a new RDataFrame (**not** modified in-place)
   - TIMBER is creating the object (`analyzer`) to modify things "in-place"
- We need the cut on the number of FatJets so we don't get a seg fault when we ask for
`FatJet_pt[0]` but there are no FatJets.
- It is not possible to give a vector entry as an argument to Histo1D (either as the variable
being drawn or the one used for per-event weights). This is why we define `pt0`.

## Exercise 3 - Adding to the selection and writing to a file *(15-20 min)*
-----------------------------
### Adding cuts
```python
from TIMBER.Analyzer import analyzer
a = analyzer('locations/Zprime2000_18.txt') # open file
a.Cut('numberFatJets','nFatJet>1')
a.Cut('pt','FatJet_pt[0] > 400 && FatJet_pt[1] > 400') # will seg fault if nFatJet<=1 !!
a.Cut('eta','abs(FatJet_eta[0]) < 2.4 && abs(FatJet_eta[1]) < 2.4')
a.Cut('oppositeHemis','hardware::DeltaPhi(FatJet_phi[0], FatJet_phi[1]) > M_PI/2')
a.Cut('DAK8','FatJet_deepTagMD_TvsQCD[0] > 0.9 && FatJet_deepTagMD_TvsQCD[1] > 0.9')
a.Define('FatJet_vects','hardware::TLvector(FatJet_pt, FatJet_eta, FatJet_phi, FatJet_msoftdrop)')
a.Define('mtt','hardware::InvariantMass({FatJet_vects[0], FatJet_vects[1]})')
h = a.DataFrame.Histo1D(('mtt','',30,1000,4000),'mtt')
h.Draw('histe')
raw_input('') # Hold for input so we can wait for system to draw
```
Note that we're starting to use TIMBER supplied C++. In this case, the
[`hardware` namespace](https://lucascorcodilos.com/TIMBER/namespacehardware.html).

### Add triggers
```python
trigDict = {
    "16": ['HLT_PFHT900','HLT_PFHT800','HLT_PFJet450'],
    "17": ['HLT_PFHT1050','HLT_PFJet500'],
    "18": ['HLT_PFHT1050','HLT_PFJet500']
}
a.Cut('trigger',a.GetTriggerString(trigDict['18']))
```
### Add flags/filters
```python
a.Cut('Flags',a.GetFlagString())
```

### Writing to a file
Histograms are saved to a TFile just as you normally would - everything here inherits from TH1.

If you'd like to save out to a TTree, you can use the [RDataFrame `Snapshot` method](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#a233b7723e498967f4340705d2c4db7f8)
directly or use the TIMBER proxy to the method via [`Node.Snapshot()`](https://lucascorcodilos.com/TIMBER/class_t_i_m_b_e_r_1_1_analyzer_1_1_node.html#ac9396d0acbc67a31bbae81c20944900c).
You can also snapshot the active Node of the `analyzer` via `analyzer.Snapshot()`.

The TIMBER version augements the interface in a few ways:
- Input of desired columns/branches to save can be a string or list of strings (all with regex matching). Can also provide "all".
- Direct option for the snapshot being lazy.
- Direct option for the option to open the desired file (ex. "RECREAT", "UPDATE", etc).

```python
a.Snapshot(['nFatJet','FatJet_.*'],'outputfile.root',
                'myFatJets',lazy=True,openOption='UPDATE')
```
Note that snapshotting a TTree in an existing file (via `UPDATE`) can be tricky and can
occassionally cause a segmentation fault.

Also note that a lazy snapshot will never execute if there is never another action to initiate
RDataFrame loop (ex. drawing or writing a histogram, printing the average value of a column, etc).

### Splitting the selection: Adding a control region
Many (if not all) analyses need control/measurement/validation regions which are
orthogonal to the signal selection but share some portion of the signal selection.
They can also share systematic uncertainties, etc but we'll cover that later.

In a standard event `for` loop, you could split your selection with a simple
`if else`. In RDataFrame (and other array-based tools), you have to 
fork your processing into two different versions of the array but with a 
shared history.
```
        Start
          |
     preselection
        /   \
      SR     CR
```

In vanilla RDataFrame, you just need to denote for yourself the RDataFrame with only
the preselection applied and then go back to that to apply the separate SR and CR
selections.
```python
rdf = RDataFrame(...)
rdf_presel = rdf.Filter(...)
rdf_SR = rdf_presel.Filter(...)
rdf_CR = rdf_presel.Filter(...)
```

Since the TIMBER `analyzer` has a carriage that tracks an active Node, you have
to keep a reference to the Node in a variable and then use it to move the carriage
back to that Node when you're ready. The TIMBER `Cut` and `Define` methods return
the new Node from the action so getting the reference is very simple.
```python
a = analyzer(...)
preselection_node = a.Cut('Preselection','...')
# First apply SR cuts
SR_node = a.Cut('SR','...')
# Reset to preselection
a.SetActiveNode(preselection_node)
CR_node = a.Cut('SR','...')
```

As an example, you could now loop over the `SR_node` and `CR_node` to plot.
```python
out_file = TFile.Open(...)
out_file.cd()
for n in [SR_node,CR_node]:
    h = n.DataFrame.Histo1D('var')
    h.Write()
out_file.Close()
```
There are various other ways to approach this of course. You could just handle
the histograms after each SR and CR cuts, write a function to do the histogram write
outs, use `HistGroup`s, etc.

For our example, we'll split our `DAK8` into two different cuts (taking
the second cut on the leading jet) and invert the cut on the leading jet
to define a control region.

## Exercise 4 - VecOps Namespace and Collection Manipulation *(15-20 min)*
------------------------------------------------------------
One incredibly useful tool that is slightly hidden behind the RDataFrame documentation
is the [VecOps namespace](https://root.cern/doc/master/namespaceROOT_1_1VecOps.html).
This namespace is a group of utilities to manipulate the `RVec`s that populate
many NanoAOD branches. There are some physics-specific tools (ex. `DeltaPhi`) and also
generic vector tools like `Map` and `Sort`. The basis of these functions makes
RVec very powerful and extends the functionality considerably - with manipulations
needed in HEP algorithms in mind!

This is not to say though that these are not confusing. When learning to think
in "arrays" instead of "loops", these algorithms may lead to even more confusion.
With that in mind, let's take a moment to think about this "loop" vs "arrays"
dichotomy before digging into the RVec and the namespace.

### Loops vs Arrays
Because a "traditional" `for` loop is explicitely written in code, it's very easy to
put yourself "in" the event. You write `for event in events:` and now you are manipulating
`event` - whatever that may be. Maybe the `event` is an object with all of the NanoAOD collections
nicely accessible. For example, 
```python
for event in events:
    ak8jets = event.FatJets
    leadJet = ak8jets[0]

    if leadJet.pt > 400:
        ...
        hist.Fill(leadJet.pt)
```
Great! Now in the `if` our thinking is that we're "in" an event with a leading AK8 jet with
at least 400 GeV in pt and it's clear our histogram will have a minimum of 400 GeV.
As we discussed earlier, we can add an `else` and we've inverted the selection... and so on.
The important part is that you are manipulating the data in a specific event and you are manipulating
them one-by-one.

What if you instead acted on all events as one big group? In fact, this is what happens
when we do a basic TTree cut for a draw command:
```
myTTree.Draw("var1","var2 > 5")
```
Here, we've said, "Draw `var1` but only when `var2` is greater than 5". Imagine
if you could have a cut command as the second argument that not only applied
many more cuts but was also able to define new variables to cut on. For example,
say you defined Lorentz vectors so that you could make a cut on a quantity 
from a sum of vectors?

That's the "arrays" method of thinking with no explicit `for` loop. You provide a list
of instructions to manipulate what is available by the time you want to 
draw your histogram (or whatever write-out you are performing).

Not so crazy, right? Well we can still do something that is quite powerful
but maybe not so clear on first glance.
A good example of `RVec` (without even diving into VecOps):
```python
rdf2 = rdf1.Define('GoodFatJet_pt','FatJet_pt[FatJet_pt > 400 && abs(FatJet_eta) < 2.4]')
```
Now `GoodFatJet_pt` is an RVec (which will eventually be calculated once the loop is initiated)
that holds only the FatJet pt values where `FatJet_pt > 400` and `abs(FatJet_eta) < 2.4`.
That's like TTree cuts on steroids - you can construct entire new `RVec`s objects based
on cuts!

But what if I have a `var2` that is actually a vector of variables in a different
collection? An example in words, "Give me all FatJet pt values where at least one subjet has
a btag score of 0.9" (ie. subjet b-tagging for top-like jet).

Maybe out of curiosity (but little hope), we write a cute one-liner...
```python
rdf2 = rdf1.Define('GoodFatJet_pt','FatJet_pt[max(SubJet_btagDeepB[FatJet_subJetIdx1], SubJet_btagDeepB[FatJet_subJetIdx2]) > 400]')
```
Unfortunately, it crashes...

So RDataFrame is "smart" but not *that* smart. The key here is that the code internal to the `[]` brackets are performing
a relatively simply computation - fill a vector of indices based on whether the statement is true or false.

```
available indices (assume 5 FatJets)    [0, 1, 2, 3, 4]
bools for evaluation                    [0, 1, 0, 0, 1]
return                                  FatJet_pt[1, 4]
```
But when we mix in another collection, SubJet, we confuse it because it's trying to decide
where these vectorization loops are happening -
or rather, which brackets to care about - does it start at `FatJet_pt[` or at `SubJet_btagDeepB[`?
Hopefully the logic behind this can improve but this is our first stop in confusion-land. There's no loop, what do I do?!

Maybe that's best handled by clarifying that there's no "event loop" but loops aren't off limits
just because RVec can do fancy one-liners.
This is where more C++ beyond one line comes in handy - and I'd argue factoring out logic like
this keeps the code cleaner for others to understand what is going on, even in the case that the long line above actually did work.

```C++
// Analysis.cc
RVec<bool> HasBSubJet(RVec<int> idx1, RVec<int> idx2, RVec<float> scores) {
    RVec<bool> out;
    float sjScore1, sjScore2;
    int nFatJets = idx1.size();
    for (int i = 0; i<nFatJets; i++) {
        if max(idx1[i], idx2[i]) < scores.size()) {
            sjScore1 = scores[ idx1[i] ];
            sjScore2 = scores[ idx2[i] ];
            out.push_back( max(sjScore1, sjScore2) > 0.9 );
        } else {
            out.push_back(false);
        } 
    }
    return out;
}
```
```python
...
from TIMBER.Tools.Common import CompileCpp
CompileCpp('Analysis.cc')
...
rdf2 = rdf1.Define('GoodFatJet_pt','FatJet_pt[HasBSubJet(FatJet_subJetIdx1,FatJet_subJetIdx2,SubJet_btagDeepB)]')
```

In the `for` example to match the above, you would have something like...
```python
for event in events:
    ak8jets = event.FatJets
    subjets = event.SubJets

    good_ak8jet_pt = []
    for ak8jet in ak8jets:
        if max(ak8jet.subJetIdx1,ak8jet.subJetIdx2) < len(subjets.btagDeepB):
            sjScore1 = subjets.btagDeepB[ ak8jet.subJetIdx1 ]
            sjScore2 = subjets.btagDeepB[ ak8jet.subJetIdx2 ]
            good_ak8jet_pt.append( max(sjScore1, sjScore2) > 0.9 )
        else:
            good_ak8jet_pt.append(False)
        
```
Not so different!

It is possible to get very clever one-liners using the VecOps namespace
(Map is particularly powerful) but you're free to use them as they feel
clear and useful to you. If in doubt, it's not so hard to write a C++ loop that you trust.

### Collections
The python `for` example pseudo-code was not pulled out of thin air - it
is based off of what you can do with NanoAOD-tools. In particular, it makes
use of `Event` and `Collection` classes to easily access the parts of an event.

The concept of an `Event` is obviously gone with RDataFrame since there's no event loop.
However the `Collection` is sorely missing - you cannot ask for the leading FatJet
and get just that physics object with all of its attributes: pt, eta, phi, mass,
tagging scores, etc. Instead, you have to resort to accessing the branches individually. 

This can become an annoyance quickly. A keen eye may have spotted that the `GoodFatJet_pt`
is just extracting the pt of the "good" FatJets. What about all of the other attributes of
FatJets? One may also notice that a `HasBSubJet` already takes in three arguments. What
if you have something more complicated that requires more variables? What if you need to do
generator particle matching to jets? Wouldn't it be simpler to be able to just pass
the whole collection and let the C++ unpack it?

To the first issue, this is where TIMBER comes in. There are dedicated methods in
the `analyzer` called `SubCollection`, `MergeCollections`, and `ReorderCollection`
which are meant to apply the sorts of manipulations above to an entire collection.
To continue with our `GoodFatJet` example, one would do
```python
a.SubCollection('GoodFatJet','FatJet','HasBSubJet(...)')
```
In subsequent lines, replace any instances of `FatJet` with `GoodFatJet` and you'll
only be working with those that have a b-tagged subjet!


To the second issue of lengthy C++ argument lists - there is also the dedicated `CollectionOrganizer` class in TIMBER which tracks
collections attributes. This powers a hidden functionality to build an
"Array of Structs" (AOS)
that creates a C++ `struct` for each collection based on the current attributes available.
This would make it possible to pass entire collections at a time and skip the long lists of
function arguments. I will be using it in the prefire correction in the next exercise so
you'll be able to see an example. However, this is an experimental feature! Without
a full explanation, it's easy to abuse and you can quickly slow your code.
If you have
an interest in working on this though to make it offical, please let me know -
these are the types of problems TIMBER should be tackling! For now though, let's move on
and come back to our analysis implementation.

## Exercise 5 - Corrections and Systematic Variations *(20-25 min)*
------------------------
While the main selection we've been working has already been using TIMBER,
this is the first exercise where we move past some of the RDataFrame basics
and towards functionality that makes interfacing with RDataFrame a bit easier
and more succinct.

As we've seen TIMBER has some basic functions that are already compiled and
ready to use once you initialize an `analyzer` instance. For anything external to 
TIMBER, one can use `TIMBER.Tools.Common.CompileCpp()` to tell ROOT about
your code (whether it be a multi-line string or a totally separate file that 
needs to be read).

The next step is then looking at the case when you need more than a 
function to perform your evaluation. The prime example of this is if
you have a file with scale factor values (or a function or histogram)
that needed to be loaded for the evaluation to happen. Why can't you
just use a function for this? Well, is your function going to also
load in the file and values stored? Because then it will do it for **every** row
of the dataframe. You just want to open the file once *before* the loop, keep
it in memory, and then access mid loop for the actual evaluation.

It is of course possible via `CompileCpp` to declare variables in the global
scope that can be accessible to functions. But in my opinion, this is bad practice
and it's safer and more robust to write a C++ class where the class can be
initialized to an object pre-loop and the values accessed as class members
mid loop (with a class method). This is the approach of most of the code
living in TIMBER/Framework/ - particularly for anything involving systematic variations.

### The `Correction` Class
A simple example that shows off multiple pieces of functionality is the PDF weight uncertainty:
```python
c_PDF = Correction('PDF','TIMBER/Framework/src/PDFweight_uncert.cc', constructor=[a.lhaid],
                    mainFunc='eval', corrtype='uncert')
...
a.AddCorrection(c_PDF)
```
The first line above initializes the object in memory. The second tells the `analyzer` to
execute the `Define` calls to perform the evaluation. Then we can ask the `analyzer` to calculate
all the variations on the event weight.
```python
a.MakeWeightCols()
```
and then to create some histograms with these different event weight scenarios to create templates.
```python
hists = a.MakeTemplateHistos(
    ROOT.TH1F('SR_mtt','Invariant mass in signal region',30,1000,4000),
    ['mtt'],lazy=True
    )

out = TFile.Open(...,'RECREATE')
out.cd()
hists.Do('Write')
out.Close()
```
We'll pick a couple of others and add them in:
- TopPt_weight.cc
- Prefire_weight.cc
- HEM_drop.cc
- TopTag_SF.cc

where the last one comes with a twist since we have two top tags in our SR and only one in our CR.

## Exercise 6 - Submitting to Condor **(15 min)**
-------------------------------------


## Exercise 7 - Codifying selections with a class **(10 min)**
----------------------------------------


## Exercise 8 - Analysis level systematics **(15 min)**
-----------------------------------------


## Exercise 9 - More tools to consider
---------------------------------------