from TIMBER.Tools.Common import CompileCpp
import re

class CollectionOrganizer:
    '''Tracks the available collections, collection attributes, and solo branches
    in the dataframe while processing. The initial set of branches will be read
    on startup and any new branch will be added accordingly. Collection names
    are deduced from the branch name by being the string before the first underscore
    (if there is an underscore).
    '''
    def __init__(self, rdf):
        '''Constructor

        @param rdf (RDataFrame): RDataFrame from which to organize.
        '''
        self._baseBranches = [str(b) for b in rdf.GetColumnNames()]
        self._generateFromRDF(rdf)
        self._builtCollections = []

    def _generateFromRDF(self, rdf):
        '''Generate the collection from the RDataFrame.

        @param rdf (RDataFrame): RDataFrame from which to organize.
        '''
        self._collectionDict = {}
        self._otherBranches = {}

        for b in self._baseBranches:
            if 'fCoordinates' in b: continue
            self.AddBranch(b,rdf.GetColumnType(b))

    def _parsetype(self, t):
        '''Deduce the type that TIMBER needs to see for the 
        collection structs. If t is an RVec, deduce the internal type
        of the RVec.

        @param t (str): Type name from RDataFrame.GetColumnType()

        Returns:
            str: TIMBER-friendly version of the type.
        '''
        nRVecs = len(re.findall('ROOT::VecOps::RVec<',t))
        if nRVecs == 0:
            collType = t
            isVect = False
        else:
            isVect = True
            collType = t.strip()
            collType = re.sub('ROOT::VecOps::RVec<','',collType,count=1)
            collType = re.sub('>','',collType,count=1)
            collType += ' &'
            if 'Bool_t' in collType:
                collType = collType.replace('Bool_t &','Bool_t&').replace('Bool_t&','std::_Bit_reference')
        
        if collType == ' &':
            collType = ''
        
        return collType, isVect

    def AddCollection(self, c):
        '''Add a collection to tracking.

        @param c (str): Collection name only.
        '''
        if c not in self._collectionDict.keys():
            self._collectionDict[c] = {'alias': False}

    def GetCollectionNames(self):
        '''Return the list of all collection names.

        Returns:
            list(str): All tracked collection names.
        '''
        return self._collectionDict.keys()

    def GetCollectionAttributes(self, c):
        '''Get all attributes of a collection. Example, for the 'Electron'
        collection, will return a list of `['pt', 'eta', ...]`.

        @param c (str): Collection name.

        Returns:
            list(str): List of attributes for the collection.
        '''
        return [c for c in self._collectionDict[c] if c != 'alias']

    def AddBranch(self, b, btype=''):
        '''Add a branch to track. Will deduce if it is in a collection
        in which case, the attribute will be added to the tracked collection.

        @param b (str): Branch name
        @param btype (str, optional): Type of branch. Defaults to '' but should only be left
            this way in rare cases.
        '''
        collname = b.split('_')[0]
        varname = '_'.join(b.split('_')[1:])
        typeStr, isVect = self._parsetype(btype)
        
        if typeStr == False or varname == '' or 'n'+collname not in self._baseBranches:
            matches = [m for m in self._otherBranches.keys() if (m.startswith(collname) and '_'.join(m.split('_')[1:]) != '')]
            if len(matches) == 0:
                self._otherBranches[b] = {
                    'type': typeStr,
                    'isVect': isVect,
                    'alias': False
                }
            else:
                if varname != '':
                    self.AddCollection(collname)
                    self._collectionDict[collname][varname] = {
                        'type': typeStr,
                        'isVect': isVect,
                        'alias': False
                    }
                    for match in matches:
                        self._collectionDict[collname]['_'.join(match.split('_')[1:])] = self._otherBranches[match]
                        del self._otherBranches[match]
        elif varname != '':
            self.AddCollection(collname)
            self._collectionDict[collname][varname] = {
                'type': typeStr,
                'isVect': isVect,
                'alias': False
            }

    def Alias(self, alias, name):
        '''Add an alias for a solo branch, collection, or collection attribute.

        @param alias (str): Alias name.
        @param name (str): Full branch name or a collection name. If an alias for a
            collection attribute is desired, provide the full branch name (ie. collectionName_attributeName).

        Raises:
            ValueError: Entries do not exist so an alias cannot be added.
        '''
        # Name is either in otherBranches, is a collection name, or is a full name <collection>_<attr>
        if name in self._otherBranches.keys():
            self._otherBranches[name]['alias'] = alias
        elif name in self._collectionDict.keys():
            self._collectionDict[name]['alias'] = alias
        else:
            collname = name.split('_')[0]
            varname = '_'.join(name.split('_')[1:])
            if collname in self._collectionDict.keys():
                if varname in self._collectionDict[collname].keys():
                    self._collectionDict[collname][varname]['alias'] = alias
                else:
                    raise ValueError('Cannot add alias `%s` because attribute `%s` does not exist in collection `%s`'%(alias,varname,collname))
            else:
                raise ValueError('Cannot add alias `%s` because collection `%s` does not exist'%(alias,collname))

    def BuildCppCollection(self,collection,node,silent=True):
        '''Build the collection as a struct in C++ so that it's accessible
        to the RDataFrame loop.

        @param collection (str): Collection name.
        @param node (Node): Node on which to act.
        @param silent (bool, optional): Whether output should be silenced. Defaults to True.

        Raises:
            RuntimeError: Collection already built.

        Returns:
            Node: Manipulated node with the collection struct now defined.
        '''
        newNode = node
        attributes = []
        for aname in self.GetCollectionAttributes(collection):
            if self._collectionDict[collection][aname]['isVect']:
                attributes.append('%s %s'%(self._collectionDict[collection][aname]['type'], aname))

        if collection+'s' not in self._builtCollections:
            self._builtCollections.append(collection+'s')
            CompileCpp(StructDef(collection,attributes))
            newNode = newNode.Define(collection+'s', StructObj(collection,attributes),silent=silent)
        else:
            raise RuntimeError('Collections `%s` already built.'%(collection+'s'))

        return newNode

    def CollectionDefCheck(self, action_str, node):
        '''Checks if a collection C++ struct is needed in the action string.
        If in the string but not defined, this function builds it. Does not
        apply the action.

        @param action_str (str): Action being performed on the Node/RDataFrame.
        @param node (Node): Node being acted on.

        Returns:
            Node: Manipulated node with the C++ struct built (the action string is not applied though).
        '''
        newNode = node
        for c in self._collectionDict.keys():
            if re.search(r"\b" + re.escape(c+'s') + r"\b", action_str) and (c+'s' not in self._builtCollections):
                print ('MAKING %ss for %s'%(c,action_str))
                newNode = self.BuildCppCollection(c,newNode,silent=True)
        return newNode

def StructDef(collectionName, varList):
    '''Defines the struct in C++/Cling memory.

    @param collectionName (str): Name of the collection to define.
    @param varList (str): List of attributes of the collection to include.

    Returns:
        str: C++ string defining the struct.
    '''
    out_str = '''
struct {0}Struct {{
        {1}
        {0}Struct({2}) :
        {3} {{
        }};
}};
    '''
    definitions = []
    ctor_args = []
    ctor_assign = []
    for i,v in enumerate(varList):
        definitions.append('%s; \n'%v)
        ctor_args.append('%s'%v)
        ctor_assign.append('%s(%s)'%(v.split(' ')[-1], v.split(' ')[-1]))

    out_str = out_str.format(collectionName, '\t'.join(definitions), ','.join(ctor_args),','.join(ctor_assign))
    return out_str

def StructObj(collectionName, varList):
    '''Initializes an instance of the C++ struct for the collection in C++/Cling memory.

    @param collectionName (str): Name of the collection to define.
    @param varList (str): List of attributes of the collection to include.

    Returns:
        str: C++ string defining the struct instance.
    '''
    out_str = '''
std::vector<{0}Struct> {0}s;
{0}s.reserve(n{0});
for (size_t i = 0; i < n{0}; i++) {{
    {0}s.emplace_back({1});
}}
return {0}s;
'''
    attr_assignment_str = ''
    for i,v in enumerate(varList):
        varname = v.split(' ')[-1]
        attr_assignment_str += '{0}_{1}[i],'.format(collectionName, varname)
    out_str = out_str.format(collectionName,attr_assignment_str[:-1])
    return out_str
