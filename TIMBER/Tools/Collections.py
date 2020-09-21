from Common import CompileCpp

class Collection(object):
    def __init__(self,collectionName,dataframe):
        column_list = dataframe.GetColumnNames()

        matching_columns = [c for c in column_list if (collectionName in c)]# and ('RVec' in dataframe.GetColumnType(c))]

        cpp = '''
class FUNCNAMECol {
    public:
        void SET(COMMATYPES);
        DECLARATION
};

void FUNCNAMECol::SET(COMMAARGS) {
    ASSIGNMENT
}
        '''

        cpp_comma_args = ''
        cpp_comma_types = ''
        cpp_declare = ''
        cpp_assign = ''
        cpp_call = ''

        for c in matching_columns:
            v = c[c.find('_')+1:]
            t = dataframe.GetColumnType(c)
            setattr(self,v,c)
            
            cpp_comma_types += '%s, '%(t)
            cpp_comma_args += '%s %s, '%(t,c)
            cpp_declare += '\t%s %s;\n'%(t,v)
            cpp_assign += '\t%s = %s;\n'%(v,c)
            cpp_call += '%s, '%c

        cpp_comma_types = cpp_comma_types[:-2]
        cpp_comma_args = cpp_comma_args[:-2]
        cpp_call = cpp_call[:-2]

        self.cpp = cpp.replace('FUNCNAME',collectionName).replace('COMMATYPES',cpp_comma_types).replace('COMMAARGS',cpp_comma_args).replace('DECLARATION',cpp_declare).replace('ASSIGNMENT',cpp_assign)
        self.call = '%sCol %s(%s);'%(collectionName,collectionName,cpp_call)

        CompileCpp(self.cpp)
        CompileCpp(self.call)

    def __repr__(self):
        return self.cpp


def MakeCollections(dataframe):
    column_list = dataframe.GetColumnNames()
    collections = []
    for c in column_list:
        if '_' in c:
            collection_name = c[:c.find('_')]
            if (collection_name not in collections) and (collection_name[0] != 'n'):
                collections.append(collection_name)

    return collections