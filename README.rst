==============
local_packages
==============
Collected Python Utilities.

A collection of Python (and a little JS) utility modules, developed science-related webdev
and processing purposes. These are not yet presentable to outside eyes, and are
intended to eventually be migrated to several seperate cleaned up repositories.

Permanent Branches
====================
The following branches are used:

* master: various support functions constructed for and used by CCCID at some point.
* simplified: an 'in-development' branch, which strips functions and packages from master, which are not currently in use
 


Important Subpackages
=======================
The `local_packages/` package contains several sub-packages. These are the ones most relevant for CCCID:

* mysql/: MySQL command templating tool which simplifies interacting with MySQL via Python. Pointedly NOT an ORM.
* richX/: Collection of various utility, file-access, and metaprogramming tools. Discussed at more length below. 
* web_utility/: Utilities to help in testing AJAX applications via mod_python. The most important are the classes: `MockRequest`, and `AJAXRequest`.
* gu_commandline_tools/: Command-line utilities made for use by non-programmer Grad students in this lab. 
 
 

Auxillary Subpackages
========================
These auxillary subpackages are much less used:

* *external/:* Small supporting Python modules, created by 3rd party authors - but used in CCCID at some point.
* *misc/:* Convenience tools which have been re-used a few times. Chainmap is a Python 2.6 port of the Python 3 data structure of the same name. xmldict reads an XML file into a dictionary. web_scraping provides convience functions for web-scraping scientific data.
* *multimaps/:*	Provides several implementations of multimaps - essentially `dict`s, but where multiple values can be associated with each key. Multiple implementations exist - depending on how they store the values: as a List, Set, or Dict. 
* *unroll/:* Simple function which allows writing the equivalent of multiline comprehensions.
* *related-js/:* A few Javascript libraries, used by CCCID at various points.
* *sdf_reader/:* Provides iterator access over MOL entries of an SDF file, with each MOL entry being read as a dict. Convenient, although not very computationally efficient.


mysql/
---------------
Simplifies interacting with MySQL via Python. This is a command-templating tool, not an ORM (unlike SQLAlchemy). 

Example usage::

	from local_packages.mysql import MySQL
	
	CXN_DATA = {
	    "host":"localhost",
	    "user":"Peters",
	    "passwd":"...", #Fill it in here
	    "unix_socket":"/var/lib/mysql/mysql.sock",
	    "default_db":"drug_db"
	}
	
	with MySQL(**CXN_DATA) as cxn:
		tables = cxn.tables()
		print(tables) #Prints a list of tables in the current database
		
		results = cxn.select('gdid_main', columns=['cd_id'], limit=5)
		print(results)
		#({'cd_id': 11083560L}, {'cd_id': 11083561L}, {'cd_id': 11083562L}, {'cd_id': 11083563L}, {'cd_id': 11083564L})


richX
------------------------
This package-of-packages is a bit of a mess - having grown out of an ad-hoc collection of programmers utilities.
The most useful of these utilities have been refactored into stand-alone Python packages - which made them clearer to understand and re-use. However, the CCCID project used them in their current (confusing) form, and hence this form is maintained for backward compatibility.
Originally, these utitilies were used more broadly in CCCID. However, I have attempted to remove their use -- to simplify and modularize the existing code base. The remaining usages include...

 - rich_core/ 	Core meta-programming and type-related functions which are used repeatedly by other `richX` related functions. The most commonly encountered is `AssertType`/`AssertKlass` - used for type-checking variables based on Abstract Base Classes, and generating informative exceptions on that basis. 
 - rich_misc/	File-access. Used for interacting with JSON or XML files.
 

gu_commandline_tools
------------------------
normalize_csv.py and normalize_csv_standalone.py apply normalization functions to numerical values in CSV files. These were generated for Naiem Issa, to apply normalization to the results of T.M.F.S. calculations.
The remaining files are not presently used.


related-js/
----------------
Meta.js contains basic 'quality-of-life' functions, such as basic type-checking and handling default arguments. In CCCID this is the preload.js in CCCID.
The remaining libraries and not used in the current version of CCCID, but are maintained for
historical reasons.


sdf_reader/
------------------- 
For reading, writing, and manipulating chemical SDF files. Supports iteration over each molecule in the SDF file, and allows interacting with the tags of the molecule-entry as a dict. 'mdl' contains the MDL/MOL-file 3d structure, and is assumed to be a component in every molecule. ::

	from sdf_reader import *

	sdf = SDFReader("Compound_057000001_057025000.sdf")
	first_mol = sdf.read_mol()

	print("Molecule keys: "+first_mol.tags())
	for mol in sdf:
        	print(mol['mdl'])

	
	Depends on aliased.py, available at http://code.activestate.com/recipes/577659-decorators-for-adding-aliases-to-methods-in-a-clas/.

