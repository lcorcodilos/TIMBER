'''@docstring Group.py

Home of Group classes for organizing cuts, new variables, and histograms

'''

from collections import OrderedDict

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
    def Do(THmethod,argsTuple):
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