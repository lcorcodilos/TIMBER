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
        
        if varname == '': continue

        if collname not in collections.keys():
            collections[collname] = []
        collections[collname].append(str(rdf.GetColumnType(b))+' '+varname)

    return collections

def StructDef(collectionName, varList):
    out_str = 'struct %sColl {\n'%collectionName
    for v in varList:
        out_str += '\t%s; \n'%v

    out_str += '};'
    return out_str

def StructObj(collectionName, varList):
    out_str = '{0}Coll {0};\n'.format(collectionName)
    for v in varList:
        varname = v.split(' ')[-1]
        out_str += '{0}.{1} = {0}_{1};\n'.format(collectionName, varname)
    out_str += 'return %s;'%collectionName
    return out_str
