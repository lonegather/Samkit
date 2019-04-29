import os
import sys
from maya import cmds

separator = ';' if cmds.about(nt=True) else ':'
ENV_PYTHONPATH = os.getenv('PYTHONPATH').split(separator)
ENV_PYTHONPATH = list(os.path.realpath(p) for p in ENV_PYTHONPATH)
SYS_PATH = list(os.path.realpath(p) for p in sys.path)

for path in ENV_PYTHONPATH:
    if path not in SYS_PATH:
        sys.path.append(path)
