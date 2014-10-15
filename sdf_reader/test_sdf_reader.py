"""
This is mostly just a stub file.
Better and more comprehensive tests should be written.

Actually, all of sdf_reader.py should be rewritten.
"""



import os
import unittest
#----
import sdf_reader


class ReaderTests(unittest.TestCase):
    
    expected_keys = [
        'PUBCHEM_IUPAC_INCHIKEY', 'PUBCHEM_COMPOUND_CANONICALIZED', 'mdl', 
        'PUBCHEM_IUPAC_INCHI', 'PUBCHEM_COMPOUND_CID', 'PUBCHEM_OPENEYE_ISO_SMILES',
        'PUBCHEM_ATOM_UDEF_STEREO_COUNT', 'PUBCHEM_MOLECULAR_FORMULA',
        'PUBCHEM_ISOTOPIC_ATOM_COUNT', 'PUBCHEM_CACTVS_COMPLEXITY', 'PUBCHEM_COORDINATE_TYPE',
        'PUBCHEM_BOND_DEF_STEREO_COUNT', 'PUBCHEM_CACTVS_HBOND_DONOR', 
        'PUBCHEM_IUPAC_OPENEYE_NAME', 'PUBCHEM_ATOM_DEF_STEREO_COUNT', 
        'PUBCHEM_IUPAC_TRADITIONAL_NAME', 'PUBCHEM_OPENEYE_CAN_SMILES', 
        'PUBCHEM_CACTVS_TAUTO_COUNT', 'PUBCHEM_IUPAC_NAME', 'PUBCHEM_MONOISOTOPIC_WEIGHT',
        'PUBCHEM_EXACT_MASS', 'PUBCHEM_CACTVS_HBOND_ACCEPTOR',
        'PUBCHEM_CACTVS_ROTATABLE_BOND', 'PUBCHEM_TOTAL_CHARGE', 'PUBCHEM_IUPAC_CAS_NAME',
        'PUBCHEM_MOLECULAR_WEIGHT', 'PUBCHEM_HEAVY_ATOM_COUNT', 
        'PUBCHEM_BOND_UDEF_STEREO_COUNT', 'PUBCHEM_CACTVS_SUBSKEYS',
        'PUBCHEM_IUPAC_SYSTEMATIC_NAME', 'PUBCHEM_CACTVS_TPSA', 'PUBCHEM_BONDANNOTATIONS',
        'PUBCHEM_XLOGP3_AA', 'PUBCHEM_COMPONENT_COUNT'
    ]
    infile = 'example.sdf'
    inpath = os.path.join( 
        os.path.split(__file__)[0],
        infile
    )
    
    def test_reader_basic(self):
        sdf = sdf_reader.SDFReader(self.inpath)
        
        first_mol = sdf.read_mol()
        
        self.assertEqual(
            sorted(self.expected_keys),
            sorted(first_mol.keys())
        )
    def test_iter(self):
        sdf = sdf_reader.SDFReader(self.inpath)
        
        expected = [
            'UKDWIUMKZWNHIN-UHFFFAOYSA-N', 
            'JBUFLJIMKAISIK-UHFFFAOYSA-N', 
            'JWZTVDQFAQCMQT-UHFFFAOYSA-N', 
            'GYKWYHSPNYKJSL-CQYWERSISA-N'
        ]
        key = 'PUBCHEM_IUPAC_INCHIKEY'
        inchikeys = [mol[key] for mol in sdf]
        
        self.assertEqual(inchikeys, expected)
            

if __name__ == "__main__":
    unittest.main()

# if __name__ == "__main__":
#     import pdb,pprint
#     #from sdf_reader import *
#     in_file = "/data/htdocs/gdid/python/local_packages/gu_commandline_tools/test_files/Compound_057000001_057025000.sdf"
#     
#     sdf = SDFReader(in_file)
#     
#     first_mol = sdf.read_mol()
#     print("Molecule keys: {0}.".format(first_mol.tags()))
#     
#     pdb.set_trace()
#     counter = 0
#     for mol in sdf:
#         counter += 1
#         print(mol['mdl'])
#         if counter >5:
#             break
