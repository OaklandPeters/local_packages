from math import exp
import os
from optparse import OptionParser
import pickle
import datetime
#---- Custom modules
from file_utility import CSVReader,CSVWriter
from organizers import FilePath
from generator_utility import gen_find_files


    
    
#====== Example calls: 
#    python normalize_csv.py --norm "flat" --output ./data_files/normalized_data.csv --coefficient 0.25 --header No ./data_files/HTVS_Docking_Output_2251.csv 2
#
#    python normalize_csv.py --norm "flat" --coefficient 0.25 --header No ./Lig_Lig_Shapes 1
#
#    python normalize_csv.py --norm "basic" --coefficient 0.25 --header No ./Post_Docking_Shape 

#====== Parameters:
#--norm    (variable name: norm_type): 
#    refers to the normalization function used.
#    'basic' - applies a sigmoid curve: f(x) = 1- abs(0.5 - (1 / (1 + exp(-alpha*x))*2 )
#        Where alpha is a customizable scalar coefficient (usually chosen 'by-hand' to maximize post-normalization variance)
#    'flat' - flatten



#====== Problems and To-Do:
#@problem:
#This will have problems when user provides input_path which is a directory
#   AND provides an output_path (ie single target output)
#@problem:
#this needs to accept a parameter to specify the 'flattened' range when the norm_type is 'flat'











#[] Mathematical Normalization functions
def sigmoid(x,coef=1):
    return 1 / (1 + exp(-coef*x))
def basic_normalization(diff,coef=1):
    #diff = target - ref
    return  1- abs(0.5 - sigmoid(diff,coef))*2
def flat_normalization(diff,coef=1,flat_range=[0,3]):
    if (diff>=flat_range[0]) and (diff<=flat_range[1]):
        return 1
    else:
        return basic_normalization(diff,coef)


#[] Core function
def apply_normalization(input_path,target_column,output_path=None,norm_type='flat',coef=1,header_flag=True):
    #This will have problems when user provides input_path which is a directory
    #   AND provides an output_path (ie single target output)
    
    record_parameters_flag = True
    record_population_flag = True
    
    if not os.path.exists(input_path):
        raise IOError("No such file or directory: {0}".format(input_path))
    if os.path.isdir(input_path):
        #input.file_names = [file_name for file_name in gen_find_files(input.in_path,".*") if os.path.isfile(file_name)]
        targets = [FilePath(input_path+os.sep+file_name) for file_name in gen_find_files(input_path,".*") if os.path.isfile(input_path+os.sep+file_name)]
    else:
        target = [FilePath(input_path)]
        #input.file_names = [input.in_path]
    
    target_column = int(target_column)  #ensure that target_column is an integer (so it can be an index to a row-list)
    
    file_counter = 1
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
    total_population = []
    
    #for target in input.file_names:
    for target in targets:
        in_csv = CSVReader(target.in_path,mode='r')   #parses file name --> in_csv.dir,in_csv.name,in_csv.ext
        
        #When no output_path provided, name each output based on input name
        if output_path is None:
            destination = FilePath(target.dir+os.sep+target.name+"_normalized"+target.ext)
        #When output_path provided, but input_path is directory (ie potentially multiple output files)
        if (output_path is not None) and (os.path.isdir(input_path)):
            out = FilePath(output_path)
            destination = FilePath(out.dir+os.sep+out.name+"_"+str(file_counter)+out.ext)
        out_csv = CSVWriter(destination.in_path,mode='w')
        #out_file = CSVWriter(output_name,mode='w')
        
        #[] Parse norm_type into a function call
        norm_parser = {'b':basic_normalization,
                       'basic':basic_normalization,
                       'f':flat_normalization,
                       'flat':flat_normalization}
        norm_function = norm_parser[norm_type]
        #[] Parse header flag
        if header_flag.lower() in ["true","yes","y","1"]:
            headers = in_csv.next()
            out_csv.write_row(headers + ["norm"])
            #out_file.write_row(headers + ["norm"])
    

        #[] Read input file
        for row in in_csv:
            norm = norm_function(float(row[target_column]),coef=coef)
            out_csv.write_row(row + [str(norm)])
            #out_file.write_row(row + [str(norm)])
            
            targets_range.check(row[target_column])
            norms_range.check(norm)
            if record_population_flag is True:
                total_population.append([row[target_column],norm])
        out_csv.close()
        file_counter += 1
    
    #Some parameters for analytic purposes
    if record_parameters_flag:
        with open(destination.dir+os.sep+"normalization_parameters_record.txt",'w') as record:
            msg = "Norm type = {0}, coefficient = {1}\n".format(norm_type,coef)
            msg += "Time = {0}\n".format(datetime.datetime.now())
            msg += "\nRange of target values = {0} to {1}\n".format(targets_range.min,targets_range.max)
            msg += "\nRange of normed values = {0} to {1}\n".format(norms_range.min,norms_range.max)
            record.write(msg)
            print(msg)        

    #Record population for more advanced analytic purposees
    if record_population_flag:
        pickle_file_name = destination.dir+os.sep+"total_population.pickle"
        pickle.dump(total_population,open(pickle_file_name,'wb'))
    return True



#[] Assemble command-line parameters
parser = OptionParser(usage="usage: %prog [options] input_path")
#parser.add_option("-i","--in_file",dest="in_file",
#                  action="store",type="string",
#                  help="Input file. Full path or relative path.",metavar="IN_FILE")


parser.add_option("-n","--norm",dest="norm_type",
                  action="store",type="string",default="basic",
                  help="Type of normalization to apply. Valid forms include: 'b'/'basic','f'/'flat'.",metavar="NORM_TYPE")
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

ret_val = apply_normalization(input_path=args[0],target_column=args[1],output_path=options.output_path,norm_type=options.norm_type,coef=options.coef,header_flag=options.header_flag)
print("Done ({0}) at {1}.".format(ret_val,datetime.datetime.now()))
