"""@docstring Analyzer.py

Home of main classes for HAMMER.

"""

import ROOT
import pprint, time, json, copy, os,sys
from collections import OrderedDict
pp = pprint.PrettyPrinter(indent=4)
from Tools.Common import GetHistBinningTuple, CompileCpp
from clang import cindex
cpp_idx = cindex.Index.create()
cpp_args =  '-x c++ --std=c++11'.split()

class analyzer(object):
    """Main class for HAMMER. 

    Implements an interface with ROOT's RDataFrame (RDF). The default values assume the data is in
    NanoAOD format. However, any TTree can be used. The class works on the basis of nodes and actions
    where nodes are an RDF instance and an action (or series of actions) can transform the RDF to create a new node(s).

    When using class functions to perform actions, an active node will always be tracked so that the next action uses 
    the active node and assigns the output node as the new active node"""
    def __init__(self,fileName,eventsTreeName="Events",runTreeName="Runs"):
        """
        Constructor

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
        # Initial RDataFrame - no modifications
        ## @var BaseNode
        # Node
        #
        # Initial Node - no modifications
        ## @var DataFrames
        # dict
        #
        # All data frames
        ## @var Corrections
        # dict
        #
        # All corrections added to track
        ## @var isData
        # bool
        #
        # Is data (true) or simulation (false) based on existence of _genEventCount branch
        ## @var preV6
        # bool
        #
        # Is pre-NanoAODv6 (true) or not (false) based on existence of _genEventCount branch
        ## @var genEventCount
        # int
        #
        # Number of generated events in imported simulation files. Zero if data.
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
                self.__eventsChain.Add(l.strip())
                RunChain.Add(l.strip())
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
        
        # Cleanup
        del RunChain
        self.ActiveNode = self.BaseNode
 
    def SetActiveNode(self,node):
        """Sets the active node.

        Args:
            node: Node to set as #ActiveNode

        Returns:
            New #ActiveNode
        """
        if not isinstance(node,Node): raise ValueError('ERROR: SetActiveNode() does not support argument of type %s. Please provide a Node.'%(type(node)))
        else: self.ActiveNode = node

        return self.ActiveNode

    def GetActiveNode(self):
        """Get the active node.

        Returns: 
            Value of #ActiveNode (Node)
        """
        return self.ActiveNode

    def GetBaseNode(self):
        """Get the base node.

        Returns: 
            Value of #BaseNode (Node)
        """
        return self.BaseNode

    def TrackNode(self,node):
        """Add a node to track. 

        Will add the node to #DataFrames dictionary with key node.name. Will raise ValueError if attempting to overwrite an already tracked Node.

        Args:
            node (Node): Node to start tracking. 

        Returns:
            None

        """
        
        if isinstance(node,Node):
            if node.name in self.GetTrackedNodeNames():
                raise ValueError('ERROR: Attempting to track a node with the same name as one that is already being tracked (%s). Please provide a unique node.'%(node.name))
            self.AllNodes.append(node)
        else:
            raise TypeError('ERROR: TrackNode() does not support arguments of type %s. Please provide a Node.'%(type(node)))

    def GetTrackedNodeNames(self):
        return [n.name for n in self.AllNodes]

    def GetCorrectionNames(self):
        """Get names of all corrections being tracked.

        Returns:
            List of Correction keys/names
        """
        return self.Corrections.keys()

    def FilterColumnNames(self,columns,node=None):
        '''Takes a list of possible columns and returns only those that exist in the RDataFrame of the supplied node'''
        if node == None: node = self.BaseNode
        cols_in_node = node.DataFrame.GetColumnNames()
        out = []
        for i in columns:
            if i in cols_in_node: out.append(i)
            else: print ("WARNING: Column %s not found and will be dropped."%i)

        return out

    #------------------------------------------------------------#
    # Node operations - same as Node class methods but have      #
    # benefit of class keeping track of an Active Node (reset by #
    # each action and used by default).                          #
    #------------------------------------------------------------#
    def Cut(self,name='',cuts='',node=None):
        """Apply a cut/filter to a provided node or the #ActiveNode by default.

        Will add the resulting node to tracking and set it as the #ActiveNode.

        Args:
            name (str): Name for the cut for internal tracking and later reference.
            cuts (str,CutGroup): A one-line C++ string that evaluates as a boolean or a CutGroup object which contains multiple C++ strings that evaluate as booleans. 
            node (Node): Node to apply the cut/filter. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.

        Returns:
            New active Node.

        """
        if node == None: node = self.ActiveNode
        newNode = node

        if isinstance(cuts,CutGroup):
            for c in cuts.keys():
                cut = cuts[c]
                newNode = newNode.Cut(c,cut)
                newNode.name = cuts.name+'__'+c
                self.TrackNode(newNode)
            # newNode.name = cuts.name
        elif isinstance(cuts,str):
            newNode = newNode.Cut(name,cuts)
            self.TrackNode(newNode)
        else:
            raise TypeError("ERROR: Second argument to Cut method must be a string of a single cut or of type CutGroup (which provides an OrderedDict).")

        # self.TrackNode(newNode)
        return self.SetActiveNode(newNode)

    def Define(self,name='',variables='',node=None):
        """Defines a variable/column on top of a provided node or the #ActiveNode by default.

        Will add the resulting node to tracking and set it as the #ActiveNode

        Args:

            name (str): Name for the column for internal tracking and later reference.
            cuts (str,CutGroup): A one-line C++ string that evaluates to desired value to store or a VarGroup object which contains multiple C++ strings that evaluate to the desired value(s). 
            node (Node): Node to create the new variable/column on top of. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.

        Returns:
            New active Node.

        """
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
            raise TypeError("ERROR: Second argument to Define method must be a string of a single var or of type VarGroup (which provides an OrderedDict).")

        # self.TrackNode(newNode)
        return self.SetActiveNode(newNode)

    # Applies a bunch of action groups (cut or var) in one-shot in the order they are given
    def Apply(self,actionGroupList,node=None,trackEach=True):
        """Applies a single CutGroup/VarGroup or an ordered list of Groups to the provided node or the #ActiveNode by default.

        Args:

            actionGroupList (Group, list(Group)): The CutGroup or VarGroup to act on node or a list of CutGroups or VarGroups to act (in order) on node.
            node (Node): Node to create the new variable/column on top of. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.

        Returns:
            New active Node.
        """
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
                    raise TypeError("ERROR: Apply() group %s does not have a defined type. Please initialize with either CutGroup or VarGroup." %ag.name)

        return self.SetActiveNode(newNode)

    def Discriminate(self,name,discriminator,node=None,passAsActiveNode=None):
        """Forks a node based upon a discriminator being True or False (#ActiveNode by default).

        Args:
            name (str): Name for the discrimination for internal tracking and later reference.
            discriminator (str): A one-line C++ string that evaluates as a boolean to discriminate for the forking of the node.
            node (Node): Node to discriminate. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.
            passAsActiveNode (bool): True if the #ActiveNode should be set to the node that passes the discriminator.
                False if the #ActiveNode should be set to the node that fails the discriminator. Defaults to None in which case the #ActiveNode does not change.

        Returns:
            Dictionary with keys "pass" and "fail" corresponding to the passing and failing Nodes stored as values.
            
        """
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
    def AddCorrection(self,correction,node=None):
        """Add a Correction to track.

        Args:
            correction (Correction): Correction object to add.
            node (Node): Node to add correction on top of. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.

        Returns:
            New active Node.

        """
        if node == None: node = self.ActiveNode

        # Quick type checking
        if not isinstance(node,Node): raise TypeError('ERROR: AddCorrection() does not support argument of type %s for node. Please provide a Node.'%(type(node)))
        elif not isinstance(correction,Correction): raise TypeError('ERROR: AddCorrection() does not support argument type %s for correction. Please provide a Correction.'%(type(correction)))

        # Add correction to track
        self.Corrections[correction.name] = correction

        # Make new node
        newNode = node.Define(correction.name+'__vec',correction.GetCall())
        if correction.type == 'weight':
            returnNode = newNode.Define(correction.name+'__nom',correction.name+'__vec[0]').Define(correction.name+'__up',correction.name+'__vec[1]').Define(correction.name+'__down',correction.name+'__vec[2]')
        elif correction.type == 'uncert':
            returnNode = newNode.Define(correction.name+'__up',correction.name+'__vec[0]').Define(correction.name+'__down',correction.name+'__vec[1]')

        self.TrackNode(returnNode)
        return self.SetActiveNode(returnNode)

    def AddCorrections(self,correctionList=[],node=None):
        """Add multiple Corrections to track.

        Args:
            correctionList (list(Correction)): List of Correction objects to add.
            node (Node): Node to add corrections on top of. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.

        Returns:
            New active Node.

        """
        if node == None: node = self.ActiveNode

        newNode = node
        for c in correctionList:
            newNode = self.AddCorrection(newNode,c)

        self.TrackNode(newNode)
        return self.SetActiveNode(newNode)

    def MakeWeightCols(self,node=None,correctionNames=None,dropList=[]):
        """Makes columns/variables to store total weights based on the Corrections that have been added.

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
            New active Node.

        """
        if node == None: node = self.ActiveNode

        correctionsToApply = _checkCorrections(correctionNames,dropList)
        
        # Build nominal weight first (only "weight", no "uncert")
        weights = {'nominal':''}
        for corrname in correctionsToApply:
            corr = self.Corrections[corrname] # MIGHT BE ABLE TO REMOVE THIS LINE AND THE STORING OF Correction INSTANCES ENTIRELY (ie just store names)
            if corr.GetType() == 'weight':
                weights['nominal']+=corrname+'__nom * '
            weights['nominal'] = weights['nominal'][:-3]

        # Vary nominal weight for each correction ("weight" and "uncert")
        for corrname in correctionsToApply:
            corr = self.Corrections[corrname]
            if corr.GetType() == 'weight':
                weights[corrname+'_up'] = weights['nominal'].replace(corrname+'__nom',corrname+'__up')
                weights[corrname+'_down'] = weights['nominal'].replace(corrname+'__nom',corrname+'__down')
            elif corr.GetType() == 'uncert':
                weights[corrname+'_up'] = weights['nominal']+' * '+corrname+'__up'
                weights[corrname+'_down'] = weights['nominal']+' * '+corrname+'__down'
            else:
                raise TypeError('ERROR: Correction "%s" not identified as either "weight" or "uncert"'%(corrname))

        # Make a node with all weights calculated
        returnNode = node
        for weight in weights.keys():
            returnNode = returnNode.Define('weight__'+weight,weights[weight])
        
        self.TrackNode(returnNode)
        return self.SetActiveNode(returnNode)

    def MakeTemplateHistos(self,templateHist,variables,node=None):
        """Generates the uncertainty template histograms based on the weights created by MakeWeightCols(). 

        Args:
            templateHist (TH1,TH2,TH3): An TH1, TH2, or TH3 used as a template to create the histograms.
            variables (list(str)): A list of the columns/variables to plot (["x","y","z"]).
            node (Node): Node to plot histograms from. Must be of type Node (not RDataFrame). Defaults to #ActiveNode.

        Returns:
            HistGroup object which stores the uncertainty template histograms.

        """
        if node == None: node = self.ActiveNode

        out = HistGroup('Templates')

        weight_cols = [cname for cname in node.GetColumnNames() if 'weight__' in cname]
        baseName = templateHist.GetName()
        baseTitle = templateHist.GetTitle()
        binningTuple,dimension = GetHistBinningTuple(templateHist)

        for c in weight_cols:
            histname = '%s__%s'%(baseName,cname.replace('weight__',''))
            histtitle = '%s__%s'%(baseTitle,cname.replace('weight__',''))

            # Build the tuple to give as argument for template
            template_attr = (histname,histtitle) + binningTuple

            if dimension == 1: thishist = node.DataFrame.Histo1D(template_attr,variables[0],cname)
            elif dimension == 2: thishist = node.DataFrame.Histo2D(template_attr,variables[0],variables[1],cname)
            elif dimension == 3: thishist = node.DataFrame.Histo3D(template_attr,variables[0],variables[1],variables[2],cname)
           
            out.Add(histname,thishist)

        return out

    #----------------------------------------------------------------#
    # Draw templates together to see up/down effects against nominal #
    #----------------------------------------------------------------#
    def DrawTemplates(hGroup,saveLocation,projection='X',projectionArgs=(),fileType='pdf'):
        """Draw the template uncertainty histograms created by MakeTemplateHistos(). 

        Args:
            hGroup (HistGroup): A HistGroup object storing the uncertainty template histograms.
            saveLocation (str): Path to folder to save histograms.
            projection (str): "X" (Default), "Y", or "Z". Axis to project onto if templates are not 1D.
            projectionArgs (tuple): A tuple of arguments provided to ROOT TH1 ProjectionX(Y)(Z).
            fileType (str): File type - "pdf", "png", etc (must be supported by TCanvas.Print()).

        Returns:
            None

        """
        canvas = TCanvas('c','',800,700)

        # Initial setup
        baseName = list(hGroup.keys())[0].split('__')[0]

        if isinstance(hGroup[baseName+'__nominal'],ROOT.TH2):
            projectedGroup = hGroup.Do("Projection"+projection.upper(),projectionArgs)
        if isinstance(hGroup[baseName+'__nominal'],ROOT.TH3): 
            raise TypeError("ERROR: DrawTemplates() does not currently support TH3 templates.")
        else:
            projectedGroup = hGroup

        nominal = projectedGroup[baseName+'__nominal']
        nominal.SetLineColor(kBlack)
        nominal.SetFillColor(kYellow-2)
        corrections = []
        for name in projectedGroup.keys():
            corr = name.split('__')[1].split('_')[0]
            if corr not in corrections:
                corrections.append(corr)

        # Loop over corrections
        for corr in corrections:
            nominal.Draw('hist')

            up = projectedGroup[baseName+'__'+corr+'_up']
            down = projectedGroup[baseName+'__'+corr+'_down']

            up.SetLineColor(kRed)
            down.SetLineColor(kBlue)

            leg = TLegend(0.8,0.8,0.9,0.9)
            leg.AddEntry('Nominal',nominal,'lf')
            leg.AddEntry('Up',up,'l')
            leg.AddEntry('Down',down,'l')

            up.Draw('same hist')
            down.Draw('same hist')
            leg.Draw()

            canvas.Print('%s/%s_%s.%s'%(saveLocation,baseName,corr,fileType),fileType)

    #----------------------------------------------#
    # Build N-1 "tree" and outputs the final nodes #
    # Beneficial to put most aggressive cuts first #
    # Return dictionary of N-1 nodes keyed by the  #
    # cut that gets dropped                        #
    #----------------------------------------------#
    def Nminus1(self,node,cutgroup):
        """Print a PDF image of the node structure of the analysis. 
        Requires python graphviz package (`pip install graphviz`) 

        Args:
            cutgroup (CutGroup): CutGroup that you'd like to scan.

        Returns:
            Dictionary with the final nodes

        """

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

        return nminusones

    def PrintNodeTree(self,outfilename,verbose=False):
        """Print a PDF image of the node structure of the analysis. Requires python graphviz package (`pip install graphviz`) 

        Args:
            outfilename (str): Name of output PDF file.

        Returns:
            None

        """
        from graphviz import Digraph
        dot = Digraph(comment='Node processing tree')
        for node in self.AllNodes:
            this_node_name = node.name
            this_node_label = node.name
            if verbose: this_node_label += '\n%s'%node.action

            # # Build larger label if requested
            # for o in options:
            #     if 'statusFlags' in o:
            #         flag = o.split(':')[1]
            #         this_node_label += '\n%s=%s'%(flag,n.statusFlags[flag])
            #     elif 'vect' in o:
            #         kin = o.split(':')[1]
            #         this_node_label += '\n%s=%s'%(kin,getattr(n.vect,kin)())
            #     else:
            #         this_node_label += '\n%s=%s'%(o,getattr(n,o))
            #
            # if jet != None:
            #     this_node_label += '\n%s=%.2f'%('\Delta R with jet',n.DeltaR(jet))

            dot.node(this_node_name, this_node_label)
            for child in node.children:
                dot.edge(this_node_name,child.name)
        
        dot.render(outfilename)

    #-------------------#
    # Private functions #
    #-------------------#
    def __checkCorrections(self,correctionNames,dropList):
        # Quick type checking
        if correctionNames == None: correctionsToApply = self.Corrections.keys()
        elif not isinstance(correctionNames,list):
            raise ValueError('ERROR: MakeWeights() does not support correctionNames argument of type %s. Please provide a list.'%(type(correctionNames)))
        else: correctionsToApply = correctionNames

        # Drop specified weights from consideration
        if not isinstance(dropList,list):
            raise ValueError('ERROR: MakeWeights() does not support dropList argument of type %s. Please provide a list.'%(type(dropList)))
        else: 
            newCorrsToApply = []
            for corr in correctionsToApply:
                if corr not in dropList: newCorrsToApply.append(corr)
            correctionsToApply = newCorrsToApply

        return correctionsToApply


##############
# Node Class #
##############
class Node(object):
    """Class to represent nodes in the DataFrame processing graph. Can make new nodes via Define, Cut, and Discriminate and setup relations between nodes (done automatically via Define, Cut, Discriminate)"""
    def __init__(self, name, DataFrame, parent=None, children=[],action=''):
        super(Node, self).__init__()
        self.DataFrame = DataFrame
        self.name = name
        self.action = action
        self.parent = parent # None or specified
        self.children = children # list of length 0, 1, or 2
        
    def Clone(self,name=''):
        if name == '':return Node(self.name,self.DataFrame,parent=[],children=[],action=self.action)
        else: return Node(name,self.DataFrame,parent=[],children=[],action=self.action)

    # Set parent of type Node
    def SetParent(self,parent): 
        if isinstance(parent,Node): self.parent = parent
        else: raise TypeError('ERROR: Parent is not an instance of Node class for node %s'%self.name)

    # Set one child of type Node
    def SetChild(self,child,overwrite=False,silence=False):
        if overwrite: self.children = []
        # if len(children > 1): raise ValueError("ERROR: More than two children are trying to be added node %s. You may use the overwrite option to erase current children or find your bug."%self.name)
        # if len(children == 1) and silence == False: raw_input('WARNING: One child is already specified for node %s and you are attempting to add another (max 2). Press enter to confirm and continue.'%self.name)

        if isinstance(child,Node): self.children.append(child)
        else: raise TypeError('ERROR: Child is not an instance of Node class for node %s' %self.name)

    # Set children of type Node
    def SetChildren(self,children,overwrite=False):
        if overwrite: self.children = []
        # if len(children > 0): raise ValueError("ERROR: More than two children are trying to be added node %s. You may use the overwrite option to erase current children or find your bug."%self.name)
        
        if isinstance(children,dict) and 'pass' in children.keys() and 'fail' in children.keys() and len(children.keys()) == 2:
            self.SetChild(children['pass'])
            self.SetChild(children['fail'])
        else:
            raise TypeError('ERROR: Attempting to add a dictionary of children of incorrect format. Argument must be a dict of format {"pass":class.Node,"fail":class.Node}')

    # Define a new column to calculate
    def Define(self,name,var):
        print('Defining %s: %s' %(name,var))
        newNode = Node(name,self.DataFrame.Define(name,var),parent=self,children=[],action=var)
        self.SetChild(newNode)
        return newNode

    # Define a new cut to make
    def Cut(self,name,cut):
        print('Filtering %s: %s' %(name,cut))
        newNode = Node(name,self.DataFrame.Filter(cut,name),parent=self,children=[],action=cut)
        self.SetChild(newNode)
        return newNode

    # Discriminate based on a discriminator
    def Discriminate(self,name,discriminator):
        passfail = {
            "pass":Node(name+"_pass",self.DataFrame.Filter(discriminator,name+"_pass"),parent=self,children=[],action=discriminator),
            "fail":Node(name+"_fail",self.DataFrame.Filter("!("+discriminator+")",name+"_fail"),parent=self,children=[],action="!("+discriminator+")")
        }
        self.SetChildren(passfail)
        return passfail
            
    # Applies a bunch of action groups (cut or var) in one-shot in the order they are given
    def Apply(self,actiongrouplist):
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
                raise TypeError("ERROR: Group %s does not have a defined type. Please initialize with either CutGroup or VarGroup." %ag.name)                

        return node


    # IMPORTANT: When writing a variable size array through Snapshot, it is required that the column indicating its size is also written out and it appears before the array in the columns list.
    # columns should be an empty string if you'd like to keep everything
    def Snapshot(self,columns,outfilename,treename,lazy=False,openOption='RECREATE'): # columns can be a list or a regular expression or 'all'
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
            # column_vec = ROOT.std.vector('string')()
            column_vec = ''
            for c in columns:
                column_vec += c+'|'
            column_vec = column_vec[:-1]
               # column_vec.push_back(c)
            self.DataFrame.Snapshot(treename,outfilename,column_vec,opts)

###############################
# C script processing classes #
###############################
class CommonCscripts(object):
    """Common c scripts all in analyzer namespace"""
    def __init__(self):
        super(CommonCscripts, self).__init__()
        self.deltaPhi ='''
        namespace analyzer {
          double deltaPhi(double phi1,double phi2) {
            double result = phi1 - phi2;
            while (result > TMath::Pi()) result -= 2*TMath::Pi();
            while (result <= -TMath::Pi()) result += 2*TMath::Pi();
            return result;
          }
        }
        '''
        self.vector = '''
        namespace analyzer {
            ROOT::Math::PtEtaPhiMVector TLvector(float pt,float eta,float phi,float m) {
                ROOT::Math::PtEtaPhiMVector v(pt,eta,phi,m);
                return v;
            }
        }
        '''
        self.invariantMass = '''
        namespace analyzer {
            double invariantMass(ROOT::Math::PtEtaPhiMVector v1, ROOT::Math::PtEtaPhiMVector v2) {
                return (v1+v2).M();
            }
        }
        '''
        self.invariantMassThree = '''
        namespace analyzer {
            double invariantMassThree(ROOT::Math::PtEtaPhiMVector v1, ROOT::Math::PtEtaPhiMVector v2, ROOT::Math::PtEtaPhiMVector v3) {
                return (v1+v2+v3).M();
            }
        }
        '''
        self.HT = '''
        namespace analyzer {
            float HT(std::vector<int> v) {
                float ht = 0.0;
                for(int pt : v) {
                    ht = ht + pt
                }
                return ht;
            }
        }
        '''
        
class CustomCscripts(object):
    """docstring for CustomCscripts"""
    def __init__(self):
        super(CustomCscripts, self).__init__()
        self.example = '''
        namespace analyzer {
            return 0
        }
        '''
        
    def Import(self,textfilename,name=None):
        if name == None: name = textfilename.split('/')[-1].replace('.cc','')
        if not os.path.isfile(textfilename): raise NameError('ERROR: %s does not exist'%textfilename)
        else: print('Found '+textfilename)
        f = open(textfilename,'r')
        blockcode = f.read()
        setattr(self,name,blockcode)
        CompileCpp(blockcode)


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
    def __init__(self,name,script,mainFunc=None,corrtype=None,isClone=False):
        """Constructor

        Args:
            name (str): Correction name.
            script (str): Path to C++ script with function to calculate correction.
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
        self.__script = script
        self.__type = self._getType()
        self.__funcInfo = self._getFuncInfo()
        self.__funcNames = self.__funcInfo.keys()
        self.__mainFunc = mainFunc

        if not isClone:
            if mainFunc != None and self.__mainFunc not in self.__funcNames:
                raise ValueError('ERROR: Correction() instance provided with mainFunc argument that does not exist in %s'%self.__script)
            if len(self.__funcNames) == 1: self.__mainFunc = self.__funcNames[0]

            script_file = open(script,'r')
            CompileCpp(script)

    def Clone(self,name,newMainFunc=None):
        """Makes a clone of current instance.

        If multiple functions are in the same script, one can clone the correction and reassign the mainFunc
        to avoid compiling the same script twice.

        Args:
            name (str): Clone name.
            newMainFunc (str): Name of the function to use inside script. Defaults to same as original.
        Returns:
            Clone of instance with same script but different function (newMainFunc)
        """
        if newMainFunc == None: newMainFunc = self.__mainFunc
        return Correction(name,self.__script,newMainFunc,corrtype=self.__type,isClone=True)

    def __getType(self):
        self.__type = None
        if corrtype in ['weight','uncert']:
            self.__type = corrtype
        elif corrtype not in ['weight','uncert'] and corrtype != None:
            print ('WARNING: Correction type %s is not accepted. Only "weight" or "uncert". Will attempt to resolve...')

        if self.__type == None:
            if '_weight.cc' in self.__script or '_SF.cc' in self.__script:
                self.__type = 'weight'
            elif '_uncert.cc' in self.__script:
                self.__type = 'uncert'
            else:
                raise ValueError('ERROR: Attempting to add correction "%s" but script name (%s) does not end in "_weight.cc", "_SF.cc" or "_uncert.cc" and so the type of correction cannot be determined.'%(name))

    def __getFuncInfo(self):
        translation_unit = cpp_idx.parse(self.__script, args=cpp_args)
        filename = translation_unit.cursor.spelling
        funcs = OrderedDict()
        # Walk cursor over script
        for c in translation_unit.cursor.walk_preorder():
            # Pass over file errors
            if c.location.file is None: pass
            elif c.location.file.name != filename: pass
            else:
                # Check for namespace with functions inside
                if c.kind == cindex.CursorKind.NAMESPACE:
                    # Loop over children of namespace
                    for child in c.get_children():
                        # If a function, store a name as key with namespace included (does not support nested namespaces)
                        if child.kind == cindex.CursorKind.FUNCTION_DECL:
                            funcname = c.spelling+'::'+child.spelling
                            # If we haven't accounted for it, store key as arg name and value as the type
                            if funcname not in funcs.keys():
                                funcs[funcname] = OrderedDict()
                                for arg in child.get_arguments():
                                    funcs[funcname][arg.spelling] = arg.type.spelling 
                # Check for functions
                elif c.kind == cindex.CursorKind.FUNCTION_DECL:
                    func_exists = False
                    # Check it wasn't already found in the namespace
                    for existing_func in funcs.keys():
                        this_func = c.spelling
                        if this_func in existing_func:
                            func_exists = True
                    # If we haven't accounted for it, store key as arg name and value as the type
                    if not func_exists:
                        funcs[c.spelling] = OrderedDict()
                        for arg in c.get_arguments():
                            funcs[c.spelling][arg.spelling] = arg.type.spelling

        return funcs

    def GetCall(self):
        """Return the call to the function with the branch/column names deduced.

        Returns:
            String of call to function from C++ script.
        """
        out = '%s('
        for a in self.__funcInfo[self.__mainFunc].keys():
            out += '%s,'%(self.__funcInfo[self.__mainFunc][a],a)
        out = out[:-1]+')'

        return out

    def SetMainFunc(self,funcname):
        """Set the function to consider in the provided script.

        Will check if funcname exists as a function in the script (can also provide a substring of the
        desired function). If it does, sets the function to the matching one.

        Returns:
            Self with new function assigned.
        """

        # Find funcname in case it's abbreviated (which it might be if the user forgot the namespace)
        full_funcname = ''
        for f in self.__funcNames:
            if funcname in f:
                full_funcname = f
                break

        if full_funcname not in self.__funcNames:
            raise ValueError('ERROR: Function name "%s" is not defined for %s'%(funcname,self.__script))

        self.__mainFunc = full_funcname
        return self

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
        return self.__funcNames
