"""


@todo: setter/getter/deleter/validator tests for WebRequest.parameter
@todo: setter/getter/deleter/validator tests for WebRequest.cookies
"""

import unittest
import json
#
import web_utility as wu
import local_packages.rich_misc as rich_misc
#import rich_misc as rich_misc







class MockRequestTests(unittest.TestCase):
    """

    @TODO setup tests for MockRequest() constructor:
    (1) url with parameters inline
    (2) url + parameters as keyword
    (3) returns via echo
    (4) returns via .html
    (5) pass via JSON
    (6) pass via HTML
    (7) What happens when I attempt a pass with variable not encoded as JSON?
    """
    def setUp(self):
        self.base = 'https://gdid-test.uis.georgetown.edu/fake/server/python/'
        self.script = 'simulated.py'

    def call_script(self, parameters=None, cookies=None, index=None):
        """Pass parameters in with url, rather than as seperate keyword"""
        if index == None:
            index = index_basic
        if parameters == None:
            parameters = {}
        if cookies == None:
            cookies = {}

        url = self.base + self.script
        #[] Call index for this script
        request = wu.MockRequest(
            url,
            parameters = parameters,
            cookies = cookies,
            echo = False
        )

        index(request)
        return request #Output now in req.html

    def test_basic(self):
        """Simplest test, index_basic, parameters and cookies, pass via JSON."""
        request = self.call_script(
            parameters={'user_code':'foo'},
            cookies={'user_name':'Mr. Bar'}
        )
        result = rich_misc.read_json_string(request.html)

        #Check return/html property of requestuest
        self.assert_(isinstance(request.html, basestring))
        #Check url parameters
        self.assertEquals(result['code'], 'foo... processed')
        #Check cookies
        self.assertEquals(result['name'], 'Mr. Bar... processed')


    #array-like URL parameters are not working - for now 
#     def test_array_params(self):
#         """Test index_for_lists, which passes arrays/lists through
#         parameters and cookies; pass via JSON."""
#         request = self.call_script(
#             parameters={'user_codes[]':'[foo,bar,baz]'},
#             cookies={'user_names[]':'[MrFoo,MrsBar,MsBaz]'},
#             index=index_for_lists
#         )
#         result = rich_misc.read_json_string(request.html)
#         
#         print(result)

# class ParameterTests(unittest.TestCase):
#     pass
# class CookiesTests(unittest.TestCase):
#     pass



#==============================================================================
#    Simulated AJAX response index()
#==============================================================================
def index_basic(request):
    """Simulates basic AJAX response."""

    #Get from url parameter
    user_code = wu.get_url_parameter(request, 'user_code')

    #Get from cookie
    user_name = wu.get_cookie(request, 'user_name')

    #Do some processing
    processed = {}
    processed['code'] = user_code + '... processed'
    processed['name'] = user_name + '... processed'

    result = json.dumps({
        'code':processed['code'],
        'name':processed['name']
    })
    request.write(result)
    return result


def index_for_lists(request):
    """As index(), but expects to operate on lists."""

        #Get from url parameter
    user_codes = wu.get_url_parameter(request, 'user_codes[]')


    #Get from cookie
    user_names = wu.get_cookie(request, 'user_names[]')
    #cookies = wu.get_cookies_dict(request)
    #user_names = cookies['user_names']

    #Do some processing
    processed = {}
    processed['codes'] = [
        code + '... processed'
        for code in user_codes
    ]
    processed['names'] = [
        name + '... processed'
        for name in user_names
    ]

    result = json.dumps({
        'codes':processed['codes'],
        'names':processed['names']
    })
    request.write(result)
    return result


if __name__ == "__main__":
    unittest.main()