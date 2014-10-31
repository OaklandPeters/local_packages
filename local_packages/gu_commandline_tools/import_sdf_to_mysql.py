import os
from optparse import OptionParser
#---- Custom modules
from organizers import Table
from mysql_connection import MySQL_Connection
from generator_utility import gen_find_files
from sdf_reader import SDFWriter


#local_packages updated during creation:
#generator_utility.py: gen_find_file
#organizers.py: Table()
#sdf_reader.py: SDFWriter()
#mysql_connection.py: MySQL_Connection().__init__
    #NOTE: mysql_connection.py may also have been changed (in different ways) in the version on the Laurel web-server

#Example: 
#python import_sdf_to_mysql.py -i /LOCAL_RAID/Virtual_Chemistry/expanded/ 



def sdf_to_mysql(input_path,destination_table,destination_database):
    '''
    If destination_table = None | 'None', then each SDF file will be placed into seperate tables,
    named by the non-extension part of the file name. 
    '''
    
    print("\n\nUsing input_path:{0}, \nand database:{1}\n-------\n\n".format(input_path,destination_database))
    
    #[] Handle input_path.
    input_exists = os.path.exists(input_path)
    if os.path.isdir(input_path):
        input_type = 'dir'
        #Get sdf files (ending in .sdf or .sdf.expanded)
        input_names = sorted(list(gen_find_files(input_path,".*(\.sdf\.expanded)|(\.sdf)")))    #look for things ending in .sdf or .sdf.expanded
    else:
        input_type = 'file'
        (input_path,temp_name) = os.path.split(input_path)
        if input_path[-1] != "/":
            input_path += "/"
        input_names = [temp_name]
        print("Input is just a single file.")
        
    #[] Handle type of destination_table
    if (destination_table is None) or (destination_table == "None"):
        destination_table_flag = "dynamic"  #name destination table after each input file
    else:
        destination_table_flag = "static"   #all destination tables into same table - named based on command line input 
    
    myConnection = MySQL_Connection(default_db=destination_database)
    destination = Table(myConnection,destination_database,destination_table)        #organizer class. No functionality

    for in_name in input_names:
        if (destination_table_flag is "dynamic"):
            destination_table = in_name.split('.')[0]
        sdf = SDFWriter(input_path+in_name,table_name=destination_table,db_name=destination_database)
        #[] Check existence of destination table. If it doesn't exist, create it
        if not myConnection.table_exists(destination_table):
            sdf.create_table()
        sdf.populate_table()
    
    
    import pprint
    pprint.pprint(destination.qualified)
    
    
        #Create table
    
    #[] ? Each file into a seperate table?
    #[] ? Issue: column specs do not match between tables ?
    #    option #1: add a column at the time -- problem: very slow
    #    option #2: ignore that information
    #    option #3: set a flag to decide
    return True



#[] Assemble command-line parameters
parser = OptionParser(usage="usage: %prog [options] input_path")
#parser.add_option("-i","--input",dest="input_path",
#                  action="store",type="string",default="./",
#                  help="Path of SDF file or directory containing SDF files to import to MATLAB.")
parser.add_option("-t","--table",dest="destination_table",
                  action="store",type="string",default="None")
parser.add_option("-d","--database",dest="destination_database",
                  action="store",type="string",default="raw_sdf",
                  help="Database containing the table to import data into.")
(options,args) = parser.parse_args()

ret_val = sdf_to_mysql(input_path=args[0],destination_table=options.destination_table,destination_database=options.destination_database)

print("Done ({0}).".format(ret_val))