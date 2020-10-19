"""@docstring Analyzer.py

Home of main classes for TIMBER.

"""

import ROOT
import pprint, time, json, copy, os, sys, subprocess
from collections import OrderedDict
pp = pprint.PrettyPrinter(indent=4)
from TIMBER.Tools.Common import GetHistBinningTuple, CompileCpp
from clang import cindex

# For parsing c++ modules
from clang import cindex
libs = subprocess.Popen('$ROOTSYS/bin/root-config --libs',shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
rootpath = subprocess.Popen('echo $ROOTSYS',shell=True, stdout=subprocess.PIPE).communicate()[0].strip()
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
        """
        Constructor. Setups the tracking of actions on an RDataFrame as nodes. Also
        looks up and stores common information in NanoAOD such as the number of generated
        events in a file (#genEventCount), the LHA ID of the PDF set in the `LHEPdfWeights`
        branch (#lhaid), if the file is data (#isData), and if the file is before NanoAOD
        version 6 (#preV6).

        Args:
            fileName (str): A ROOT file path or the path to a txt file which contains several ROOT file paths separated by 
                new line characters.

            eventsTreeName (str): Name of TTree in fileName where events are stored. Defaults to "Events" (for NanoAOD)
            
            runTreeName (str): NAme of TTree in fileName where run information is stored (for generated event info in 
                simulation). Defaults to "Runs" (for NanoAOD) 
        """

        ## @var BaseDataFrame 
        # ROOT.RDataFrame
        #
        # Initial RDataFrame - no modifications.
        ## @var BaseNode
        # Node
        #
        # Initial Node - no modifications.
        ## @var DataFrames
        # dict
        #
        # All data frames.
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
        # LHA ID of the PDF weight set in the NanoAOD. -1 if not found or data.
        ## @var ActiveNode
        # Node
        #
        # Active node. Access via GetActiveNode(). Set via SetActiveNode().

        super(analyzer, self).__init__()
        self.__fileName = fileName 
        self.__eventsTreeName = eventsTreeName

        # Setup TChains for multiple or single file
        self.__eventsChain = ROOT.TChain(self.__eventsTreeName) 
        RunChain = ROOT.TChain(runTreeName) # Has generated event count information - will be deleted after initialization
        if ".root" in self.__fileName: 
            self.__eventsChain.Add(self.__fileName)
            RunChain.Add(self.__fileName)
        elif ".txt" in self.__fileName: 
            txt_file = open(self.__fileName,"r")
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
        self.AllNodes = [] 
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
 
    @property
    def DataFrame(self):
        '''
        Returns:
            RDataFrame: Dataframe for the active node.
        '''        
        return self.ActiveNode.DataFrame

    def Snapshot(self,columns,outfilename,treename,lazy=False,openOption='RECREATE'):
        '''@see Node#Snapshot'''
        self.ActiveNode.Snapshot(columns,outfilename,treename,lazy,openOption)

    def SetActiveNode(self,node):
        '''Sets the active node.

        Args:
            node (Node): Node to set as #ActiveNode.

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
        Will add the node to #DataFrames dictionary with key node.name.

        Args:
            node (Node): Node to start tracking.

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
        '''
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

        Args:
            columns ([str]): List of column names (str)
            node (Node, optional): Node to compare against. Defaults to #BaseNode.

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

    def ConcatCols(self,colnames,val='1',connector='&&'):
        '''Concatenates a list of column names evaluating to a common `val` (usually 1 or 0) 
        with some `connector` (boolean logic operator).

        Args:
            colnames ([str]): List of column names (str).
            val (str, optional): Value to test equality of all columns. Defaults to '1'.
            connector (str, optional): C++ boolean logic operator between column equality checks. Defaults to '&&'.

        Returns:
            str: Concatenated string of the entire evaluation that in C++ will return a bool.
        '''
        concat = ''
        for i,c in enumerate(colnames):
            if concat == '': 
                concat = '((%s==%s)'%(c,val)
            else: 
                concat += ' %s (%s==%s)'%(connector,c,val)

        if concat != '': 
            concat += ')' 
            
        return concat

    def GetTriggerString(self,trigList):
        '''Checks input list for missing triggers and drops those missing (#FilterColumnNames)
        and then concatenates those remaining into an OR (`||`) string (#ConcatCols)

        Args:
            trigList [str]: List of trigger names 

        Returns:
            str: Statement to evaluate as the set of triggers.
        '''
        trig_string = ''
        available_trigs = self.FilterColumnNames(trigList)
        trig_string = self.ConcatCols(available_trigs,'1','||')
        return trig_string

    def GetFlagString(self,flagList):
        '''Checks input list for missing flags and drops those missing (#FilterColumnNames)
        and then concatenates those remaining into an AND string (#ConcatCols)

        Args:
            flagList [str]: List of flag names 

        Returns:
            str: Statement to evaluate as the set of flags.
        '''
        flag_string = ''
        available_flags = self.FilterColumnNames(flagList)
        flag_string = self.ConcatCols(available_flags,'1','&&')
        return flag_string

    def GetFileName(self):
        '''Get input file name.

        Returns:
            str: File name
        '''
        return self.__fileName

    #------------------------------------------------------------#
    # Node operations - same as Node class methods but have      #
    # benefit of class keeping track of an Active Node (reset by #
    # each action and used by default).                          #
    #------------------------------------------------------------#
    def Cut(self,name,cuts,node=None):
        '''Apply a cut/filter to a provided node or the #ActiveNode by default.
        Will add the resulting node to tracking and set it as the #ActiveNode.

        Args:
            name (str): Name for the cut for internal tracking and later reference.
            cuts (str,#CutGroup): A one-line C++ string that evaluates as a boolean or a CutGroup object which contains multiple actions that evaluate as booleans.
            node (Node, optional): Node on which to apply the cut/filter. Defaults to #ActiveNode.

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
                newNode = newNode.Cut(c,cut)
                newNode.name = cuts.name+'__'+c
                self.TrackNode(newNode)
        elif isinstance(cuts,str):
            newNode = newNode.Cut(name,cuts)
            self.TrackNode(newNode)
        else:
            raise TypeError("Second argument to Cut method must be a string of a single cut or of type CutGroup (which provides an OrderedDict).")

        return self.SetActiveNode(newNode)

    def Define(self,name,variables,node=None):
        '''Defines a variable/column on top of a provided node or the #ActiveNode by default.
        Will add the resulting node to tracking and set it as the #ActiveNode.

        Args:
            name (str): Name for the column for internal tracking and later reference.
            cuts (str,#VarGroup): A one-line C++ string that evaluates to desired value to store
                or a #VarGroup object which contains multiple actions that evaluate to the desired values. 
            node (Node, optional): Node to create the new variable/column on top of. Defaults to #ActiveNode.

        Raises:
            TypeError: If argument type is not Node.

        Returns:
            Node: New #ActiveNode.
        '''
        if node == None: node = self.ActiveNode
        newNode = node

        if isinstance(variables,VarGroup):
            for v in variables.keys():
                var = variables[v]
                newNode = newNode.Define(v,var)
                newNode.name = variables.name+'__'+v
                self.TrackNode(newNode)
            # newNode.name = variables.name
        elif isinstance(variables,str):
            newNode = newNode.Define(name,variables)
            self.TrackNode(newNode)
        else:
            raise TypeError("Second argument to Define method must be a string of a single var or of type VarGroup (which provides an OrderedDict).")

        # self.TrackNode(newNode)
        return self.SetActiveNode(newNode)

    # Applies a bunch of action groups (cut or var) in one-shot in the order they are given
    def Apply(self,actionGroupList,node=None,trackEach=True):
        '''Applies a single CutGroup/VarGroup or an ordered list of Groups to the provided node or the #ActiveNode by default.

        Args:
            actionGroupList (Group, list(Group)): The CutGroup or VarGroup to act on node or a list of CutGroups or VarGroups to act (in order) on node.
            node ([type], optional): Node to create the new variable/column on top of. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.
            trackEach (bool, optional): [description]. Defaults to True.

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

        Args:
            name (str): Name for the discrimination for internal tracking and later reference.
            discriminator (str): A one-line C++ string that evaluates as a boolean to discriminate for the forking of the node.
            node (Node, optional): Node to discriminate. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.
            passAsActiveNode (bool, optional): True if the #ActiveNode should be set to the node that passes the discriminator.
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

    #---------------------#
    # Corrections/Weights #
    #---------------------#
    # Want to correct with analyzer class so we can track what corrections have been made for final weights and if we want to save them out in a group when snapshotting
    def AddCorrection(self,correction,evalArgs=[],node=None):
        '''Add a Correction to track. Sets new active node with all correction
        variations calculated as new columns.

        Args:
            correction (Correction): Correction object to add.
            evalArgs ([str], optional): List of arguments (NanoAOD branch names) to provide to per-event evaluation method.
                              Default empty and clang will deduce if method definition argument names match columns in RDataFrame.
            node (Node, optional): Node to add correction on top of. Defaults to #ActiveNode.

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
        newNode = self.Define(correction.name+'__vec',correction.GetCall(),node)
        if correction.GetType() == 'weight':
            variations = ['nom','up','down']
        elif correction.GetType() == 'uncert':
            variations = ['up','down']
        else:
            raise ValueError('Correction.GetType() returns %s'%correction.GetType())

        for i,v in enumerate(variations):
            newNode = self.Define(correction.name+'__'+v,correction.name+'__vec[%s]'%i,newNode)

        # self.TrackNode(returnNode)
        return self.SetActiveNode(newNode)

    def AddCorrections(self,correctionList,node=None):
        '''Add multiple Corrections to track. Sets new #ActiveNode with all correction
        variations calculated as new columns.

        Args:
            correctionList ([Correction]): List of Correction objects to add.
            node (Node, optional): [description]. Defaults to None.

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

        Args:
            correctionNames ([str]): List of correction names to include.
            dropList ([type]): List of correction names to drop.

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

        Args:
            node (Node): Node to calculate weights on top of. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.
            correctionNames list(str): List of correction names (strings) to consider. Default is None in which case all corrections
                being tracked are considered.
            dropList list(str): List of correction names (strings) to not consider. Default is empty lists in which case no corrections
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
            if corr.GetType() == 'weight':
                weights['nominal']+=' '+corrname+'__nom *'
        weights['nominal'] = weights['nominal'][:-2]

        # Vary nominal weight for each correction ("weight" and "uncert")
        for corrname in correctionsToApply:
            corr = self.Corrections[corrname]
            if corr.GetType() == 'weight':
                weights[corrname+'_up'] = weights['nominal'].replace(' '+corrname+'__nom',' '+corrname+'__up') #extra space at beginning of replace to avoid substrings
                weights[corrname+'_down'] = weights['nominal'].replace(' '+corrname+'__nom',' '+corrname+'__down')
            elif corr.GetType() == 'uncert':
                weights[corrname+'_up'] = weights['nominal']+' * '+corrname+'__up'
                weights[corrname+'_down'] = weights['nominal']+' * '+corrname+'__down'
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

        Args:
            templateHist (TH1,TH2,TH3): A TH1, TH2, or TH3 used as a template to create the histograms.
            variables ([str]): A list of the columns/variables to plot (ex. ["x","y","z"]).
            node (Node): Node to plot histograms from. Defaults to #ActiveNode.

        Returns:
            HistGroup: Uncertainty template histograms.
        '''
        if node == None: node = self.ActiveNode

        out = HistGroup('Templates')

        weight_cols = [cname for cname in node.DataFrame.GetColumnNames() if 'weight__' in cname]
        baseName = templateHist.GetName()
        baseTitle = templateHist.GetTitle()
        binningTuple,dimension = GetHistBinningTuple(templateHist)

        if isinstance(variables,str): variables = [variables]

        for cname in weight_cols:
            histname = '%s__%s'%(baseName,cname.replace('weight__',''))
            histtitle = '%s__%s'%(baseTitle,cname.replace('weight__','').replace('__nominal',''))

            # Build the tuple to give as argument for template
            template_attr = (histname,histtitle) + binningTuple

            if dimension == 1: 
                thishist = node.DataFrame.Histo1D(template_attr,variables[0],cname)
                thishist.GetXaxis().SetTitle(variables[0])
            elif dimension == 2: 
                thishist = node.DataFrame.Histo2D(template_attr,variables[0],variables[1],cname)
                thishist.GetXaxis().SetTitle(variables[0])
                thishist.GetYaxis().SetTitle(variables[1])
            elif dimension == 3: 
                thishist = node.DataFrame.Histo3D(template_attr,variables[0],variables[1],variables[2],cname)
                thishist.GetXaxis().SetTitle(variables[0])
                thishist.GetYaxis().SetTitle(variables[1])
                thishist.GetZaxis().SetTitle(variables[2])

            out.Add(histname,thishist)

        return out

    #----------------------------------------------------------------#
    # Draw templates together to see up/down effects against nominal #
    #----------------------------------------------------------------#
    def DrawTemplates(self,hGroup,saveLocation,projection='X',projectionArgs=(),fileType='pdf'):
        '''Draw the template uncertainty histograms created by #MakeTemplateHistos(). 

        Args:
            hGroup (HistGroup): Uncertainty template histograms.
            saveLocation (str): Path to folder to save histograms.
            projection (str, optional): "X" (Default), "Y", or "Z". Axis to project onto if templates are not 1D.
            projectionArgs (tuple, optional): A tuple of arguments provided to ROOT TH1 ProjectionX(Y)(Z).
            fileType (str, optional): File type - "pdf", "png", etc (must be supported by TCanvas.Print()).

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
            leg.AddEntry(nominal.GetName(),'Nominal','lf')
            leg.AddEntry(up.GetName(),'Up','l')
            leg.AddEntry(down.GetName(),'Down','l')

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
    def Nminus1(self,node,cutgroup):
        '''Create an N-1 tree structure of nodes building off of `node`
        with the N cuts from `cutgroup`.

        The structure is optimized so that as many actions are shared as possible
        so that the N different nodes can be made. Use #PrintNodeTree() to visualize. 

        Args:
            node (Node): Node to build on.
            cutgroup (CutGroup): Group of N cuts to apply.

        Returns:
            dict: N nodes in dictionary with keys indicating the cut that was not applied.
        '''
        # Initialize
        print ('Performing N-1 scan for CutGroup %s'%cutgroup.name)

        nminusones = {}
        thisnode = node
        thiscutgroup = cutgroup

        # Loop over all cuts (`cut` is the name not the string to filter on)
        for cut in cutgroup.keys():
            # Get the N-1 group of this cut (where N is determined by thiscutgroup)
            minusgroup = thiscutgroup.Drop(cut)
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

    def PrintNodeTree(self,outfilename,verbose=False):
        '''Print a PDF image of the node structure of the analysis.
        Requires python graphviz package which should be an installed dependency.

        Args:
            outfilename (str): Name of output PDF file.
            verbose (bool, optional): Turns on verbose node labels. Defaults to False.

        Returns:
            None
        '''
        from graphviz import Digraph
        dot = Digraph(comment='Node processing tree')
        for node in self.AllNodes:
            this_node_name = node.name
            this_node_label = node.name
            if verbose: this_node_label += '\n%s'%node.action

            dot.node(this_node_name, this_node_label)
            for child in node.children:
                dot.edge(this_node_name,child.name)
        
        dot.render(outfilename)

##############
# Node Class #
##############
class Node(object):
    '''Class to represent nodes in the DataFrame processing graph. 
    Can make new nodes via Define, Cut, and Discriminate and setup
    relations between nodes (done automatically via Define, Cut, Discriminate)'''
    def __init__(self, name, DataFrame, action='', children=[]):
        '''Constructor. Holds the RDataFrame and other associated information
        for tracking in the #analyzer().

        Methods which act on the RDataFrame always return a new node
        since RDataFrame is not modified in place.

        Args:
            name (str): Name for the node. Duplicate named nodes cannot be tracked simultaneously in the analyzer.
            DataFrame (RDataFrame): Dataframe to track.
            children ([Node], optional): Child nodes if they exist. Defaults to [].
            action (str, optional): Action performed (the C++ line). Default is '' but should only be used for a base RDataFrame.
        '''
        super(Node, self).__init__()
        self.DataFrame = DataFrame
        self.name = name
        self.action = action
        self.children = children
        
    def Clone(self,name=''):
        '''Clones Node instance without child information and with new name if specified.

        Args:
            name (str, optional): Name for clone. Defaults to current name.

        Returns:
            Node: Clone of current instance.
        '''
        if name == '':return Node(self.name,self.DataFrame,children=[],action=self.action)
        else: return Node(name,self.DataFrame,children=[],action=self.action)

    def SetChild(self,child,overwrite=False):
        '''Set one of child for the node.

        Args:
            child (Node): Child node to add.
            overwrite (bool, optional): Overwrites all current children stored. Defaults to False.

        Raises:
            TypeError: If argument type is not Node.
        '''
        if overwrite: self.children = []

        if isinstance(child,Node):
            if child.name not in [c.name for c in self.children]:
                self.children.append(child)
            else:
                raise NameError('Attempting to add child node "%s" but one with this name already exists in node "%s".'%(child.name, self.name))
        else:
            raise TypeError('Child is not an instance of Node class for node %s' %self.name)

    def SetChildren(self,children,overwrite=False):
        '''Set multiple children for the node.

        Args:
            children ([Node], {str:Node}): List of children or dictionary of children.
            overwrite (bool, optional): Overwrites all current children stored. Defaults to False.

        Raises:
            TypeError: If argument type is not dict or list of Node.
        '''
        if overwrite: self.children = []
        
        if isinstance(children,dict):
            for c in children.keys():
                if isinstance(child,Node):
                    self.SetChild(children[c])
                else:
                    raise TypeError('Child is not an instance of Node class for node %s' %self.name)

        elif isinstance(children,list):
            for c in children:
                if isinstance(child,node):
                    self.SetChild(c)
                else:
                    raise TypeError('Child is not an instance of Node class for node %s' %self.name)
        else:
            raise TypeError('Attempting to add chidren that are not in a list or dict.')

    def Define(self,name,var):
        '''Produces a new Node with the provided variable/column added.

        Args:
            name (str): Name for the column for internal tracking and later reference.
            cuts (str): A one-line C++ string that evaluates to desired value to store. 

        Returns:
            Node: New Node object with new column added.
        '''
        print('Defining %s: %s' %(name,var))
        newNode = Node(name,self.DataFrame.Define(name,var),children=[],action=var)
        self.SetChild(newNode)
        return newNode

    def Cut(self,name,cut):
        '''Produces a new Node with the provided cut/filter applied.

        Args:
            name (str): Name for the cut for internal tracking and later reference.
            cuts (str): A one-line C++ string that evaluates as a boolean.

        Returns:
            Node: New #ActiveNode.
        '''
        print('Filtering %s: %s' %(name,cut))
        newNode = Node(name,self.DataFrame.Filter(cut,name),children=[],action=cut)
        self.SetChild(newNode)
        return newNode

    def Discriminate(self,name,discriminator):
        '''Produces a dictionary with two new Nodes made by forking the current node based upon a discriminator being True or False.

        Args:
            name (str): Name for the discrimination for internal tracking and later reference.
            discriminator (str): A one-line C++ string that evaluates as a boolean to discriminate on.

        Returns:
            dict: Dictionary with keys "pass" and "fail" corresponding to the passing and failing Nodes stored as values.
        '''
        passfail = {
            "pass":Node(name+"_pass",self.DataFrame.Filter(discriminator,name+"_pass"),children=[],action=discriminator),
            "fail":Node(name+"_fail",self.DataFrame.Filter("!("+discriminator+")",name+"_fail"),children=[],action="!("+discriminator+")")
        }
        self.SetChildren(passfail)
        return passfail
            
    def Apply(self,actiongrouplist):
        '''Applies a single CutGroup/VarGroup or an ordered list of Groups to the provided node or the #ActiveNode by default.

        Args:
            actionGroupList (Group, list(Group)): The CutGroup or VarGroup to act on node or a list of CutGroups or VarGroups to act (in order) on node.
            node ([type], optional): Node to create the new variable/column on top of. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.
            trackEach (bool, optional): [description]. Defaults to True.

        Raises:
            TypeError: If argument type is not Node.

        Returns:
            Node: New #ActiveNode.
        '''
        if type(actiongrouplist) != list: actiongrouplist = [actiongrouplist]
        node = self
        for ag in actiongrouplist:
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

        Args:
            columns ([str] or str): List of columns to keep (str) with regex matching.
                Provide single string 'all' to include all columns.
            outfilename (str): Name of the output file
            treename ([type]): Name of the output TTree
            lazy (bool, optional): If False, the RDataFrame actions until this point will be executed here. Defaults to False.
            openOption (str, optional): TFile opening options. Defaults to 'RECREATE'.
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
    """Organizes objects in OrderedDict with basic functionality to add and drop items, add Groups together, get keys, and access items."""
    def __init__(self, name):
        """Constructor

        Args:
            name: Name (string) for instance.
        """

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

    def Add(self,name,item):
        """Add item to Group with a name.

        Args:
            name (str): Name/key (string) for added item.
            item (obj): Item to add.

        Returns:
            None
        """
        self.items[name] = item 
        
    def Drop(self,name):
        """Drop item from Group with provided name/key.

        Args:
            name (str): Name/key (string) for dropped item.

        Returns:
            New group with item dropped.
        """
        dropped = copy.deepcopy(self.items)
        del dropped[name]
        if self.type == None: newGroup = Group(self.name+'-'+name)
        elif self.type == 'var': newGroup = VarGroup(self.name+'-'+name)
        elif self.type == 'cut': newGroup = CutGroup(self.name+'-'+name)
        newGroup.items = dropped
        return newGroup

    def __add__(self,other):
        """Adds two Groups together.

        Args:
            other (Group): Group to add to current Group.

        Returns:
            Addition of the two groups.
        """
        added = copy.deepcopy(self.items)
        added.update(other.items)
        if self.type == 'var' and other.type == 'var': newGroup = VarGroup(self.name+"+"+other.name)
        elif self.type == 'cut' and other.type == 'cut': newGroup = CutGroup(self.name+"+"+other.name)
        else: newGroup = Group(self.name+"+"+other.name)
        newGroup.items = added
        return newGroup

    def keys(self):
        """Gets list of keys from Group.
        Returns:
            Names/keys from Group.
        """
        return self.items.keys()

    def values(self):
        """Gets list of values from Group.
        Returns:
            Values from Group.
        """
        return self.items.values()
    
    def __setitem__(self, key, value):
        self.items[key] = value

    def __getitem__(self,key):
        """
        Args:
            key: Key for name/key in Group.
        Returns:
            Item for given key.
        """
        return self.items[key]

# Subclass for cuts
class CutGroup(Group):
    """Stores Cut actions"""
    def __init__(self, name):
        """
        Args:
            name: Name (string) for instance.
        """
        ## @var type
        # string
        #
        # Group type - "cut", "var", "hist"
        super(CutGroup,self).__init__(name)
        self.type = 'cut'
        
# Subclass for vars/columns
class VarGroup(Group):
    """Stores Define actions"""
    def __init__(self, name):
        """
        Args:
            name: Name (string) for instance.
        """
        ## @var type
        # string
        #
        # Group type - "cut", "var", "hist"
        super(VarGroup,self).__init__(name)
        self.type = 'var'

# Subclass for histograms
class HistGroup(Group):
    """Stores histograms with dedicated function to use TH1/2/3 methods in a batch"""
    def __init__(self, name):
        """
        Args:
            name: Name (string) for instance.
        """
        ## @var type
        # string
        #
        # Group type - "cut", "var", "hist"
        super(HistGroup,self).__init__(name)
        self.type = 'hist'

    #  - THmethod is a string and argsTuple is a tuple of arguments to pass the THmethod
    def Do(self,THmethod,argsTuple=()):
        '''Batch act on histograms using ROOT TH1/2/3 methods.

        Args:
            THmethod (str): String of the ROOT TH1/2/3 method to use.
            argsTuple (tuple): Tuple of arguments to pass to THmethod.
        Returns:
            New HistGroup with THmethod applied if THmethod does not return None. Else None.
        Example:
            To scale all histograms by 0.5
                myHistGroup.Do("Scale",(0.5))

        '''
        # Book new group in case THmethod returns something
        newGroup = Group(self.name+'_%s%s'%(THmethod,argsTuple))
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


####################
# Correction class #
####################
class Correction(object):
    """Correction class to handle corrections produced by C++ modules.

    Uses clang in python to parse the C++ code and determine function names, 
    namespaces, and argument names and types. 

    Writing the C++ modules has two requirements:

    (1) the desired branch/column names must be used as the argument variable names
    to allow the framework to automatically determine what branch/column to use in GetCall(),

    (2) the return must be a vector ordered as <nominal, up, down> for "weight" type and 
    <up, down> for "uncert" type.    

    """
    def __init__(self,name,script,constructor=[],mainFunc='eval',corrtype=None,columnList=None,isClone=False,existingObject=None):
        """Constructor

        Args:
            name (str): Correction name.
            script (str): Path to C++ script with function to calculate correction.
            constructor ([str]): Arguments to script class constructor.
            mainFunc (str): Name of the function to use inside script. Defaults to None
                and the class will try to deduce it.
            corrtype (str): "weight" (nominal weight to apply with an uncertainty) or 
                "uncert" (only an uncertainty). Defaults to None and the class will try to
                deduce it.
            isClone (bool): For internal use when cloning. Defaults to False.

        """

        ## @var name
        # str
        # Correction name

        self.name = name
        self.__script = self.__getScript(script)
        self.__setType(corrtype)
        self.__funcInfo = self.__getFuncInfo(mainFunc)
        self.__mainFunc = self.__funcInfo.keys()[0]
        self.__columnNames = LoadColumnNames() if columnList == None else columnList
        self.__constructor = constructor 
        self.__objectName = self.name if existingObject == None else existingObject
        self.__call = None
        # self.__funcNames = self.__funcInfo.keys()        

        if not isClone or existingObject == None:
            if self.__mainFunc not in self.__funcInfo.keys():
                raise ValueError('Correction() instance provided with mainFunc argument that does not exist in %s'%self.__script)
            CompileCpp(self.__script,library=True)

        if existingObject == None:
            self.__instantiate(constructor)      

        

    def Clone(self,name,newMainFunc=None,cpObj=False):
        """Makes a clone of current instance.

        If multiple functions are in the same script, one can clone the correction and reassign the mainFunc
        to avoid compiling the same script twice.

        Args:
            name (str): Clone name.
            newMainFunc (str): Name of the function to use inside script. Defaults to same as original.
        Returns:
            Clone of instance with same script but different function (newMainFunc)
        """
        if newMainFunc == None: newMainFunc = self.__mainFunc.split('::')[-1]

        useObj = None if not cpObj else self.name

        return Correction(name,self.__script,self.__constructor,newMainFunc,corrtype=self.__type,isClone=True,columnList=self.__columnNames,existingObject=useObj)

    def __getScript(self,script):
        if ('TIMBER/Framework' not in script) or (TIMBERPATH in script):
            outname = script
        else:
            outname = TIMBERPATH+script
        
        if not os.path.isfile(outname):
            raise NameError('File %s does not exist'%outname)
        return outname

    def __setType(self,in_type):
        out_type = None
        if in_type in ['weight','uncert']:
            out_type = in_type
        elif in_type not in ['weight','uncert'] and in_type != None:
            print ('WARNING: Correction type %s is not accepted. Only "weight" or "uncert". Will attempt to resolve...')

        if out_type == None:
            if '_weight.cc' in self.__script.lower() or '_sf.cc' in self.__script.lower():
                out_type = 'weight'
            elif '_uncert.cc' in self.__script.lower():
                out_type = 'uncert'
            else:
                raise ValueError('Attempting to add correction "%s" but script name (%s) does not end in "_weight.cc", "_SF.cc" or "_uncert.cc" and so the type of correction cannot be determined.'%(self.name,self.__script))

        self.__type = out_type

    def __getFuncInfo(self,funcname):
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
        classname = self.__mainFunc.split('::')[-2]
        # constructor_name = classname+'::'+classname

        line = classname + ' ' + self.name+'('
        for a in args:
            line += a+', '
        line = line[:-2] + ');'

        print ('Instantiating...')
        ROOT.gInterpreter.Declare(line)

    def MakeCall(self,inArgs):
        """Return the call to the function with the branch/column names deduced or added from input.

        Returns:
            inArgs ([str]): List of arguments (NanoAOD branch names) to provide to per-event evaluation method.
            String of call to function from C++ script.
        """

        args_to_use = []

        if len(inArgs) == 0:
            print ('Determining arguments for correction %s automatically'%self.name)
            for a in self.__funcInfo[self.__mainFunc].keys():
                if a not in self.__columnNames:
                    raise ValueError('Not able to find arg %s written in %s in available columns'%(a,self.__script))
                else:
                    args_to_use.append(a)

        else:
            if len(inArgs) != len(self.__funcInfo[self.__mainFunc].keys()):
                raise ValueError('Provided number of arguments (%s) does not match required (%s).'%(len(inArgs),len(self.__funcInfo[self.__mainFunc].keys())))
            args_to_use = inArgs

        # var_types = [self.__funcInfo[self.__mainFunc][a] for a in self.__funcInfo[self.__mainFunc].keys()]
        out = '%s('%(self.__objectName+'.'+self.__mainFunc.split('::')[-1])
        for i,a in enumerate(args_to_use):
            out += '%s, '%(a)
        out = out[:-2]+')'

        self.__call = out

    def GetCall(self):
        return self.__call

    # def SetMainFunc(self,funcname):
    #     """Set the function to consider in the provided script.

    #     Will check if funcname exists as a function in the script (can also provide a substring of the
    #     desired function). If it does, sets the function to the matching one.

    #     Returns:
    #         Self with new function assigned.
    #     """

    #     # Find funcname in case it's abbreviated (which it might be if the user forgot the namespace)
    #     full_funcname = ''
    #     for f in self.__funcNames:
    #         if funcname in f:
    #             full_funcname = f
    #             break

    #     if full_funcname not in self.__funcNames:
    #         raise ValueError('Function name "%s" is not defined for %s'%(funcname,self.__script))

    #     self.__mainFunc = full_funcname
    #     return self

    def GetMainFunc(self):
        """Gets full main function name.
        Returns:
            Name of function assigned from C++ script.
        """
        return self.__mainFunc

    def GetType(self):
        """Gets Correction type.
        Returns:
            Correction type.
        """
        return self.__type

    def GetFuncNames(self):
        """Gets list of function names in C++ script.
        Returns:
            List of possible function names.
        """
        return self.__funcInfo.keys()

def LoadColumnNames(source=None):
    if source == None: 
        file = TIMBERPATH+'TIMBER/data/NanoAODv6_cols.txt'
    else:
        file = source
    f = open(file,'r')
    cols = []
    for c in f.readlines():
        cols.append(c.strip('\n'))
    f.close()
    return cols
