import sys
import os
from maya import cmds

module_path = cmds.moduleInfo(path=True, moduleName='Samkit')
site_package = os.path.join(module_path, 'pydist/python-2.7.11.amd64/Lib/site-packages')

if site_package not in sys.path:
    sys.path.append(site_package)

print("Samkit say hello")
