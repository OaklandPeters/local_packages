import unittest
#----
from mysql import MySQL #pylint: disable=relative-import



CXN_DATA = {
    "host":"localhost",
    "user":"Peters",
    "passwd":"tsibetcwwi",
    "unix_socket":"/var/lib/mysql/mysql.sock",
    "default_db":"drug_db"
}

class MySQLTests(unittest.TestCase):
    def test_gdid(self):
        with MySQL(**CXN_DATA) as cxn: #pylint: disable=star-args
            assert(cxn.row_exists('pubchem_ids',{'table_id':1,'cid':57000001})
                == True)
            assert(cxn.row_exists('pubchem_ids',{'table_id':1,'cid':57000003})
                == False)
        
        from MySQLdb import ProgrammingError
        self.assertRaises(ProgrammingError, cxn.close)
        
    def test_tables(self):
        with MySQL(**CXN_DATA) as cxn:  #pylint: disable=star-args
            tables = cxn.tables()
            expected = ['JChemProperties', 'binding', 'chembl_14', 'pubchem_ids', 'gdid_main', 'gdid_main_UL', 'gdin_drug']
            for name in expected:
                self.assert_(name in tables, 'Misisng table: '+name)
                
    def test_databases(self):
        with MySQL(**CXN_DATA) as cxn:  #pylint: disable=star-args
            dbs = cxn.databases()
            expected = ['information_schema', 'drug_db', 'ng']
            for name in expected:
                self.assert_(name in dbs, 'Misisng database: '+name)
    
    def test_column_types(self):
        expected = {'smiles': 'text', 'drugbankcode': 'varchar(15)', 'name': 'text', 'drugid': 'int(11)'}
        with MySQL(**CXN_DATA) as cxn: #pylint: disable=star-args
            
            column_types = cxn.column_types('gdin_drug')
            
            for expected_name, expected_type in expected.items():
                self.assert_(expected_name in column_types, "Missing column: "+expected_name)
                self.assertEqual(
                    expected_type,
                    column_types[expected_name],
                    str.format("Column {0} should be of type {1}",
                        expected_name, expected_type
                    )
                )
    
    def test_primary_key(self):
        
        expected = {
            'gdid_main':'cd_id',
            'gdid_main_UL': 'update_id',
            'pubchem_ids': 'table_id'
        }
        
        with MySQL(**CXN_DATA) as cxn: #pylint: disable=star-args
            for table, pkey_column in expected.items():
                self.assert_(
                    cxn.primary_key(table) == pkey_column,
                    "Mismatching primary key for table: "+table
                )
    
    def test_create_drop_database(self):
        with MySQL(**CXN_DATA) as cxn: #pylint: disable=star-args
            cxn.create_database('temp_unit_test')
            self.assert_(
                cxn.database_exists('temp_unit_test'),
                "Test databse not created."
            )
            cxn.drop(database='temp_unit_test')
            self.assert_(
                not cxn.database_exists('temp_unit_tests'),
                "Database not dropped."
            )

    def test_exists(self):
        expected_row = {
            'cd_pre_calculated': 0,
            'cd_molweight': 292.35300000000001,
            'polarsurfacearea': 81.420000000000002
        }
        unexpected_row = {
            'cd_pre_calculated': 0,
            'cd_molweight': 292.35300000000001,
            'polarsurfacearea': 81.420000000000002,
            'refractivity': 1000
        }
        
        with MySQL(**CXN_DATA) as cxn: #pylint: disable=star-args
            self.assert_(cxn._database_exists('ng'))
            self.assert_(not cxn._database_exists('fakery'))

            self.assert_(cxn._table_exists('gdid_main'))
            self.assert_(not cxn._table_exists('gdid_main_foo'))
            
            self.assert_(cxn._column_exists('cd_id', 'gdid_main', database='drug_db'))
            self.assert_(not cxn._column_exists('cd_id_bar', 'gdid_main', database='drug_db'))
            
            self.assert_(cxn._row_exists('gdid_main',expected_row))
            self.assert_(not cxn._row_exists('gdid_main',unexpected_row, search_limit=1000))

    def test_exception(self):
        exc = None
        with MySQL(**CXN_DATA) as cxn:
            try:
                columns = cxn.columns(table='nonexistant')
            except Exception as exc:
                pass
            self.assert_(
                isinstance(exc, MySQL.SQLExceptionType),
                "Type of encountered exception did not match list of MySQL Exceptions."
            )
            
                        
if __name__ == "__main__":
    unittest.main()