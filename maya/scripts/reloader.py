import sys


reload_list = [
    'action',
    'action.plugins',
    'connection',
    'connection.utils',
    'interface',
    'interface.delegate',
    'interface.model',
    'interface.widget',
]


def execute():

    from interface.widget import DockerMain
    DockerMain.instance.close()

    for mod in reload_list:
        try:
            __import__(mod)
            reload(sys.modules[mod])
        except Exception as err:
            print(err)
