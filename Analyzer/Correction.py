import sys
sys.path.append('../')
from Tools.Common import GetHistBinningTuple, CompileCpp

import clang.cindex
cpp_idx = cindex.Index.create()
cpp_args =  '-x c++ --std=c++11'.split()

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

    def Clone(self,name,newMainFunc=self.__mainFunc):
        """Makes a clone of current instance.

        If multiple functions are in the same script, one can clone the correction and reassign the mainFunc
        to avoid compiling the same script twice.

        Args:
            name (str): Clone name.
            newMainFunc (str): Name of the function to use inside script. Defaults to same as original.
        Returns:
            Clone of instance with same script but different function (newMainFunc)
        """
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