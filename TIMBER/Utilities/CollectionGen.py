def BuildCollectionDict(rdf, includeType = True):
    '''Turns a list of branches from an RDataFrame into a dictionary of collections.

    Args:
        rdf ([str]): RDataFrame from which to get the branches and types.
        includeType (bool, optional): Include the type in the stored variable name (prepended). Defaults to True.

    Returns:
        dict: Dictionary where key is collection name and value is list of variable names.
    '''
    collections = {}

    branch_names = [str(b) for b in rdf.GetColumnNames()]
    for b in branch_names:
        collname, varname = GetKeyValForBranch(rdf, b, includeType)
        if varname == '' or 'n'+collname not in branch_names: continue
        if collname not in collections.keys():
            collections[collname] = []
        collections[collname].append(varname)

    return collections

def GetKeyValForBranch(rdf, bname, includeType=True):
    collname = bname.split('_')[0]
    varname = '_'.join(bname.split('_')[1:])
    out = (collname, '')

    branch_names = [str(b) for b in rdf.GetColumnNames()]
    if varname == '' or 'n'+collname not in branch_names:
        pass
    elif varname != '':
        collType = str(rdf.GetColumnType(bname)).replace('ROOT::VecOps::RVec<','')
        if collType.endswith('>'): collType = collType[:-1]
        collType += '&'
        if 'Bool_t' in collType: collType = collType.replace('Bool_t &','Bool_t&').replace('Bool_t&','std::_Bit_reference')
        if includeType:
            out = (collname, collType+' '+varname)
        else:
            out = (collname, collType+' '+varname)

    return out

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
    for i,v in enumerate(varList):
        varname = v.split(' ')[-1]
        attr_assignment_str += '{0}_{1}[i],'.format(collectionName, varname)
    out_str = out_str.format(collectionName,attr_assignment_str[:-1])
    return out_str
