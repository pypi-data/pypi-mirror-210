"""
Shell embedding into python as psh() 

Example: 
    print(psh("echo bash-version"))
"""
import os
import pathlib
import sys
import shutil
import tempfile
import textwrap


# Interact with command line
# TODO: test shcmd implementation and stick to it on linux box as well
# IS_WIN = sys.platform.startswith("win")
# if IS_WIN:
#     from . import shcmd as sh
# else:
#     import sh
from . import shcmd as sh


def get_tool(tool_name):
    try:
        return sh.Command(tool_name)
    except (sh.CommandNotFound, ImportError) as error:
        print("{} is not found on your PATH:\n\n{}".
              format(tool_name, os.environ["PATH"]))
        raise error


# Initiate CLI tools we require to interact with in via SHELL
bash = get_tool('bash')

def psh(*code_blocks):
    """Unwrap multiline bash code and run."""
    tmp_bash_code_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
    print("#!/bin/bash", file=tmp_bash_code_file)
    print("set -eu", file=tmp_bash_code_file)
    for code in code_blocks:
        cmd = [arg for line in textwrap.dedent(code).split("\n")
               for arg in line.split(" ") if arg.strip()]
        print(' '.join(cmd), file=tmp_bash_code_file)
    tmp_bash_code_file.close()
    script_path = pathlib.Path(tmp_bash_code_file.name + '.sh').as_posix()
    shutil.move(tmp_bash_code_file.name, script_path)

    try:
        res = bash(script_path)
    except Exception as error:
        print("---BEGIN-BASH-CODE---")
        print(open(script_path).read())
        print("---END-OF-BASH---")
        raise error
    os.unlink(script_path)
    return res
