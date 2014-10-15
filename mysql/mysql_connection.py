"""
Notice: a more modern version of this has been developed:
    mysql.py
But this is being retained because quite a few scripts already use it,
    and I'm not 100% sure that the functionality is identical.
"""

import MySQLdb
import os
import sys
import warnings
#----- Custom modules
#import utility
from .. import rich_misc #pylint: disable=relative-import
from ..external import aliased #pylint: disable=relative-import


@aliased.aliased
class MySQL_Connection(object):
    """Rather old version of a light-weight alternative to MySQL ORMs.
    More modern and well-composed alternative is mysql.py.
    """
    def __init__(self, host=None, user=None, passwd=None, default_db=None,
        mysql_config_file=None, unix_socket=None):
        '''Supplying mysql_config_file is an alternative to directly
        supplying host,user,passwd,default_db.
        '''

        if mysql_config_file is None:
            (class_dir, _) = os.path.split(__file__)
            mysql_config_file = class_dir + "/mysql_connection_config.json"
        if not os.path.exists(mysql_config_file):
            raise Exception("File not found: {0}".format(mysql_config_file))

        self._parameters = self._get_connection_parameters(
            host=host, user=user, passwd=passwd, default_db=default_db,
            unix_socket=unix_socket,mysql_config_file=mysql_config_file
        )

        if 'linux' in sys.platform:
            (self.mysql_cursor,self.mysql_cxn) = self.initialize(
                self._parameters['host'],self._parameters['user'],
                self._parameters['passwd'],self._parameters['default_db'],
                unix_socket=self._parameters['unix_socket']
            )
        else:
            (self.mysql_cursor,self.mysql_cxn) = self.initialize(
                self._parameters['host'],self._parameters['user'],
                self._parameters['passwd'],self._parameters['default_db']
            )

    @aliased.alias('initialize_parameters')
    def initialize(self, host, user, passwd, database, unix_socket=None):
        """
        @todo: Update this to use defaults read from
            self._parameters['host'],'user','passwd','default_db'
        """
        mysql_cxn = MySQLdb.connect(host, user, passwd, unix_socket=unix_socket)
        mysql_cursor = mysql_cxn.cursor(MySQLdb.cursors.DictCursor)
        mysql_cursor.execute("USE {0}".format(database))
        return (mysql_cursor, mysql_cxn)
    def close(self):
        """Close cursor and connection."""
        self.mysql_cursor.close()
        self.mysql_cxn.close()
    @property
    def open(self):
        """Predicate. Is the connection open?"""
        return bool(self.mysql_cxn.open)
    @property
    def closed(self):
        """Predicate. Is the connection closed?"""
        return not self.open

    def execute(self, sql_command, params=None):
        """Execute a sql command, with optional formatting parameters."""
        with warnings.catch_warnings():
            ret_val = self.mysql_cursor.execute(sql_command,params)
        return ret_val

    def run(self,sql_command,params=None):
        '''Sugar for combining .execute(sql_command) and
        .get_results() for simplicity of writing.'''
        self.execute(sql_command,params)
        return self.mysql_cursor.fetchall()
    def get_results(self):
        """Retreive all results of last query."""
        results = self.mysql_cursor.fetchall()
        return results
    def commit(self):
        """Commit all pending database transactions."""
        self.mysql_cxn.commit()
    def _get_connection_parameters(self, **kwargs): #pylint: disable=star-args
        '''Often reads from mysql_config_file='mysql_connection_config.json'.
        This function is kludge-y and very inelegant....
        Example mysql_connection_config.json:
        {
        "host":"localhost",
        "user":"USER",
        "passwd":"PASSWORD",
        "unix_socket":"/tmp/mysql.sock",
        "default_db":"DB_NAME"
        }
        Another common "unix_socket":"/var/lib/mysql/mysql.sock"
        '''
        parameter_names = ('host','user','passwd','default_db','unix_socket')
        mysql_config_file = kwargs.get('mysql_config_file','mysql_connection_config.json')

        #[] Set defaults - via config file
        try:
            _parameters = rich_misc.read_json(mysql_config_file)
        except Exception:
            _parameters = {}

        #[] Overwrite defaults with kwargs
        for key,val in kwargs.items():
            if (key in parameter_names) and (val is not None):
                _parameters[key] = val

        #[] Check that all Parameters Provided and not None
        for pname in parameter_names:
            #if pname not in _parameters.keys(), or _parameters[pname] is None
            if _parameters.get(pname, None) is None:
                raise Exception(("Connection parameter named '{0}' was not"
                                 " provided  as a keyword, or in mysql_config_file ({1})."
                                ).format(pname,mysql_config_file))
        return _parameters

    def get_table_names(self, database=None):
        """Retreive names of all tables in a database (can use the default database)."""
        if database is None:
            self.mysql_cursor.execute("SHOW TABLES")
        else:
            self.mysql_cursor.execute("SHOW TABLES in {0}".format(database))

        rows = self.mysql_cursor.fetchall()
        table_names = [row.values()[0] for row in rows]
        return table_names


    def get_column_names(self, table_name, database=None):
        """Retreive the names of all columns in a table."""
        try:
            if database is None:
                self.execute("DESCRIBE {0}".format(table_name))
            else:
                self.execute("DESCRIBE {1}.{0}".format(table_name,database))
        except Exception:
            print "Could not find the table called {0}.".format(table_name)
            raise
        results = self.get_results()

        column_names = [row['Field'] for row in results]
        return column_names

    def columns(self, table, database=None):
        """Retreive names of all columns from a table."""
        return self.get_column_names(table, database)

    def get_column_types(self, table, database=None):
        """Retreive the types of columns."""
        try:
            if database is None:
                self.mysql_cursor.execute("SHOW FIELDS FROM {0}".format(table))
            else:
                self.mysql_cursor.execute(
                    "SHOW FIELDS FROM {0}.{1}".format(
                        database,
                        table
                    )
                )
        except Exception:
            print "Could not find the table called {0}.".format(table)
            raise

        results = self.mysql_cursor.fetchall()
        columns_and_types = {}
        for res in results:
            columns_and_types[res['Field']] = res['Type']
        return columns_and_types

    def table_exists(self,table_name,database=None):
        """Does a table exist?"""
        if database is None:
            self.execute("SHOW TABLES LIKE '{0}'".format(table_name))
        else:
            self.execute("SHOW TABLES IN {0} LIKE '{1}'".format(database,table_name))
        results = self.get_results()
        if len(results) > 0:
            return True
        else:
            return False

    def table_size(self,table):
        """Retreive the number of rows in a table."""
        results = self.run("SELECT count(*) FROM {0};".format(table))

        if not len(results):
            #if no results found
            return 0
        else:
            #Results looks like: ({'count(*)': 24999L},)
            #--> takes some wrangling
            return int(first(first(results).values()))

    def drop_table(self,table_name):
        """Drop a table from the default database."""
        if not self.table_exists(table_name):
            return "Table {0} does not exist in db {1}".format(
                table_name,self._parameters['default_db']
            )
        try:
            self.execute("DROP TABLE {0}".format(table_name))
            return ""
        except Exception as exc:
            return (str.format(
                "Error while attempting to drop table {0}.\nReceived exception: {1}.",
                table_name,exc
            ))
    def find_primary_key(self, mysql_cursor, database, table):
        '''Finds a primary key in database.table, using mysql_cursor.
        Assumes only one primary key.'''
        #mysqlConnection.run()
        mysql_cursor.execute("DESCRIBE {0}".format(database+"."+table))
        results = mysql_cursor.fetchall()
        #Results: one tuple per column, each tuple contains a dict
        #Example column dict: {'Extra': 'auto_increment',
        #    'Default': None, 'Field': 'cd_id', 'Key': 'PRI',
        #    'Null': 'NO', 'Type': 'int(11)'
        #}
        for column_dict in results:
            if column_dict['Key'] == 'PRI':
                return column_dict['Field']

    #===========================  Dict-Based Inputs
    def insert_dict(self,table_name,data_dict):
        '''Adds contents of dictionary to a table. keys() define columns.'''
        table_columns = self.get_column_names(table_name)   #get columns of table
        #Filter out data keys(~columns) not in the table
        valid_data_dict = dict(
            (k,v)
            for k,v in data_dict.items()
            if k in table_columns
        )
        if valid_data_dict == {}:
            return None
        else:
            sql_insert = (
                "INSERT INTO {table} ({columns}) "
                "VALUES ('{values}');"
                ).format(
                    table   = table_name,
                    columns = ', '.join(str(k) for k in valid_data_dict.keys()),
                    values  = "', '".join(str(v) for v in valid_data_dict.values())
                )
            self.run(sql_insert)
            return sql_insert

    def row_exists(self,table_name,data_dict,print_sql=False):
        """Does row exist?"""
        sql_select = self._compose(
            "SELECT *",
            "FROM {table}",
            "{where}",
            "    {limit}",
            table=table_name,
            where=self._where_clause(data_dict),
            limit=self._limit_clause('1')
            )

        if print_sql:
            print(sql_select)

        results = self.run(sql_select)

        return len(results) != 0    #if at least 1 result found --> row exists

    def _compose(self,*clauses,**format_inserts):
        '''Turn SQL clauses into a single statement string,
        formatted for readability, and removing empty clauses.
            Keyword arguments are applied as formatting
            ~clause.format(kwarg). An example:  

        >>> cxn._compose("SELECT *","FROM {table}","{where}","LIMIT 1",
                                table='protein',where='')
        "SELECT *\nFROM protein\nLIMIT 1;\n"
        '''
        #[] Apply formatting (which may make some parts empty)
        parts = [part.format(**format_inserts) for part in clauses]

        #[] Filter out empty parts
        parts = [part for part in parts if part not in (None,'')]

        #[] Ensure that sequence ends with ';\n'
        if parts[-1].endswith(';'):
            parts[-1] += '\n'
        elif parts[-1].endswith(';\n'):
            pass
        elif parts[-1].endswith('\n'):
            parts[-1] = parts[-1][:-1]+';\n'
        else:
            parts[-1] += ';\n'
        phrase = '\n'.join(parts)
        return phrase
        #return self.escape(phrase)
    def _validate_indent(self, indent='    '):
        """--"""
        if indent is False:
            indent = ''
        elif indent is True:
            indent = '    '
        elif type(indent) is int:
            indent = ' '*indent
        assert(isinstance(indent, basestring))
        return indent
    def _where_clause(self,iterable,indent='    '):
        ''' 'iterable' specifies {column}={value} pairs.
        Either as an iterable of pairs, or as a dict.'''
        indent = self._validate_indent(indent)
        if len(indent)==0:
            #for any 'AND' clauses
            inner_indent = ' '
        else:
            inner_indent = indent*2

        #duck-typing for:    if iterable is None,False,{},[],tuple()  IE empty
        if bool(iterable) == False:
            return ""


        if hasattr(iterable,"items"):
            iterator = iterable.iteritems()
        elif hasattr(iterable,"__iter__"):
            iterator = ((col,val) for col,val in iterable)
        else:
            raise TypeError("'iterable' must be a Mapping, or key,value pairs")

        where_parts = [
            "{0} = '{1}'".format(col,self.escape(val))
            for col,val in iterator
        ]


        where_clause =  (indent+'WHERE ')
        where_clause += ('\n'+indent+inner_indent+'AND ').join(where_parts)
        #where_clause += '\n'
        return where_clause
    def _limit_clause(self, limit, indent='    '):
        """Construct a limit clause, properly indented."""
        indent=self._validate_indent(indent)
        if limit in (None,''):
            return ""
        if type(limit) in [tuple,list]:
            assert( len(limit) in [1,2]), "'limit' must be one or two numbers."
            limit = ', '.join(limit)
        elif type(limit) is int:
            limit = str(limit)
        assert(type(limit) in (str,unicode)), (
            "Input 'limit' must be string or list/tuple of 1 or 2 integers."
        )
        return 'LIMIT {0}'.format(limit)




    def select(self,tables,columns,where=None,limit=None):
        '''
        if columns is list/tuple --> SELECT {columns}
        if columns is dict --> SELECT {columns.keys()} WHERE
        '''
        if not hasattr(tables,'__iter__'):
            tables = [tables]
        if not hasattr(columns,'__iter__'):
            columns = [columns]
        if hasattr(columns, 'keys'):
            columns = columns.keys() #pylint: disable=maybe-no-member

        if hasattr(columns,"keys"):
            assert(where is None), (
                "If 'columns' is a dict, then a 'where' input should not be provided."
            )
            clauses = {
                'select': "SELECT "+', '.join(str(k) for k in columns),
                'from': "FROM "+', '.join(k for k in tables),
                'where': self._where_clause(columns),
                'limit': self._limit_clause(limit)
            }
        elif hasattr(columns,"__iter__"):     #duck-typing for:    if type(columns) in [tuple,list]:
            clauses = {
                'select': "SELECT "+', '.join(str(k) for k in columns),
                'from': "FROM "+', '.join(k for k in tables),
                'where': self._where_clause(where),
                'limit': self._limit_clause(limit)
            }
        else:
            raise TypeError()

        sql_select = self._compose( #pylint: disable=star-args
            "{select}","{from}","{where}","{limit}",
            **clauses
        )
        return self.run(sql_select)
    #================================== END: Dict-Based Inputs


    def create_database(self,new_name):
        """Create a databse by name."""
        self.run("CREATE DATABASE {0}".format(new_name))
    def drop_database(self,database):
        """Drop a database entirely.
        @TODO Remove this function. It's dangerous.
        """
        self.run("DROP DATABASE {0};".format(database))
    def database_exists(self,database):
        """Predicate. Does database exist?"""
        sql_check = str.format(
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{0}';",
            database
        )
        results = self.run(sql_check)
        if len(results) != 0:
            return True
        else:
            return False
    def rename_database(self,old_name, new_name):
        """Rename a database."""
        assert(self.database_exists(old_name)), (
            str.format(
                "Database renaming failed, because database '{0}' does not exist.",
                old_name
            )
        )
        assert(not self.database_exists(new_name)), (
            str.format(
                "Database renaming failed, because database '{0}' already exists.",
                new_name
            )
        )

        self.create_database(new_name)
        for table in self.get_table_names(old_name):       #Rename each table
            sql_rename = '''RENAME TABLE {0}.{2} TO {1}.{2};'''.format(old_name,new_name,table)
            self.run(sql_rename)
            
        self.drop_database(old_name)

    def create_table(self,new_table,like=None,columns=None,primary_key=None):
        '''
        'like': if provided a table name
        'columns': string specifying columns
        '''
        assert(bool(like) != bool(columns)), (
            "One, and only one of 'like' or 'columns' should be provided."
        )

        if like:
            assert(self.table_exists(like)), (
                "Table specified by 'like' ({0}) does not exist.".format(like)
            )
            sql_create_insert = (
                "CREATE TABLE {0} LIKE {1};"
                "INSERT {1} SELECT * FROM {0};"
            ).format(new_table,like)
            return self.run(sql_create_insert)
        else:   #assumes
            assert(type(columns) in [list,tuple]), (
                "Columns should be specified as a list or tuple of strings."
            )
            assert(all([type(col)==str for col in columns])), (
                "Not all entries in 'columns' are strings."
            )
            assert(not self.table_exists(new_table))

            if primary_key in [None,False]:
                pkey = ""
            else:
                pkey = "    {0}\n".format(primary_key)

            sql_create = (
                "CREATE TABLE {name}(\n"
                "    {all_columns}\n"
                "{pkey});"
            ).format(
                name=new_table,
                all_columns=",\n    ".join(columns),
                pkey=pkey)

            return self.run(sql_create)

    def copy_table(self, old_table, new_table):
        """Copy a table from one name to another."""
        assert(self.table_exists(old_table)), (
            str.format(
                "Copy failed. Existing table '{0}' already exists.",
                old_table
            )
        )
        assert(not self.table_exists(new_table)), (
            str.format(
                "Copy failed. New table '{0}' already exists.",
                new_table
            )
        )

        self.create_table(new_table,like=old_table)
    def escape(self, string):
        """Escape a string."""
        return self.mysql_cxn.escape_string(str(string))
    def format(self, command, *args, **kwargs):
        """Format a command, but escape the arguments first."""
        fargs = [self.escape(arg) for arg in args]
        fkwargs = dict(
            (key,self.escape(value))
            for key,value in kwargs.items()
        )
        return command.format(*fargs, **fkwargs) #pylint: disable=star-args
    #==================================================================
    #Context Manager
    #==================================================================
    def __enter__(self,*args,**kwargs):
        return self
    def __exit__(self,exception_type, exception_value, traceback):
        try:
            self.close()
        except MySQLdb.ProgrammingError:
            #Not closable
            return True

    #===================================================================
    #    Magic Methods
    #===================================================================
    def __bool__(self):
        """MySQL_Connection() object considered true when cxn is open. """
        return self.open

    #==================================================================
    #    Very New
    #==================================================================
    def describe(self, table, database=None):
        """Describe a table."""
        return self.run("DESCRIBE {0};".format(self.qualified(table, database)))
    def qualified(self, table, database=None):
        """Generate qualified table name."""
        #@future: store default database
        if database == None:
            if self.default_db == None:
                raise Exception("Cannot qualify table, because no database "
                    "provided, or default database set.")
            return self.default_db+"."+table
        else:
            return database+"."+table
    @property
    def default_db(self):
        """Default value to use for database name."""
        database = singleton(self.run("SELECT DATABASE();"))
        if database in ["null","NULL","Null"]:
            return None #No default database set
        return database
    #@property
    #def default_db(self):
    #    result = self.run("SELECT DATABASE();")
    #    return result[0].values()[0]

    #==================================================================
    #def call_linux(self):
    #    pass
    #def get_column_names(self):
    #    pass
    #def get_table_names(self):
    #    pass




#==============================================================================
#        Convience Functions
#==============================================================================
def first(iterable):
    """Return first element of an iterable."""
    return next(iter(iterable))
def singleton(results):
    """Get the first value. Used repetively for queries returning a single
    piece of data.
    >>> results = cxn.run("SELECT DATABASE();")
    >>> print(singleton(results))
    #print default db
    """
    return first(first(results).values())




