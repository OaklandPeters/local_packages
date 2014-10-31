import sys
import os
import time


filename = sys.argv[1]
if not os.path.exists(filename):
    sys.exit("File {0} does not exist.".format(filename))

statbuf = os.stat(filename)
now = time.time() 
delta = now-statbuf.st_mtime


print("File {0} last modified {1} sec ago.".format(filename,delta))
