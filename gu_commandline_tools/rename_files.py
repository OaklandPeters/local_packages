import os
import re
from optparse import OptionParser
#---- Custom modules
from generator_tools import gen_find,gen_match

#Example function calls:
#python rename_files.py -d "/home/Peters/workspace/test_files" -m "(.*)(\.sdf)(gz)" -r "{0}{1}.{2}"
#python rename_files.py -d "/home/Naiem/Documents/Siva_Kaiser_Project/Docking/Output_Files" -m "(.*)(\.sdf)(gz)" -r "{0}{1}.{2}"

def rename_files(target_directory=None,match_regex=".*",renaming_format="{0}",recursive_flag=False):
    #3MVH_HTVS_Rigid_Docking_lib.sdfgz
    if target_directory is None:
        target_directory = os.getcwd()
    if recursive_flag is False:
        max_depth = 0
    else:
        max_depth = -1
        
    
    #[] Get files
    files = gen_find("*",target_directory,max_depth)
    #for elm in files_groups:
    #    elm[0] : original full file name
    #    elm[1] : (*groups)
    files_groups = gen_match(match_regex,files)
    #files_groups = ( (fi,re.match(match_regex,fi).groups()) for fi in files)
#    (os.rename(renaming_format.format(*grps),old_path_name) for old_path_name,grps in files_groups)
    for old_path_name,grps in files_groups:
        new_path_name = renaming_format.format(*grps)
        print "About to rename {0} to {1}, based on {2}".format(old_path_name,new_path_name,match_regex)
        os.rename(old_path_name, new_path_name)
    
    
        
    

parser = OptionParser(usage="usage: %prog [options]")
parser.add_option("-d","--directory",dest="dir",
                  action="store",type="string",
                  help="Directory to read file names from. Defaults to current directory.",metavar="DIR")
parser.add_option("-m","--match",dest="match_regex",
                  action="store",type="string",
                  help="Regular expression selecting file names. Can contain groups, if so, each group should appear in the 'RENAME' parameter. Defaults to selecting all files in DIR.",metavar="MATCH")
parser.add_option("-r","--rename",dest="renaming_format",
                  action="store",type="string",
                  help="Python style format string used to rename each selected file. Each group specified by MATCH should appear in this. The entire matched string is {0}; first group {1}; etc. Defaults to the original file name.",metavar="RENAME")
parser.add_option("--recursive",dest="recursive",
                  action="store_true",default=False,
                  help="Causes this function to examine subdirectories as well.")

(options,args) = parser.parse_args()
#options    : a dictionary of the options specified for OptionParser()
#             the keys of the directionary are specified by 'dest'
#args       : positional arguments left over after parsing


#options.dir = "/home/Peters/workspace/test_files"
#options.match_regex = "(.*)(\.sdf)(gz)"
#options.renaming_format = "{0}{1}.{2}"
#options.recursive = False

rename_files(target_directory=options.dir,match_regex=options.match_regex,renaming_format=options.renaming_format,recursive_flag=options.recursive)