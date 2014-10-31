import collections
import string
try:
    #cElementTree is MUCH faster than standard ElementTree
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

import xml.dom.minidom

import warnings
warnings.simplefilter(
    "once",
    category=(PendingDeprecationWarning, DeprecationWarning))



#==============================================================================
#        XML
#==============================================================================

#------------------------------------------------------------
#  XMLDict() is the most modern of the *simple* XML parsers.
#  For a more sophisticated version, see xmldict.py
#------------------------------------------------------------
class XMLDict(object):
    """Operator. Very simple XML parser - handles nesting, but
    ignores possibility of attributes or lists.
    
    Notice: this returns a dict, rather than an XMLDict object
    (it is an operator, not a class constructor). 
    
    >>> config = XMLDict('datafiles/cccid_config.xml')
    >>> sorted(config.keys())[:4]
    ['actual_pdbs_dir', 'additional_return_options', 'auxillary_smiles_column', 'auxillary_table']
    >>> sorted(config.keys())[-4:]
    ['similarity_threshold', 'structural_row_increment', 'website_directory', 'write_log_flag']
    """
    def __new__(cls, *args, **kwargs):
        return cls.__call__(*args, **kwargs)
    @classmethod
    def __call__(cls, xmlpath):
        return cls.parse(cls.read(xmlpath))
    @classmethod
    def read(cls,xmlpath):
        tree = ElementTree.parse(xmlpath)
        return tree.getroot()
    @classmethod
    def parse(cls,elements):
        this = {}
        for elm in elements:
            this[elm.tag] = cls.parse(elm) if elm else elm.text
        return this
    
    
def dict2xml(D, xml_string="", depth=0):
    '''Convert moderately complicated dictionaries to XML strings.
    Ignores xml attributes.
    Supports contents which are themselves dicts, lists, tuples,
    strings, numbers, and maybe more.
    
    
    >>> sample = {  'a': 'a contents',
    ...             'b': {'c': 'c contents',
    ...                   'd': {'d1':'d1 contents',
    ...                         'd2':'d2 contents'},    },
    ...             'e': range(3),
    ...             'f': {'f1':123}    }
    >>> sample_xml = dict2xml(sample)
    '''
    filler = 'i__'
    for k, v in D.items():
        k = validate_xml_name(k, filler)

        #[] Open tag
        xml_string += "{pad}<{name}>".format(pad="\t"*depth, name=k)

        #[] Iterate through children, or add contents
        #if child is an iterable container (~NonStringIterable)
        if hasattr(v, "__iter__"):
            #if it is not a dict, or dict-like
            if not isinstance(v, collections.Mapping):
                #turn into a dict, using index #s as keys
                v = dict((filler+str(i), elm) for i, elm in enumerate(v))
            xml_string += "\n"
            xml_string = dict2xml(v, xml_string, depth+1)
            #[] Close tag: with padding
            xml_string += "{pad}</{name}>\n".format(pad="\t"*depth, name=k)
        else:
            #[] Close tag:
            #If closing without inner iteration -- do not add padding
            xml_string += "{content}</{name}>\n".format(content=v, name=k)
    return xml_string

def indent(elem, level=0, width=4):
    '''Works on XML objects, to indent them 'prettily'.
    Basically a work around for the fact that ElementTree's
    pretty printer doesn't work.'''
    #i = "\n" + level*"  "
    i = "\n" + " "*level*width
    if len(elem):
        if not elem.text or not elem.text.strip():
            #elem.text = i + "  "
            elem.text = i + " "*width
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level=level+1, width=width)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def indenter(xml_string, width=4, remove_header=False):
    '''Makes XML or HTML string pretty.
    Standard Python indent size is 4 spaces.'''
    #? What is difference between indent() and indenter()?
    xmlDom = minidom.parseString(xml_string)
    pretty = xmlDom.toprettyxml(encoding='UTF-8')
    if remove_header is False:
        return pretty
    #remove XML header - inserted by minidom
    else: 
        return re.sub(
            "<\?xml"  #Open XML declaration
            ".*?"     #Middle parts of XML tag
            "\?>"     #Close xml declaration
            "[\n]?"   #Possible trailing newline
            , '', pretty)