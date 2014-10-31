#python backup.py backup.py FILENAME.EXT {MESSAGE} {VERSIONS_DIR}
#------
#Very file version script.
#Creates a copy of a file with a version number appended to name, inside a version subdirectory.
#Date, versioned file name, and an optional message stored in a JSON log file inside 
#the version subdirectory.
#Default value for VERSIONS_DIR is ./versions/ in the same directory as this script.
#------
#In Linux, to allow this to be more easily called via command line, in the style of:
#backup 
#Add the following line to the file ~/.bashrc:
#    alias backup="python /PATH_OF_THIS_SCRIPT/backup.py"
#-------


import sys
import os
import time
import shutil
import datetime
import json

if len(sys.argv) >= 2:
    in_file_path = sys.argv[1]
else:   #If len(sys.argv) == 1 because no paramters were provided 
    sys.exit("Must have a file name specified.")

#Split file parts
(in_file_dir,in_file_name_ext) = os.path.split(in_file_path)
(in_file_name,in_file_ext) = os.path.splitext(in_file_name_ext)
if len(in_file_dir) is 0:
    in_file_dir = "./"
if in_file_dir[-1] is not "/":
    in_file_dir += "/"

if len(sys.argv) >= 3:
    extra_message = sys.argv[2]         #extra message is used in writing the log file
else:
    extra_message = ""

if len(sys.argv) >= 4:
    versions_dir = sys.argv[3]
else:
    path_of_this_script = os.path.dirname(os.path.realpath(__file__))
    versions_dir = path_of_this_script + "/versions/"
    #used to be:
    #versions_dir = in_file_dir + "versions"
    
    
#Confirm that in_file exists
if os.path.exists(in_file_path) is False:
    sys.exit("ERROR: " + in_file_path + " does not exist.")





if versions_dir[-1] is not "/":
    versions_dir += "/"

#If versions_dir does not exist, make it
if not os.path.exists(versions_dir):
    print "Making directory " + versions_dir
    os.makedirs(versions_dir)
#Confirm that versions_dir is actually a directory
if not os.path.isdir(versions_dir):
    sys.exit("ERROR: " + versions_dir + " is a file, but should be a directory.")

#print in_file_dir
#print versions_dir
#print in_file_name
#print in_file_ext

ver_no = 1
tentative_path_name = versions_dir + in_file_name + "_v" + str(ver_no) + in_file_ext
while os.path.exists(tentative_path_name):
    ver_no += 1
    tentative_path_name = versions_dir + in_file_name + "_v" + str(ver_no) + in_file_ext
    

print "copying " + in_file_path + " to " + tentative_path_name
shutil.copy(in_file_path, tentative_path_name)



#=========   Now make log file with date information  =======
in_file_ver = "v"+str(ver_no)
ver_log_file = versions_dir + "a_version_log.json"
if os.path.exists(ver_log_file):
    #read from file to variable
    jfile = open(ver_log_file)      #open, read and close file
    jtext = jfile.read()
    jfile.close()
    try:
        jdata = json.loads(jtext)
    except:
        print Exception
        print "Using a blank document"
        jdata = dict()
else:
    jdata = dict()

jfile = open(ver_log_file,'w')  #open with overwriting, potentially creating file

archive_names = jdata.keys()        #all archive names in log:

if (in_file_name_ext not in archive_names):
    jdata[unicode(in_file_name_ext)] = dict()

jdata[in_file_name_ext][in_file_ver] = [unicode(datetime.datetime.now()), extra_message]
jtext = json.dumps(jdata,sort_keys = False, indent=4)   

jfile.write(jtext)  #Write to log file
jfile.close()       #Close log file