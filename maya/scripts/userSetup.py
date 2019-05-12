from maya import cmds, mel


def setup(*_):
    print('--------Samkit starting--------')
    from interface.qtdocker import DockerMain
    import connection

    DockerMain.setup()
    layout = mel.eval('$tmp = $gAttributeEditorButton').split('|attributeEditorButton')[0]
    button = cmds.formLayout(layout, q=True, ca=True)[0]
    length = cmds.iconTextCheckBox(button, q=True, height=True)
    width = cmds.formLayout(layout, q=True, width=True) + length + 1
    cmds.formLayout(layout, e=True, width=width)
    btn = cmds.iconTextButton(
        parent=layout,
        width=length,
        height=length,
        image='tool_icon.svg',
        style='iconOnly',
        command=lambda *_: DockerMain.setup()
    )
    cmds.formLayout(layout, e=True, attachForm=[(btn, 'right', 1), (btn, 'top', 1)])
    cmds.scriptJob(event=['quitApplication', lambda *_: connection.session.close()])
    cmds.inViewMessage(message='Samkit Ready', position='midCenter', fade=True)


cmds.evalDeferred(setup)
