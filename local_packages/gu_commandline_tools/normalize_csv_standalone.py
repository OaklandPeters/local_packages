#--- Standard modules
from math import exp
import os, sys
import functools
from optparse import OptionParser
import pickle
import datetime
#--- Modules used by Support Functions:
import re
import csv


help = '''
====== Calling:
    python normalize_csv_standalone.py [options] INPUT_PATH [TARGET_COLUMN]
        TARGET_COLUMN:    the column to be normalized. Default: 
    options:
        --output OUTPUT_PATH
        --coefficient COEFF                : coefficient for the sigmoid equation. Defaults to 1
        --header YES_NO                    : whether or not a header row is at the top of the csv
        --norm FLAT_OR_BASIC               : if 'flat', sets range of inputs == [0-3] --> output of 0, and normalizes based only on everything above this
====== Example calls: 
-- For Naiem:
    python normalize_csv_standalone.py --norm "basic" --coefficient 0.25 --header No /home/Naiem/Documents/Testing/Conformer_Reflig_Euclidean_Distances/HMDB00020 1

-- For testing the 'flat' condition:
    python normalize_csv_standalone.py --norm "flat" --coefficient 0.25 --header No ./test_files/test_flat_v2.csv 0
    python normalize_csv_standalone.py --norm "flat" --flat-max 2 --coefficient 0.25 --header No ./test_flat_norm.csv 0

-- For testing the 'negative' condition:
    python normalize_csv_standalone.py --norm "negative" --coefficient 0.25 --header No ./test_inverse.csv 0

-- Extra examples:
    python normalize_csv_standalone.py --norm "flat" --output ./data_files/normalized_data.csv --coefficient 0.25 --header No ./data_files/HTVS_Docking_Output_2251.csv 2
    python normalize_csv_standalone.py --norm "flat" --coefficient 0.25 --header No ./Lig_Lig_Shapes 1
    python normalize_csv_standalone.py --norm "basic" --coefficient 0.25 --header No ./Post_Docking_Shape 


====== Parameters:
--norm    (variable name: norm_type): 
    refers to the normalization function used.
    'basic' - applies a sigmoid curve: f(x) = 1- abs(0.5 - (1 / (1 + exp(-alpha*x))*2 )
        Where alpha is a customizable scalar coefficient (usually chosen 'by-hand' to maximize post-normalization variance)
    'flat' - flatten
'''






#=================== Support Functions ==========================
#Originally found in other files - moved here so this can be a stand-alone script.

#From: generator_utility.py
def gen_find_files(directory,regex):
    '''Look for files in directory which match regex. Only looks one level deep.'''
    for file_name in os.listdir(directory):
        if os.path.isfile(os.path.join(directory,file_name)):
            if re.match(regex,file_name):
                yield file_name

#From: organizers.py
class FilePath(object):
    '''Splits up path of folder or file into component parts, 
    and checks if it exists (.exists). 
        Variables:
            self.exists
            self.dir
            self.check (method)           : Confirms that the file exists.
        For directories:
            self.ftype == "dir"
            self.full_name == self.name   : the final directory (~after the last '/')
            self.ext                      : blank
        For files:
            self.ftype == "file"
            self.full_name                : NAME.EXT
            self.name                     : NAME        
            self.ext                      : .EXT
        '''
    def __init__(self,in_path):
        self.in_path = in_path
        self.exists = os.path.exists(in_path)
        self.ftype = 'dir' if os.path.isdir(in_path) else 'file'
        (self.dir,self.full_name) = os.path.split(in_path)   
        (self.name,self.ext) = os.path.splitext(self.full_name)
        
        if self.dir == "":  #if no 'dir' - such as for relative paths
            self.dir = "."
            
        #@deprecated ???
        self.dir_parts = (self.dir).split(os.path.sep)

    def check(self):
        self.exists = os.path.exists(self.in_path)
        if self.exists is False:
            raise IOError("No such file or directory: '{0}'".format(input.in_path))
    def join(self):
        return os.path.join(self.dir,self.name+self.ext)
    def __str__(self):
        return self.in_path
    def __repr__(self):
        return str(self.__dict__)


#From: file_utility.py
#Used by CSVReader, CSVWriter
class FileReader(object):
    '''Basic class, not useful by itself - intended to be base class for CSVReader() and CSVWriter().
    Note, this class is not just for reader, but general file I/O.
    On object creation, finds name parts (directory,name,extension), and opens file.
    Creation:
        myFile = FileReader(full_path,mode='r')
        fDir,fName,fExt = myFile.parts()
    '''
    def __init__(self,full_path,mode='r'):
        self.full_path = full_path
        (self.dir,self.full_file_name) = os.path.split(full_path)
        (self.name,self.ext) = os.path.splitext(self.full_file_name)
        if mode is not None:
            self.open(mode)
        else:
            self.file = None
    def parts(self):
        '''Returns: (dir,name,ext) for file.'''
        return self.dir,self.name,self.ext
    def open(self,mode='r'):
        self.mode = mode
        try:
            self.file = open(self.full_path,self.mode)
        except IOError as ioexc:
            print("Could not open file {0}.".format(self.full_path))
            print(ioexc)
            if not os.path.exists(self.full_path):
                print("That path does not exist.")
                try:
                    import getpass
                    print("Or possibly current user '{0}' does not have permissions to see it.".format(getpass.getuser()))
                except:
                    pass
            print("\n\n============")
            raise
    def write(self,seq):
        if hasattr(seq,'__iter__'):
            for elm in seq:
                self.file.write(str(elm))
        else:
            self.file.write(str(elm))
    def __del__(self):
        if self.file is not None:
            self.file.close()
    close = __del__ #set alias for __del__
    
#From: file_utility.py
class CSVReader(FileReader):
    def __init__(self,path,columns_name=None,mode='rU',get_header=True,delimiter=",",quotechar="\""):
        FileReader.__init__(self, path,mode)    #'rU' read in universal-newline mode
        self.reader = csv.reader(self.file,delimiter=delimiter,quotechar=quotechar)
        if columns_name is not None:
            self.headers = columns_name
            if get_header is True:
                self.reader.next()        #Advance past the header line
        else:
            if get_header is True:      #Get column names from the first line
                self.headers = self.reader.next()
            else:                       #Simply number the columns
                first_line = self.peek()
                self.headers = range(len(first_line))
                #first_line = self.reader.next()
                #self.file.seek(0)
                #self.headers = range(len(first_line))
    def __iter__(self):
        return self.reader
    def next(self):
        return self.reader.next()
    def peek(self,N=1):
        '''Return the next $count lines, without moving the file-pointer.'''
        
        try:
            original_position = self.file.tell()
            #list(itertools.islice(self.file,N))
            lines = [self.reader.next() for _ in range(N)] #Do create do as a generator, because that would move the file pointer as they were generated.
            self.file.seek(original_position)
            return lines
        except:
            print(self.parts())
        
    def set_key(self,key_name):
        self.key = key_name
        #self.keys = [key for key in key_names if key in self.headers]
        #return self.keys
    def get_lines(self):
        return [row for row in self.reader]
        #return [line for line in self.file]
    def get_lines_dict(self,split_on=","):
        return [dict(zip(self.headers,row)) for row in self.reader]
        #return [dict(zip(self.headers,line.split(split_on))) for line in self.file]
    def gen_lines(self):
        '''This is not used presently.'''
        for row in self.reader:
            yield row
    #Line generators (~deferred execution)
    def gen_lines_dict(self):
        for row in self.reader:
            yield dict(zip(self.headers,row))

    def gen_lines_key(self,key):
        for row in self.reader:
            yield dict(zip(self.headers,row))[key]

#From: file_utility.py
class CSVWriter(FileReader):
    def __init__(self,path,mode='w',delimiter=",",quotechar="\""):
        #super(CSVReader,self).__init__()
        FileReader.__init__(self, path,mode)
        #put quotes around all non-numeric fields, and convert all numeric fields to float
        self.writer = csv.writer(self.file,delimiter=delimiter,quotechar=quotechar,quoting=csv.QUOTE_NONNUMERIC)
        self.delimiter = delimiter
        self.quotechar = quotechar
    def write_row(self,seq):
        #this might need me to convert things to str()
        #full_delim = self.quotechar + self.sep + self.delim #goes between entries ~ for .join()
        #self.file.write(self.delim + full_delim.join(seq) + self.delim)
        if type(seq) is dict:
            seq = seq.values()
        self.writer.writerow(seq)
        
#From: meta.py - modified for this purpose
def _ensure_number(obj):
    basic_types = (int,long,float,complex)
    #If it is already a number - do nothing
    if type(obj) in basic_types:
        return obj
    #If it is a string - try to convert it
    elif type(obj) in (str,unicode):
        converted_value = None
        #Try to convert to each of the basic types until one works
        for num_type in basic_types:
            try:
                return num_type(obj)
            except:
                pass
    #Fallthrough condition - turn to string
    return str(obj)
#=============================================



#=========================================================================
#                 Mathematical Normalization functions
#=========================================================================
class Norms(object):
    @staticmethod
    def sigmoid(x,coef=1):
        return 1 / (1 + exp(-coef*x))
    @staticmethod
    def basic(diff,coef=1):
        #diff = target - ref
        return  1- 2*abs(0.5 - Norms.sigmoid(diff,coef))
    @staticmethod
    def flat(diff,coef=1,flat_max=3):
        #flat_max ~~> flat_range : 0 <= diff <= flat_max
        if diff <= flat_max:
            return 1
        else:
            return Norms.basic(diff-flat_max,coef)
    @staticmethod
    def negative(diff,coef=1,base=11.0):
        if diff >= 0:   #positive values --> 0
            return 0
        else:           #negative values --> normalized as if they were positive
            #return basic_normalization(-diff,coef)
            #return basic_normalization(-(1.0/diff),coef)    #standard range inversion about 1
            #return Norms.basic(-(11.0-diff),coef)
            return Norms.basic(-(base-diff),coef)
    @staticmethod
    def inverted(diff,coef=1,numerator=10.0):
        #Developed for Naiem's docking results
        #Found reasonable results for coef = 1, numerator=10.0
        numerator = float(numerator)
        if diff >= 0:
            return 0
        else:
            return Norms.basic(numerator/diff,coef)
    @staticmethod
    def positive_definite(diff,coef=1):
        return sigmoid(diff,coef)
    @staticmethod
    #def flip_positive_definite(diff,coef=1):
    def flip_positive_definite(diff,coef=1):
        #Negative values limit --> 1
        #Positive values limit --> 0
        return 1 - Norms.sigmoid(diff,coef)
Norms.func_map = [
        (('f','flat'),Norms.flat),
        (('b','basic'),Norms.basic),
        (('n','negative'),Norms.negative),
        (('i','inverted','inverse'),Norms.inverted),
        (('pos_def','positive_definite'),Norms.positive_definite),
        (('flip_pos_def','flip_positive_definite'),Norms.flip_positive_definite)
    ]
Norms.keywords = [word for kywds in Norms.func_map for word in kywds[0]]



#=========================================================================
#                 Core Functions
#=========================================================================

            
#[] Core function - new version
def normalize_input(input_path,target_column,output_path=None,norm_type='flat',coef=1,header_flag=True,flat_max=3):
    '''Work-horse function for normalizing the input.
    Problems: 
    #1: Having a 'main' function this large is bad program design. 
        It should be refactored and split (and I would if I had time).
    '''
    #[] Validate input
    assert(norm_type in Norms.keywords), "norm_type should be one of {0}".format(Norms.keywords)    
    
    #[] Initialize Variables
    #Output reporting flags
    record_parameters_flag      = True
    record_population_flag      = True
    record_unprocessed_files_flag   = True
    quoting_flag = False    #if True-prefers to output numbers as quoted strings, if False - prefers to output numbers as unquotes floats
    # Flow control flags
    report_index_error = True
    index_error_message = ""
    #Counters
    file_counter = 1
    #Data accumulators
    total_population = []
    unprocessed_files = []
    
    #[] Get root directory & target files from input_path
    if os.path.isdir(input_path):
        #input.file_names = [file_name for file_name in gen_find_files(input.in_path,".*") if os.path.isfile(file_name)]
        root_dir = input_path
        if root_dir[-1] != os.sep:
            root_dir += os.sep
        #@note: the use of FilePath here is redundant with FileReader... I should probably merge those classes when I have time.
        targets = [FilePath(input_path+os.sep+file_name) for file_name in gen_find_files(input_path,".*") if os.path.isfile(input_path+os.sep+file_name)]
    else:
        root_dir,_ = os.path.split(input_path)
        if root_dir[-1] != os.sep:
            root_dir += os.sep
        
        targets = [FilePath(input_path)]        
        #input.file_names = [input.in_path]
    
    population_file_name = "total_population.pickle"
    population_file_full_path = root_dir+os.sep+population_file_name
    parameters_file_name = "normalization_processing_record.txt"
    parameters_file_full_path = root_dir+os.sep+parameters_file_name
    
    
    #[] Filter Out Unwanted Files
    targets = (target for target in targets
               if target.full_name not in (population_file_name,parameters_file_name)
               and not re.match('.*?_normalized\..*?',target.full_name))
    
    
    class Numeric_Range(object):
        def __init__(self,default_min,default_max):
            self.min = default_min
            self.max = default_max
        def check(self,value):
            if (self.min == None) or (value < self.min):
                self.min = value  #set new minimum
            if (self.max == None) or (value > self.max):
                self.max = value #set new max
    targets_range = Numeric_Range(None,None)
    norms_range = Numeric_Range(None,None)
        
    #for target in input.file_names:
    for target in targets:
        try:
            in_csv = CSVReader(target.in_path,mode='r',get_header=header_flag)   #parses file name --> in_csv.dir,in_csv.name,in_csv.ext
            

            if output_path is None:             out = target
            else:                               out = FilePath(output_path)
            
            if os.path.isdir(input_path):       out.name += '_'+str(file_counter)
            else:                               out.name += '_normalized'
            
            destination = FilePath(out.join())
            out_csv = CSVWriter(destination.in_path,mode='w')
            
            #[] Parse norm_type into a function call
            for keywords,func in Norms.func_map:
                if norm_type in keywords:
                    if norm_type in ('f','flat'):
                        norm_function = functools.partial(func,flat_max=flat_max) #set the flat_range keyword argument now, so the norm_function's call profile --> norm_function(diff,coef)
                    else:
                        norm_function = func
                    break
            else:   #No norm_function found
                raise Exception("Invalid 'norm_type', should be one of {0}.".format(Norms.keywords))

            #[] Parse header flag
            if header_flag.lower() in ["true","yes","y","1"]:
                headers = in_csv.next()
                out_csv.write_row(headers + ["norm"])

            #[] Read input file
            for row in in_csv:
                try:
                    norm = norm_function(float(row[target_column]),coef=coef)
                except IndexError as indexc:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    error_info = {'lineno':exc_tb.tb_lineno,
                                  'filename': os.path.split(exc_tb.tb_frame.f_code.co_filename)[1],
                                  'columnno':target_column}
                    excmsg = ("\n\n"
                              "=================================\n"
                              "  Encountered an IndexError at line {lineno} for input file '{filename}',\n"
                              "  while trying to normalize column #{columnno}\n"
                              "  This probably indicates you entered the wrong target column at the commandline.\n"
                              "  Column numbering begins at '0'. Thus, the 2nd column in a file should be '1'.\n"
                              "=================================\n"
                              ).format(**error_info)
                    index_error_message = excmsg
                    report_index_error = True
                    raise IndexError(excmsg)
                

                
                try:
                    if quoting_flag:    #output numbers as quoted strings
                        out_csv.write_row(row + [str(norm)])
                    else:   #output numbers without quotes
                        out_csv.write_row([_ensure_number(elm) for elm in row+[norm]])
                except:
                    print(sys.exc_info())
                    import pdb
                    pdb.set_trace()
                    print([_ensure_number(elm) for elm in row+[norm]])
                
                
                targets_range.check(row[target_column]) #Check for new min/max
                norms_range.check(norm)                 #Check for new min/max
                if record_population_flag is True:
                    total_population.append([row[target_column],norm])
        except:
            #Get Exception info for files which failed to process
            #This data will be reported after all files have succeeded or failed.
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            
            
            if exc_type == IndexError and report_index_error == True:
                report_index_error = False
                print(exc_obj)
            
            #In file that leads to error, error'ed file name, error'ed line number
            unprocessed_files.append({'target file':target.full_name,
                                      'target path':target.in_path,
                                      'exception':exc_type,
                                      'errored file':fname,
                                      'errored line':exc_tb.tb_lineno})
            
            
        #[] Cleanup after loop execution
        try:
            in_csv.close()
            out_csv.close()
        except: 
            #the in_csv() and out_csv may not be exist, if so, they don't need to be closed.
            pass
        file_counter += 1
    
    #[] Record parameters for analytic & debugging purposes
    #[] ALSO: print list of all files which could not be processed
    if record_parameters_flag or record_unprocessed_files_flag:
        with open(parameters_file_full_path,'a') as record:
            print_msg = ""
            file_msg = ("For input-path: {inpath}\n"
                   "Date-time = {date}\n"
                   "Norm type = {norm_type}, Flat max={flat_max}, coefficient = {coef}\n"
                   "Range of target values = {t_min} to {t_min}\n"
                   "Range of normed values = {n_min} to {n_max}\n"
                   ).format(inpath=input_path,
                            date=datetime.datetime.now(),
                            norm_type=norm_type,       flat_max=flat_max,        coef=coef,
                            t_min=targets_range.min,    t_max=targets_range.max,
                            n_min=norms_range.min,      n_max=norms_range.max
                            )
            
            #----------------------     Record unprocessed files
            if record_unprocessed_files_flag and (len(unprocessed_files)>0):
                print_msg += "---- Unprocessed Files: ----\n"
                file_msg  += "---- Unprocessed Files: ----\n"
                
                for exception_data in unprocessed_files:
                    file_msg += ("    {target file}: {target path}"
                            " encountered Exception '{exception}'"
                            " at line {errored line} in {errored file}\n"
                            ).format(**exception_data)
                    print_msg += ("    {target file}\n".format(**exception_data))
                print_msg += ("\n\n--------\n"
                              "Please see file {0} for more information on why"
                              "these files were not processed."
                              ).format(parameters_file_full_path)
                
            #Close messages
            file_msg  += "\n=========================\n\n"
            file_msg  += index_error_message
            print_msg += index_error_message
            #Output
            record.write(file_msg)
            print(print_msg)       

    #[] Record population for more advanced analytic purposees
    if record_population_flag:
        pickle.dump(total_population,open(population_file_full_path,'wb'))
        
    return True




if __name__ == "__main__":
    #[] Assemble command-line parameters
    parser = OptionParser(usage="usage: %prog [options] input_path target_column")
    #parser.add_option("-i","--in_file",dest="in_file",
    #                  action="store",type="string",
    #                  help="Input file. Full path or relative path.",metavar="IN_FILE")
    parser.add_option("-n","--norm",dest="norm_type",
                      action="store",type="string",default="basic",
                      help="Type of normalization to apply. Valid forms include: {0}.".format(Norms.keywords),metavar="NORM_TYPE")
    parser.add_option("-f","--flat-max",dest="flat_max",
                      action="store",type="float",default=3.0,
                      help="If norm type (-n/--norm) == 'f'/'flat', then this specifies the range: [0,FLAT_MAX].",metavar="FLAT_MAX")
    parser.add_option("-o","--output",dest="output_path",default=None,
                      action="store",type="string",
                      help="CSV file (or directory containing csv files) to operate on.")
    parser.add_option("-c","--coefficient",dest="coef",default=1,
                      action="store",type="float",
                      help="Coefficient for the slope in normalization.")
    parser.add_option("--header",dest="header_flag",default='True',
                      action="store",type="string",
                      help="If yes/true/y, then reads and writes a header (column names) row from input and output file.")
    (options,args) = parser.parse_args()
    
    #[] Required Arguments
    try:
        input_path=args[0]
        assert(os.path.exists(input_path)), "No such file or directory: {0}".format(input_path)
    except:
        raise
    try:
        target_column = int(args[1])
    except:
        raise Exception(("Missing target column number after input path.\n"
                         "Column numbering begins at '0'."
                         " Thus, the 2nd column in a file should be '1'."))
    
    #ret_val = apply_normalization(input_path=args[0],target_column=args[1],output_path=options.output_path,norm_type=options.norm_type,coef=options.coef,header_flag=options.header_flag)
    #Using updated core function, which records unprocessed files:
    ret_val = normalize_input(input_path=args[0],
                              target_column=target_column,
                              output_path=options.output_path,
                              norm_type=options.norm_type,
                              coef=options.coef,
                              header_flag=options.header_flag,
                              flat_max=options.flat_max)
    print("Done ({0}) at {1}.".format(ret_val,datetime.datetime.now()))