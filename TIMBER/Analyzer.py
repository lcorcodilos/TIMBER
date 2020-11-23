"""@docstring Analyzer.py

Home of main classes for TIMBER.

"""

from TIMBER.Tools.Common import GetHistBinningTuple, CompileCpp, ConcatCols
from clang import cindex
from collections import OrderedDict

import ROOT
import pprint, copy, os, subprocess, textwrap
pp = pprint.PrettyPrinter(indent=4)


# For parsing c++ modules
libs = subprocess.Popen('$ROOTSYS/bin/root-config --libs',shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].strip()
rootpath = subprocess.Popen('echo $ROOTSYS',shell=True, stdout=subprocess.PIPE, universal_newlines=True).communicate()[0].strip()
cpp_args =  '-x c++ -c --std=c++11 -I %s/include %s -lstdc++'%(rootpath,libs)
cpp_args = cpp_args.split(' ')

TIMBERPATH = os.environ["TIMBERPATH"]

class analyzer(object):
    """Main class for TIMBER. 

    Implements an interface with ROOT's RDataFrame (RDF). The default values assume the data is in
    NanoAOD format. However, any TTree can be used. The class works on the basis of nodes and actions
    where nodes are an RDF instance and an action (or series of actions) can transform the RDF to create a new node(s).

    When using class functions to perform actions, an active node will always be tracked so that the next action uses 
    the active node and assigns the output node as the new #ActiveNode"""
    def __init__(self,fileName,eventsTreeName="Events",runTreeName="Runs"):
        """Constructor.
        
        Sets up the tracking of actions on an RDataFrame as nodes. Also
        looks up and stores common information in NanoAOD such as the number of generated
        events in a file (#genEventCount), the LHA ID of the PDF set in the `LHEPdfWeights`
        branch (#lhaid), if the file is data (#isData), and if the file is before NanoAOD
        version 6 (#preV6).

        @param fileName (str): A ROOT file path or the path to a txt file which contains several ROOT file paths separated by 
                new line characters.
        @param eventsTreeName (str, optional): Name of TTree in fileName where events are stored. Defaults to "Events" (for NanoAOD)
        @param runTreeName (str, optional): NAme of TTree in fileName where run information is stored (for generated event info in 
                simulation). Defaults to "Runs" (for NanoAOD) 
        """

        ## @var fileName
        #
        # Path of the input file.
        ## @var BaseNode
        # Node
        #
        # Initial Node - no modifications.
        ## @var AllNodes
        # {str:Node}
        #
        # List of all nodes being tracked.
        ## @var Corrections
        # dict
        #
        # All corrections added to track.
        ## @var isData
        # bool
        #
        # Is data (true) or simulation (false) based on existence of _genEventCount branch.
        ## @var preV6
        # bool
        #
        # Is pre-NanoAODv6 (true) or not (false) based on existence of _genEventCount branch.
        ## @var genEventCount
        # int
        #
        # Number of generated events in imported simulation files. Zero if not found or data.
        ## @var lhaid
        # int
        #
        # LHA ID of the PDF weight set in the NanoAOD derived from the LHEPdfWeight branch title. -1 if not found or data.
        ## @var ActiveNode
        # Node
        #
        # Active node. Access via GetActiveNode(). Set via SetActiveNode().

        super(analyzer, self).__init__()
        self.fileName = fileName 
        self.__eventsTreeName = eventsTreeName

        # Setup TChains for multiple or single file
        self.__eventsChain = ROOT.TChain(self.__eventsTreeName) 
        RunChain = ROOT.TChain(runTreeName) # Has generated event count information - will be deleted after initialization
        if ".root" in self.fileName: 
            self.__eventsChain.Add(self.fileName)
            RunChain.Add(self.fileName)
        elif ".txt" in self.fileName: 
            txt_file = open(self.fileName,"r")
            for l in txt_file.readlines():
                thisfile = l.strip()
                if 'root://' not in thisfile and '/store/' in thisfile: thisfile='root://cms-xrd-global.cern.ch/'+thisfile
                self.__eventsChain.Add(thisfile)
                RunChain.Add(thisfile)
        else: 
            raise Exception("File name extension not supported. Please provide a single .root file or a .txt file with a line-separated list of .root files to chain together.")

        # Make base RDataFrame
        BaseDataFrame = ROOT.RDataFrame(self.__eventsChain) 
        self.BaseNode = Node('base',BaseDataFrame) 
        self.BaseNode.children = [] # protect against memory issue when running over multiple sets in one script
        self.AllNodes = [self.BaseNode] 
        self.Corrections = {} 

        # Check if dealing with data
        if hasattr(RunChain,'genEventCount'): 
            self.isData = False 
            self.preV6 = True 
        elif hasattr(RunChain,'genEventCount_'): 
            self.isData = False
            self.preV6 = False
        else: self.isData = True
 
        # Count number of generated events if not data
        self.genEventCount = 0 
        if not self.isData: 
            for i in range(RunChain.GetEntries()): 
                RunChain.GetEntry(i)
                if self.preV6: self.genEventCount+= RunChain.genEventCount
                else: self.genEventCount+= RunChain.genEventCount_

        # Get LHAID from LHEPdfWeights branch
        self.lhaid = "-1"
        if not self.isData:
            pdfbranch = self.__eventsChain.GetBranch("LHEPdfWeight")
            if pdfbranch != None:
                branch_title = pdfbranch.GetTitle()
                if branch_title != '': 
                    self.lhaid = ''
                    for c in branch_title:
                        if c.isdigit(): 
                            self.lhaid+=str(c)
                        elif self.lhaid == '':
                            continue
                        else:
                            break
                    self.lhaid = str(int(self.lhaid)-1)
                    print ('LHA ID: '+self.lhaid)

        # Cleanup
        del RunChain
        self.ActiveNode = self.BaseNode
 
    def Close(self):
        '''Safely deletes analyzer instance.
        
        Returns:
            None
        '''
        self.BaseNode.Close()
        self.__eventsChain.Reset()

    def __str__(self):
        '''Call with `print(<analyzer>)` to print a nicely formatted description
        of the analyzer object for debugging.
        
        Returns:
            str
        '''
        out = ''
        for a in dir(self):
            if not a.startswith('_') and not callable(getattr(self, a)):
                if isinstance(getattr(self, a),list) and len(getattr(self, a))>0 and isinstance(getattr(self, a)[0],Node):
                    out += '{:15s} = {}\n'.format(a,[n.name for n in getattr(self,a)])
                else:
                    out += '{:15s} = {}\n'.format(a,getattr(self,a))
        return out

    @property
    def DataFrame(self):
        '''
        DataFrame of the ActiveNode

        Returns:
            RDataFrame: Dataframe for the active node.
        '''        
        return self.ActiveNode.DataFrame

    def Snapshot(self,columns,outfilename,treename,lazy=False,openOption='RECREATE'):
        '''@see Node#Snapshot'''
        self.ActiveNode.Snapshot(columns,outfilename,treename,lazy,openOption)

    def SetActiveNode(self,node):
        '''Sets the active node.

        @param node (Node): Node to set as #ActiveNode.

        Raises:
            ValueError: If argument type is not Node.

        Returns:
            Node: New #ActiveNode.
        '''
        if not isinstance(node,Node): raise ValueError('SetActiveNode() does not support argument of type %s. Please provide a Node.'%(type(node)))
        else: self.ActiveNode = node

        return self.ActiveNode

    def GetActiveNode(self):
        '''Get the active node.

        Returns: 
            Node: Value of #ActiveNode.
        '''
        return self.ActiveNode

    def GetBaseNode(self):
        '''Get the base node.

        Returns: 
            Node: Value of #BaseNode.
        '''
        return self.BaseNode

    def TrackNode(self,node):
        '''Add a node to track.
        Will add the node to #AllNodes dictionary with key node.name.

        @param node (Node): Node to start tracking.

        Raises:
            NameError: If attempting to track nodes of the same name.
            TypeError: If argument type is not Node.

        Returns:
            None
        '''        
        if isinstance(node,Node):
            if node.name in self.GetTrackedNodeNames():
                raise NameError('Attempting to track a node with the same name as one that is already being tracked (%s). Please provide a unique node.'%(node.name))
            self.AllNodes.append(node)
        else:
            raise TypeError('TrackNode() does not support arguments of type %s. Please provide a Node.'%(type(node)))

    def GetTrackedNodeNames(self):
        '''Gets the names of the nodes currently being tracked.

        Returns:
            [str]: List of names of nodes being tracked.
        '''
        return [n.name for n in self.AllNodes]

    def GetCorrectionNames(self):
        '''Get names of all corrections being tracked.

        Returns:
            [str]: List of Correction keys/names.
        '''
        return self.Corrections.keys()

    def FilterColumnNames(self,columns,node=None):
        '''Takes a list of possible columns and returns only those that
        exist in the RDataFrame of the supplied node.

        @param columns ([str]): List of column names (str)
        @param node (Node, optional): Node to compare against. Defaults to #BaseNode.

        Returns:
            [str]: List of column names that union with those in the RDataFrame.
        '''
        if node == None: node = self.BaseNode
        cols_in_node = node.DataFrame.GetColumnNames()
        out = []
        for i in columns:
            if i in cols_in_node: out.append(i)
            else: print ("WARNING: Column %s not found and will be dropped."%i)

        return out

    def GetTriggerString(self,trigList):
        '''Checks input list for missing triggers and drops those missing (#FilterColumnNames)
        and then concatenates those remaining into an OR (`||`) string.

        @param trigList [str]: List of trigger names 

        Returns:
            str: Statement to evaluate as the set of triggers.
        '''
        trig_string = ''
        available_trigs = self.FilterColumnNames(trigList)
        trig_string = ConcatCols(available_trigs,'1','||')
        return trig_string

    def GetFlagString(self,flagList):
        '''Checks input list for missing flags and drops those missing (#FilterColumnNames)
        and then concatenates those remaining into an AND string.

        @param flagList [str]: List of flag names 

        Returns:
            str: Statement to evaluate as the set of flags.
        '''
        flag_string = ''
        available_flags = self.FilterColumnNames(flagList)
        flag_string = ConcatCols(available_flags,'1','&&')
        return flag_string

    def GetFileName(self):
        '''Get input file name.

        Returns:
            str: File name
        '''
        return self.fileName

    #------------------------------------------------------------#
    # Node operations - same as Node class methods but have      #
    # benefit of class keeping track of an Active Node (reset by #
    # each action and used by default).                          #
    #------------------------------------------------------------#
    def Cut(self,name,cuts,node=None,nodetype=None):
        '''Apply a cut/filter to a provided node or the #ActiveNode by default.
        Will add the resulting node to tracking and set it as the #ActiveNode.

        @param name (str): Name for the cut for internal tracking and later reference.
        @param cuts (str, CutGroup): A one-line C++ string that evaluates as a bool or a CutGroup object which contains multiple actions that evaluate as bools.
        @param node (Node, optional): Node on which to apply the cut/filter. Defaults to #ActiveNode.
        @param nodetype (str, optional): Defaults to None in which case the new Node will
            be type "Define".

        Raises:
            TypeError: If argument type is not Node.

        Returns:
            Node: New #ActiveNode.
        '''
        if node == None: node = self.ActiveNode
        newNode = node

        if isinstance(cuts,CutGroup):
            for c in cuts.keys():
                cut = cuts[c]
                newNode = newNode.Cut(c,cut,nodetype=nodetype)
                newNode.name = cuts.name+'__'+c
                self.TrackNode(newNode)
        elif isinstance(cuts,str):
            newNode = newNode.Cut(name,cuts,nodetype=nodetype)
            self.TrackNode(newNode)
        else:
            raise TypeError("Second argument to Cut method must be a string of a single cut or of type CutGroup (which provides an OrderedDict).")

        return self.SetActiveNode(newNode)

    def Define(self,name,variables,node=None,nodetype=None):
        '''Defines a variable/column on top of a provided node or the #ActiveNode by default.
        Will add the resulting node to tracking and set it as the #ActiveNode.

        @param name (str): Name for the column for internal tracking and later reference.
        @param variables (str, VarGroup): A one-line C++ string that evaluates to desired value to store
                or a VarGroup object which contains multiple actions that evaluate to the desired values. 
        @param node (Node, optional): Node to create the new variable/column on top of. Defaults to #ActiveNode.
        @param nodetype (str, optional): Defaults to None in which case the new Node will
            be type "Define".

        Raises:
            TypeError: If argument type is not Node.

        Returns:
            Node: New ActiveNode.
        '''
        if node == None: node = self.ActiveNode
        newNode = node

        if isinstance(variables,VarGroup):
            for v in variables.keys():
                var = variables[v]
                newNode = newNode.Define(v,var,nodetype=nodetype)
                newNode.name = variables.name+'__'+v
                self.TrackNode(newNode)
            # newNode.name = variables.name
        elif isinstance(variables,str):
            newNode = newNode.Define(name,variables,nodetype=nodetype)
            self.TrackNode(newNode)
        else:
            raise TypeError("Second argument to Define method must be a string of a single var or of type VarGroup (which provides an OrderedDict).")

        # self.TrackNode(newNode)
        return self.SetActiveNode(newNode)

    # Applies a bunch of action groups (cut or var) in one-shot in the order they are given
    def Apply(self,actionGroupList,node=None,trackEach=True):
        '''Applies a single CutGroup/VarGroup or an ordered list of Groups to the provided node or the #ActiveNode by default.

        @param actionGroupList (Group, list(Group)): The CutGroup or VarGroup to act on node or a list of CutGroups or VarGroups to act (in order) on node.
        @param node ([type], optional): Node to create the new variable/column on top of. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.
        @param trackEach (bool, optional): [description]. Defaults to True.

        Raises:
            TypeError: If argument type is not Node.

        Returns:
            Node: New #ActiveNode.
        '''
        if node == None: node = self.ActiveNode
        newNode = node

        if not isinstance(actionGroupList, list): actionGroupList = [actionGroupList]

        if not trackEach:
            newNode = node.Apply(actionGroupList)
        else:
            for ag in actionGroupList:
                if ag.type == 'cut':
                    newNode = self.Cut(name=ag.name,cuts=ag,node=newNode)
                elif ag.type == 'var':
                    newNode = self.Define(name=ag.name,variables=ag,node=newNode)
                else:
                    raise TypeError("Apply() group %s does not have a defined type. Please initialize with either CutGroup or VarGroup." %ag.name)

        return self.SetActiveNode(newNode)

    def Discriminate(self,name,discriminator,node=None,passAsActiveNode=None):
        '''Forks a node based upon a discriminator being True or False (#ActiveNode by default).

        @param name (str): Name for the discrimination for internal tracking and later reference.
        @param discriminator (str): A one-line C++ string that evaluates as a bool to discriminate for the forking of the node.
        @param node (Node, optional): Node to discriminate. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.
        @param passAsActiveNode (bool, optional): True if the #ActiveNode should be set to the node that passes the discriminator.
                False if the #ActiveNode should be set to the node that fails the discriminator. Defaults to None in which case the #ActiveNode does not change.

        Returns:
            dict: Dictionary with keys "pass" and "fail" corresponding to the passing and failing Nodes stored as values.
        '''
        if node == None: node = self.ActiveNode

        newNodes = node.Discriminate(name,discriminator)

        self.TrackNode(newNodes['pass'])
        self.TrackNode(newNodes['fail'])

        if passAsActiveNode == True: self.SetActiveNode(newNodes['pass'])
        elif passAsActiveNode == False: self.SetActiveNode(newNodes['fail'])

        return newNodes

    def SubCollection(self,name,basecoll,condition,skip=[]):
        '''Creates a collection of a current collection (from a NanoAOD-like format)
        where the array-type branch is slimmed based on some selection.

        @param name (str): Name of new collection.
        @param basecoll (str): Name of derivative collection.
        @param condition (str): C++ condition that determines which items
        @param skip ([str]): List of variable names in the collection to skip.

        Returns:
            None. New nodes created with the sub collection.

        Example:
            SubCollection('TopJets','FatJet','FatJet_msoftdrop > 105 && FatJet_msoftdrop < 220')
        '''
        collBranches = [str(cname) for cname in self.DataFrame.GetColumnNames() if basecoll in str(cname) and str(cname) not in skip]
        self.Define(name+'_idx','%s'%(condition))
        for b in collBranches:
            replacementName = b.replace(basecoll,name)
            if b == 'n'+basecoll:
                self.Define(replacementName,'std::count(%s_idx.begin(), %s_idx.end(), 1)'%(name,name),nodetype='SubCollDefine')
            elif 'RVec' not in self.DataFrame.GetColumnType(b):
                print ('Found type %s during SubCollection'%self.DataFrame.GetColumnType(b))
                self.Define(replacementName,b,nodetype='SubCollDefine')
            else:
                self.Define(replacementName,'%s[%s]'%(b,name+'_idx'),nodetype='SubCollDefine')

    def MergeCollections(self,name,collectionNames):
        '''Merge collections (provided by list of names in `collectionNames`) into
        one called `name`. Only common variables are taken and stored in the new 
        collection.

        @param name (str): Name of new collection
        @param collectionNames ([str]): List of names of collections to merge.

        Example:
            a = analyzer(<...>)
            a.MergeCollections("Lepton",["Electron","Muon"])
        '''
        vars_to_make = self.CommonVars(collectionNames)
        for var in vars_to_make:
            if 'RVec' in self.DataFrame.GetColumnType(collectionNames[0]+'_'+var):
                concat_str = collectionNames[0]+'_'+var
                for collName in collectionNames:
                    if collName != collectionNames[0]:
                        concat_str = 'Concatenate(%s,%s)'%(concat_str,collName+'_'+var)

                self.Define(name+'_'+var,concat_str,nodetype='MergeDefine')

        self.Define('n'+name,'+'.join(['n'+n for n in collectionNames]),nodetype='MergeDefine')

    def CommonVars(self,collections):
        '''Find the common variables between collections.

        @param collections ([str]): List of collections names (not branch names).

        Returns:
            [str]: List of variables shared among the collections.
        '''
        commonVars = []
        for c in collections:
            out = []
            colNames = sorted([str(b) for b in self.DataFrame.GetColumnNames()])
            for bname in colNames:
                if c+'_' in str(bname):
                    out.append(str(bname).replace(c+'_',''))
            commonVars.append(out)

        return list(set.intersection(*map(set,commonVars)))

    #---------------------#
    # Corrections/Weights #
    #---------------------#
    # Want to correct with analyzer class so we can track what corrections have been made for final weights and if we want to save them out in a group when snapshotting
    def AddCorrection(self,correction,evalArgs=[],node=None):
        '''Add a Correction to track. Sets new active node with all correction
        variations calculated as new columns.

        @param correction (Correction): Correction object to add.
        @param evalArgs ([str], optional): List of arguments (NanoAOD branch names) to provide to per-event evaluation method.
                              Default empty and clang will deduce if method definition argument names match columns in RDataFrame.
        @param node (Node, optional): Node to add correction on top of. Defaults to #ActiveNode.

        Raises:
            TypeError: If argument types are not Node and Correction.
            ValueError: If Correction type is not a weight or uncertainty.

        Returns:
            Node: New #ActiveNode.
        '''
        if node == None: node = self.ActiveNode

        # Quick type checking
        if not isinstance(node,Node): raise TypeError('AddCorrection() does not support argument of type %s for node. Please provide a Node.'%(type(node)))
        elif not isinstance(correction,Correction): raise TypeError('AddCorrection() does not support argument type %s for correction. Please provide a Correction.'%(type(correction)))

        # Make the call
        correction.MakeCall(evalArgs)

        # Add correction to track
        self.Corrections[correction.name] = correction

        # Make new node
        newNode = self.Define(correction.name+'__vec',correction.GetCall(),node,nodetype='Correction')
        if correction.GetType() == 'weight':
            variations = ['nom','up','down']
        elif correction.GetType() == 'uncert':
            variations = ['up','down']
        elif correction.GetType() == 'corr':
            variations = ['nom']
        else:
            raise ValueError('Correction.GetType() returns %s'%correction.GetType())

        for i,v in enumerate(variations):
            newNode = self.Define(correction.name+'__'+v,correction.name+'__vec[%s]'%i,newNode,nodetype='Correction')

        # self.TrackNode(returnNode)
        return self.SetActiveNode(newNode)

    def AddCorrections(self,correctionList,node=None):
        '''Add multiple Corrections to track. Sets new #ActiveNode with all correction
        variations calculated as new columns.

        @param correctionList ([Correction]): List of Correction objects to add.
        @param node (Node, optional): [description]. Defaults to None.

        Returns:
            Node: New #ActiveNode.
        '''
        if node == None: node = self.ActiveNode

        newNode = node
        for c in correctionList:
            newNode = self.AddCorrection(newNode,c)

        return self.SetActiveNode(newNode)

    def __checkCorrections(self,correctionNames,dropList):
        '''Does type checking and drops specified corrections by name.

        @param correctionNames ([str]): List of correction names to include.
        @param dropList ([type]): List of correction names to drop.

        Raises:
            ValueError: If lists aren't provided.

        Returns:
            [str]: List of remaining correction names.
        '''
        # Quick type checking
        if correctionNames == None: correctionsToApply = self.Corrections.keys()
        elif not isinstance(correctionNames,list):
            raise ValueError('MakeWeightCols() does not support correctionNames argument of type %s. Please provide a list.'%(type(correctionNames)))
        else: correctionsToApply = correctionNames

        # Drop specified weights from consideration
        if not isinstance(dropList,list):
            raise ValueError('MakeWeightCols() does not support dropList argument of type %s. Please provide a list.'%(type(dropList)))
        else: 
            newCorrsToApply = []
            for corr in correctionsToApply:
                if corr not in dropList: newCorrsToApply.append(corr)
            correctionsToApply = newCorrsToApply

        return correctionsToApply

    def MakeWeightCols(self,node=None,correctionNames=None,dropList=[]):
        '''Makes columns/variables to store total weights based on the Corrections that have been added.

        This function automates the calculation of the columns that store the nominal weight and the 
        variation of weights based on the corrections in consideration. The nominal weight will be the product
        of all "weight" type Correction objects. The variations on the nominal weight correspond to 
        the variations/uncertainties in each Correction object (both "weight" and "uncert" types).

        For example, if there are five different Correction objects considered, there will be 11 weights
        calculated (nominal + 5 up + 5 down).

        A list of correction names can be provided if only a subset of the corrections being tracked are 
        desired. A drop list can also be supplied to remove a subset of corrections.

        @param node (Node): Node to calculate weights on top of. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.
        @param correctionNames list(str): List of correction names (strings) to consider. Default is None in which case all corrections
                being tracked are considered.
        @param dropList list(str): List of correction names (strings) to not consider. Default is empty lists in which case no corrections
                are dropped from consideration.

        Returns:
            Node: New #ActiveNode.
        '''
        if node == None: node = self.ActiveNode

        correctionsToApply = self.__checkCorrections(correctionNames,dropList)
        
        # Build nominal weight first (only "weight", no "uncert")
        weights = {'nominal':''}
        for corrname in correctionsToApply:
            corr = self.Corrections[corrname] 
            if corr.GetType() in ['weight','corr']:
                weights['nominal']+=' '+corrname+'__nom *'
        weights['nominal'] = weights['nominal'][:-2]

        if weights['nominal'] == '':  weights['nominal'] = '1'

        # Vary nominal weight for each correction ("weight" and "uncert")
        for corrname in correctionsToApply:
            corr = self.Corrections[corrname]
            if corr.GetType() == 'weight':
                weights[corrname+'_up'] = weights['nominal'].replace(' '+corrname+'__nom',' '+corrname+'__up') #extra space at beginning of replace to avoid substrings
                weights[corrname+'_down'] = weights['nominal'].replace(' '+corrname+'__nom',' '+corrname+'__down')
            elif corr.GetType() == 'uncert':
                weights[corrname+'_up'] = weights['nominal']+' * '+corrname+'__up'
                weights[corrname+'_down'] = weights['nominal']+' * '+corrname+'__down'
            elif corr.GetType() == 'corr':
                continue
            else:
                raise TypeError('Correction "%s" not identified as either "weight" or "uncert"'%(corrname))

        # Make a node with all weights calculated
        returnNode = node
        for weight in weights.keys():
            returnNode = self.Define('weight__'+weight,weights[weight],returnNode)
        
        # self.TrackNode(returnNode)
        return self.SetActiveNode(returnNode)

    def MakeTemplateHistos(self,templateHist,variables,node=None):
        '''Generates the uncertainty template histograms based on the weights created by #MakeWeightCols(). 

        @param templateHist (TH1,TH2,TH3): A TH1, TH2, or TH3 used as a template to create the histograms.
        @param variables ([str]): A list of the columns/variables to plot (ex. ["x","y","z"]).
        @param node (Node): Node to plot histograms from. Defaults to #ActiveNode.

        Returns:
            HistGroup: Uncertainty template histograms.
        '''
        if node == None: node = self.ActiveNode

        weight_cols = [str(cname) for cname in node.DataFrame.GetColumnNames() if 'weight__' in str(cname)]
        baseName = templateHist.GetName()
        baseTitle = templateHist.GetTitle()
        binningTuple,dimension = GetHistBinningTuple(templateHist)
        out = HistGroup(baseName+'_templates')

        if isinstance(variables,str): variables = [variables]

        for cname in weight_cols:
            histname = '%s__%s'%(baseName,cname.replace('weight__',''))
            histtitle = '%s__%s'%(baseTitle,cname.replace('weight__','').replace('__nominal',''))

            # Build the tuple to give as argument for template
            template_attr = (histname,histtitle) + binningTuple

            if dimension == 1: 
                thishist = node.DataFrame.Histo1D(template_attr,variables[0],cname)
            elif dimension == 2: 
                thishist = node.DataFrame.Histo2D(template_attr,variables[0],variables[1],cname)
            elif dimension == 3: 
                thishist = node.DataFrame.Histo3D(template_attr,variables[0],variables[1],variables[2],cname)

            out.Add(histname,thishist)

        # Wait to GetValue and SetTitle so that the histogram filling happens simultaneously
        for k in out.keys():
            if dimension == 1: 
                out[k] = out[k].GetValue()
                out[k].GetXaxis().SetTitle(variables[0])
            elif dimension == 2: 
                out[k] = out[k].GetValue()
                out[k].GetXaxis().SetTitle(variables[0])
                out[k].GetYaxis().SetTitle(variables[1])
            elif dimension == 3: 
                out[k] = out[k].GetValue()
                out[k].GetXaxis().SetTitle(variables[0])
                out[k].GetYaxis().SetTitle(variables[1])
                out[k].GetZaxis().SetTitle(variables[2])

        return out

    #----------------------------------------------------------------#
    # Draw templates together to see up/down effects against nominal #
    #----------------------------------------------------------------#
    def DrawTemplates(self,hGroup,saveLocation,projection='X',projectionArgs=(),fileType='pdf'):
        '''Draw the template uncertainty histograms created by #MakeTemplateHistos(). 

        @param hGroup (HistGroup): Uncertainty template histograms.
        @param saveLocation (str): Path to folder to save histograms.
        @param projection (str, optional): "X" (Default), "Y", or "Z". Axis to project onto if templates are not 1D.
        @param projectionArgs (tuple, optional): A tuple of arguments provided to ROOT TH1 ProjectionX(Y)(Z).
        @param fileType (str, optional): File type - "pdf", "png", etc (must be supported by TCanvas.Print()).

        Returns:
            None
        '''
        ROOT.gStyle.SetOptStat(0)

        canvas = ROOT.TCanvas('c','',800,700)

        # Initial setup
        baseName = list(hGroup.keys())[0].split('__')[0]

        if isinstance(hGroup[baseName+'__nominal'],ROOT.TH2):
            projectedGroup = hGroup.Do("Projection"+projection.upper(),projectionArgs)
        if isinstance(hGroup[baseName+'__nominal'],ROOT.TH3): 
            raise TypeError("DrawTemplates() does not currently support TH3 templates.")
        else:
            projectedGroup = hGroup

        nominal = projectedGroup[baseName+'__nominal']
        nominal.SetLineColor(ROOT.kBlack)
        nominal.SetFillColor(ROOT.kOrange)
        nominal.SetMaximum(1.3*nominal.GetMaximum())
        nominal.SetTitle('')

        corrections = []
        for name in projectedGroup.keys():
            corr = name.split('__')[1].replace('_up','').replace('_down','')
            if corr not in corrections and corr != "nominal":
                corrections.append(corr)

        # Loop over corrections
        for corr in corrections:
            nominal.Draw('hist')

            up = projectedGroup[baseName+'__'+corr+'_up']
            down = projectedGroup[baseName+'__'+corr+'_down']

            up.SetLineColor(ROOT.kRed)
            down.SetLineColor(ROOT.kBlue)

            leg = ROOT.TLegend(0.7,0.7,0.9,0.9)
            leg.AddEntry(nominal,'Nominal','lf')
            leg.AddEntry(up,'Up','l')
            leg.AddEntry(down,'Down','l')

            up.Draw('same hist')
            down.Draw('same hist')
            leg.Draw()

            canvas.Print('%s%s_%s.%s'%(saveLocation,baseName,corr,fileType),fileType)

    #----------------------------------------------#
    # Build N-1 "tree" and outputs the final nodes #
    # Beneficial to put most aggressive cuts first #
    # Return dictionary of N-1 nodes keyed by the  #
    # cut that gets dropped                        #
    #----------------------------------------------#
    def Nminus1(self,cutgroup,node=None):
        '''Create an N-1 tree structure of nodes building off of `node`
        with the N cuts from `cutgroup`.

        The structure is optimized so that as many actions are shared as possible
        so that the N different nodes can be made. Use #PrintNodeTree() to visualize. 

        @param cutgroup (CutGroup): Group of N cuts to apply.
        @param node (Node, optional): Node to build on. Defaults to #ActiveNode.

        Returns:
            dict: N nodes in dictionary with keys indicating the cut that was not applied.
        '''
        if node == None: node = self.ActiveNode

        # Initialize
        print ('Performing N-1 scan for CutGroup %s'%cutgroup.name)

        nminusones = {}
        thisnode = node
        thiscutgroup = cutgroup

        # Loop over all cuts (`cut` is the name not the string to filter on)
        for cut in cutgroup.keys():
            # Get the N-1 group of this cut (where N is determined by thiscutgroup)
            minusgroup = thiscutgroup.Drop(cut,makeCopy=True)
            thiscutgroup = minusgroup
            minusgroup.name = 'Minus(%s)'%cut
            # Store the node with N-1 applied
            nminusones[cut] = self.Apply(minusgroup,thisnode)
            
            # If there are any more cuts left, go to the next node with current cut applied (this is how we keep N as the total N and not just the current N)
            if len(minusgroup.keys()) > 0:
                thisnode = self.Cut(cut,cutgroup[cut],node=thisnode)
                self.SetActiveNode(thisnode)
            else:
                nminusones['full'] = self.Cut('full_'+cutgroup.name,cutgroup[cut],node=thisnode)

        self.SetActiveNode(node)

        return nminusones

    def PrintNodeTree(self,outfilename,verbose=False,toSkip=[]):
        '''Print a PDF image of the node structure of the analysis.
        Requires python graphviz package which should be an installed dependency.

        @param outfilename (str): Name of output PDF file.
        @param verbose (bool, optional): Turns on verbose node labels. Defaults to False.
        @param toSkip ([], optional): Skip list of types of nodes (with sub-string matching
            so providing "Define" will cut out *all* definitions). Possible options
            are "Define", "Cut", "Correction", "MergeDefine", and "SubCollDefine".
            Defaults to empty list.

        Returns:
            None
        '''
        import networkx as nx
        graph = nx.DiGraph(comment='Node processing tree')
        # Build graph with all nodes
        for node in self.AllNodes:
            this_node_name = node.name
            this_node_label = node.name
            if verbose: this_node_label += '\n%s'%textwrap.fill(node.action,50)

            graph.add_node(this_node_name, label=this_node_label, type=node.type)
            for child in node.children:
                graph.add_edge(this_node_name,child.name)
        # Contract egdes where we want nodes dropped
        for skip in toSkip:
            for node in graph.nodes:
                if skip in graph.nodes[node]["type"]:
                    graph = nx.contracted_edge(graph,(graph.pred[node].keys()[0],node),self_loops=False)
        # Write out dot and draw
        dot = nx.nx_pydot.to_pydot(graph)
        extension = outfilename.split('.')[-1]
        filename = outfilename.split('.')[:-1]
        if extension not in [outfilename,'dot']:
            try:
                getattr(dot,'write_'+extension)(outfilename)
            except:
                print ('PrintNodeTree() warning!! File extension %s not supported by graphviz on this system. Will write out .dot instead.'%(extension))
                dot.write(filename+'.dot')
        elif extension == 'dot':
            dot.write(outfilename)
        elif extension == outfilename: # meaning, no '.' in outfilename
            dot.write(filename+'.dot')

    def MakeHistsWithBinning(self,histDict,name='',weight=None):
        '''Batch creates histograms at the current #ActiveNode based on the input `histDict`
        which is formatted as `{[<column name>]: <binning tuple>}` where `[<column name>]` is a list
        of column names that you'd like to plot against each other in [x,y,z] order and `binning_tuple` is
        the set of arguments that would normally be passed to `TH1`. The dimensions of the returned
        histograms are determined based on the size of `[<column name>]`.

        @param histDict ({std:tuple}): formatted as `{<column name>: <binning tuple>}` where `binning_tuple` are
            the arguments that would normally be passed to `TH1`. Size determines dimension of histogram.
        @param name (str, optional): Name for the output HistGroup. Defaults to '' in which case the name of the 
            #ActiveNode will be used.
        @param weight (str, optional): Weight (as a string) to apply to all histograms. Defaults to None.

        Returns:
            dict: Dictionary with same structure as the input (column names for keys) with 
                new histograms evaluated on the #ActiveNode as the values.
        '''
        out = HistGroup(name if name != '' else self.ActiveNode.name)
        
        for varnames in histDict.keys():
            # Modify hist name
            arg_list = list(histDict[varnames])
            arg_list[0] = arg_list[0] + '_' + out.name
            this_tuple = tuple(arg_list)
            # Convert key to list(str) if needed
            if isinstance(varnames,str):
                varnames = [varnames]
            # Get name for histgroup entry
            entry_name = '_vs_'.join(varnames)+'_'+out.name
            # Add weight to args if specified
            if len(varnames) == 1:
                if weight == None: 
                    h = self.DataFrame.Histo1D(this_tuple,varnames[0])
                else:
                    h = self.DataFrame.Histo1D(this_tuple,varnames[0],weight)
            elif len(varnames) == 2:
                if weight == None: 
                    h = self.DataFrame.Histo2D(this_tuple,varnames[0],varnames[1])
                else:
                    h = self.DataFrame.Histo2D(this_tuple,varnames[0],varnames[1],weight)
            elif len(varnames) == 3:
                if weight == None:
                    h = self.DataFrame.Histo3D(this_tuple,varnames[0],varnames[1],varnames[2])
                else:
                    h = self.DataFrame.Histo3D(this_tuple,varnames[0],varnames[1],varnames[2],weight)
            out.Add(entry_name, h)
           
        return out

##############
# Node Class #
##############
class Node(object):
    '''Class to represent nodes in the DataFrame processing graph. 
    Can make new nodes via Define, Cut, and Discriminate and setup
    relations between nodes (done automatically via Define, Cut, Discriminate)'''
    def __init__(self, name, DataFrame, action='', nodetype='', children=[]):
        '''Constructor. Holds the RDataFrame and other associated information
        for tracking in the {@link analyzer}.

        Methods which act on the RDataFrame always return a new node
        since RDataFrame is not modified in place.

        @param name (str): Name for the node. Duplicate named nodes cannot be tracked simultaneously in the analyzer.
        @param DataFrame (RDataFrame): Dataframe to track.
        @param children ([Node], optional): Child nodes if they exist. Defaults to [].
        @param nodetype (str, optional): The type of the Node. Useful for organizing and grouping Nodes. Defaults to ''.
        @param action (str, optional): Action performed (the C++ line). Default is '' but should only be used for a base RDataFrame.
        '''
        ## @var DataFrame
        #
        # DataFrame for the Node.
        ## @var name
        #
        # Name of the Node.
        ## @var action
        #
        # Action performed to create this Node.
        ## @var type
        #
        # Either 'Cut' or 'Define' depending what generated the Node.
        ## @var children
        #
        # List of child nodes.
        ## @var type
        #
        # The "type" of Node. Can be modified but by default will be either
        # "Define", "Cut", "MergeDefine", "SubCollDefine", or "Correction".

        super(Node, self).__init__()
        self.DataFrame = DataFrame
        self.name = name
        self.action = action
        self.children = children
        self.type = nodetype
        
    def Close(self):
        '''Safely deletes Node instance and all descendants.
        
        Returns:
            None
        '''
        for c in self.children:
            c.Close()
        self.children = []
        self.DataFrame = None
        self.name = None
        self.action = None

    def __str__(self):
        '''Call with `print(<Node>)` to print a nicely formatted description
        of the Node object for debugging.
        
        Returns:
            str
        '''
        out = 'NODE:\n'
        for a in dir(self):
            if not a.startswith('__') and not callable(getattr(self, a)):
                if a == 'children':
                    out += '\t {:15s} = {}\n'.format(a,[c.name for c in getattr(self,a)])
                else:
                    out += '\t {:15s} = {}\n'.format(a,getattr(self,a))
        return out[:-1]

    def Clone(self,name=''):
        '''Clones Node instance without child information and with new name if specified.

        @param name (str, optional): Name for clone. Defaults to current name.

        Returns:
            Node: Clone of current instance.
        '''
        if name == '':return Node(self.name,self.DataFrame,children=[],action=self.action)
        else: return Node(name,self.DataFrame,children=[],action=self.action)

    def SetChild(self,child,overwrite=False):
        '''Set one of child for the node.

        @param child (Node): Child node to add.
        @param overwrite (bool, optional): Overwrites all current children stored. Defaults to False.

        Raises:
            TypeError: If argument type is not Node.
        '''
        if overwrite: self.children = []

        if isinstance(child,Node):
            if child.name not in [c.name for c in self.children]:
                self.children.append(child)
            else:
                raise NameError('Attempting to add child node "%s" but one with this name already exists in node "%s" (%s).'%(child.name, self.name, [c.name for c in self.children]))
        else:
            raise TypeError('Child is not an instance of Node class for node %s' %self.name)

    def SetChildren(self,children,overwrite=False):
        '''Set multiple children for the node.

        @param children ([Node], {str:Node}): List of children or dictionary of children.
        @param overwrite (bool, optional): Overwrites all current children stored. Defaults to False.

        Raises:
            TypeError: If argument type is not dict or list of Node.
        '''
        if overwrite: self.children = []
        
        if isinstance(children,dict):
            for c in children.keys():
                if isinstance(c,Node):
                    self.SetChild(children[c])
                else:
                    raise TypeError('Child is not an instance of Node class for node %s' %self.name)

        elif isinstance(children,list):
            for c in children:
                if isinstance(c,Node):
                    self.SetChild(c)
                else:
                    raise TypeError('Child is not an instance of Node class for node %s' %self.name)
        else:
            raise TypeError('Attempting to add children that are not in a list or dict.')

    def Define(self,name,var,nodetype=None):
        '''Produces a new Node with the provided variable/column added.

        @param name (str): Name for the column for internal tracking and later reference.
        @param var (str): A one-line C++ string that evaluates to desired value to store. 
        @param nodetype (str, optional): Defaults to None in which case the new Node will
            be type "Define".

        Returns:
            Node: New Node object with new column added.
        '''
        print('Defining %s: %s' %(name,var))
        newNodeType = 'Define' if nodetype == None else nodetype
        newNode = Node(name,self.DataFrame.Define(name,var),children=[],action=var,nodetype=newNodeType)
        self.SetChild(newNode)
        return newNode

    def Cut(self,name,cut,nodetype=None):
        '''Produces a new Node with the provided cut/filter applied.

        @param name (str): Name for the cut for internal tracking and later reference.
        @param cut (str): A one-line C++ string that evaluates as a boolean.
        @param nodetype (str, optional): Defaults to None in which case the new Node will
            be type "Cut".

        Returns:
            Node: New Node object with cut applied.
        '''
        print('Filtering %s: %s' %(name,cut))
        newNodeType = 'Define' if nodetype == None else nodetype
        newNode = Node(name,self.DataFrame.Filter(cut,name),children=[],action=cut,nodetype=newNodeType)
        self.SetChild(newNode)
        return newNode

    def Discriminate(self,name,discriminator):
        '''Produces a dictionary with two new Nodes made by forking this Node based upon a discriminator being True or False.

        @param name (str): Name for the discrimination for internal tracking and later reference.
        @param discriminator (str): A one-line C++ string that evaluates as a bool to discriminate on.

        Returns:
            dict: Dictionary with keys "pass" and "fail" corresponding to the passing and failing Nodes stored as values.
        '''
        passfail = {
            "pass":Node(name+"_pass",self.DataFrame.Filter(discriminator,name+"_pass"),children=[],action=discriminator,nodetype='Cut'),
            "fail":Node(name+"_fail",self.DataFrame.Filter("!("+discriminator+")",name+"_fail"),children=[],action="!("+discriminator+")",nodetype='Cut')
        }
        self.SetChildren(passfail)
        return passfail
            
    def Apply(self,actionGroupList):
        '''Applies a single CutGroup/VarGroup or an ordered list of Groups to this Node to produce a new final Node.

        @param actionGroupList (Group, list(Group)): The CutGroup or VarGroup to act on node or a list of CutGroups or VarGroups to act (in order) on node.

        Raises:
            TypeError: If argument type is not Node.

        Returns:
            Node: New Node with all actions applied.
        '''
        if type(actionGroupList) != list: actionGroupList = [actionGroupList]
        node = self
        for ag in actionGroupList:
            if isinstance(ag,CutGroup):
                for c in ag.keys():
                    cut = ag[c]
                    node = node.Cut(c,cut)
            elif isinstance(ag,VarGroup):
                for v in ag.keys():
                    var = ag[v]
                    node = node.Define(v,var)
            else:
                raise TypeError("Group %s does not have a defined type. Please initialize with either CutGroup or VarGroup." %ag.name)                

        return node

    # IMPORTANT: When writing a variable size array through Snapshot, it is required that the column indicating its size is also written out and it appears before the array in the columns list.
    # columns should be an empty string if you'd like to keep everything
    def Snapshot(self,columns,outfilename,treename,lazy=False,openOption='RECREATE'): # columns can be a list or a regular expression or 'all'
        '''Takes a snapshot of the RDataFrame corresponding to this Node.
        Compression algorithm set to 1 (ZLIB) and compression level are set to 1.

        @param columns ([str] or str): List of columns to keep (str) with regex matching.
                Provide single string 'all' to include all columns.
        @param outfilename (str): Name of the output file
        @param treename ([type]): Name of the output TTree
        @param lazy (bool, optional): If False, the RDataFrame actions until this point will be executed here. Defaults to False.
        @param openOption (str, optional): TFile opening options. Defaults to 'RECREATE'.

        Returns:
            None
        '''
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fLazy = lazy
        opts.fMode = openOption
        opts.fCompressionAlgorithm =1 
        opts.fCompressionLevel = 1
        print("Snapshotting columns: %s"%columns)
        print("Saving tree %s to file %s"%(treename,outfilename))
        if columns == 'all':
            self.DataFrame.Snapshot(treename,outfilename,'',opts)
        elif type(columns) == str:
            self.DataFrame.Snapshot(treename,outfilename,columns,opts)
        else:
            column_vec = ''
            for c in columns:
                column_vec += c+'|'
            column_vec = column_vec[:-1]
            self.DataFrame.Snapshot(treename,outfilename,column_vec,opts)
      
##############################
# Group class and subclasses #
##############################
class Group(object):
    '''Organizes objects in OrderedDict with basic functionality to add and
    drop items, add Groups together, get keys, and access items.'''
    def __init__(self, name):
        '''Constructor

            name (str): Name for instance.
        '''
        ## @var name
        # str
        #
        # Name of Group
        ## @var items
        # OrderedDict()
        #
        # Items stored as an OrderedDict()
        ## @var type
        # string
        #
        # Group type - "cut", "var", "hist"
        super(Group, self).__init__()
        self.name = name
        self.items = OrderedDict()
        self.type = None

    def Add(self,name,item,makeCopy=False):
        '''Add item to Group with a name. Modifies in-place if copy == False.

        @param name (str): Name/key for added item.
        @param item (obj): Item to add.
        @param makeCopy (bool, optional): Creates a copy of the group with the item added.

        Returns:
            None
        '''
        if makeCopy:
            added = copy.deepcopy(self.items)
            added[name] = item
            if self.type == None: newGroup = Group(self.name+'+'+name)
            elif self.type == 'var': newGroup = VarGroup(self.name+'+'+name)
            elif self.type == 'cut': newGroup = CutGroup(self.name+'+'+name)
            newGroup.items = added
            return newGroup
        else:
            self.items[name] = item 
        
    def Drop(self,name,makeCopy=False):
        '''Drop item from Group with provided name/key. Modifies in-place if copy == False.

        @param name (str): Name/key for dropped item.
        @param makeCopy (bool, optional): Creates a copy of the group with the item dropped.

        Returns:
            None
        '''
        if makeCopy:
            dropped = copy.deepcopy(self.items)
            del dropped[name]
            if self.type == None: newGroup = Group(self.name+'-'+name)
            elif self.type == 'var': newGroup = VarGroup(self.name+'-'+name)
            elif self.type == 'cut': newGroup = CutGroup(self.name+'-'+name)
            newGroup.items = dropped
            return newGroup
        else:
            del self.items[name]

    def Clone(self,name):
        '''Clone the current group with a new name.

        @param name (str): Name for clone.

        Returns:
            Group: Group clone (will be VarGroup, CutGroup, or HistGroup if applicable).
        '''
        newGroup = copy.deepcopy(self.items)
        if self.type == None: newGroup = Group(name)
        elif self.type == 'var': newGroup = VarGroup(name)
        elif self.type == 'cut': newGroup = CutGroup(name)
        elif self.type == 'hist': newGroup = HistGroup(name)
        return newGroup

    def __add__(self,other):
        '''Adds two Groups together. Items in `other` override duplicates. 
        If groups do not have matching #type, a generic Group will be returned.
        Ex. `newgroup = group1 + group2`

        @param other (Group): Group to add to current Group. 

        Returns:
            Group: Addition of the two groups (will be VarGroup, CutGroup, or HistGroup if applicable).
        '''
        added = {}
        for k in self.items.keys():
            added[k] = self.items[k]
        for k in other.items.keys():
            added[k] = other.items[k]

        if self.type == 'var' and other.type == 'var': newGroup = VarGroup(self.name+"+"+other.name)
        elif self.type == 'cut' and other.type == 'cut': newGroup = CutGroup(self.name+"+"+other.name)
        elif self.type == 'hist' and other.type == 'hist': newGroup = HistGroup(self.name+"+"+other.name)
        else: newGroup = Group(self.name+"+"+other.name)
        newGroup.items = added
        return newGroup

    def keys(self):
        '''Gets list of keys from Group.

        Returns:
            list: Names/keys from Group.
        '''
        return list(self.items.keys())

    def values(self):
        '''Gets list of values from Group.

        Returns:
            list: Values from Group.
        '''
        return list(self.items.values())
    
    def __setitem__(self, key, value):
        '''Set key-value pair as you would with dictionary.
        Ex. `mygroup["item_name"] = new_value`

        @param key (obj): Key for value.
        @param value (obj): Value to store.
        '''
        self.items[key] = value

    def __getitem__(self,key):
        '''Get value from key as you would with dictionary.
        Ex. `val = mygroup["item_name"]`

        @param key (obj): Key for name/key in Group.
        Returns:
            obj: Item for given key.
        '''
        return self.items[key]

# Subclass for cuts
class CutGroup(Group):
    '''Stores Cut actions'''
    def __init__(self, name):
        '''Constructor

        @param name (str): Name for instance.
        '''
        super(CutGroup,self).__init__(name)
        ## @var type
        #
        # Set to 'cut' so group is treated as cut/filter actions.
        self.type = 'cut'
        
# Subclass for vars/columns
class VarGroup(Group):
    '''Stores Define actions'''
    def __init__(self, name):
        '''Constructor

        @param name (str): Name for instance.
        '''
        super(VarGroup,self).__init__(name)
        ## @var type
        #
        # Set to 'var' so group is treated as column definition actions.
        self.type = 'var'

# Subclass for histograms
class HistGroup(Group):
    '''Stores histograms with dedicated function to use TH1/2/3 methods in a batch'''
    def __init__(self, name):
        '''Constructor

        @param name (str): Name for instance.
        '''
        super(HistGroup,self).__init__(name)
        ## @var type
        #
        # Set to 'hist' so group is treated as histograms.
        self.type = 'hist'

    def Do(self,THmethod,argsTuple=()):
        '''Batch act on histograms using ROOT TH1/2/3 methods.

        @param THmethod (str): String of the ROOT TH1/2/3 method to use.
        @param argsTuple (tuple): Tuple of arguments to pass to THmethod.

        Returns:
            HistGroup or None: New HistGroup with THmethod applied if THmethod does not return None; else None.

        Example:
            To scale all histograms by 0.5
                myHistGroup.Do("Scale",(0.5))

        '''
        # Book new group in case THmethod returns something
        newGroup = HistGroup(self.name+'_%s%s'%(THmethod,argsTuple))
        # Initialize check for None return type
        returnNone = False
        # Loop over hists
        for name,hist in self.items.items():
            out = getattr(hist,THmethod)(*argsTuple)
            # If None type, set returnNone = True
            if out == None and returnNone == False: returnNone = True
            # If return is not None, add 
            if not returnNone:
                newGroup.Add(name+'_%s%s'%(THmethod,argsTuple),out)

        if returnNone: del newGroup
        else: return newGroup

    def Merge(self):
        '''Merge together the histograms in the group.

        Returns:
            TH1: Merged histogram.
        '''
        for ikey,key in enumerate(self.keys()):
            if ikey == 0:
                out = self[key].Clone(self.name)
            else:
                out.Add(self[key])
        return out

####################
# Correction class #
####################
class Correction(object):
    '''Class to handle corrections produced by C++ modules.

    Uses clang in python to parse the C++ code and determine function names, 
    namespaces, and argument names and types. 

    Writing the C++ modules has two requirements:

    (1) the desired branch/column names must be used as the argument variable names
    to allow the framework to automatically determine what branch/column to use in GetCall(),

    (2) the return must be a vector ordered as <nominal, up, down> for "weight" type and 
    <up, down> for "uncert" type.    

    '''
    def __init__(self,name,script,constructor=[],mainFunc='eval',corrtype='',columnList=None,isClone=False):
        '''Constructor

        @param name (str): Correction name.
        @param script (str): Path to C++ script with function to calculate correction.
        @param constructor ([str], optional): List of arguments to script class constructor. Defaults to [].
        @param mainFunc (str, optional): Name of the function to use inside script. Defaults to None
                and the class will try to deduce it.
        @param corrtype (str, optional): Either "weight" (nominal weight to apply with an uncertainty), "corr"
                (only a correction) or 
                "uncert" (only an uncertainty). Defaults to '' and the class will try to
                deduce it.
        @param columnList ([str], optional): List of column names to search mainFunc arguments against.
                Defaults to None and the standard NanoAOD columns from LoadColumnNames() will be used.
        @param isClone (bool, optional): For internal use when cloning. Defaults to False. If True, will
                not duplicate compile the same script if two functions are needed in one C++ script.
        '''

        ## @var name
        # str
        # Correction name

        self.name = name
        self.__script = self.__getScript(script)
        self.__setType(corrtype)
        self.__funcInfo = self.__getFuncInfo(mainFunc)
        self.__mainFunc = list(self.__funcInfo.keys())[0]
        self.__columnNames = LoadColumnNames() if columnList == None else columnList
        self.__constructor = constructor 
        self.__objectName = self.name
        self.__call = None
        # self.__funcNames = self.__funcInfo.keys()        

        if not isClone:
            if self.__mainFunc not in self.__funcInfo.keys():
                raise ValueError('Correction() instance provided with mainFunc argument does not exist in %s'%self.__script)
            CompileCpp(self.__script,library=True)

        self.__instantiate(constructor)

    def Clone(self,name,newMainFunc=None,newType=None):
        '''Makes a clone of current instance.

        If multiple functions are in the same script, one can clone the correction and reassign the mainFunc
        to avoid compiling the same script twice.

        @param name (str): Clone name.
        @param newMainFunc (str, optional): Name of the function to use inside script. Defaults to None and the original is used.
        @param newType (str, optional): New type for the cloned correction. Defaults to None and the original is used.
        Returns:
            Correction: Clone of instance with same script but different function (newMainFunc).
        '''
        if newMainFunc == None: newMainFunc = self.__mainFunc.split('::')[-1]
        return Correction(name,self.__script,self.__constructor,newMainFunc,
                          corrtype=self.__type if newType == None else newType,
                          isClone=True,columnList=self.__columnNames)

    def __getScript(self,script):
        '''Does a basic check that script file exists and modifies path if necessary
        so relative paths to TIMBER/Framework/ can be used.

        @param script (str): Name of script (must exist on system PATH).

        Raises:
            NameError: If file does not exist.

        Returns:
            str: File name.
        '''
        if TIMBERPATH in script: # global path given to TIMBER module
            outname = script
        elif 'TIMBER/Framework' in script: # relative path given to TIMBER module
            outname = TIMBERPATH+script
        else: # non-TIMBER module
            outname = script
        
        if not os.path.isfile(outname):
            raise NameError('File %s does not exist'%outname)
        return outname

    def __setType(self,inType):
        '''Sets the type of correction.
        Will attempt to deduce from input script name if inType=''. File name
        must have suffix '_weight' or '_SF' for weight type (correction plus uncertainties)
        or '_uncert' for 'uncert' type (only uncertainties).

        @param inType (str): Type of Correction. Use '' to deduce from input script name.

        Raises:
            NameError: If inType is '' and the type cannot be deduced from the input
                script name.
        '''
        out_type = None
        if inType in ['weight','uncert','corr']:
            out_type = inType
        elif inType not in ['weight','uncert','corr'] and inType != None:
            print ('WARNING: Correction type %s is not accepted. Only "weight" or "uncert". Will attempt to resolve...'%inType)

        if out_type == None:
            if '_weight.cc' in self.__script.lower() or '_sf.cc' in self.__script.lower():
                out_type = 'weight'
            elif '_uncert.cc' in self.__script.lower():
                out_type = 'uncert'
            else:
                raise NameError('Attempting to add correction "%s" but script name (%s) does not end in "_weight.cc", "_SF.cc" or "_uncert.cc" and so the type of correction cannot be determined.'%(self.name,self.__script))

        self.__type = out_type

    def __getFuncInfo(self,funcname):
        '''Parses script with clang to get the function information including name, namespace, and argument names.

        @param funcname (str): C++ class method name to search for in script.

        Returns:
            OrderedDict: Dictionary organized as `myreturn[methodname][argname] = argtype`.
        '''
        cpp_idx = cindex.Index.create()
        translation_unit = cpp_idx.parse(self.__script, args=cpp_args)
        filename = translation_unit.cursor.spelling
        funcs = OrderedDict()
        namespace = ''
        classname = None
        methodname = None

        print ('Parsing %s with clang...'%self.__script)
        # Walk cursor over script
        for c in translation_unit.cursor.walk_preorder():
            # Pass over file errors
            if c.location.file is None: pass
            elif c.location.file.name != filename: pass
            else:
                # Check for namespace with functions inside
                if c.kind == cindex.CursorKind.NAMESPACE:
                    namespace = c.spelling
                elif c.kind == cindex.CursorKind.CLASS_DECL or c.kind == cindex.CursorKind.CONSTRUCTOR:
                    classname = c.spelling
                elif c.kind == cindex.CursorKind.CXX_METHOD:
                    methodname = classname+'::'+c.spelling
                    if namespace != '': # this will not support classes outside of the namespace and always assume it's inside
                        methodname = namespace + '::' + methodname

                    # print methodname.split('::')[-1]
                    # print funcname
                    if methodname.split('::')[-1] == funcname:
                        # print methodname
                        if methodname not in funcs.keys():
                            # print methodname
                            funcs[methodname] = OrderedDict()
                            for arg in c.get_arguments():
                                funcs[methodname][arg.spelling] = arg.type.spelling 

        # print funcs
        return funcs

    def __instantiate(self,args):
        '''Instantiates the class in the provided script with the provided arguments.

        @param args ([str]): Ordered list of arguments to provide to C++ class to instantiate
                the object in memory.
        '''
        classname = self.__mainFunc.split('::')[-2]
        # constructor_name = classname+'::'+classname

        line = classname + ' ' + self.name+'('
        for a in args:
            line += a+', '

        if len(args) > 0:
            line = line[:-2] + ');'
        else:
            line = line[:-1] + ';'

        print ('Instantiating...'+line)
        ROOT.gInterpreter.Declare(line)

    def MakeCall(self,inArgs = []):
        '''Makes the call (stored in class instance) to the method with the branch/column names deduced or added from input.

        @param inArgs (list, optional): List of arguments (branch/column names) to provide to per-event evaluation method.
                Defaults to [] in which case the arguments are deduced from what is written in the C++ script.

        Raises:
            NameError: If argument written in C++ script cannot be found in available columns.
            ValueError: If provided number of arguments does not match the number in the method.

        Returns
            str: Call to function from C++ script.
        '''
        args_to_use = []

        if len(inArgs) == 0:
            print ('Determining arguments for correction %s automatically'%self.name)
            for a in self.__funcInfo[self.__mainFunc].keys():
                if a not in self.__columnNames:
                    raise NameError('Not able to find arg %s written in %s in available columns'%(a,self.__script))
                else:
                    args_to_use.append(a)

        else:
            if len(inArgs) < len(self.__funcInfo[self.__mainFunc].keys()):
                print ('Provided number of arguments (%s) does not match required (%s). Asssuming there are default arguments not specified...'%(len(inArgs),len(self.__funcInfo[self.__mainFunc].keys())))
            elif len(inArgs) > len(self.__funcInfo[self.__mainFunc].keys()):
                raise ValueError('Provided number of arguments (%s) does not match required (%s).'%(len(inArgs),len(self.__funcInfo[self.__mainFunc].keys())))
            args_to_use = inArgs

        # var_types = [self.__funcInfo[self.__mainFunc][a] for a in self.__funcInfo[self.__mainFunc].keys()]
        out = '%s('%(self.__objectName+'.'+self.__mainFunc.split('::')[-1])
        for i,a in enumerate(args_to_use):
            out += '%s, '%(a)
        out = out[:-2]+')'

        self.__call = out

    def GetCall(self,inArgs = []):
        '''Gets the call to the method to be evaluated per-event.

        @param inArgs (list, optional): Args to use for eval if #MakeCall() has not already been called. Defaults to [].
                If #MakeCall() has not already been called and inArgs == [], then the arguments to the method will
                be deduced from the C++ method definition argument names.

        Returns:
            str: The string that calls the method to evaluate per-event. Pass to Analyzer.Define(), Analyzer.Cut(), etc.
        '''
        if self.__call == None:
            self.MakeCall(self, inArgs)
        return self.__call

    def GetMainFunc(self):
        '''Gets full main function name.

        Returns:
            str: Name of function assigned from C++ script.
        '''
        return self.__mainFunc

    def GetType(self):
        '''Gets Correction type.

        Returns:
            str: Correction type.
        '''
        return self.__type

    def GetFuncNames(self):
        '''Gets list of function names in C++ script.

        Returns:
            [str]: List of possible function names found in C++ script.
        '''
        return list(self.__funcInfo.keys())

def LoadColumnNames(source=''):
    '''Loads column names from a text file.

    Args:
        @param source (str, optional): File location if default TIMBER/data/NanoAODv6_cols.txt
            is not to be used. Defaults to ''.

    Returns:
        [str]: List of all column names.
    '''
    if source == '': 
        file = TIMBERPATH+'TIMBER/data/NanoAODv6_cols.txt'
    else:
        file = source
    f = open(file,'r')
    cols = []
    for c in f.readlines():
        cols.append(c.strip('\n'))
    f.close()
    return cols
