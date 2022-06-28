# Test correct piping of stdout of run.cmd()

import sys, os, pathlib
import run

# set environment variables
scriptpath = str(pathlib.Path(__file__).parent.absolute())

cmd = scriptpath + '/service.sh'
arg = [cmd]

run.cmd(arg)