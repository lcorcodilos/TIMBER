'''@addtogroup Common Common Tools (Common.py)
Commonly used functions available for use that can be generic or TIMBER specific.
@{
'''

import json, os, subprocess, sys, glob, ROOT, random, string
from contextlib import contextmanager
from collections import OrderedDict
#-----------------#
# TIMBER specific #
#-----------------#
def CutflowDict(node,initial=None):
    '''Turns the RDataFrame cutflow report into an OrderedDict.

    @param node (Node): Input Node from which to get the cutflow.
    @param initial (int): Initial number events. Defaults to None
        in which case the number in the top-most parent Node is used.

    Returns:
        OrderedDict: Ordered cutflow dictionary with filter names as keys and number of 
            events as values.
    '''
    filters = node.DataFrame.GetFilterNames()
    rdf_report = node.DataFrame.Report()
    cutflow = OrderedDict()
    if initial == None: 
        cutflow['Initial'] = int(node.GetBaseNode().DataFrame.Count().GetValue())
    else:
        cutflow['Initial'] = initial
    for filtername in filters: 
        cutflow[str(filtername)] = int(rdf_report.At(filtername).GetPass())

    return cutflow

def CutflowHist(name,node,initial=None,efficiency=False):
    '''Draws a cutflow histogram using the report feature of RDF.

    @param name (str): Name of output histogram
    @param node (Node): Input Node from which to get the cutflow.
    @param initial (int): Initial number events. Defaults to None
        in which case the number in the top-most parent Node is used.
    @param efficiency (bool, optional): Reports an efficiency instead of yields
            (relative to number of events before any cuts on Node).

    Returns:
        TH1: Histogram with each bin showing yield (or efficiency) for
            progressive cuts.
    '''
    cutflow_dict = CutflowDict(node,initial)
    ncuts = len(cutflow_dict.keys())
    h = ROOT.TH1F(name,name,ncuts,0,ncuts)

    for i,filtername in enumerate(cutflow_dict.keys()): 
        h.GetXaxis().SetBinLabel(i+1,filtername)
        cut = cutflow_dict[filtername]
        if efficiency:
            h.SetBinContent(i+1,cut/cutflow_dict['Initial'])
        else:
            h.SetBinContent(i+1,cut)

    return h

def CutflowTxt(name,node,efficiency=False):
    '''Writes out the cutflow as a text file using the report feature of RDF.

    @param name (str): Name of output text file.
    @param node (Node): Input Node from which to get the cutflow.
    @param efficiency (bool, optional): Reports an efficiency instead of yields
            (relative to number of events before any cuts on Node).

    Returns:
        None
    '''
    cutflow_dict = CutflowDict(node)
    out = open(name,'w')
    for filtername in cutflow_dict.keys(): 
        cut = cutflow_dict[filtername]
        if efficiency:
            out.write('%s %s'%(filtername,cut/cutflow_dict['Initial']))
        else:
            out.write('%s %s'%(filtername,cut))
    out.close()

def StitchQCD(QCDdict,normDict=None):
    '''Stitches together histograms in QCD hist groups.

    @param QCDdict ({string:HistGroup}): Dictionary of HistGroup objects
    @param normDict ({string:float}): Factors to normalize each sample to where keys must match QCDdict keys.
            Default to None and assume normalization has already been done.
    Returns:
        HistGroup: New HistGroup with histograms in group being the final stitched versions
    '''
    from TIMBER.Analyzer import HistGroup
    # Normalize first if needed
    if normDict != None:
        for k in normDict.keys():
            for hkey in QCDdict[k].keys():
                QCDdict[k][hkey].Scale(normDict[k])
    # Stitch
    out = HistGroup("QCD")
    for ksample in QCDdict.keys(): 
        for khist in QCDdict[ksample].keys():
            if khist not in out.keys():
                out[khist] = QCDdict[ksample][khist].Clone()
            else:
                out[khist].Add(QCDdict[ksample][khist])

    return out

def LoadColumnNames(path=os.environ["TIMBERPATH"],source=''):
    '''Loads column names from a text file.

    @param path (str, optional): Path to TIMBER folder.
    @param source (str, optional): File location if default TIMBER/data/NanoAODv6_cols.txt
        is not to be used. Defaults to ''.

    Returns:
        [str]: List of all column names.
    '''
    if source == '': 
        file = path+'TIMBER/data/NanoAODv6_cols.txt'
    else:
        file = source
    f = open(file,'r')
    cols = []
    for c in f.readlines():
        cols.append(c.strip('\n'))
    f.close()
    return cols

#---------#
# Generic #
#---------#
## Dictionary of the JES/JEC tags corresponding to
# tarballs stored in TIMBER/data/JES.
JEStags = {
    "2016": "Summer16_07Aug2017_V11",
    "2017": "Fall17_17Nov2017_V32",
    "2018": "Autumn18_V19",
    "2017UL": "Summer19UL17_V5",
    "2018UL": "Summer19UL18_V5"
}
## Dictionary of the JER tags corresponding to
# tarballs stored in TIMBER/data/JER.
JERtags = {
    "2016":"Summer16_25nsV1b",
    "2017":"Fall17_V3b",
    "2018":"Autumn18_V7b",
    "2017UL":"Summer19UL17_JRV2",
    "2018UL":"Summer19UL18_JRV2"
}

def GetJMETag(t,year,setname):
    '''Return the latest JME tag corresponding to the type `t` (JES or JER),
    `year`, and `setname` (MC for simulation and A, B, C, etc for data).
    Returned string is compatible with input needed by JME modules. 

    Args:
        t (str): JES or JER
        year (str): 2016, 2017, 2018, 2017UL, or 2018UL
        setname (str): MC for simulation. A, B, C, D, E, F, G, or H for data.

    Raises:
        ValueError: Did not provide `t` that is either JES or JER.  

    Returns:
        str: JME tarball/tag name compatible with input needed by JME modules.
    '''
    if setname == 'MC':
        MCorData = 'MC'
        subset = ''
    else:
        MCorData = 'DATA'
        subset = setname
        if year == '2018' or 'UL' in year:
            subset = '_Run'+setname

    if t == 'JES':
        tag = JEStags[year]
        tag_and_version = ['_'.join(tag.split('_')[:-1]),tag.split('_')[-1]]
        if MCorData == "DATA":
            fullpath = os.environ["TIMBERPATH"]+"TIMBER/data/JES/{0}*{1}*_{2}_{3}.tar.gz".format(tag_and_version[0],subset,tag_and_version[1],MCorData)
            out = glob.glob(fullpath)[0].replace(os.environ["TIMBERPATH"]+"TIMBER/data/JES/",'').replace('.tar.gz','')
        else:
            out = '{0}{1}_{2}_{3}'.format(tag_and_version[0],subset,tag_and_version[1],MCorData)

    elif t == 'JER':
        out = '{0}_{1}'.format(JERtags[year],MCorData)
    else:
        raise ValueError("Type must be either 'JES' or 'JER'")
    
    return out

def CompileCpp(blockcode,library=False):
    '''Compiles C++ code via the gInterpreter.

    A python string (the actual code) can be passed or a file name 
    (the file will be opened and read). If a file is passed,
    the C++ code can be compiled
    as a library and if in the future the C++ script is older than the library,
    then the library will be loaded instead.

    @param blockcode (str): Either a block of C++ code or a file name to open.
    @param library (bool, optional): Compiles a library which can be later loaded
            to avoid compilation time. Defaults to False.
    '''
    if '-I"'+os.environ["TIMBERPATH"]+'"' not in ROOT.gSystem.GetIncludePath():
        ROOT.gInterpreter.AddIncludePath(os.environ["TIMBERPATH"])
        ROOT.gInterpreter.AddIncludePath(os.environ["TIMBERPATH"]+'TIMBER/Framework/src')
        ROOT.gInterpreter.AddIncludePath(os.environ["TIMBERPATH"]+"bin")
        ROOT.gInterpreter.ProcessLine('#pragma clang diagnostic ignored "-Wunknown-attributes"')
        if 'CMSSW_BASE' in os.environ.keys():
            ROOT.gSystem.Load('libCondFormatsJetMETObjects')

    if not ROOT.gInterpreter.IsLibraryLoaded(os.environ["TIMBERPATH"]+'bin/libtimber/libtimber.so'):
        ROOT.gSystem.Load(os.environ["TIMBERPATH"]+'bin/libarchive/lib/libarchive.so')
        ROOT.gSystem.Load(os.environ["TIMBERPATH"]+'bin/libtimber/libtimber.so')

    if not library:
        if '\n' in blockcode or ';' in blockcode: # must be multiline string\
            ROOT.gInterpreter.Declare(blockcode)
        else: # must be file name to compile
            if ('TIMBER/Framework/' in blockcode) and (os.environ['TIMBERPATH'] not in blockcode):
                path = os.environ['TIMBERPATH']
            else:
                path = ''
            blockcode_str = open(path+blockcode,'r').read()
            ROOT.gInterpreter.Declare(blockcode_str)
    else:
        if '.so' not in blockcode:
            extension = blockcode.split('.')[-1]
            lib_path = blockcode.replace('.'+extension,'_'+extension)+'.so'
        else: 
            lib_path = blockcode
        
        loaded = False
        if os.path.exists(lib_path): # If library exists and is older than the cc file, just load
            mod_time_lib = os.path.getmtime(lib_path)
            mod_time_cc = os.path.getmtime(blockcode)
            if mod_time_lib > mod_time_cc:
                print ('Loading library...')
                ROOT.gSystem.Load(lib_path)
                loaded = True
        
        if not loaded: # Else compile a new lib
            ROOT.gSystem.AddIncludePath(" -I%s "%os.getcwd())
            print ('Compiling library...')
            ROOT.gROOT.ProcessLine(".L "+blockcode+"+")

def OpenJSON(filename):
    '''Opens JSON file as a dictionary (accounting for unicode encoding)

    @param filename (str): JSON file name to open.

    Returns:
        dict: Python dictionary with JSON content.
    '''
    if sys.version_info.major == 3:
        return json.load(open(filename,'r')) 
    else:
        return json.load(open(filename,'r'), object_hook=AsciiEncodeDict)

def AsciiEncodeDict(data):
    '''Encodes dict to ascii from unicode for python 2.7. Not needed for python 3.

    Credit Andrew Clark on [StackOverflow](https://stackoverflow.com/questions/9590382/forcing-python-json-module-to-work-with-ascii/28339920).

    @param data (dict): Input dictionary.

    Returns:
        dict: New dictionary with unicode converted to ascii.
    '''
    ascii_encode = lambda x: x.encode('ascii') if isinstance(x, unicode) else x 
    return dict(map(ascii_encode, pair) for pair in data.items())

def ConcatCols(colnames,val='1',connector='&&'):
    '''Concatenates a list of column names evaluating to a common `val` (usually 1 or 0) 
    with some `connector` (bool logic operator).

    @param colnames ([str]): List of column names.
    @param val (str): Value to test equality of all columns. Defaults to '1'.
    @param connector (str): C++ bool logic operator between column equality checks. Defaults to '&&'.

    Returns:
        str: Concatenated string of the entire evaluation that in C++ will return a bool.
    '''
    concat = ''
    for c in colnames:
        if concat == '': 
            concat = '((%s==%s)'%(c,val)
        else: 
            concat += ' %s (%s==%s)'%(connector,c,val)

    if concat != '': 
        concat += ')' 
        
    return concat

def GetHistBinningTuple(h):
    '''Gets the binning information for a histogram and returns it 
    as a tuple ordered like the arguments to construct a new histogram.
    Supports TH1, TH2, and TH3.

    @param h (TH1): Input histogram from which to get the binning information.

    Raises:
        TypeError: If histogram does not derive from TH1.

    Returns:
        tuple(tuple, int): First element of return is the binning and the second element is the dimension.
    '''
    # At least 1D (since TH2 and TH3 inherit from TH1)
    if isinstance(h,ROOT.TH1):
        # Variable array vs fixed binning
        if h.GetXaxis().GetXbins().GetSize() > 0:
            xbinning = (h.GetNbinsX(),h.GetXaxis().GetXbins())
        else:
            xbinning = (h.GetNbinsX(),h.GetXaxis().GetXmin(),h.GetXaxis().GetXmax())
        ybinning = ()
        zbinning = ()
        dimension = 1
    else:
        raise TypeError('ERROR: GetHistBinningTuple() does not support a template histogram of type %s. Please provide a TH1, TH2, or TH3.'%type(h))

    # Check if 2D
    if isinstance(h,ROOT.TH2):
        # Y variable vs fixed binning
        if h.GetYaxis().GetXbins().GetSize() > 0:
            ybinning = (h.GetNbinsY(),h.GetYaxis().GetXbins())
        else:
            ybinning = (h.GetNbinsY(),h.GetYaxis().GetXmin(),h.GetYaxis().GetXmax())
        zbinning = ()
        dimension = 2
    # Check if 3D
    elif isinstance(h,ROOT.TH3):
        # Y variable vs fixed binning
        if h.GetYaxis().GetXbins().GetSize() > 0:
            ybinning = (h.GetNbinsY(),h.GetYaxis().GetXbins())
        else:
            ybinning = (h.GetNbinsY(),h.GetYaxis().GetXmin(),h.GetYaxis().GetXmax())
        # Z variable vs fixed binning
        if h.GetZaxis().GetXbins().GetSize() > 0:
            zbinning = (h.GetNbinsZ(),h.GetZaxis().GetXbins())
        else:
            zbinning = (h.GetNbinsZ(),h.GetZaxis().GetXmin(),h.GetZaxis().GetXmax())
        dimension = 3

    return xbinning + ybinning + zbinning, dimension

def ColliMate(myString,width=18):
    '''Collimates strings to have consistent spacing between first character
    of word i with the first character of word i+1 and i-1.

    Recommended instead to use format() method of python strings as 
    described [here](https://stackoverflow.com/questions/10623727/python-spacing-and-aligning-strings).

    @param myString (str): String to space (words only separated by single space).
    @param width (int, optional): Column widths. Defaults to 18.

    Returns:
        str: String with new spacing between words.
    '''
    sub_strings = myString.split(' ')
    new_string = ''
    for i,sub_string in enumerate(sub_strings):
        string_length = len(sub_string)
        n_spaces = width - string_length
        if i != len(sub_strings)-1:
            if n_spaces <= 0:
                n_spaces = 2
            new_string += sub_string + ' '*n_spaces
        else:
            new_string += sub_string
    return new_string

def DictStructureCopy(inDict):
    '''Recursively copies the structure of a dictionary with non-dict items replaced with 0.

    @param inDict (dict): Dictionary with structure to copy.

    Returns:
        dict: Output dict.
    '''
    newDict = {}
    for k1,v1 in inDict.items():
        if type(v1) == dict:
            newDict[k1] = DictStructureCopy(v1)
        else:
            newDict[k1] = 0
    return newDict

def DictCopy(inDict):
    '''Recursively copy dictionary structure and values.

    @param inDict (dict): Dictionary to copy.

    Returns:
        dict: Output copy.
    '''
    newDict = {}
    for k1,v1 in inDict.items():
        if type(v1) == dict:
            newDict[k1] = DictCopy(v1)
        else:
            newDict[k1] = v1
    return newDict

def ExecuteCmd(cmd,dryrun=False):
    '''Executes shell command via `subprocess.call()` and prints
    the command for posterity.

    @param cmd (str): Shell command to run.
    @param dryrun (bool, optional): Prints command but doesn't execute it. Defaults to False.
    '''
    print('Executing: '+cmd)
    if not dryrun:
        subprocess.call([cmd],shell=True)

def DictToLatexTable(dict2convert,outfilename,roworder=[],columnorder=[]):
    '''Converts a dictionary with two layers (ie. only one set of sub-keys) to 
    a LaTeX table. First set of keys (ie. external) are rows, second (ie. internal) are columns.
    If the column entry for a given row is not provided (ie. missing key), then '-' is substituted.

    @param dict2convert (dict): Input dictionary.
    @param outfilename (str): Output .tex file name.
    @param roworder (list, optional): Custom ordering of rows. Defaults to [] in which case the sorted keys are used.
    @param columnorder (list, optional): Custom ordering of columns. Defaults to [] in which case the sorted keys are used.
    '''
    # Determine order of rows and columns
    if len(roworder) == 0:
        rows = sorted(dict2convert.keys())
    else:
        rows = roworder
    if len(columnorder) == 0:
        columns = []
        for r in rows:
            thesecolumns = dict2convert[r].keys()
            for c in thesecolumns:
                if c not in columns:
                    columns.append(c)
        columns.sort()
    else:
        columns = columnorder
    # Book output
    latexout = open(outfilename,'w')
    latexout.write('\\begin{table}[] \n')
    latexout.write('\\begin{tabular}{|c|'+len(columns)*'c'+'|} \n')
    latexout.write('\\hline \n')
    # Write first line with column names
    column_string = ' &'
    for c in columns:
        column_string += str(c)+'\t& '
    column_string = column_string[:-2]+'\\\\ \n'
    latexout.write(column_string)
    # Write rows
    latexout.write('\\hline \n')
    for r in rows:
        row_string = '\t'+r+'\t& '
        for c in columns:
            if c in dict2convert[r].keys():
                row_string += str(dict2convert[r][c])+'\t& '
            else:
                row_string += '- \t& '
        row_string = row_string[:-2]+'\\\\ \n'
        latexout.write(row_string)

    latexout.write('\\hline \n')
    latexout.write('\\end{tabular} \n')
    latexout.write('\\end{table}')
    latexout.close()

class MemoryFile():
    '''Stores file in memory with access similar to how a file would be written and read on disk.
        Intention is just to have a string in memory with the same methods as a standard python I/O
        file so that TIMBER doesn't care which one it is using (ie. they both have "write" methods).
    '''
    def __init__(self):
        '''Create empty file.
        
        Stores file in memory with access similar to how a file would be written and read on disk.
        Intention is just to have a string in memory with the same methods as a standard python I/O
        file so that TIMBER doesn't care which one it is using (ie. they both have "write" methods).
        '''
        ## @var str
        # str
        # String stored in memory.
        self.str = ''
    def write(self,inStr):
        '''Write string to the file.

        @param inStr (str): String to write.
        '''
        self.str += inStr

def DictToMarkdownTable(dict2convert,outfilename=None,roworder=[],columnorder=[]):
    '''Converts a dictionary with two layers (ie. only one set of sub-keys) to 
    a Markdown table. First set of keys (ie. external) are rows, second (ie. internal) are columns.
    If the column entry for a given row is not provided (ie. missing key), then '-' is substituted.

    @param dict2convert (dict): Input dictionary.
    @param outfilename (str): Output .md file name. Defaults to None in which case the markdown as a string is returned.
    @param roworder (list, optional): Custom ordering of rows. Defaults to [] in which case the sorted keys are used.
    @param columnorder (list, optional): Custom ordering of columns. Defaults to [] in which case the sorted keys are used.
    '''
    # Determine order of rows and columns
    if len(roworder) == 0:
        rows = sorted(dict2convert.keys())
    else:
        rows = roworder
    if len(columnorder) == 0:
        columns = []
        for r in rows:
            thesecolumns = dict2convert[r].keys()
            for c in thesecolumns:
                if c not in columns:
                    columns.append(c)
        columns.sort()
    else:
        columns = columnorder
    # Book output
    if outfilename == None: mdout = MemoryFile()
    else: mdout = open(outfilename,'w')
    # Write first line with column names
    column_string = '| |'
    for c in columns:
        column_string += str(c)+'\t| '
    column_string = column_string[:-2]+'\n'
    mdout.write(column_string)
    # Write rows
    mdout.write('-'.join(['|' for i in range(len(columns)+2)]) +'\n')
    for r in rows:
        row_string = '| '+r+'\t| '
        for c in columns:
            if c in dict2convert[r].keys():
                row_string += str(dict2convert[r][c])+'\t| '
            else:
                row_string += '- \t| '
        row_string = row_string[:-2]+' |\n'
        mdout.write(row_string)

    if outfilename != None: mdout.close()
    else: return mdout.str

def FindCommonString(string_list):
    '''Finds a common string between a list of strings.

    @param string_list ([str]): List of strings to compare.

    Returns:
        str: Matched sub-string.
    '''
    to_match = ''   # initialize the string we're looking for/building
    for s in string_list[0]:    # for each character in the first string
        passed = True
        for istring in range(1,len(string_list)):   # compare to_match+s against strings in string_list
            string = string_list[istring]
            if to_match not in string:                  # if in the string, add more
                passed = False
            
        if passed == True:
            to_match+=s

    if to_match[-2] == '_':
        return to_match[:-2] 
    else:
        return to_match[:-1]                # if not, return to_match minus final character

    return to_match[:-2]

def GetStandardFlags():
    '''List of the following recommended flags as of Jan. 6th, 2021.

    Returns:
        ["Flag_goodVertices",
         "Flag_globalTightHalo2016Filter", 
         "Flag_eeBadScFilter", 
         "Flag_HBHENoiseFilter", 
         "Flag_HBHENoiseIsoFilter", 
         "Flag_ecalBadCalibFilter", 
         "Flag_EcalDeadCellTriggerPrimitiveFilter"]
    '''
    flags = ["Flag_goodVertices",
               "Flag_globalTightHalo2016Filter", 
               "Flag_eeBadScFilter", 
               "Flag_HBHENoiseFilter", 
               "Flag_HBHENoiseIsoFilter", 
               "Flag_ecalBadCalibFilter", 
               "Flag_EcalDeadCellTriggerPrimitiveFilter"]
    return flags

@contextmanager
def cd(newdir):
    '''Context manager to cd to another folder in the middle of
    a python script. Useful to use if you're producing a lot of files
    in a dedicated folder. Change into the folder and then produce the files.

    @param newdir (str): Directory to cd into.
    '''
    prevdir = os.getcwd()
    os.chdir(os.path.expanduser(newdir))
    try:
        yield
    finally:
        os.chdir(prevdir)

def GenerateHash(length=8):
    '''Generate a alphanumeric hash of a specified length. Used internally for tracking unique nodes.

    @param length (int, optional): Length of hash. Defaults to 8.

    Returns:
        str: Hash
    '''
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for i in range(length))

## @}