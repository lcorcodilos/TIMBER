from TIMBER.Tools.Common import CompileCpp
import re
'''
- Check for current handling of __collectionDict in Analyzer and replace with this
- Replace instances of BuildCollectionDict and GetKeyValForBranch
- Write ProcessLine
- Implement ProcessLine in analyzer
'''
class CollectionOrganizer:
    def __init__(self, rdf):
        self.baseBranches = [str(b) for b in rdf.GetColumnNames()]
        self.generateFromRDF(rdf)
        self.builtCollections = []

    def generateFromRDF(self, rdf):
        self.collectionDict = {}
        self.otherBranches = {}

        for b in self.baseBranches:
            self.AddBranch(b,rdf.GetColumnType(b))

    def parsetype(self, t):
        if not t.startswith('ROOT::VecOps::RVec<'):
            collType = False
        else:
            collType = str(t).replace('ROOT::VecOps::RVec<','')
            if collType.endswith('>'):
                collType = collType[:-1]
            collType += '&'
            if 'Bool_t' in collType:
                collType = collType.replace('Bool_t&','std::_Bit_reference')
        
        if collType == '&':
            collType = ''
        
        return collType

    def AddCollection(self, c):
        if c not in self.collectionDict.keys():
            self.collectionDict[c] = {'alias': False}

    def GetCollectionAttributes(self, c):
        return [c for c in self.collectionDict[c] if c != 'alias']

    def AddBranch(self, b, btype=''):
        collname = b.split('_')[0]
        varname = '_'.join(b.split('_')[1:])
        typeStr = self.parsetype(btype)
        
        if typeStr == False or varname == '' or 'n'+collname not in self.baseBranches:
            self.otherBranches[b] = {
                'type': typeStr,
                'alias': False
            }
        elif varname != '':
            self.AddCollection(collname)
            self.collectionDict[collname][varname] = {
                'type': typeStr,
                'alias': False
            }

    def Alias(self, alias, name):
        # Name is either in otherBranches, is a collection name, or is a full name <collection>_<attr>
        if name in self.otherBranches.keys():
            self.otherBranches[name]['alias'] = alias
        elif name in self.collectionDict.keys():
            self.collectionDict[name]['alias'] = alias
        else:
            collname = name.split('_')[0]
            varname = '_'.join(name.split('_')[1:])
            if collname in self.collectionDict.keys():
                if varname in self.collectionDict[collname].keys():
                    self.collectionDict[collname][varname]['alias'] = alias
                else:
                    raise ValueError('Cannot add alias `%s` because attribute `%s` does not exist in collection `%s`'%(alias,varname,collname))
            else:
                raise ValueError('Cannot add alias `%s` because collection `%s` does not exist'%(alias,collname))

    def ProcessLine(self, line):
        return line

    def BuildCppCollection(self,collection,node,silent=True):
        newNode = node
        attributes = []
        for aname in self.GetCollectionAttributes(collection):
            attributes.append('%s %s'%(self.collectionDict[collection][aname]['type'], aname))

        if collection+'s' not in self.builtCollections:
            self.builtCollections.append(collection+'s')
            CompileCpp(StructDef(collection,attributes))
            newNode = newNode.Define(collection+'s', StructObj(collection,attributes),silent=silent)
        else:
            raise RuntimeError('Collections `%s` already built.'%(collection+'s'))

        return newNode

    def CollectionDefCheck(self, action_str, node):
        newNode = node
        for c in self.collectionDict.keys():
            if re.search(r"\b" + re.escape(c+'s') + r"\b", action_str) and (c+'s' not in self.builtCollections):
                print ('MAKING %ss for %s'%(c,action_str))
                newNode = self.BuildCppCollection(c,newNode,silent=True)
        return newNode

#
# Utilities already written
#
# def BuildCollectionDict(rdf, includeType = True):
#     '''Turns a list of branches from an RDataFrame into a dictionary of collections.

#     Args:
#         rdf ([str]): RDataFrame from which to get the branches and types.
#         includeType (bool, optional): Include the type in the stored variable name (prepended). Defaults to True.

#     Returns:
#         dict: Dictionary where key is collection name and value is list of variable names.
#     '''
#     collections = {}
#     lone_branch = []

#     branch_names = [str(b) for b in rdf.GetColumnNames()]
#     for b in branch_names:
#         collname, varname = GetKeyValForBranch(rdf, b, includeType)
#         if varname == '' or 'n'+collname not in branch_names:
#             lone_branch.append(collname)
#         if collname not in collections.keys():
#             collections[collname] = []
#         collections[collname].append(varname)

#     return collections,lone_branch

# def GetKeyValForBranch(rdf, bname, includeType=True):
#     collname = bname.split('_')[0]
#     varname = '_'.join(bname.split('_')[1:])
#     out = (collname, '')

#     branch_names = [str(b) for b in rdf.GetColumnNames()]
#     if varname == '' or 'n'+collname not in branch_names:
#         pass
#     elif varname != '':
#         collType = str(rdf.GetColumnType(bname)).replace('ROOT::VecOps::RVec<','')
#         if collType.endswith('>'): collType = collType[:-1]
#         collType += '&'
#         if 'Bool_t' in collType: collType = collType.replace('Bool_t&','std::_Bit_reference')
#         if includeType:
#             out = (collname, collType+' '+varname)
#         else:
#             out = (collname, collType+' '+varname)

#     return out

def StructDef(collectionName, varList):
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
    out_str = '''
std::vector<{0}Struct> {0}s;
{0}s.reserve(n{0});
for (size_t i = 0; i < n{0}; i++) {{
    {0}s.emplace_back({1});
}}
return {0}s;
'''
    attr_assignment_str = ''
    print (varList)
    for i,v in enumerate(varList):
        varname = v.split(' ')[-1]
        attr_assignment_str += '{0}_{1}[i],'.format(collectionName, varname)
    out_str = out_str.format(collectionName,attr_assignment_str[:-1])
    return out_str
