import collections
import subprocess
import shlex

from .. import rich_core

#==============================================================================
#    Linux Access
#==============================================================================
def linux_command(cmd_list,msg=None):
    """Pass a shell-command as a list of components, to the shell."""
    assert(isinstance(cmd_list, collections.Sequence)), ("cmd_list must be a sequence")
    if msg in ['',None]:
        msg = "For shell call:\n{0}\nReceived errors:\n".format(
            ' '.join(cmd_list))
    else:
        assert(isinstance(msg, basestring))
        msg += "\nReceived error from shell call:\n"
        
    p = subprocess.Popen(cmd_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=256*1024*1024
        #bufsize=1
    )
    output, errors = p.communicate()
    
    if errors:
        raise EnvironmentError(msg+str(errors))
    return output


class LinuxCommand(object):
    """Operator. 
    (basestring or Sequence of basestring, NoneType or basestring) --> object 
    @todo Unit test this. Currently entirely untested
    """
    def __new__(cls, *args, **kwargs):
        return cls.__call__(*args, **kwargs)
    @classmethod
    def __call__(cls, commands, outfile=None):
        commands, outfile = cls.validate(commands, outfile)
        core_function = cls.dispatch(outfile)
        return core_function(commands, outfile)
    
    @classmethod
    def validate(cls, commands, outfile=None):
        if isinstance(cmds, basestring):
            commands = shlex.split(cmds)
        rich_core.AssertKlass(commands, rich_core.NonStringSequence, name='commands')
        rich_core.AssertKlass(outfile, (type(None),basestring, file), name='outfile')
        return commands, outfile
    @classmethod
    def dispatch(cls, outfile):
        if outfile == None:
            return cls._dispatch_on_none
        elif isinstance(outfile, basestring):
            return cls._dispatch_on_basestring
        elif isinstance(outfile, file):
            return cls._dispatch_on_file
        else:
            raise TypeError("Invalid outfile of type: "+str(type(outfile)))
        
    @classmethod
    def _dispatch_on_none(cls, commands, outfile):
        p = subprocess.Popen(commands,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=256*1024*1024)
        output, errors = p.communicate()
        if errors:
            raise EnvironmentError(str(errors))
        return output
    @classmethod
    def _dispatch_on_basestring(cls, commands, outfile):
        with open(outfile, 'w') as fi:            
            p = subprocess.Popen(commands,
                stdout=fi,
                stderr=subprocess.PIPE,
                bufsize=256*1024*1024)
            output, errors = p.communicate()
        if errors:
            raise EnvironmentError(str(errors))
        return errors
    @classmethod
    def _dispatch_on_file(cls, commands, outfile):
        p = subprocess.Popen(cmds,
            stdout=outfile,
            stderr=subprocess.PIPE,
            bufsize=256*1024*1024)
        errors = p.communicate()
        if errors:
            raise EnvironmentError(str(errors))
        return errors

class cd:
    """Context manager for changing the current working directory.
    
    with cd(CCCID.cache_dir):
        pass...
    
    """
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)