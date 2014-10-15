"""

@todo Revise SDFReader() for interfaces (Iterable)
    (Iterable, maybe from a file or StringIO class)
@todo Revise Molecule() to support Mapping interface (not mutable)
@todo Give SDFReader() a file context manager
@todo Remove unrequired methods from SDFWriter (?populate?)
@todo Make this an independent package, named sdf
    sdf/
        molecule.py: Molecule
        writer.py: SDFWriter
        reader.py: SDFReader
        test.py + sample.sdf

@todo Write unit-tests
"""


#!/usr/bin/python
# Filename: sdf_reader.py
#------
#A module for reading SDF chemical files

#@todo: remove the _call_linux function --> another file

#FUNCTIONS:
#[] Open file in initialization
#[] Read in one molecule to a variable
#[] Parse one molecule into a dictionary
#[] Filter one molecule for certain keys
#[] Get all tags of a molecule
#[] Get all tags of a file (check the first X molecules)


#Other customizable special functions to set potentially....
#__repr__(self):            turns it into a string when required
#__str__(self):            turns it into a string when PRINTED - If not defined, returns __repr__
#__nonzero__ (self):        Called to implement truth value testing; should return 0 or 1.
#__len__(self):            
#__getitem__ (self, key):    Called to implement evaluation of self[key].
#__setitem__ (self, key, value):    Called to implement assignment to self[key]. Same note as for __getitem__().
#__delitem__ (self, key):        Called to implement deletion of self[key]. Same note as for __getitem__(). This should only be implemented for mappings if the objects support removal of keys
#__contains__ (self, item):        Called to implement membership test operators. Should return true if item is in self, false otherwise.

import re
import StringIO             #Allows strings to be treated as input files
from os import getcwd,devnull
import subprocess 
#---- Custom packages
from ..external.aliased import aliased, alias #code by Jose Nahuel Cuesta Luengo
#from ..external import aliased
#from aliased import *       #code by Jose Nahuel Cuesta Luengo

#@todo: Test this for files/strings that do not end in a clean '$$$$'





@aliased
class SDFReader:
    """Used to read in an SDF file, inevitably one molecule at a time.
    It is intended to be used with the Molecule class."""
    valid_types = [file,StringIO,str]
    def __init__(self,input_object,input_type=file):
        '''__init__(self,input_object,input_type=file)
        input_type==file --> input_object should be a file name.
        input_type==str or StringIO --> input_object should be a string (as if already read from an SDF file)
        '''
        #Valid types for input_type = [file,StringIO,str]
        if input_type not in SDFReader.valid_types:
            raise Exception("{0} is not a valid input_object type.".format(input_type))
        
        self.input_type = input_type
        if input_type is file:
            self.file = open(input_object,'r')
        elif (input_type is str) or (input_type is StringIO):
            self.file = StringIO.StringIO(input_object)
        
    @alias('close')
    def __del__(self):
        self.file.close()
    
    def __iter__(self):
        return SDFIterator(self)
    
    @alias('read_molecule','get_mol','get_molecule')
    def read_mol(self):
        """read in a molecule, and returns a Molecule object (~list of lines)"""
        mol = Molecule()
        for line in self.file:
            if line.strip() == "$$$$":
                break;
            mol.append(line)
        return mol
    def _sample_mol(self):
        """Reads a molecule via 'read_mol()', without changing file pointer."""
        last_pos = self.file.tell()
        mol = self.read_mol()
        self.file.seek(last_pos)
        return mol
    @alias('get_keys','tags')
    def get_tags(self):
        """Returns a subset of tags associated with the first two molecules
        This function should not change the file pointer."""
        
        last_pos = self.file.tell()
        tags1 = self.read_mol().tags()
        tags2 = self.read_mol().tags()
        combined_tags = tags1 + tags2
        unique_tags = self._unique(combined_tags)
        
        self.file.seek(last_pos)
        return unique_tags
    def readline(self):
        for line in self.file:      #only returns one line - uses 'for' syntax to preserve position of file pointer
            return line
    def _unique(self,taglist):
        #Internal function. Gets unique elements of a list, while preserving order.
        checked = []
        for e in taglist:
            if e not in checked:
                checked.append(e)
        return checked
    
    def __str__(self):
        '''Reads/prints all *remaining* molecule entries in SDF.
        Relevantly, if some mols are read via sdf.read_mol(), then str(sdf) will
        only return unread mols.'''
        return self.__repr__()
    def __repr__(self):
        return "".join([str(mol) for mol in self])
    def dict(self):
        '''Returns a list of dicts - one per molecule in the sdf.'''
        return [mol.dict() for mol in sdf]

class SDFIterator(object):
    '''Used for iterating across SDFReader() objects, one molecule at a time.'''
    def __init__(self,sdf):
        self.sdf = sdf
    def __iter__(self):
        return self
    def next(self):
        new_mol = self.sdf.read_mol()
        if not (new_mol):
            raise StopIteration
        else:
            return new_mol


class SDFWriter(SDFReader):
    '''In development. 
    Class used to write SDF data to MySQL. Extends SDFReader. Uses JChem's 'jcman' function - which
    has problems for some applications. 
    '''
    #full path to jcman function. Will vary between computers.
    #IF you receive error: 'OSError: [Errno 2] No such file or directory'
    #Then you probably need to change jcman_path here.
    #... yes, this is a crude kludge.
    jcman_path = '/home/Peters/ChemAxon/JChem/bin/jcman'
    jcman_login = "Peters"
    jcman_password = "tsibetcwwi"
    def __init__(self,sdf_file_name,table_name=None,db_name=None):
        '''
        >>> sdf = SDFWriter("my_sdf_file.sdf",table_name,db_name)
        '''
        SDFReader.__init__(self, sdf_file_name, input_type=file)
        self.file_name = sdf_file_name
        if table_name is None:
            self.table_name = sdf_file_name.split(".")[0]
        else:
            self.table_name = table_name
            
        if db_name is None:
            self.db_name = "raw_sdf"
        else:
            self.db_name = db_name
        self.set_database(self.db_name)
    def create_table(self):
        #file_name = os.path.splitext(self.file_name)[0]
        #self.table_name = file_name
        column_definitions = self._jcman_c_tagstring()
        cmdList = [self.jcman_path,"c",self.table_name,"--coldefs",column_definitions,"--dburl",self.dburl]
        #print "Attempting to call: \n'{0}'\n".format(" ".join(cmdList))
        #msg = subprocess.call(cmdList)
        try:
            msg = self._call_linux(cmdList)
        except:
            formatted_cmdlist = cmdList[0] + " '" + "' '".join(cmdList[1:]) + "'"
            print("Failed to execute the linux command: {0}".format(formatted_cmdlist))
            print("Executed in current directory={0}".format(getcwd()))
            raise
        return (msg,cmdList)
    def drop_table(self):
        #table_name = os.path.splitext(self.file_name)[0]
        #if table exists
        cmdList = [self.jcman_path,"d",self.table_name,"--dburl",self.dburl]
        msg = self._call_linux(cmdList,hide_output=True)
        #FNULL = open(os.devnull,'w')  #hide output
        #msg = subprocess.call(cmdList,stdout=FNULL,stderr=FNULL)
        return (msg, cmdList)
    def populate_table(self):
        #for [] as :
        #table_name = os.path.splitext(self.file_name)[0]
        #file_name_ext = self.file_name
        column_specs = self._jcman_a_tagstring()
        cmdList = [self.jcman_path,"a",self.table_name,self.file_name,"--connect",column_specs,"--dburl",self.dburl]
        msg = self._call_linux(cmdList)
        return (msg,cmdList)
    def _jcman_c_tagstring(self):
        tag_string = ""
        tagDict = self.get_tags()
        columnTypes = self._get_mysql_types()
        for tag in tagDict:
            try:
                column_type = columnTypes[tag]
            except:
                column_type = "TEXT"
            column_name = self._mysql_naming(tag)
            tag_string = tag_string + ", {0} {1}".format(column_name,column_type)
        return tag_string
    def _jcman_a_tagstring(self):
        tag_string = ""
        tagDict = self.get_tags()
        for tag in tagDict:
            column_name = self._mysql_naming(tag)
            tag_string = tag_string + "{0}={0};".format(column_name)
        tag_string = tag_string + ""
        return tag_string
    def _get_mysql_types(self,mol=None):
        """Checks if mol[tag] can be cast as an integer, then a decimal/float, 
            If neither of these is valid, then defaults to text."""
        if mol is None:
            mol = self._sample_mol().dict()
        typeDict = {}
        for tag in mol:
            #try:
                #int(mol[tag])
                #typeDict[tag] = "INT(30)"
            #except:
            
            #Kludge - because DECIMAL fields end up giving me trouble when nonnumeric variables are input
            #... hence, everything is cast as TEXT
            typeDict[tag] = "TEXT"
#            try:
#                float(mol[tag])
#                typeDict[tag] = "DECIMAL(30,15)"
#            except:
#                typeDict[tag] = "TEXT"
        return typeDict
    def _mysql_naming(self,in_string):
        mysql_rep = {'-':'_',
                        ' ':'_'}
        return self._replacements(in_string,mysql_rep.keys(),mysql_rep.values())
    def set_database(self,db_name):
        self.dburl = "jdbc:mysql://localhost/{0}".format(db_name)
    def _call_linux(self,cmdList,hide_output=False):
        DEBUG = True
        if DEBUG:
            formatted_cmdlist = cmdList[0] + " '" + "' '".join(cmdList[1:]) + "'"
            print("Calling {0}".format(formatted_cmdlist))
        if(hide_output):
            FNULL = open(devnull,'w')  #hide output, by redirecting to null
            msg = subprocess.call(cmdList,stdout=FNULL,stderr=FNULL)
        else:
            try:
                msg = subprocess.call(cmdList)
                
                #Move the following up to where cmdList is defined
                #? How to see if Python recognizes an alias for 'jcman'??  
                #try:
                #if doesn't work, try other path for jcman
                #cmdList[0] = "/home/Peters/ChemAxon/JChem/bin/jcman"
                #cmdList[0]
            except:
                print("In function _call_linux():")
                print("Failed to execute the linux command: {0}".format(formatted_cmdlist))
                print("Executed in current directory={0}".format(getcwd()))
                raise
        if DEBUG:
            print("Done")
        return msg
    def _replacements(self,in_string,old_substrings,new_substrings):
        """Utility function. Replaces multiple substrings in 'in_string'."""
        for (old,new) in zip(old_substrings,new_substrings):
            in_string = in_string.replace(old, new)
        return in_string

@aliased
class Molecule:
    """Used to hold and manipulate the entries of individual molecules read by 'SDFReader'.
    The most important functions are .lines(), .tags(), and .dict()
    """
    def __init__(self):
        self.lines = []
    def __repr__(self):
        return self.string()
    def __str__(self):
        return self.string()
    def __nonzero__(self):
        return self.lines != []
    @alias('tostring','str')
    def string(self):
        return ''.join(self.lines)
    def append(self,line):
        self.lines.append(line)
    def lines(self):            # ? Can I append multiple lines this way?
        return self.lines
    @alias('keys')
    def tags(self):
        #returns a subset of tags & values associated with the molecule
        #return dict(self).keys()
        return (self.dict()).keys()
    def split(self):
        tags = []
        split_on_string = "> <"
        pattern = re.compile(">\s{1,2}<")
        mol_strings = pattern.split(self.string())
        #mol_strings = self.string().split(split_on_string)    #old - does not account for one or two spaces in ">  <"
        mdl = mol_strings.pop(0)
        for tag_entry in mol_strings:
            tag_entry = split_on_string + tag_entry  #Reinsert the tag name demarcation
            tags.append(tag_entry)
        return (mdl,tags)
    def dict(self):
        """Turns a molecule (list of lines) into a dictionary
        Each tag name (plus MDL) becomes a key, and it's contents become the values
        The trailing blank line of each entry is removed."""
        (mdl,tags) = self.split()
        mol_dict = {'mdl':mdl}
        for tag in tags:
            tag_lines = tag.splitlines()
            (tag_name,tag_value) = self._get_tag(tag_lines)
            mol_dict[tag_name] = tag_value
        return mol_dict
    def __getitem__(self, key):
        d = self.dict()
        return d[key]       #if key doesn't exist - this should error
    def __setitem__(self,key,value):
        self.append(">  <{0}>\n".format(key))
        self.append("{0}\n".format(value))
        self.append("\n") 
    def _get_tag(self,tag_lines):
        #Private method. Does not directly operate on a Molecule object 
        
        first_line = tag_lines.pop(0)
        tag_match = re.match("(>\s+<)(.+)(>.*)",first_line)
        if(tag_match is not None):
            tag_name = tag_match.group(2)
        else:
            #raise Exception("No tag name found in first line: " + first_line)
            tag_name = ""
        
        if tag_lines[-1] is "\n":
            tag_lines.pop(-1)
        tag_value = ''.join(tag_lines)
        
        return (tag_name,tag_value)

    