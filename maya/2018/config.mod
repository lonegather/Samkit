+ PLATFORM:win64 MAYAVERSION:2018 CGPiper 1.0 ./2018/
PYTHONPATH+:= ./pydist/python-2.7.11.amd64/Lib/site-packages
PYBLISH_QML_PYTHON_EXECUTABLE:= ./pydist/python-2.7.11.amd64/python.exe
MAYA_PLUG_IN_PATH+:= ./plug-ins
scripts: ../commons/scripts
icons: ../commons/icons

+ PLATFORM:win64 MAYAVERSION:2016 CGPiper 1.0 ./2016/
PYTHONPATH+:= ./pydist/python-2.7.11.amd64/Lib/site-packages
PYBLISH_QML_PYTHON_EXECUTABLE:= ./pydist/python-2.7.11.amd64/python.exe
MAYA_PLUG_IN_PATH+:= ./plug-ins
scripts: ./scripts
icons: ./icons
