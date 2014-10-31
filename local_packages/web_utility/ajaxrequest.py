import json

class AJAXRequest(object):
    """Operator-style callable class.
    Simulates an AJAX call, returning JSON. Used for testing.
    
    """
    def __new__(cls, *args, **kwargs):
        return cls.__call__(*args, **kwargs)
    @classmethod
    def __call__(cls, index, request=None, **keywords):
        """request is usually a MockRequest object."""
        index, request = cls.validate(index, request=request, **keywords)
        result = index(request)
        cls.validate_result(result)
        return cls.convert(result)
    @classmethod
    def validate(cls, index, request=None, **keywords):
        if not callable(index):
            raise TypeError("index must be callable.")
        if request is None:
            if not 'url' in keywords:
                raise TypeError("Must provide either a request or url argument")
            request = MockRequest(
                keywords['url'],
                parameters = keywords.get('parameters', {}),
                cookes = keywords.get('cookies', {}),
                echo = False
            )
        return index, request
    @classmethod
    def validate_result(cls, result):
        if not isinstance(result, basestring):
            raise TypeError("'result' is expected to be a string.")
    @classmethod
    def convert(cls, _string):
        """Converts the results before being returned."""
        return json.loads(_string.strip('\''))