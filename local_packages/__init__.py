
__all__ = [
    'rich_args', 'rich_category', 'rich_collections', 'rich_core', 'rich_decorator',
    'rich_misc', 'rich_operator', 'rich_property', 'rich_recursion',
    'chainmap', 'xmldict', 'web_scraping',
    'multimaps',
    'sdf_reader',
    'aliased', 'ordereddict',
    'mysql',
    'unroll',
    'web_utility'
]

#==============================================================================
#    RichX
#==============================================================================
from local_packages.richX import (
    rich_args,
    rich_category,
    rich_collections,
    rich_core,
    rich_decorator,
    rich_misc,
    rich_operator,
    rich_property,
    rich_recursion
)
# from .richX import rich_args
# from .richX import rich_category
# from .richX import rich_collections
# from .richX import rich_core
# from .richX import rich_decorator
# from .richX import rich_misc
# from .richX import rich_operator
# from .richX import rich_property
# from .richX import rich_recursion




#==============================================================================
#    Minor Support Facilities
#==============================================================================
from local_packages.misc import chainmap, xmldict, web_scraping
from local_packages import multimaps
#from .misc import chainmap, xmldict, web_scraping
#from . import multimaps

#==============================================================================
#    Stand-alone facilities
#==============================================================================
# import multimaps
# import sdf_reader
from local_packages import sdf_reader

#==============================================================================
#    Externally Created Minor Packages
#==============================================================================
from local_packages.external import aliased
from local_packages.external import ordereddict
# import external.aliased as aliased
# import external.ordereddict as ordereddict


#==============================================================================
#    Subpackages
#==============================================================================
from local_packages.mysql import mysql
from local_packages import unroll
from local_packages import web_utility

# import mysql.mysql as mysql
# import unroll
# import web_utility










