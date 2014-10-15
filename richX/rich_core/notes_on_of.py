
# ----- 3 new pieces of functionality for AssertKlass
#     Accessible through keywords
# of
#    Checking obj[index], for iterable, sized records
# having
# promise



    --> _dispatch_mapping(obj, _types, name)
        #Alternate: duck-typing on attributes
        #if _types is dict... _types={'key':key_types, 'value':value_types}
        if isinstance(_types, Mapping):
            key_types = _types.get('key', types.get('keys'))
            value_types = _types.get('value', types.get('values'))
        #else, simplest to assume it's checking type of values
        else: #isinstance(_types, Atomic or Sequence):
            key_types = None
            value_types = _types
        for key, value in obj.items():
            if key_types != None:
                AssertKlass(key, key_types, name="{0} key:'{1}'".format(name,key))
            if name_types != None:
                AssertKlass(value, value_types, name="{0}['{1}']".format(name, key))
    --> _dispatch_iterable(obj, _types, name)
        #ALTERNATE: make 'promise' its own keyword
        ... requires monkey-patching it's __iter__ with a 'promise' object.
        ... 'promise' intercepts result of .next()/iter() and typechecks it.
        ... it will also need to count the # of checks
        ... operate like dispatch_sequence, with name="{0} #{1}".format(name, i)


#    () AssertKlass(..., of=(types,...), name='NAME')
#    () Only for Sequences, but add placeholders for Mapping, Iterable
#        Sequences are simple,
#        but Mappings are nuanced,
#        and Iterables require advanced monkey-patching and 'promise' objects.
def _record_of(obj, _types, name):
    """
    Requires obj to be a sequence or mapping. ('DiscreteRecord'?)
    Only supports positive ('pos') types
    """
    for index, elm in pairs(obj):
        AssertKlass(elm, _types, name="{0}[{1}]".format(name, index)))