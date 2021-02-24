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
        collname = b.split('_')[0]
        varname = '_'.join(b.split('_')[1:])
        
        if varname == '' or 'n'+collname not in branch_names: continue

        if collname not in collections.keys():
            collections[collname] = []
        collType = str(rdf.GetColumnType(b)).replace('ROOT::VecOps::RVec<','')[:-1]
        if not includeType: collType = ''
        collections[collname].append(collType+' '+varname)

    return collections

def StructDef(collectionName, varList):
    out_str = 'struct %sStruct {\n'%collectionName
    for v in varList:
        out_str += '\t%s; \n'%v

    out_str += '};'
    print (out_str)
    return out_str

def StructObj(collectionName, varList):
    out_str = '''
ROOT::VecOps::RVec<{0}Struct> {0}s(n{0});
for (size_t i = 0; i < n{0}; i++) {{
{1}
}}
return {0}s;
'''
    attr_assignment_str = ''
    for v in varList:
        varname = v.split(' ')[-1]
        attr_assignment_str += '\t{0}s[i].{1} = {0}_{1}[i];\n'.format(collectionName, varname)
    out_str = out_str.format(collectionName,attr_assignment_str)
    return out_str
