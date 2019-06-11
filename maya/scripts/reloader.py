import sys


reload_list = [
    'samkit',
    'samcon',
    'samcon.utils',
    'samgui',
    'samgui.delegate',
    'samgui.model',
    'samgui.widget',
]


def execute():

    from samgui.widget import DockerMain
    DockerMain.instance.close()

    for mod in reload_list:
        try:
            __import__(mod)
            reload(sys.modules[mod])
        except Exception as err:
            print(err)
