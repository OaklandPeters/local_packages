===========================
Collected Python Utilities
===========================

A collection of Python (and a little JS) utility modules, developed science-related webdev
and processing purposes. These are not yet presentable to outside eyes, and are
intended to eventually be migrated to several seperate cleaned up repositories.



Permanent Branches
==========
 - CCCID:	for functions used by the CCCID	project at the Dakshanamurthy laboratory.
 - master:	for general lab and web use.
 - external: for my outside projects (often web-dev stuff, or my obsession with functional programming tools).
 - stable:	for functions I have decided are moderately cleaned up. This one may aquire version numbers. 


Folders
========
 - ./gu_commandline_tools/		Made for use by non-programmer Grad students in this lab.
 - ./example_code/				Examples not worthy of being independent functions.
 - ./in_development/			Incompleted projects which may eventually become standardized functions.
 - ./related-js/				Javascript goes here. utility.js is a generic custom functions for web-work.
								collection.js and meta.js may eventually be imitated in Python.							
								underscore.js is a useful standard library I did NOT develop.
							

 


HTML.py
----
Home grown simple class for building and nesting HTML tags via Python. No dependencies. 
An example of building a form as per a SQL-table column structure returned from a query::

	include HTML
	#show_columns = [(column_name,column_display_string,column_type) for ... in sql_results]
	with HTML.Form(id_attr="my_form_id",classes="pythonic") as col_form:
		for col_name,col_display,col_type in show_columns:
			with HTML.Tag(tag='fieldset',parent=col_form) as fieldset:
				fieldset.nest(HTML.Checkbox(id=col_name)
				fieldset.nest(HTML.Label(for_id=col_name,content=col_display)
				fieldset.nest(HTML.Tag(tag='b',content="contains:"))
				fieldset.nest(HTML.Textbox(value=""))
	print(col_form)


multiprocess_utility.py
---- 
Aides in simple multiprocessing tasks. Includes examples for illustrating both multiprocesing
in Python, and this collection of utility functions.

sdf_reader.py
--- 
For reading, writing, and manipulating chemical SDF files. Supports iteration over each molecule in the SDF file, and allows interacting with the tags of the molecule-entry as a dict. 'mdl' contains the MDL/MOL-file 3d structure, and is assumed to be a component in every molecule. ::

	from sdf_reader import *

	sdf = SDFReader("Compound_057000001_057025000.sdf")
	first_mol = sdf.read_mol()

	print("Molecule keys: "+first_mol.tags())
	for mol in sdf:
        	print(mol['mdl'])

	
	Depends on aliased.py, available at http://code.activestate.com/recipes/577659-decorators-for-adding-aliases-to-methods-in-a-clas/.

mysql_connection.py
---
Simplifies interacting with MySQL via Python, and supports configuration files for standard connection settings.

organizers.py
----
Supports Configuration files in JSON and XML formats - which are imported as dict-like Configuration objects. These  support both item-style (['name']) and attribute-style (.name) access, as well as converstion to dict(), XML, and JSON formats.


Javascript Modules
==================

collection.js
---
A tool for array-style access and function application on collections of similar objects.
Still in development (although it is working as an alpha-version).
Likely will be replicated in Python.

meta.js
---
A collection of tools to make Javascript a reasonable language.
For example, category and type-checking, handling default arguments, etc.