'''@docstring Group.py

Home of Node class for handling and tracking of RDataFrame objects
'''

import ROOT
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
        self._colnames = self.DataFrame.GetColumnNames()
        
    def Clone(self,name=''):
        if name == '':return Node(self.name,self.DataFrame,parent=self.parent,children=self.children,action=self.action)
        else: return Node(name,self.DataFrame,parent=self.parent,children=self.children,action=self.action)

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
        newNode = Node(name,self.DataFrame.Define(name,var),parent=self,action=var)
        self.SetChild(newNode)
        return newNode

    # Define a new cut to make
    def Cut(self,name,cut):
        print('Filtering %s: %s' %(name,cut))
        newNode = Node(name,self.DataFrame.Filter(cut,name),parent=self,action=cut)
        self.SetChild(newNode)
        return newNode

    # Discriminate based on a discriminator
    def Discriminate(self,name,discriminator):
        pass_sel = self.DataFrame
        fail_sel = self.DataFrame
        passfail = {
            "pass":Node(name+"_pass",pass_sel.Filter(discriminator,name+"_pass"),parent=self,action=discriminator),
            "fail":Node(name+"_fail",fail_sel.Filter("!("+discriminator+")",name+"_fail"),parent=self,action="!("+discriminator+")")
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
    def Snapshot(self,columns,outfilename,treename,lazy=False): # columns can be a list or a regular expression or 'all'
        lazy_opt = ROOT.RDF.RSnapshotOptions()
        lazy_opt.fLazy = lazy
        print("Snapshotting columns: %s"%columns)
        print("Saving tree %s to file %s"%(treename,outfilename))
        if columns == 'all':
            self.DataFrame.Snapshot(treename,outfilename,'',lazy_opt)
        if type(columns) == str:
            self.DataFrame.Snapshot(treename,outfilename,columns,lazy_opt)
        else:
            # column_vec = ROOT.std.vector('string')()
            column_vec = ''
            for c in columns:
                column_vec += c+'|'
            column_vec = column_vec[:-1]
               # column_vec.push_back(c)
            self.DataFrame.Snapshot(treename,outfilename,column_vec,lazy_opt)