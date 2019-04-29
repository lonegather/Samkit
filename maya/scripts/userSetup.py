from maya import cmds, mel
from qtdocker import dock_window, DockerMain


def setup(*_):
    print('--------Samkit starting--------')

    layout = mel.eval('$tmp = $gAttributeEditorButton').split('|attributeEditorButton')[0]
    button = cmds.formLayout(layout, q=True, ca=True)[0]
    length = cmds.iconTextCheckBox(button, q=True, height=True)
    width = cmds.formLayout(layout, q=True, width=True) + length + 1
    cmds.formLayout(layout, e=True, width=width)
    btn = cmds.iconTextCheckBox(
        parent=layout,
        width=length,
        height=length,
        image='tool_icon.svg',
        style='iconOnly'
    )
    cmds.formLayout(layout, e=True, attachForm=[(btn, 'right', 1), (btn, 'top', 1)])

    win = dock_window(DockerMain)
    cmds.inViewMessage(message='Samkit Ready', position='midCenter', fade=True)


cmds.evalDeferred(setup)
