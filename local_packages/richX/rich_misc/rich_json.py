import collections
import json
#==============================================================================
#        JSON
#==============================================================================
def convert_to_string(data):
    '''Converts potentially abstract objects to strings.
    Commonly used to convert JSON to dicts.'''
    #basestrings: convert directly to string
    if isinstance(data,basestring):
        return str(data)
    #Mappings: recurse on it's elements, and convert to a dict.
    elif isinstance(data, collections.Mapping):
        return dict(convert_to_string(item) for item in data.iteritems())
        #return dict(map(convert_to_string, data.iteritems()))
    #Iterables: recurse on it's elements, and preserve it's type.
    elif isinstance(data, collections.Iterable):
        return type(data)(convert_to_string(elm) for elm in data)
        #return type(data)(map(convert_to_string, data))
    #Others: no change
    else:
        return data

def read_json(file_name):
    '''Read a JSON file, and convert it to a Python-friendly
    string-based object (may be string or dict).

    note: to turn resultant dictionary into local variables
    (inside the calling function), have the calling function execute:
    locals().update(_conf)
    '''
    with open(file_name) as fi:
        config = json.load(fi)
    return convert_to_string(config)
def read_json_config(json_file_path):
    """Read a JSON file to a dict, and remove the root node."""
    json_dict = read_json(json_file_path)
    return json_dict.itervalues().next()
def read_json_string(input):
    """Convert a JSON-string into Python objects. Commonly used to pass
    dict's as JSON during AJAX calls."""
    config = json.loads(input)
    return convert_to_string(config)