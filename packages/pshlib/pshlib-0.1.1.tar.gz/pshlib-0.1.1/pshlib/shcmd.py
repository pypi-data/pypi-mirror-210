"""
Revamp of https://github.com/amoffat/sh for much simpler shell embedding.
"""
import os
import subprocess
import sys
import logging
import contextlib
from pathlib import Path
import tempfile


logger = logging.getLogger(__name__)


IS_PY3 = sys.version_info[0] == 3
if IS_PY3:
    raw_input = input
    unicode = str


@contextlib.contextmanager
def working_directory(path):
    """Changes working directory and returns to previous on exit."""
    prev_cwd = Path.cwd()
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(prev_cwd)


def find_executable(executable, path=None):
    """Find if 'executable' can be run. Looks for it in 'path'
    (string that lists directories separated by 'os.pathsep';
    defaults to os.environ['PATH']). Checks for all executable
    extensions. Returns full path or None if no command is found.
    """
    if path is None:
        path = os.environ['PATH']
    paths = path.split(os.pathsep)
    extlist = ['']
    if sys.platform == 'win32':
        pathext = os.environ['PATHEXT'].lower().split(os.pathsep)
        (base, ext) = os.path.splitext(executable)
        if ext.lower() not in pathext:
            extlist = pathext
    for ext in extlist:
        execname = executable + ext
        if os.path.isfile(execname):
            return execname
        else:
            for p in paths:
                f = os.path.join(p, execname)
                if os.path.isfile(f):
                    return f
    else:
        return None


class CommandNotFound(Exception): pass


class ShellError(Exception):
    """Critical shell error has occurred."""


class ShellCommandResult:

    def __init__(self):
        self.return_code = 0
        self.output = ""
        self.error = ""

    @property
    def stdout(self):
        return self.output

    @property
    def stderr(self):
        return self.error

    def parse(self, process, tmp_out_file=None, tmp_err_file=None):
        """Parse process results."""
        # return code
        self.return_code = process.returncode
 
        # output
        if tmp_out_file is not None:
            # go to first line of tmp_out_file
            tmp_out_file.seek(0)
            for line in tmp_out_file:
                line = line.decode("utf8").rstrip("\n")
                logger.debug(line)
                self.output += f"{line}\n"
        else:
            for line in (iter(proc.stdout.readline, b'')):
                line = line.decode("utf8").strip()
                logger.debug(line)
                self.output += f"{line}\n"
    
        # error
        if tmp_err_file is not None:
            # go to first line of tmp_err_file
            tmp_err_file.seek(0)
            for line in tmp_err_file:
                line = line.decode("utf8").strip()
                logger.error(line)
                self.error += f"{line}\n"
        else:
            for line in (iter(proc.stdout.readline, b'')):        
                line = line.decode("utf8").strip()
                logger.error(line)
                self.error += f"{line}\n"
     
        def __str__(self):
            return self.__unicode__()
     
        def __unicode__(self):
            """To string"""
            if self.return_code > 0:
                return None
            return self.output
     
        def __eq__(self, other):
            return unicode(self) == unicode(other)
     
        def __repr__(self):
            """ in python3, should return unicode.  in python2, should return a
            string of bytes """
            try:
                return str(self)
            except UnicodeDecodeError:
                if self.process:
                    if self.stdout:
                        return repr(self.stdout)
                return repr("")
     
        def __long__(self):
            return long(str(self).strip())
     
        def __float__(self):
            return float(str(self).strip())
     
        def __int__(self):
            return int(str(self).strip())


def Command(exec_path, params=None, fail_on_error=True, use_tmpfile_io=True):
    """Return function that runs a shell command."""
    logger.debug("Creating shell command: {}".format(exec_path))
    if "/" not in exec_path:
        # locate executable on the system PATH
        exec_path = find_executable(exec_path)
    if not exec_path or not os.path.exists(exec_path):
        raise IOError("Executable path not found: {}", exec_path)
    if params is None:
        params = dict()
    
    def _shell_fn(*args):
        if args is None:
            args = list()
        else:
            # assume iterable
            args = list(args)
        cmd = [exec_path] + args
        logger.info("running {}".format(cmd))        
        
        if use_tmpfile_io:
            tmp_out_file = tempfile.TemporaryFile()
            tmp_err_file = tempfile.TemporaryFile()
            stdout = tmp_out_file
            stderr = tmp_err_file
        else:
            stdout = subprocess.PIPE
            stderr = subprocess.PIPE
    
        proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr)
        proc.wait()
    
        # Parse result
        result = ShellCommandResult()
        result.parse(proc, tmp_out_file, tmp_err_file)
        if fail_on_error and result.return_code > 0:
            raise ShellError("ShellError(returncode: {}): {} \nERROR: {}"
                                .format(result.return_code, result.output, result.error))
        return result
    
    return _shell_fn