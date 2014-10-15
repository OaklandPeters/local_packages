"""
Utility functions for interacting and mock-testing with mod_python.

Importantly, the MockRequest() object provides a reasonably functional
stand-in for simulating mod_python request objects.


@TODO Ensure that this handles array-like url parameters correctly
    ... I think it does not
"""

import inspect
import urllib
import urlparse
import collections
import pprint
import abc
import re
import json
#----- custom modules:
from local_packages import multimaps #pylint: disable=relative-import


#----------- Local Support functions
def cut(haystack, needle):
    """Cut string 'needle' from string 'haystack'."""
    return re.sub(needle, "", haystack)
def begins_with(haystack, needle):
    """Predicate. Does sequence 'haystack' begin with 'needle'."""
    return haystack[:len(needle)] == needle


try:
    #mod_python must be installed on your Apache server
    #... this is an outdated hold-over, that should really
    #be replaced with mod_wsgi or similar
    
    #import mod_python   #pylint: disable=import-error
    from mod_python import Cookie
    from mod_python import util
    
    #from mod_python import Cookie, util
    MOD_PYTHON_IMPORTED = True

    class MP(object):
        """Interface to cookie-related tasks in mod_python.
        Partly used to allow dispatching.
        """
        @classmethod
        def get_cookie(cls, req, name):
            """Retreive cookie by name from request object."""
            #cookies = mod_python.Cookie.get_cookies(req)
            cookies = Cookie.get_cookies(req)
            this_cookie = cookies.get(name)
            value = cut(str(this_cookie), "{0}=".format(name))
            return value
        @classmethod
        def get_cookies_dict(cls, cookies):
            """Retreive dict of cookies from request object."""
            cookies_dict = {}
            for name, value in cookies.items():
                cookies_dict[name] = cut(str(value), name+"=")
            return cookies_dict
        @classmethod
        def get_cookies(cls, req):
            """Retreive cookies via mod_python"""
            #return mod_python.Cookie.get_cookies(req)
            return Cookie.get_cookies(req)
except ImportError:
    MOD_PYTHON_IMPORTED = False

#=================== Functions not requiring mod_python =================



#==============================================================================
#    Dispatch functions
#==============================================================================
#Dispatches on the first parameter: mod_python.Request object, or MockRequest() objects.
#
def get_cookies(req):
    """Dispatcher. Retreive cookies from a mod_python.Request or MockRequestABC
    object."""
    if isinstance(req, MockRequestABC):
        return req.cookies
    elif MOD_PYTHON_IMPORTED:
        return MP.get_cookies(req)
    else:
        raise Exception("'req' is an unrecognized type, perhaps "
            "because mod_python is not loaded.")

def get_cookie(req, name, clean=False):
    """Dispatcher. Retreive a cookie by name from a mod_python.Request
    or MockRequestABC object."""
    if isinstance(req, MockRequestABC):
        raw_cookie = req.cookies[name]
    elif MOD_PYTHON_IMPORTED:
        raw_cookie = MP.get_cookie(req, name)
    else:
        raise Exception("'req' is an unrecognized type, perhaps "
            "because mod_python is not loaded.")
    if clean:
        return clean_cookie(raw_cookie, name)
    else:
        return raw_cookie
def get_cookies_dict(req, cookies=None):
    """Dispatcher. Returns a dict of cookies from a mod_python.Request
    or MockRequestABC object."""
    if cookies == None:
        cookies = get_cookies(req)

    if isinstance(req, MockRequestABC):
        return cookies
    elif MOD_PYTHON_IMPORTED:
        return MP.get_cookies_dict(cookies)
    else:
        raise Exception("'req' is an unrecognized type, perhaps "
            "because mod_python is not loaded.")
def get_url_parameter(req, name=None, default=None):
    """Dispatcher.
    Newer version of get_url_parameter
    """
    #[] Offline testing: assumes req is a MockRequest object.
    if isinstance(req, MockRequestABC):
        top = dict(req.parameters)
    #[] Mod-Python: assumes this is a req object from mod-python
    elif MOD_PYTHON_IMPORTED:
        #storage = mod_python.util.FieldStorage(req)
        storage = util.FieldStorage(req)
        top = dict(storage)
    #[] Error Case
    else:
        raise Exception("'request' is an unrecognized type.")

    if name == None:
        return top
    else:
        return top.get(name, default)


#==============================================================================
#        Mock Request Objects
#==============================================================================
class MockRequestABC(object):
    """Interface-class for imitating mod_python request objects.
    Also used to mutually recognize Testing_Request objects (deprecated), and
    MockRequest object (more modern."""
    __metaclass__ = abc.ABCMeta
    @property
    def html(self):
        """Stores the results intended to be passed back via the request."""
        if not hasattr(self, '_html'):
            self.html = ""
        return self._html
    @html.setter
    def html(self, value):
        """Setter for the html storage property."""
        self._html = value  #pylint: disable=attribute-defined-outside-init
    def __repr__(self):
        return "{0}(html='{1}')".format(self.__class__.__name__, self.html)
    def __str__(self):
        return str(self.html)
    write = abc.abstractmethod(lambda self, *args, **kwargs: NotImplemented)
    read = abc.abstractmethod(lambda self, *args, **kwargs: NotImplemented)
    parameters = abc.abstractproperty(lambda self: NotImplemented)
    url = abc.abstractmethod(lambda self: NotImplemented)


class Testing_Request(MockRequestABC):  #pylint: disable=invalid-name
    '''Used in testing Python web-scripts.
    This is highly-deprecated, and maintained only for backward compatibility.

    Doc-tests
    >>> if __name__ == "__main__":
    >>>     req = Testing_Request(table_name="disease", node_name="Ovarian carcinoma")
    >>>     results_html = index(req)        #Where index() is the main function for the webscript
    #Then, to get url parameters inside index()
    >>> def index(req):
    >>>     if __name__=="__main__":        #ie when run for testing
    >>>         table_name = req.url_parameters['table_name']
    >>>     else:                           #when run from web-server
    >>>         table_name = get_url_parameter(req, "table_name")
    '''
    def __init__(self, *url_string, **url_params):
        '''Provide only one of:
        (A) a url string (as the first keyword argument), or
        (B) a set of url-parameters as keyword arguments.
        '''
        self.html = ""
        #Attempting to retreive an unprovided url parameter returns None
        self.url_parameters = collections.defaultdict(None)
        assert(bool(url_string) != bool(url_params)), (
            "Provide only one of (A) a url string (as the first keyword "
            "argument), or (B) a set of url-parameters as keyword arguments."
        )

        #[] If url_string provided (positional arg)
        if url_string:
            assert(len(url_string) == 1), (
                "If a url-string is provided, only one should be provided."
            )

            self.url_parts = urlparse.urlparse(url_string[0])
            self.url_path = (
                self.url_parts.scheme
                + self.url_parts.netloc
                + self.url_parts.path
            )
            temp_params = urlparse.parse_qs(self.url_parts.query)

            for key, val in temp_params.items():
                #temp_params values are usually enclosed in [] --> convert to simple string
                if type(val) is list:
                    val = val[0]
                self.url_parameters[key] = val

        #[] If url_params provided (keywords)
        for key, val in url_params.items():
            self.url_parameters[key] = val
        self.debug_data = {}
    def write(self, seq):
        """Write a sequence to html output."""
        assert(isinstance(seq, (basestring, collections.Sequence)))
        if (isinstance(seq, basestring)) or (hasattr(seq, 'str')):
            self.html += str(seq)
        else:
            self.html += '\n'.join(seq)
        if len(self.html) > 0:
            if seq[-1] != "\n":
                self.html += "\n"
    def read(self):
        return self.html
    def get_url_parameters(self, parameter_name, default=None):
        '''Simulates retreiving a single url parameter.
        Emulates web_utility.py:get_url_parameter(), which functions on
        mod_python Request objects.'''
        #return self.url_parameters[parameter_name]
        return self.url_parameters.get(parameter_name, default)     #Return default value of None
    def set_url_parameters(self, **url_params):
        '''Sets all URL parameters, based on url_params.'''
        for key, val in url_params.items():
            self.url_parameters[key] = val
    @property
    def parameters(self):
        """Stores url-parameters. Read only."""
        return self.url_parameters
    def __del__(self):
        print(str(self.html))
    def url(self):
        '''Retreives a URL-like string for this Testing_Request object.'''
        url_string = ""
        #[] Get file name for root function (~top of the call stack)
        url_string += inspect.stack()[-1][1]
        if len(self.url_parameters)>0:
            url_string += "?" + urllib.urlencode(self.url_parameters)
        return url_string
    def closeout(self, seq_of_strings):
        """Write sequence of strings to html output, and return result."""
        self.write(seq_of_strings)
        return self.html



class MockRequest(MockRequestABC):
    """Class used to imitate mod_python Request objects.

    Used and tested fairly extensively for various website projects,
    which are not included in the unit-tests.

    @todo Move the assertions and setup into a validation function.
    @todo Refactor _parse_url into the validation function.
    """
    def __init__(self, url=None, parameters=None, cookies=None, echo=True):
        """
        echo: if True, print self.html before removing MockRequest from
            memory. Usually occurs at end of main function (default: True).
        """
        assert(isinstance(url, (type(None), basestring)))
        assert(isinstance(parameters, (type(None), dict)))
        assert(isinstance(cookies, (type(None), dict)))


        #... why did I use a multimap for this?
        self.parameters = multimaps.URLMultimap()

        self.url_parts = None   # New ?
        self.url_path = None    # New ?
        if url != None:
            self._parse_url(url)
        if parameters != None:
            self.parameters.update(parameters)
        if cookies != None:
            self.cookies.update(cookies)
        self.echo = echo

        #Validate and assign
#         (   self.url,
#             self.parameters,
#             self.cookies,
#             self.echo,
#             self.url_parts,
#             self.url_path) = self.validate(url, parameters, cookies, echo)
#
#     def validate(self, url, parameters, cookies, echo):
#         """
#         Tenative validation function for MockRequest(). Not used yet, because I don't
#         have time to setup the tests.
#
#         Once it works, it should replace _parse_url, and major parts of __init__
#         """
#         rich_core.AssertKlass(parameters,
#            (type(None), collections.MutableMapping), name='parameters'
#         )
#         rich_core.AssertKlass(cookies,
#             (type(None), collections.MutableMapping),
#             name='cookies'
#         )
#         rich_core.AssertKlass(echo, bool, name='echo')
#
#         url, url_parts, url_path, temp_params = self._validate_url(url)
#         parameters = multimaps.URLMultimap()
#         parameters.update(temp_params)
#
#         return url, parameters, cookies, echo, url_parts, url_path
#
#     def _validate_url(self, url):
#         rich_core.AssertKlass(url, (type(None), basestring), name='url')
#         if url == None:
#             url_parts, url_path, temp_params = None, None, {}
#         else:
#             url_parts = urlparse.urlparse(url_string)
#             url_path = url_parts.scheme + url_parts.netloc + url_parts.path
#             temp_params = urlparse.parse_qs(url_parts.query)
#
#         return url, url_parts, url_path, temp_params

    def _parse_url(self, url_string):
        """Part of __init__ process.
        For array parameters ('smiles[]') --> multimaps.URLMultimap().update() should
        correctly handle this.
        .... actually, according to my current experiments... it does NOT
        """
        self.url_parts = urlparse.urlparse(url_string)
        self.url_path = self.url_parts.scheme + self.url_parts.netloc + self.url_parts.path
        temp_params = urlparse.parse_qs(self.url_parts.query)
        self.parameters.update(temp_params)

    def write(self, obj, simple=True):
        """Write object to output stream. Held in self.html."""
        if simple:
            self.html += str(obj)
        else:
            self.html += pprint.pformat(obj, indent=4)
    def read(self):
        return self.html
    #----- property: parameters
    @property
    def parameters(self):
        """Getter for url parameters property. Also sets default."""
        if not hasattr(self, '_parameters'):
            #self._parameters = collections.defaultdict(None)
            self._parameters = multimaps.URLMultimap()
        return self._parameters
    @parameters.setter
    def parameters(self, value):
        """Setter for url parameters property."""
        self._parameters = value    #pylint: disable=attribute-defined-outside-init
    #----- property: cookies
    @property
    def cookies(self):
        """Getter property for cookies."""
        if not hasattr(self, '_cookies'):
            self._cookies = collections.defaultdict(None)
        return self._cookies
    @cookies.setter
    def cookies(self, value):
        """Setter property for cookies."""
        self._cookies = value   #pylint: disable=attribute-defined-outside-init
    #-----
    def get_url_parameters(self, name, default=None):
        '''Simulates retreiving a single url parameter.
        Emulates web_utility.py:get_url_parameter(),
        which functions on mod_python Request objects.'''
        return self.parameters.get(name, default)
    def set_url_parameters(self, **url_params):
        '''Sets all URL parameters, based on url_params.'''
        for key, val in url_params.items():
            self.parameters[key] = val
    def __del__(self):
        """If self.echo is True, prints the stored HTML.
        In either case, calls __del__ of parent class, if possible.
        """
        if self.echo:
            print(str(self.html))
        try:
            super(type(self), self).__del__()   #pylint: disable=bad-super-call
        except AttributeError:
            pass
    def url(self):
        '''Retreives a URL-like string for this object. Since it is called from
        a Python script - used the name of the function at the top of the call
        stack.'''
        url_string = ""
        #[] Get file name for root function (~top of the call stack)
        url_string += inspect.stack()[-1][1]
        if len(self.parameters)>0:
            url_string += "?" + urllib.urlencode(self.parameters)
        return url_string
    def closeout(self, seq_of_strings):
        """Write sequence of strings to html output, and return result."""
        self.write(seq_of_strings)
        return self.html




#==============================================================================
#        Local Utility Functions
#==============================================================================
def clean_html(html):
    """Use to display html/json returned by web_utility.MockRequest objects."""
    return json.loads(html.strip('\''))
def clean_cookie(raw_cookie, name):
    """Cleans (unquotes) a raw cookie string, and takes everything after the
    '=' sign."""
    if (name+'=') in raw_cookie:
        take_after = lambda haystack, needle: haystack.split(needle)[1]
        cookie = take_after(raw_cookie, name+"=")
    else:
        cookie = raw_cookie
    return urllib.unquote(cookie)
